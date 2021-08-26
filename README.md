# Ultimate Procrastination

### Table of content
* [About](#about)
* [About technical details](#about-technical-details)
    * [How it works](#how-it-works)
    * [Telegram Bot](#telegram-bot)
    * [Web service](#web-service)
* [Deploy](#deploy)
    * [Build](#build)
    * [Project's settings](#projects-settings)
    
## About

It is a system to provide support for your procrastination and as a bonus increasing your intelligence level!
When you don't know what to do, or you know but don't want to bother yourself with necessary task this service will help you out!
Giving you literally infinite amount of unimportant but interesting facts.
After small registration you can configure your own feed and receive the information about categories you prefer most.


## About Technical details

This project currently contains telegram bot and a back-end web-service.

**Current stack**: python3.9+, asyncio(lots of it), aiohttp(as main web-service), postgreSQL(operated by gino)
aiogram(as Telegram Bot), Redis(for storing session data), Docker.

### How it works

![Current scheme](https://github.com/Glavrab/ultimate_procrastination/blob/web_app%2Bbot/docs/working_scheme.png?raw=true)
### Telegram Bot

Telegram bot is written using aiogram. Currently, receiving update object from telegram using long pooling.
It communicates with web service by HTTP.

### Web service

Web service is written on aiohttp. 
Currently, it handles requests from bot users. In future some front-end service will be added.


## Deploy

### Build

You need to have docker and docker-compose installed.

1. Create project dir named ultimate_procrastination;
2. Clone this repo;
3. Create `.env` and `config.json` file. About .env and config.json files
4. Run `docker-compose build`;
5. Start with running `docker-compose up`.
6. To fill db with titles run searcher.py 

```shell script
$ mkdir ultimate_procrastination
$ cd ultimate_procrastination
$ git clone https://github.com/Glavrab/ultimate_procrastination
$ vim .env
$ vim config.json
$ docker-compose build
$ docker-compose up
$ python3 wiki_searcher/searcher.py
```

### Project's settings
`.env` file composition. Values appear in docker-compose.yaml

1. POSTGRES_PASSWORD
2. REDIS_PASSWORD

```shell script
POSTGRES_PASSWORD="POSTGRES_PASSWORD123"
REDIS_PASSWORD="REDIS_PASSWORD123"
```

`config.json` file composition. Since it's not even MVP we use gmail smtp server without oauth2 just with password
and account name. In order to use it you have to [allow less secure apps.](https://myaccount.google.com/lesssecureapps)
In the future, we will use some service to be more secure.

1. telegram_token
2. apply_migration
3. pg_host
4. pg_username
5. pg_password
6. pg_port
7. pg_db
8. debug_status
9. redis_password
10. smtp_server
11. service_account_name
12. service_account_password

```json
{
  "telegram_token": "bot_token123",
  "apply_migration": "head",
  "pg_host": "db",
  "pg_username": "procrastination_admin",
  "pg_password":"POSTGRES_PASSWORD123",
  "pg_port": 5432,
  "pg_db": "ultimate_procrastination",
  "debug_status": "True",
  "redis_password": "REDIS_PASSWORD123",
  "smtp_server": "smtp.gmail.com",
  "service_account_name": "service@gmail.com",
  "service_account_password": "secret_password1234"
}
```
## Developers

Project is initially developed and maintained by [Alexey Baranov](https://github.com/Glavrab).
Reviewed by [Dennis Dobrovolsky](https://github.com/AngliD).
