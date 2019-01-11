# Word2vec backend

## Requirements
- Python 2.7 (64 bit)
- Gensim

## Run the server:
python app.py

or alternative as a service: sudo systemctl enable pyrpc.service (move the .service file to your systems service directory prior to enabling the service)

## Word2Vec model
Prior to using the word2vec model, make sure you download the pretrained model into the /model directory
https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit?usp=sharing

models:
https://www.quora.com/Where-can-I-find-pre-trained-models-of-word2vec-and-sentence2vec-trained-on-Wikipedia-or-other-large-text-corpus
https://github.com/idio/wiki2vec/
https://github.com/3Top/word2vec-api#where-to-get-a-pretrained-models