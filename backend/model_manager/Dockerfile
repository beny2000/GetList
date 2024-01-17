FROM python:3.9

LABEL org.opencontainers.image.source https://github.com/beny2000/GetList

WORKDIR /code

COPY ./backend/model_manager/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./backend/model_0.69.tar.gz /code/model_0.69.tar.gz 

RUN mkdir /code/model_files

RUN tar -xzvf model_0.69.tar.gz -C /code/model_files

COPY ./backend/model_manager /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8082", "--reload"]