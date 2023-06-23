FROM ubuntu:18.04 as shell-ready
MAINTAINER zap

ENV TZ=Europe/Moscow
ENV DEBIAN_FRONTEND=noninteractive

# Required so that we can run add-apt-repository to add repositories later
RUN apt-get update && \
    apt-get -q -y install \
    software-properties-common

# nano to edit files inside (debug)
# mc easily navigate files inside (debug)
# inetutils-ping seems to be good also
RUN add-apt-repository -y 'ppa:deadsnakes/ppa' && \
    apt-get update && \
    apt-get install -q -y nano mc inetutils-ping

FROM shell-ready as python-ready

# pip is required because we use Ubuntu based distro without initial python support
# various pythons are required by tox test system
# disutils required for python3.10 because tox under python3.6 can't find deprecated distutils
RUN apt-get -q -y install \
    python3.8 python3.10 python3-pip python3.10-distutils

RUN mkdir -p /app/service_data
COPY ./z5r.ini /app/service_data/

WORKDIR /app
COPY . .

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt && \
    python3 -m pip install -r requirements-test.txt

FROM python-ready

CMD ["python3", "src/httpd.py", "-r"]
