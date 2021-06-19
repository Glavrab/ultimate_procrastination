FROM python:3.9
LABEL project=ultimate_procrastination

WORKDIR /ultimate_procrastination
ENV PYTHONPATH /ultimate_procrastination

COPY api /ultimate_procrastination/api
COPY database /ultimate_procrastination/database
COPY shared /ultimate_procrastination/shared
COPY wiki_searcher /ultimate_procrastination/wiki_searcher

COPY wait-for-port-availability.sh /ultimate_procrastination/
COPY requirements.txt /ultimate_procrastination/

RUN apt-get update && apt-get install -y libpq-dev gcc
RUN pip3 install -r /ultimate_procrastination/requirements.txt

COPY alembic.ini /ultimate_procrastination/
COPY alembic /ultimate_procrastination/alembic