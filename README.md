# messages-demo
A minimal message server for educational purposes

## Quick Start

The service is expected to run in tandem with a relational database with locking support.
 

### Run the server via `docker-compose`

Invoke `make run` to build the docker image. When the system is running, direct a browser to
http://localhost:8080 to get an interactive view of the API.

### Requirements

You need to have reasonably recent versions of `make` and `docker-compose` installed 
in order to run the `messages-demo`.

## Notes 

The `Makefile` defines a few targets for common operations.

### Dev server

To run the dev server using a sqlite database, do the following.

```bash
> pipenv install
> pipenv shell
> make runserver
```

As any reader with a keen eye may have already guessed, `pipenv` is a requirement 
for running the dev server.
