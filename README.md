# Greenfield Events
A tiny web app to crawl local venues in Greenfield MA and provide me with an
iCAL feed of the fun stuff coming up in my city.

Built using Django and Scrapy.

### Running
Using [docker](https://www.docker.com), of course.

```bash
# Build
$ docker-compose build

# Run
$ docker-compose up

# Run crawls
$ docker-compose run --rm app ./manage.py crawl

# Crawl a single venue
$ docker-compose run --rm app ./manage.py crawl --name=<spider-name>
```
