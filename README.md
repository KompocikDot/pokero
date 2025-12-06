# pokero

## Running a dev environment

To run a dev environment you'll need:

- docker
- docker compose (soonish)

Before running you'll need to create these files in secrets directory:
- db_password

To run docker container run these two commands in main project directory.

```bash
docker build -t pokero/backend -f docker/Dockerfile.dev .
docker run -t -p 8000:8000 pokero/backend
```

If you want to detach from running container, simply remove `-t` flag
from the `docker run`.
