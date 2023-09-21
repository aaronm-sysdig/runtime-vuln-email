FROM python:3.11-slim

RUN apt-get update
RUN apt-get -y install unzip curl wget pip nano
RUN pip install selenium pyyaml
RUN apt-get -y install chromium=117.0.5938.62-1~deb12u1
RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/117.0.5938.62/linux64/chromedriver-linux64.zip
RUN unzip chromedriver-linux64.zip
RUN mv ./chromedriver-linux64/chromedriver /usr/bin/chromedriver
RUN chown root:root /usr/bin/chromedriver
RUN chmod +x /usr/bin/chromedriver

# Copy your script into the container
COPY runtimeVulnEmail.py /app/runtimeVulnEmail.py

#Run as non root
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Set the working directory to /app
WORKDIR /app

# The command that will be executed when the container starts
CMD ["python3", "/app/runtimeVulnEmail.py", "-c" ,"/app/config.yaml"]
