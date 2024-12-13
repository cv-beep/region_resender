FROM python:3.12-alpine3.19
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

ENV URLBITRIX=None
ENV LISTID=None
ENV ENVAUTH=None
ENV URLSERVICE=None
ENV REGUF=None
ENV LISTID=None

COPY . /app
EXPOSE 8000
CMD uvicorn UpdateRegion:app --host 0.0.0.0 --port 8000 --reload
