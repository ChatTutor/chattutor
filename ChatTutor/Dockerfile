FROM python:3.11-bullseye

ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
ENV PORT 5000
EXPOSE 5000

WORKDIR $APP_HOME

COPY . ./

# Install dependencies
RUN apt-get update && apt-get install -y wget build-essential libreadline-dev zlib1g-dev

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/* && rm -rf sqlite-autoconf-3430200.tar.gz && rm -rf sqlite-autoconf-3430200

RUN echo "/usr/local/lib" > /etc/ld.so.conf.d/sqlite3.conf && ldconfig

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app

# CMD ["python", "main.py"]
