FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

# Ffmpeg ko optimized tarike se install kiya hai taaki memory crash na ho
RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends curl unzip xz-utils \
    && curl -O https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz \
    && tar xvf ffmpeg-release-amd64-static.tar.xz \
    && mv ffmpeg-*-static/ffmpeg /usr/local/bin/ \
    && mv ffmpeg-*-static/ffprobe /usr/local/bin/ \
    && rm -rf ffmpeg-* \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install -U pip && pip3 install -U -r requirements.txt

COPY . .

# Syntax error fix kar diya hai (Agar script ka naam sirf 'start' hai toh '.sh' hata dena)
CMD ["bash", "start.sh"]
