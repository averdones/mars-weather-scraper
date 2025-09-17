FROM python:3.10

# Install Chrome (browser)
RUN apt-get update && apt-get install -y wget gnupg \
 && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
 && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
 && apt-get update && apt-get install -y google-chrome-stable

# Copy and setup your application
COPY . /app
WORKDIR /app

# Install your dependencies (selenium >= 4.10)
RUN pip install --upgrade pip && pip install selenium>=4.10 -r requirements.txt

ENTRYPOINT ["python", "upload_daily_weather.py"]