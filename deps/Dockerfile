FROM alpine:latest

RUN apk add --no-cache \
    bash \
    curl \
    git \
    jq \
    openssh-client \
    python3 \
    py3-pip \
    rsync \
    zip

RUN pip3 install --upgrade pip
COPY ./ak-plan-optimierung /ak-plan-optimierung
WORKDIR /ak-plan-optimierung


WORKDIR /
