# Example configuration for plugin

## Requirements

Latest version of Docker Toolbox.

I repeat: **Latest version** of Docker Toolbox.

## tl;dr

```shell
$ docker-machine create --driver virtualbox default
$ eval `docker-machine env default`
$ docker-compose pull
$ docker-compose build --pull --no-cache plugin
$ docker-compose start db redis
$ sleep 10
$ docker-compose up -d app plugin
$ curl -H "Content-Type: application/json" -X POST \
    -d '{"action":"catapi:get"}' http://`docker-machine ip default`:3000
{"result":{"message":"OK","url":"http://24.media.tumblr.com/tumblr_li3gm7l8nz1qhd9p6o1_1280.jpg"}}
```

## I want to create a Docker Machine

```shell
# Create Docker Machine called `default`
$ docker-machine create --driver virtualbox default

# Tell Docker you want to use this Docker Machine
$ eval `docker-machine env default`
```

If the Docker Machine is stopped, you can restart the same Docker Machine:

```shell
# Start Docker Machine called `default`
$ docker-machine start default

# Tell Docker you want to use this Docker Machine
$ eval `docker-machine env default`
```

## I want to get skygear / I want to upgrade skygear

```shell
# Pull all dependent Docker images
$ docker-compose pull

# Optionally, you can pull the skygear image only by specifying the service name `app`
# (service name can be found in docker-compose.yml)
$ docker-compose pull app
```

## I want to build/rebuild/upgrade the plugin

```shell
# This command always pull the latest image and rebuild your plugin without using the cache.
$ docker-compose build --pull --no-cache plugin

# Optionally, if what you have changed is the Dockerfile and requirements.txt:
$ docker-compose build plugin
```

Note: You may need to migrate database. The procedure is to be included
here in the future.

## I want to start skygear without starting database and redis every time

```shell
# Start database and redis first
$ docker-compose start db redis

# Start skygear and plugin in the foreground.
$ docker-compose up app plugin

# Alternatively, you can start skygear and plugin in the background
$ docker-compose up -d app plugin

# Alternatively, you can start skygear by itself, then run the plugin in the foreground
$ docker-compose start app  # or docker-compose up -d app
$ docker-compose up plugin
```

You can press CTRL+C to stop the containers. If the containers are stuck,
press CTRL+C again. Run `docker-compose up app plugin` again to start skygear
and plugin again.

Note: If you run `docker-compose up` (without service names), the
database and redis will be stopped when you press CTRL+C. Make sure
you specify the service name if you do not want the database and redis
to stop.

## I changed my requirements.txt file

See *I want to build/rebuild/upgrade the plugin*.

## I need to install additional software in my plugin

Customize `Dockerfile` with additional commands to install your dependencies.
Then see *I want to build/rebuild/upgrade the plugin* to rebuild your plugin.

## I need a clean start

**Important**: The `docker-compose.yml` in this sample is designed such that your data
in the container are persisted across container delete and re-create cycle.
If you deviate from the sample `docker-compose.yml`, you should read about
[managing data in
containers](https://docs.docker.com/engine/userguide/dockervolumes/) and why
[docker data containers are good](https://medium.com/@ramangupta/why-docker-data-containers-are-good-589b3c6c749e), and you are on your own.

### Delete skygear and plugin containers

```shell
$ docker-compose stop app plugin
$ docker-compose rm app plugin  
Going to remove catapi_plugin_1, catapi_app_1
Are you sure? [yN] y
Removing catapi_plugin_1 ... done
Removing catapi_app_1 ... done
```

Your data is not deleted even if skygear and plugin containers are removed.
This is because your data is stored in a data container (suffixed `_data`).

### Delete database and redis containers

```shell
$ docker-compose stop
$ docker-compose rm app plugin db redis
Going to remove catapi_plugin_1, catapi_app_1, catapi_db_1, catapi_redis_1
Are you sure? [yN] y
Removing catapi_plugin_1 ... done
Removing catapi_app_1 ... done
Removing catapi_db_1 ... done
Removing catapi_redis_1 ... done
```

Your data is not deleted even if skygear and plugin containers are removed.
This is because your data is stored in a data container (suffixed `_data`).

**Important**: If you delete the database or redis containers,
you must delete the skygear and the plugin containers as well.

### If all else fails

You can delete all containers defined in `docker-compose.yml` by
running `docker-compose stop` and `docker-compose rm`.

You can also delete Docker Machine to start over: `docker-machine rm default`.

## I need to deploy to production

The sample `docker-compose.yml` may be used to deploy to production, but
you need expert advice. Especially, you should take precaution on how
data is persisted.

## Troubleshooting

### I deleted the database container, and then the skygear cannot connect the database anymore

Since containers are dependent on each other, you cannot delete the database
container and expect the skygear container to find the database container
automatically. You need to recreate skygear container and plugin container.

You should use the commands stated in the *I need a clean start* section.
