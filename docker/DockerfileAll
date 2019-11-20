# Build AskOmics
FROM askomics/flaskomics-base:3.2.0-alpine3.9 AS askomics_builder
MAINTAINER "Xavier Garnier <xavier.garnier@irisa.fr>"

COPY . /askomics
WORKDIR /askomics

RUN rm -f config/askomics.ini && \
    /askomics/install.sh && \
    /askomics/build.sh && \
    mv /askomics/docker/start_all.sh /askomics/start_all.sh

# Build Corese
FROM xgaia/corese:latest AS corese_builder

# Build Virtuoso
FROM askomics/virtuoso:7.2.5.1 AS virtuoso_builder

# Final image
FROM alpine:3.8

ENV DEPMODE="prod" \
    MAX_CELERY_QUEUE="1" \
    SPARQL_UPDATE=true \
    ASKO_triplestore_load_url="http://localhost:5000" \
    ASKO_federation_query_engine="corese" \
    ASKO_federation_endpoint="http://localhost:8080/sparql" \
    PATH="/usr/local/virtuoso-opensource/bin/:$PATH"

WORKDIR /askomics

RUN apk add --no-cache openssl py-pip && \
    pip install crudini && \
    mkdir -p /usr/local/virtuoso-opensource/var/lib/virtuoso/db && \
    ln -s /usr/local/virtuoso-opensource/var/lib/virtuoso/db /data && \
    apk --no-cache add --update openjdk11 --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community && \
    mkdir /corese && \
    apk add --no-cache redis sqlite && \
    apk add --no-cache python3 bash git libc-dev libstdc++ nodejs nodejs-npm

COPY --from=virtuoso_builder /usr/local/virtuoso-opensource /usr/local/virtuoso-opensource
COPY --from=virtuoso_builder /virtuoso /virtuoso
COPY --from=corese_builder /corese /corese
COPY --from=askomics_builder /askomics /askomics

EXPOSE 5000
CMD bash /askomics/start_all.sh
