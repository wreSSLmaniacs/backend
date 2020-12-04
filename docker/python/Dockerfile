FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3

ADD ../../codes/ /code/

WORKDIR /code

CMD [ "/bin/bash" ]