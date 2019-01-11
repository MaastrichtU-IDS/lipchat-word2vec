import sys
reload(sys)
import pickle
import re
from string import punctuation
from nltk.tokenize import word_tokenize
sys.setdefaultencoding("utf-8")

import numpy as np
import math


class PhraseVector:
    def __init__(self, wordvec_model, phrase):
        self.phrase = phrase
        self.wordvec_model = wordvec_model
        self.vector = self.PhraseToVec(phrase)

    # Retireve original phrase text
    def GetPhrase(self):
        return self.phrase

    # Combine multiple vectors
    def ConvertVectorSetToVecAverageBased(self, vectorSet, ignore=[]):
        if len(ignore) == 0:
            return np.mean(vectorSet, axis=0)
        else:
            return np.dot(np.transpose(vectorSet), ignore) / sum(ignore)

    # Some basic clean up of phrase
    def standardize_text(self, phrase):
        remove = punctuation
        remove = remove.replace("\'", "")
        pattern = r"[{}]".format(remove)
        phrase = re.sub(r"http\S+", "", phrase)
        phrase = re.sub(r"http", "", phrase)
        phrase = re.sub(r"@\S+", "", phrase)
        phrase = re.sub(pattern, "", phrase)
        phrase = re.sub(r"[^\w\s\d+]", "", phrase)
        phrase = re.sub(r"[^\D+]", "", phrase)
        phrase = re.sub(r"@", "at", phrase)
        phrase = phrase.lower()
        return phrase

    def tokenMaker(self, phrase):
        words = word_tokenize(phrase)

        with open('model/stopwords.pickle', 'rb') as f:
            custom_stopwords = pickle.load(f)

        custom_stopwords = custom_stopwords + ['nt', 'eur', 'euro', 'ive', 'hey']
        filtered_words = [word for word in words if word not in custom_stopwords]
        return filtered_words

    # Retrieve the phrase vector based on the vectors of each word in the phrase
    def PhraseToVec(self, phrase):
        phrase_clean = self.standardize_text(phrase)
        wordsInPhrase = self.tokenMaker(phrase_clean)  # [word for word in phrase.split()]
        vectorSet = []
        for aWord in wordsInPhrase:
            try:
                wordVector = self.wordvec_model[aWord]
                vectorSet.append(wordVector)
            except:
                # Word not in vocabulary
                pass
        return self.ConvertVectorSetToVecAverageBased(vectorSet)

    # Calculate the cosine similarity for the current phrase and another phrase vector
    def CosineSimilarity(self, otherPhraseVec):
        cosine_similarity = np.dot(self.vector, otherPhraseVec) / (np.linalg.norm(self.vector) * np.linalg.norm(otherPhraseVec))
        try:
            if math.isnan(cosine_similarity):
                cosine_similarity = 0
        except:
            cosine_similarity = 0
        return cosine_similarity