#!/bin/bash
cd ./frontend
npm install
npm run build
cd ..
PORT=5000
gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app