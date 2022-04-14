FROM alpine:latest

WORKDIR /var/www
RUN apk add --no-cache python3 py3-pip git

RUN git clone https://github.com/bkesk/bad-apps-blog.git app
RUN pip install -e app/

ENV FLASK_APP=bad_apps_blog

CMD ["flask", "run", "--host=0.0.0.0"]
