# Example configuration for plugin

To run this example:

```shell

# Pull dependent docker images such as postgresql, redis and skygear
$ docker-compose pull

# Build the docker image for the plugin
$ docker-compose build

# Create the docker container for database and redis
$ docker-compose up -d db redis

# Wait 10 seconds for services to initialize

# Start skygear container
$ docker-compose up -d app

# Start plugin in the foreground
$ docker-compose up plugin
```
