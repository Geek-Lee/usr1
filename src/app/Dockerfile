FROM python:2.7

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY pip.conf /root/.pip/pip.conf
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

WORKDIR /usr/src/app/sql_history

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8090"]