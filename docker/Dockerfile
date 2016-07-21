FROM alpine:latest

RUN echo -e "@testing http://dl-4.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN apk add --update python py-pip git openssh-client build-base musl-dev

RUN pip install git+https://github.com/decentlab/coverage-mapper

CMD cmgist

