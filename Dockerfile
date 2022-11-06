FROM python:3.10-alpine

WORKDIR /tmp
ADD ./app/reqs.pip /tmp

ENV LIBRARY_PATH=/lib:/usr/lib
RUN apk add --update --no-cache build-base libxml2-dev libxslt-dev libffi-dev && \
    pip install -r reqs.pip && \
    apk del build-base && \
    rm -rf /var/cache/apk/*

COPY ./app /src
WORKDIR /src

# Add the crawl script - cannot contain "." in the name
ADD ./app/crawl.sh /etc/periodic/daily/crawl
RUN chmod +x /etc/periodic/daily/crawl

RUN ./manage.py collectstatic --no-input

# Run crond in the foreground
# CMD crond -l 2 -f

CMD ["sh", "./run.sh"]
