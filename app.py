# encoding=utf8

import csv
import sys
import os.path
import json
import gensim
from datetime import timedelta
from flask import Flask, make_response, request, current_app
from functools import update_wrapper
from PhraseVector import PhraseVector
from NumpyEncoder import NumpyEncoder

app = Flask(__name__)
print >> sys.stderr, 'Initiating word2vec server...'
assert gensim.models.word2vec.FAST_VERSION > -1, "Gensim fast version is disabled!"

# Load word2vec model
print >> sys.stderr, 'Preloading word2vec model...'
basepath = os.path.dirname(__file__)
filepath = os.path.abspath(os.path.join(basepath, "model/GoogleNews-vectors-negative300.bin"))
wordvec_model = gensim.models.keyedvectors.KeyedVectors.load_word2vec_format(filepath, binary=True)

print >> sys.stderr, 'Preheating word2vec model...'
wordvec_model.similar_by_word("heat")

# Load sample questions
print >> sys.stderr, 'Preloading question-answer vectors...'
question_vector_array = []
datapath = os.path.abspath(os.path.join(basepath, "model/civil_law_qa_en.csv"))
# datapath = os.path.abspath(os.path.join(basepath, "model/qa_unofficial.csv"))
f = open(datapath, 'rb')
reader = csv.reader(f)
# row = question,answer (row[0] = question, row[1] = answer)
# getting the (vector) embeddings for each question-answer pair
for row in reader:
    qa = row[0] + row[1]
    #for now we will compare question to question and not combined
    question_vector_array.append([PhraseVector(wordvec_model, row[0]), row[1]])
f.close()

print >> sys.stderr, 'Starting server...'

# Communication with frontend stuff and other models e.g. Watson, ontology reasoner etc: allow cross domain connections
def crossdomain(origin=None, methods=None, headers=None, max_age=21600,
                attach_to_all=True, automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        """ Determines which methods are allowed
        """
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        """The decorator function
        """
        def wrapped_function(*args, **kwargs):
            """Caries out the actual cross domain code
            """
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

@app.route("/get", methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_bot_response():
	# get question from the user
    userText = request.args.get('msg')

    # Create phrase vector from user input
    userVector = PhraseVector(wordvec_model, userText)

    # Match input vector with qa data
    bestScore = 0
    bestScoring = ''
    for question_vector in question_vector_array:
        similarity_to_query = userVector.CosineSimilarity(question_vector[0].vector)
        if similarity_to_query > bestScore:
            bestScore = similarity_to_query
            bestScoring = question_vector[1]

    if bestScoring == '' or bestScore < 0.5: bestScoring = 'Sorry, I can not help you with that problem.'
    return bestScoring

@app.route("/classify", methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def classify_phrases():
    # Classify the given text as belonging to phrase1 or phrase2
    text = request.args.get('text')
    phrase1 = request.args.get('phrase1')
    phrase2 = request.args.get('phrase2')

    # Create phrase vector from user input
    userVector = PhraseVector(wordvec_model, text)
    phrase1Vector = PhraseVector(wordvec_model, phrase1)
    phrase2Vector = PhraseVector(wordvec_model, phrase2)

    # Classify
    sim_1 = userVector.CosineSimilarity(phrase1Vector.vector)
    sim_2 = userVector.CosineSimilarity(phrase2Vector.vector)

    if sim_1 + sim_2 < 0.5:
        return 'UNCLASSIFIED'
    elif sim_1 > sim_2:
        return 'phrase1'
    else:
        return 'phrase2'

@app.route("/getsimilar", methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_similar_words():
    word = request.args.get('word')

    try:
        similar_words = wordvec_model.similar_by_word(word)
        return json.dumps(similar_words, cls=NumpyEncoder)
    except KeyError:
        return False

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
    # app.run(port=5566)


