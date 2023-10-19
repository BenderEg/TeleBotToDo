This bot helps to be effective and don't forget important things to do.

Technology stack:

1. Python;
2. Aiogram3;
3. SQLAlchemy;
4. Redis;
5. Pydantic;
6. Postgresql;
7. Docker.

It is possible to start bot in two modes:

1. In development mode: in this case only Postgresql and Redis instances are containerised. App with telegram bot
is started from IDE (docker compose -f compose-dev.yaml up -d).
2. Production mode: for running on server two more containers are included. Main app and also cleaner, which is
cron job for removing outdated task from Postgresql database (docker compose up -d).

To start create .envdev file for development mode or .env file for production mode (see .env_example for more information).
Than create docker network to_do (bridge type).
For develompent mode startup after starting conteiners:

1. Create virtual environment and install all neccassary requirements;
2. Make your current locaation in app folder;
3. Run 'alembic upgrade head' for database tables creation;
4. Run 'python main.py' for telegrambot startup.