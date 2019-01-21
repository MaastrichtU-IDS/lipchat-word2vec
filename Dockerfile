FROM python:2

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt && \
  python -m spacy download en_core_web_sm && \
  python -m spacy link en_core_web_sm en_default && \
  python -c "import nltk; nltk.download('all');"
  
RUN cd model && \
  wget https://s3.eu-central-1.amazonaws.com/lipchat-word-embeddings/GoogleNews-vectors-negative300.bin

ENTRYPOINT ["python", "app.py"]
