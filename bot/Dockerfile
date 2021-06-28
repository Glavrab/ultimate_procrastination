FROM python:3.9

ENV PYTHONPATH /ultimate_procrastination

WORKDIR /ultimate_procrastination

COPY bot /ultimate_procrastionation/bot
COPY requirements.txt /ultimate_procrastionation/

RUN apt-get update && apt-get install -y libpq-dev gcc
RUN pip3 install -r /ultimate_procrastionation/requirements.txt
