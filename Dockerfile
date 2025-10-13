FROM nginx:alpine
COPY ./fhufranko-main 2/bowdowa/ /usr/share/nginx/html
RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
