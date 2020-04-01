FROM askomics/flaskomics-base:3.2.7-alpine3.9 AS builder
MAINTAINER "Xavier Garnier <xavier.garnier@irisa.fr>"

COPY . /askomics
WORKDIR /askomics

RUN make clean-config fast-install build

# Final image
FROM alpine:3.9

WORKDIR /askomics
RUN apk add --no-cache make python3 bash git libc-dev libstdc++ nodejs nodejs-npm build-base openldap-dev python2-dev python3-dev
COPY --from=builder /askomics .

EXPOSE 5000
CMD make serve-askomics
