FROM askomics/virtuoso:7.2.5.1

MAINTAINER "Xavier Garnier <xavier.garnier@irisa.fr>"

COPY . /askomics
WORKDIR /askomics

ENV DEPMODE="prod" \
    MAX_CELERY_QUEUE="1" \
    SPARQL_UPDATE=true \
    ASKO_triplestore_load_url="http://localhost:5000"

RUN apk update && apk del openssl openssl-dev && \
    apk add --no-cache \
    redis sqlite \
    gcc g++ libstdc++ make \
    zlib-dev libzip-dev bzip2-dev xz-dev \
    python3 python3-dev \
    py3-numpy \
    nodejs nodejs-npm \
    git bash wget && \
    rm -f config/askomics.ini && \
    /askomics/install.sh && \
    /askomics/build.sh && \
    mv /askomics/docker/start_all.sh /askomics/start_all.sh && \
    apk del gcc g++ make zlib-dev libzip-dev bzip2-dev xz-dev && \
    rm -rf /var/cache/apk/* && \
    rm -rf /root/.cache/* && \
    rm -rf /root/.npm/*

EXPOSE 5000
CMD ["/askomics/start_all.sh"]
