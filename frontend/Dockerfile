FROM nginx:stable-alpine

LABEL MAINTAINER="zach@nono.fi"

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY www /usr/share/nginx/html

EXPOSE 80