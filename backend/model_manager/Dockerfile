FROM python:3.9

LABEL org.opencontainers.image.source https://github.com/beny2000/GetList

WORKDIR /code

COPY ./backend/model_manager/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./backend/label_mapping.json /code/label_mapping.json 

COPY ./backend/model_manager /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8082", "--reload"]