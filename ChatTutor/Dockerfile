

# ---- Build Angular App ----
FROM node:18.10 AS build-angular
ARG ANGULAR_ENV=production
WORKDIR /app/frontend
RUN echo "current directory $(pwd)"

COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend ./
# RUN npm run build
RUN npm run build -- --configuration=${ANGULAR_ENV}

# ---- Python Setup ----
FROM python:3.11-bookworm
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
ENV PORT 5000

WORKDIR $APP_HOME

# Install system dependencies
RUN apt-get update && apt-get install -y wget build-essential libreadline-dev zlib1g-dev

# Copy built Angular app from build-angular stage
COPY --from=build-angular /app/frontend/dist /app/frontend/dist

# Copy backend (Flask) app files
COPY . ./

# Install Python dependencies -- TODO: remove --no-cache-dir
#RUN #pip install --no-cache-dir -r requirements.txt
RUN python3 -m pip install -r requirements.txt
RUN python3 -m nltk.downloader words

# RUN pip install -r requirements.txt

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/* && rm -rf sqlite-autoconf-3430200.tar.gz && rm -rf sqlite-autoconf-3430200
RUN echo "/usr/local/lib" > /etc/ld.so.conf.d/sqlite3.conf && ldconfig

#CMD exec ls -a
EXPOSE 5000
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app


