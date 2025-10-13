FROM nginx:alpine
COPY default.conf.template /etc/nginx/templates/default.conf.template
COPY ["./fhufranko-main 2/bowdowa/", "/usr/share/nginx/html"]
