FROM python:3.11-slim

RUN apt update
RUN apt-get -y install unzip curl wget pip
RUN pip install selenium
RUN apt-get -y install chromium=116.0.5845.180-1~deb12u1
RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/117.0.5938.62/linux64/chromedriver-linux64.zip
RUN unzip chromedriver-linux64.zip
RUN mv ./chromedriver-linux64/chromedriver /usr/bin/chromedriver
RUN chown root:root /usr/bin/chromedriver
RUN chmod +x /usr/bin/chromedriver

# Copy script into the container.  Just set your configuration file as appropriate, or rebuild container to pass in... up to you
COPY runtimeVulnEmail.py /app/runtimeVulnEmail.py
COPY runtimeVulnEmail-config.yaml /app/runtimeVulnEmail-config.yaml

# Set the working directory to /app
WORKDIR /app

# The command that will be executed when the container starts
CMD ["python3", "/app/runtimeVulnEmail.py", "--config /app/runtimeVulnEmail-config.yaml"]
