FROM python:3.8

RUN mkdir /bot

COPY . /bot

WORKDIR /bot

RUN pip install -r requirements.txt

CMD ["python", "main.py"]