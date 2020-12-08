FROM ubuntu:latest

RUN apt-get update && apt-get install -y ruby-full

ADD ./codes /code/

WORKDIR /code

CMD [ "/bin/bash" ]
