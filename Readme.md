To work with telebot backend container type (from folder TeleBotAll/app/):

    docker build -t backbot:1 .
    docker run --rm -d --name main --env-file=../.env --net=app back_bot:1

    To enter container with bash type:

        docker exec -it main bash


To start container with database type:

    docker run --rm -d --name db -v test:/var/lib/postgresql/data --env-file=../.env -p 5433:5432 --net=app postgres

    To enter container with psql type:

        docker exec -it db psql --username sam --dbname to_do_list


To work with API container type (from folder fast_api):

    docker build -t fast_api:1 .
    docker run --rm -d --name fa --env-file=../.env -p 80:80 --net=app fast_api:1
