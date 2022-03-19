FROM python:3.8-buster
ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt /requirements.txt
RUN apt-get update && apt-get -yy install libmariadb-dev libmariadb3 
RUN apt-get install gcc musl-dev 

RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements.txt
EXPOSE 8000
RUN mkdir /app
WORKDIR /app
COPY ./ /app

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN adduser user
RUN chown -R user:user /vol/
RUN chmod -R 755 /vol/web
USER user