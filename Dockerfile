FROM python:2

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt && \
  python -m spacy download en_core_web_sm && \
  python -m spacy link en_core_web_sm en_default && \
  python -c "import nltk; nltk.download('all');"


ENTRYPOINT ["python", "app.py"]
