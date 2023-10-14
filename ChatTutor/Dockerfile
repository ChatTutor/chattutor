FROM python:3.11-bookworm

ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
ENV PORT 5000
EXPOSE 5000
ENV CHATUTOR_GCP TRUE
ENV OPENAI_OPEN = 

WORKDIR $APP_HOME

COPY . ./

# Install dependencies
RUN apt-get update && apt-get install -y wget build-essential libreadline-dev zlib1g-dev

# Download, compile, and install SQLite 3.35.0 or newer from source
# RUN wget https://www.sqlite.org/src/tarball/sqlite.tar.gz?r=release -O sqlite.tar.gz
# RUN tar xzf sqlite.tar.gz
# RUN cd sqlite/ && ./configure
# RUN cd sqlite/ && make
# RUN cp sqlite/sqlite3.[ch] pysqlite3/
# RUN cd pysqlite3 && python setup.py build_static build

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/* && rm -rf sqlite-autoconf-3430200.tar.gz && rm -rf sqlite-autoconf-3430200

RUN echo "/usr/local/lib" > /etc/ld.so.conf.d/sqlite3.conf && ldconfig

# CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app

CMD ["python", "main.py"]
