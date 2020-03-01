import pickle
import numpy
from operator import itemgetter
import re
from tree_utils import *

def Levenshtein(s1, s2):
    m = numpy.zeros((len(s1), len(s2)))
    for i in range(len(s1)):
        m[i, 0] = i
    for j in range(len(s2)):
        m[0, j] = j
    for i in range(1, len(s1)):
        for j in range(1, len(s2)):
            if s1[i] == s2[j]:
                m[i, j] = min(1+m[i-1,j], 1+m[i,j-1], m[i-1,j-1])
            else:
                m[i, j] = min(1+m[i-1,j], 1+m[i,j-1], 1+m[i-1,j-1])
    return m[len(s1)-1, len(s2)-1]


DIGITS = re.compile("[0-9]", re.UNICODE)

def case_normalizer(word, dictionary):
  """ In case the word is not available in the vocabulary,
     we can try multiple case normalizing procedure.
     We consider the best substitute to be the one with the lowest index,
     which is equivalent to the most frequent alternative."""
  w = word
  lower = (dictionary.get(w.lower(), 1e12), w.lower())
  upper = (dictionary.get(w.upper(), 1e12), w.upper())
  title = (dictionary.get(w.title(), 1e12), w.title())
  results = [lower, upper, title]
  results.sort()
  index, w = results[0]
  if index != 1e12:
    return w
  return word


def normalize(word, word_id):
    """ Find the closest alternative in case the word is OOV."""
    if not word in word_id:
        word = DIGITS.sub("#", word)
    if not word in word_id:
        word = case_normalizer(word, word_id)

    if not word in word_id:
        return None
    return word


def l2_nearest(word, word_id, id_word, total_embeddings, labeled_embeddings, labeled2wordid):
    """Sorts words according to their Euclidean distance.
       To use cosine distance, embeddings has to be normalized so that their l2 norm is 1."""
    word = normalize(word, word_id)
    if not word:
        print("OOV word")
        return
    word_embedding = total_embeddings[word_id[word]]
    distances = (((labeled_embeddings - word_embedding) ** 2).sum(axis=1) ** 0.5)
    sorted_distances = sorted(enumerate(distances), key=itemgetter(1))
    return id_word[labeled2wordid[sorted_distances[0][0]]], sorted_distances[0][1] #ATTENTION RETOURNE L'ID DANS LA LISTE DES LABELED_EMBEDDING


def closest_PoS(word, lexicon, words, total_embeddings):
    # Map words to indices and vice versa
    word_id = {w:i for (i, w) in enumerate(words)}
    id_word = dict(enumerate(words))
    # Normalize digits by replacing them with #
    # Special tokens
    Special_ID = {"<UNK>": 0, "<S>": 1, "</S>":2, "<PAD>": 3}
    ID_Special = dict(enumerate(Special_ID.keys()))
    # Treatment of the tokens already in the lexicon
    tokens = [t for t in lexicon.keys()]
    for i, token in enumerate(tokens):
        tokens[i] = normalize(token, word_id)
        if not tokens[i]:
            tokens[i] = ID_Special[0]
    labeled_embeddings = [total_embeddings[word_id[token]] for token in tokens]
    labeled2wordid = {i:word_id[token] for (i, token) in enumerate(tokens)}
    closest_token = l2_nearest(word, word_id, id_word, total_embeddings, labeled_embeddings, labeled2wordid)[0]
    if closest_token:
        PoS = max(lexicon[closest_token].items(), key=itemgetter(1))[0]
        return PoS
    return

def OOVModule(word, lexicon, words, total_embeddings):
    try:
        PoS = closest_PoS(word, lexicon, words, total_embeddings)
        return PoS
    except TypeError:
        # Compute the Levenshtein distance to every word of the Polyglot dictionnary
        distances = [Levenshtein(word, w) for w in words]
        sorted_distances = sorted(enumerate(distances), key=itemgetter(1))
        closest_idx = []
        i = 0
        while sorted_distances[i][1] == sorted_distances[0][1]:
            closest_idx.append(sorted_distances[i][0])
            i += 1
        closest_Levenshtein = words[min(closest_idx)]
        print("Replaced the word " + word + " by " + closest_Levenshtein)
        return closest_PoS(closest_Levenshtein, lexicon, words, total_embeddings)

def sentence2PoS(sentence, lexicon, words, total_embeddings):
    nodeList = []
    tokens = sentence.split(' ')
    for token in tokens:
        N = Node()
        N.symbol = OOVModule(token, lexicon, words, total_embeddings)
        N.token = token
        nodeList.append(N)
    return nodeList
