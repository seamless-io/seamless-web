FROM python:3.6

ADD postgres_requirements.txt /tmp/requirements.txt
RUN cd /tmp && pip install -U -r requirements.txt

ENV PYTHONPATH=/src

WORKDIR /src

ADD . /src