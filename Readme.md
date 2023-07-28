To start container with bot backend type:

    docker run --rm -d --name main --env-file=../.env --net=app back_bot:1

    To enter container with bash type:

        docker exec -it main bash


To start container with database type:

    docker run --rm -d --name db -v test:/var/lib/postgresql/data --env-file=../.env -p 5433:5432 --net=app postgres

    To enter container with psql type:

        docker exec -it db psql --username sam --dbname to_do_list
