from tree_utils import *
from oov import *
from CYK import *
import random

# sent = "(S (Suj Je) (Vb mange) (NP (Det des) (N pates)))"
# st = SentenceTree(sent)
# st.extractStructure()
# st.printSentence()

# FROM TXT TO LIST OF STRINGS
path_to_training = '/home/matthieu/Documents/Cours/NLP/HW2/sequoia-corpus+fct.mrg_strict'
with open(path_to_training, 'r') as file:
    sentences = file.readlines()

# DIVIDE THE INPUT SET INTO TRAINING / TEST SET
random.shuffle(sentences)
nTraining = int(0.1*len(sentences))
trainingSet = sentences[:nTraining]
testSet = sentences[nTraining:]

# Compute the PCFG corresponding to the training corpus and put it in Chomsky normal form
pcfg = PCFG.generatePCFG(trainingSet)
pcfg.Chomsky_term()
pcfg.Chomsky_bin()
pcfg.Chomsky_unit()

# Loading the Polyglot embeddings
words, total_embeddings = pickle.load(open('polyglot-fr.pkl', 'rb'), encoding='latin1')

sentence = 'Je mange des bananes .'
nodeList = sentence2PoS(sentence, pcfg.lexicon, words, total_embeddings)
print(CYK(pcfg, nodeList))
