from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
import logging
import argparse
import yaml
from datetime import datetime, timedelta


def validate_config(config):
    """
    Validates the provided configuration dictionary to ensure all required keys and values are present.

    :param config: The configuration dictionary to validate.
    :raise ValueError: If a required key or value is missing.
    """

    required_keys = [
        'settings.logLevel',
        'settings.email.server',
        'settings.email.port',
        'settings.email.from',
        'settings.email.subject',
        'settings.email.body',
        'settings.email.username',
        'config[0].url',
        'config[0].email'
    ]

    for key in required_keys:
        parts = key.split('.')
        current = config

        for part in parts:
            if '[' in part and ']' in part:  # handle list indices
                section = part.split('[')[0]
                index = int(part.split('[')[1].split(']')[0])
                if section not in current or len(current[section]) <= index:
                    raise ValueError(f"Missing or insufficient items in section: {section}")
                current = current[section][index]
            else:  # handle dictionary keys
                if part not in current:
                    raise ValueError(f"Missing key: {key}")
                current = current[part]

        if not current:  # Check for empty string or None values
            raise ValueError(f"Value for {key} is not provided or empty.")


def parse_arguments():
    """
    Parses command-line arguments.

    :return: A namespace containing the arguments provided by the user.
    """
    parser = argparse.ArgumentParser(description="Vulnerability pro")

    # Argument for the configuration file
    parser.add_argument("-c", "--config", type=str, required=True,
                        help="Path to the configuration YAML file.")

    return parser.parse_args()


def main():
    args = parse_arguments()
    with open(args.config, 'r') as file:
        obj_config = yaml.safe_load(file)
    validate_config(obj_config)

    logging.basicConfig(level=getattr(logging, 'INFO'),
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    str_username = os.environ.get('SYSDIG_USERNAME')
    str_password = os.environ.get('SYSDIG_PASSWORD')
    str_email_server_password = os.environ.get('EMAIL_SERVER_PASSWORD')
    if str_username is None \
            or str_password is None \
            or str_email_server_password is None:
        print('Please ensure SYSDIG_USERNAME, SYSDIG_PASSWORD and EMAIL_SERVER_PASSWORD environment variables are set')
        exit(1)

    for index, item in enumerate(obj_config['config']):
        logging.info(f"Processing item no: {index}")
        logging.info(f"Processing URL:{item['url']}")
        logging.info(f"Processing Email:{item['email']}")
        str_vuln_url = item['url']


        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument(f"--window-size={obj_config['settings']['screen']['width']}x{obj_config['settings']['screen']['height']}")
        driver = webdriver.Chrome(options=chrome_options)

        # Today
        today = datetime.now().date()
        # Yesterday
        yesterday = today - timedelta(days=1)

        # Midnight epoch
        start_date = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0)
        # End of day
        end_date = start_date + timedelta(days=1) - timedelta(seconds=1)

        # Epoch as int
        int_start_epoch = int(start_date.timestamp())
        int_end_epoch = int(end_date.timestamp())

        str_today_vuln_url = str_vuln_url + f"&from={int_start_epoch}&to={int_end_epoch}"

        driver.implicitly_wait(10)
        logging.info('Getting URL')
        driver.get(str_today_vuln_url)
        logging.info('Setting Username')
        id_username = driver.find_element(by=By.NAME,
                                          value='username')
        id_username.click()
        id_username.send_keys(str_username)

        logging.info('Setting Password')
        id_password = driver.find_element(by=By.NAME,
                                          value='password')
        id_password.click()
        id_password.send_keys(str_password)

        logging.info('Logging In')
        id_submit = driver.find_element(by=By.XPATH,
                                        value="//button[@type='submit']")
        id_submit.click()

        wait = WebDriverWait(driver=driver,
                             timeout=driver.timeouts.implicit_wait)

        driver.find_element(By.XPATH, '//div[@data-test="app-nav-collapse-btn"]').click()

        # Wait for the data to be visible

        try:
            for str_wait in item['waits'][0].values():
                logging.info(f"Waiting for {str_wait}")
                wait.until(EC.visibility_of_element_located(locator=(By.XPATH, str_wait)))
        except Exception as e:
            logging.error(f"An error occurred waiting for the display: {e}, continuing anyway")

        str_screenshot = "RuntimeVulns.png"
        logging.info('Taking screenshot')
        driver.save_screenshot(str_screenshot)
        logging.info('Cleaning up.  Running driver.quit()')
        driver.quit()

        # Email the screenshot as an inline image
        logging.info('Emailing enter()')
        str_sender = obj_config['settings']['email']['from']
        str_receiver = item['email']
        str_subject = obj_config['settings']['email']['subject']
        str_body = obj_config['settings']['email']['body']

        msg = MIMEMultipart('alternative')
        msg['From'] = str_sender
        msg['To'] = str_receiver
        msg['Subject'] = str_subject

        # Attach the plain text
        msg.attach(MIMEText(str_body, 'plain'))

        # Attach the PNG image inline
        with open(str_screenshot, 'rb') as img:
            mime_img = MIMEImage(img.read())
            mime_img.add_header('Content-ID', '<screenshot>')
            mime_img.add_header('Content-Disposition', 'inline', filename=str_screenshot)
            msg.attach(mime_img)

        # Attach HTML version referencing the inline image
        html_body = f'{str_body}<br><img src="cid:screenshot">'
        msg.attach(MIMEText(html_body, 'html'))

        text = msg.as_string()

        # Set up the SMTP server
        server = smtplib.SMTP(obj_config['settings']['email']['server'], obj_config['settings']['email']['port'])
        server.starttls()
        server.login(obj_config['settings']['email']['username'], str_email_server_password)
        server.sendmail(str_sender, str_receiver, text)
        server.quit()
        logging.info('Emailing exit()')

        # Cleanup: Delete the screenshot
        os.remove(str_screenshot)
        logging.info('')
    logging.info('finished')


if __name__ == '__main__':
    main()
