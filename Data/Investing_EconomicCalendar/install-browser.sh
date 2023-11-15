#!/bin/bash
echo "Downloading Chromium..."
curl "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1203200%2Fchrome-linux.zip?generation=1695993725821995&alt=media" > /tmp/chromium.zip
unzip /tmp/chromium.zip -d /tmp/
mv /tmp/chrome-linux/ /opt/chrome
curl "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1203200%2Fchromedriver_linux64.zip?generation=1695993729397198&alt=media" > /tmp/chromedriver_linux64.zip
unzip /tmp/chromedriver_linux64.zip -d /tmp/
mv /tmp/chromedriver_linux64/chromedriver /opt/chromedriver