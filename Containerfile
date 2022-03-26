FROM alpine:latest

WORKDIR /var/www
RUN apk add --no-cache python3 py3-pip git

RUN git clone https://github.com/bkesk/bad-apps-blog.git app
RUN pip install -e app/

ENV FLASK_APP=bad_apps_blog
# The next line isn't ideal, it will always generate a new, empty db!
RUN flask init-db
# NOTE: the following line introduces a security issue :)
RUN flask init-config

CMD ["flask", "run", "--host=0.0.0.0"]
