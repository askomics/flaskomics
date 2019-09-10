FROM alpine:3.9

MAINTAINER "Xavier Garnier <xavier.garnier@irisa.fr>"

COPY . /askomics
WORKDIR /askomics

ENV DEPMODE="prod"

RUN apk add --no-cache \
    gcc g++ make \
    zlib-dev libzip-dev bzip2-dev xz-dev \
    python3 python3-dev \
    py3-numpy \
    nodejs nodejs-npm \
    git bash && \
    rm -f config/askomics.ini && \
    /askomics/install.sh && \
    /askomics/build.sh && \
    apk del gcc g++ && \
    rm -rf /var/cache/apk/* && \
    rm -rf /root/.cache/* && \
    rm -rf /root/.npm/*

EXPOSE 5000
ENTRYPOINT /askomics/run_askomics.sh -d ${DEPMODE}
