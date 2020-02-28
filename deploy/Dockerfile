FROM python:3.7-stretch

RUN apt-get -y update && apt-get -y upgrade && apt-get install nginx git -y

RUN git clone https://github.com/onsplatform/platform_reprocess.git /var/www/reprocess

WORKDIR /var/www/reprocess

RUN pip install pipenv gunicorn
RUN pipenv install --system --deploy


RUN cp /var/www/reprocess/deploy/reprocess.nginx /etc/nginx/sites-available/reprocess

RUN mkdir /var/log/reprocess \
 && rm -rf /etc/nginx/sites-enabled/default \
 && ln -s /etc/nginx/sites-available/reprocess /etc/nginx/sites-enabled/reprocess

ENV GUNICORN_TIMEOUT 3000

EXPOSE 9099

RUN cp /var/www/reprocess/deploy/docker_entrypoint.sh /docker_entrypoint.sh
RUN cp /var/www/reprocess/deploy/reprocess.sh /reprocess.sh

RUN chmod +x /docker_entrypoint.sh
RUN chmod +x /reprocess.sh

ENTRYPOINT ["sh", "/docker_entrypoint.sh"]
