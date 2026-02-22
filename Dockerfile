FROM python:3.14.2-slim-trixie

# Set the working directory in the container
WORKDIR /app

# Instalar Chromium y todas sus dependencias
RUN apt-get update && apt-get install -y \
    chromium curl\
    chromium-driver \
    libxcb1 libx11-6 libxcomposite1 libxrender1 libxext6 libxfixes3 \
    libxi6 libxrandr2 libxss1 libxtst6 libglib2.0-0 libnss3 libnspr4 \
    libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libdbus-1-3 \
    libfontconfig1 libgbm1 libgtk-3-0 libxkbcommon0 libasound2 \
    fonts-liberation fonts-noto-color-emoji xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Configurar variables de entorno para Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER=/usr/bin/chromedriver

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python","src/daemon.py","--run"]

# docker build . -t realadvisor:22.02.21 -t realadvisor:latest
# docker run -it realadvisor /bin/bash
# docker rmi -f $(docker images -f "dangling=true" -q)