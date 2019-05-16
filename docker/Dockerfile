FROM alpine:3.9

MAINTAINER "Xavier Garnier <xavier.garnier@irisa.fr>"

COPY . /askomics
WORKDIR /askomics

RUN apk add --no-cache \
    python3 python3-dev \
    nodejs nodejs-npm \
    git bash && \
    /askomics/install.sh && \
    /askomics/build.sh && \
    rm -rf /var/cache/apk/* && \
    rm -rf /root/.cache/* && \
    rm -rf /root/.npm/*

EXPOSE 5000
ENTRYPOINT /askomics/run_askomics.sh
