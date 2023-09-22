FROM python:3.11-slim

RUN apt update \ 
  && apt-get -y install unzip curl wget pip chromium=117.0.5938.62-1~deb12u1 \
  && wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/117.0.5938.62/linux64/chromedriver-linux64.zip \
  && unzip chromedriver-linux64.zip \
  && mv ./chromedriver-linux64/chromedriver /usr/bin/chromedriver \
  && chown root:root /usr/bin/chromedriver \
  && chmod +x /usr/bin/chromedriver

# Copy script into the container. Just set your configuration file as appropriate, or rebuild container to pass in... up to you
COPY runtimeVulnEmail.py requirements.txt /app/

# Set the working directory to /app
WORKDIR /app

RUN pip install -r requirements.txt

#Run as non root
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# The command that will be executed when the container starts
CMD ["python3", "/app/runtimeVulnEmail.py", "--config", "/app/config.yaml"]
