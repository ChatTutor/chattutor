FROM 3.11-bullseye
ENV PYTHONUNBUFFERED True

RUN apt update
WORKDIR /app
ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

CMD ["gunicorn", "app:app", "--config=config.py"]
