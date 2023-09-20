# Disclaimer

Notwithstanding anything that may be contained to the contrary in your agreement(s) with Sysdig, Sysdig provides no support, no updates, and no warranty or guarantee of any kind with respect to these script(s), including as to their functionality or their ability to work in your environment(s).  Sysdig disclaims all liability and responsibility with respect to any use of these scripts. 

# runtime-vuln-email
A selenium based system that takes a screenshot of your sysdig UI and emails it.

# Execution
Simply run
`python runtime-vuln-email.py --config <path to config file>`

# Configuration
Achieved via a yaml file.  Items speak for themselves for the most part but some items worth mentioning

- Screen size can be set with the `screen.width` and `screen.height` parameters
- Email password must be an environment variable called `EMAIL_SERVER_PASSWORD`
- Sysdig username and password crendentials need to be environment variables called `SYSDIG_USERNAME` and `SYSDIG_PASSWORD` respectively
- the `waits` section needs a little explanation.  The script is configured to after logging in and navigating to your URL, to wait for the data to be visible.  This is achieved via a series of `XPath` waits.  The example is for the vulns to ensure they are visible before the screenshot is taken

```
# Remember to configure SYSDIG_USERNAME, SYSDIG_PASSWORD and EMAIL_SERVER_PASSWORD as environment variables
settings:
  logLevel: DEBUG
  screen:
    width: 1400
    height: 850
  email:
   server: smtp.gmail.com #password needs to be an environment variable called EMAIL_SERVER_PASSWORD
   username: miles3719@gmail.com
   port: 587
   from: sysdig@aamiles.org
   subject: Runtime Vulnerabilities Screenshot
   body: Please find below the latest runtime Vulnerabilities.

config: # the date for 'yesterday' will be appended to the URLS specified below via the &from= and &to=
  - url: https://app.au1.sysdig.com/secure/#/vulnerabilities/overview/runtime?filter=context+%3D+%22runtime%22&cve=vulnSeverity+in+%28%22Critical%22%2C+%22High%22%29+and+vulnIsRunning+%3D+true
    email: miles3719@gmail.com
    waits: #Configure XPATH waits so that the screenshot is as you want (ie: the data is visible).  These are passed into visibility_of_element_located
      - 1: //div[@data-test="collapsible-block-open"]//div[text()="Policies"]
        2: //div[@title="Namespace"]//span[text()="Namespace"]
        3: (//div[@data-test="panel-wrapper"]//div[@title="Vulnerability Name"])[1]
        4: (//div[@data-test="panel-wrapper"]//div[@title="Vulnerability Name"])[2]
  - url: https://app.au1.sysdig.com/secure/#/vulnerabilities/overview/runtime?filter=context+%3D+%22runtime%22&cve=vulnSeverity+in+%28%22Critical%22%2C+%22High%22%29+and+vulnIsRunning+%3D+true
    email: anotheremail@gmail.com
    waits: #Configure XPATH waits so that the screenshot is as you want (ie: the data is visible).  These are passed into visibility_of_element_located
      - 1: //div[@data-test="collapsible-block-open"]//div[text()="Policies"]
        2: //div[@title="Namespace"]//span[text()="Namespace"]
        3: (//div[@data-test="panel-wrapper"]//div[@title="Vulnerability Name"])[1]
        4: (//div[@data-test="panel-wrapper"]//div[@title="Vulnerability Name"])[2]
```
