FROM askomics/flaskomics-base:3.2.0-alpine3.9 AS builder
MAINTAINER "Xavier Garnier <xavier.garnier@irisa.fr>"

COPY . /askomics
WORKDIR /askomics

RUN rm -f config/askomics.ini && \
    /askomics/install.sh -i js


# Final image
FROM alpine:3.9
ENV DEPMODE="prod"
ENV MAX_CELERY_QUEUE="1"
WORKDIR /askomics
RUN apk add --no-cache python3 bash git libc-dev libstdc++
COPY --from=builder /askomics .

CMD /askomics/run_celery.sh -d ${DEPMODE} -c ${MAX_CELERY_QUEUE}
