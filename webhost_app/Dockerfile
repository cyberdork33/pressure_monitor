FROM cyberdork33/nginx-uwsgi-flask

COPY website /app/website
COPY main.py /app/
COPY requirements.txt /app/
COPY uwsgi-app.ini /app/
RUN pip3 install -U -r /app/requirements.txt

RUN chown -R www-data:www-data /app/website/database
