FROM nginx:latest

LABEL MAINTAINER="zack@nono.fi"

COPY ./default.conf /etc/nginx/conf.d/default.conf

COPY front_end /usr/share/nginx/html

EXPOSE 8001