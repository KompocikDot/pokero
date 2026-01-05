# pokero

## Running a dev environment

To run a dev environment you'll need:

- docker
- docker compose (soonish)

Before running you'll need to create these files in secrets directory:

- db_password

To run docker container run these two commands in main project directory.

Development mode (with hot reload etc.)

```bash
docker compose --profile=dev build
docker compose --profile=dev up
```

In production mode

```bash
docker compose --profile=prod build
docker compose --profile=prod up
```

Also do not forget to run migrations first time (or each time after doing changes to the models.) like so:

Go inside the app container

```bash
docker ps -a # Get id of app container
docker exec -it <id> bash
```

```bash
python manage.py migrate
```

If you want to detach from running container, simply add `-d` flag like so:

```bash
docker compose -d --profile=dev up
```


Helm deploy
Login to Azure and configure kubectl (instruction in pokero_infra rpo)

Example secret and password is provided in ./helm/values.yaml. Change it on production.

```bash
helm install pokero ./helm
```

Verify with

```bash
kubectl get deployments
kubectl get pods
```


