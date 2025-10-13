FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY ["./fhufranko-main 2/bowdowa/", "/usr/share/nginx/html"]
EXPOSE 80
