FROM quay.io/askomics/flaskomics-base:4.0.0-alpine3.13 AS builder
MAINTAINER "Xavier Garnier <xavier.garnier@irisa.fr>"

COPY . /askomics
WORKDIR /askomics

RUN make clean-config fast-install build

# Final image
FROM alpine:3.13

WORKDIR /askomics
RUN apk add --no-cache make python3 bash git libc-dev libstdc++ nodejs-current npm openldap-dev
COPY --from=builder /askomics .

EXPOSE 5000
CMD make serve-askomics
