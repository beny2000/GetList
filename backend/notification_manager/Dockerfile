FROM python:3.9

LABEL org.opencontainers.image.source https://github.com/beny2000/GetList

WORKDIR /code

COPY ./backend/notification_manager/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./backend/lib_db-0.1.0.tar.gz /code/lib_db-0.1.0.tar.gz 

RUN tar -xzvf lib_db-0.1.0.tar.gz && pip install ./lib_db_package
 
COPY ./backend/notification_manager /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8083", "--reload"]