FROM python:3.9

ENV PYTHONPATH /ultimate_procrastination

WORKDIR /ultimate_procrastination

COPY api /ultimate_procrastionation/api
COPY database /ultimate_procrastionation/database

COPY wiki_searcher /ultimate_procrastination/wiki_seacher

COPY wait-for-port-availability.sh /ultimate_procrastionation/
COPY requirements.txt /ultimate_procrastionation/


RUN apt-get update && apt-get install -y libpq-dev gcc
RUN pip3 install -r /ultimate_procrastionation/requirements.txt

# alembic
COPY alembic.ini /ultimate_procrastionation/
COPY alembic /ultimate_procrastionation/alembic