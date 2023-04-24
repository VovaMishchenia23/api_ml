FROM python:3.9

RUN apt-get update
RUN apt-get install -y build-essential python3-dev libpq-dev libffi-dev libssl-dev
RUN /usr/local/bin/python -m pip install --upgrade pip

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["flask", "--app", "api", "run", "--host=0.0.0.0"]