FROM python:3.9

LABEL project=ultimate_procrastination
WORKDIR /ultimate_procrastination

ENV PYTHONPATH /ultimate_procrastination

COPY shared /ultimate_procrastination/shared
COPY bot /ultimate_procrastination/bot
COPY requirements.txt /ultimate_procrastination/

RUN apt-get update && apt-get install -y libpq-dev gcc
RUN pip3 install -r /ultimate_procrastination/requirements.txt
