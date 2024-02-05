#!/bin/bash

# Setting environment variables
export OPENAI_API_KEY="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"
export PLATFORM="managed"
export ROOT_PW="admin"
export ROOT_USER="root"
export SERVICE_NAME="beta-chattutor"
export SQL_DB="chatmsg"
export SQL_DB_HOST="34.41.31.71"
export SQL_DB_PASSWORD="AltaParolaPuternica1245"
export SQL_DB_USER="admin"
export STAT_SQL_DB="sessiondat"
export TRIGGER_ID="15c370bb-664a-45db-b8f9-a3f1322085c8"
export VECTOR_DB_HOST="34.133.39.77:8000"

python main.py
