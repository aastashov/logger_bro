FROM python:3.9-alpine

RUN apk add --no-cache gcc g++

WORKDIR /srv/app

COPY requirements.txt /srv/app/requirements.txt
RUN pip install --no-cache-dir -r /srv/app/requirements.txt

COPY . /srv/app

CMD ["python", "manage.py", "--runbot"]
