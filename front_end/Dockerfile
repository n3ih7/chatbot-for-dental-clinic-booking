FROM nginx:stable-alpine

LABEL MAINTAINER="zack@nono.fi"

COPY ./nginx.conf /etc/nginx/conf.d/default.conf

COPY front_end /usr/share/nginx/html

EXPOSE 80