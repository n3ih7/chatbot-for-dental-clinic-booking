FROM python:3.8-alpine

LABEL MAINTAINER="zach@nono.fi"

RUN apk update && apk add --no-cache supervisor

RUN mkdir -p /var/log/supervisor

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY requirements.txt /t/

COPY pre_processing /t/pre

COPY dentist_service /t/d_s

COPY timeslot_service /t/t_s

WORKDIR /t

RUN pip install -r requirements.txt

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
