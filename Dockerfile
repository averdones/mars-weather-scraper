FROM python:3.10

# Set up the Chrome PPA
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Install google chrome
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# Install Chromedriver version that matches Chrome version
RUN BROWSER_MAJOR=$(google-chrome --version | sed 's/Google Chrome \([0-9]*\).*/\1/g') && \
  wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${BROWSER_MAJOR} -O chromedriver_version && \
  wget https://chromedriver.storage.googleapis.com/`cat chromedriver_version`/chromedriver_linux64.zip && \
  unzip chromedriver_linux64.zip chromedriver -d /usr/local/bin/

COPY requirements.txt /usr/local/bin/requirements.txt
WORKDIR /usr/local/bin
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /usr/local/bin
ENTRYPOINT ["python", "main.py"]