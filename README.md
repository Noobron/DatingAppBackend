# DatingAppBackend

This is the repository to handle the backend part for the [DatingAppFrontend](https://github.com/Noobron/DatingAppFrontend) 

It uses [Django REST framework](https://www.django-rest-framework.org/) to work with the API requests made by the client.

# Dependencies

- [PostgreSQL](https://www.postgresql.org/)

- [Redis](https://redis.io/) (or [Memurai](https://www.memurai.com/) for Windows)

- [Cloudinary](https://cloudinary.com/) Account

# Setup

This backend solution uses Django's WSGI server to handle HTTPS requests and ASGI server to handle WSS requests. And [Celery](https://docs.celeryproject.org/en/stable/) to run cron jobs.

To run the servers on HTTPS and WSS, trusted SSL certificates are required.

For a temporary solution, [this repository](https://github.com/RubenVermeulen/generate-trusted-ssl-certificate) can be used to generate and trust SSL certificates.

 
**Note: The commands below should be executed in the working directory set as the location of the project.**


To install the python packages, run the following command in the working directory.

```console
$ pip install -r /path/to/requirements.txt
```

It uses an ```.env``` file present in /path/to/DatingAppBackend/DatingAppBackend/ to set the initial configurations.

The contents of the ```.env``` are as follows

```
SECRET_KEY=<secret_key>
DATABASE_NAME=<db_name>
DATABASE_USER=<db_user_anme>
DATABASE_PASS=<db_password>
DB_ENGINE_PORT=<db_server_port>
DB_ENGINE_HOST=<db_server_hostname>
LOG_FILE=<log_file_location>
DOMAIN_URL=<domain_url>
CLOUDINARY_CLOUD_NAME=<cloudinary_account_name>
CLOUDINARY_API_KEY=<cloudinary_api_key>
CLOUDINARY_API_SECRET=<cloudinary_api_secret>
DEFAULT_PROFILE_URL=<image_file_url>
REDIS_HOST=<redis_server_hostname>
REDIS_PORT=<redis_server_port>
CELERY_BROKER_URL=<celery_broker_url>
```

The files for migration to create the database are available in the repository. To run the migrations, run the command below

```console
$ python manage.py migrate
```

To run the WSGI server, execute the command

```console
$ python manage.py runsslserver --certificate /path/to/server.crt --key /path/to/server.key
```

For the ASGI server, execute the command

```console
$ daphne -e ssl:8001:privateKey=/path/to/server.key:certKey=/path/to/server.crt DatingAppBackend.asgi:application 
```

Cron jobs are handled by Celery. To start the service, run 

```console
$ celery -A DatingAppBackend worker -l info -P gevent  
```


