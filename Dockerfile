FROM python:2

WORKDIR app

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "app.py"]

