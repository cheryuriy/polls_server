 FROM python:3.8
 ENV PYTHONUNBUFFERED 1
 RUN mkdir /code
 WORKDIR /code
 ADD requirements.txt /code/
 RUN pip install --upgrade pip && pip install -r requirements.txt
 ADD . /code
 RUN python /code/manage.py collectstatic --no-input --clear && python /code/manage.py migrate;
