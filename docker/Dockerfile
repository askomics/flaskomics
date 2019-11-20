FROM askomics/flaskomics-base:3.2.0-alpine3.9 AS builder
MAINTAINER "Xavier Garnier <xavier.garnier@irisa.fr>"

COPY . /askomics
WORKDIR /askomics

RUN rm -f config/askomics.ini && \
    /askomics/install.sh && \
    /askomics/build.sh


# Final image
FROM alpine:3.9
ENV DEPMODE="prod"
WORKDIR /askomics
RUN apk add --no-cache python3 bash git libc-dev libstdc++ nodejs nodejs-npm
COPY --from=builder /askomics .

EXPOSE 5000
CMD bash /askomics/run_askomics.sh -d ${DEPMODE}
