from tree_utils import *
from oov import *
from CYK import *
import random
from time import time
import pickle

# sent = "(S (Suj Je) (Vb mange) (NP (Det des) (N pates)))"
# st = SentenceTree(sent)
# st.extractStructure()
# st.printSentence()

# FROM TXT TO LIST OF STRINGS
path_to_training = '/home/matthieu/Documents/Cours/NLP/HW2/sequoia-corpus+fct.mrg_strict'
with open(path_to_training, 'r') as file:
    sentences = file.readlines()

# DIVIDE THE INPUT SET INTO TRAINING / TEST SET
nTraining = int(0.8*len(sentences))
trainingSet = sentences[:nTraining]
nTest = int(0.1*len(sentences))
testSet = sentences[-nTest:]

# Compute the PCFG corresponding to the training corpus and put it in Chomsky normal form
print('Computing the PCFG...')
pcfg = PCFG.generatePCFG(trainingSet)
print('Converting it into Chomsky normal form...')
pcfg.Chomsky_term()
pcfg.Chomsky_bin()

unit = False
while not unit:
    pcfg, unit = PCFG.Chomsky_unit_recu(pcfg)
pcfg.computeReverseProd()

# Loading the Polyglot embeddings
words, total_embeddings = pickle.load(open('polyglot-fr.pkl', 'rb'), encoding='latin1')

ngood, ntot = 0, 0
PoSgood = defaultdict(float)
PoStot = defaultdict(float)
parsable, senttot = 0, 0
start = time()
textfile = open('bail.txt', 'w')
for sentence in testSet:
    st = SentenceTree(sentence)
    st.extractStructure()
    st.cleanHyphen()
    truePoSlist = st.root.PoSlist()
    s = st.root.printSentence()
    print('Affecting a PoS to every token...')
    nodeList = sentence2PoS(s, pcfg.lexicon, words, total_embeddings)
    st.root.addGrammar(pcfg)
    for i in range(len(nodeList)):
        PoStot[truePoSlist[i]] += 1
        if nodeList[i].symbol == truePoSlist[i]:
            PoSgood[truePoSlist[i]] += 1
            ngood += 1
        ntot += 1
    print('Executing CYK...')
    c = CYK(pcfg, nodeList)
    print('Undoing the CNF...')
    if c is not None:
        parsable += 1
        senttot += 1
        c.remove_BIN()
        c.remove_TERM()
        print(c.sentence2bracketed())
        textfile.write(c.sentence2bracketed())
        textfile.write('\n')
    else:
        senttot += 1
        textfile.write('None\n')
with open('PoSaccu.txt', 'w') as file:
    PoSaccu = str({PoS : 100*PoSgood[PoS]/PoStot[PoS] for PoS in PoSgood.keys()})
    file.write(PoSaccu)

print('Proportion of good PoS : ' + str(100*ngood/ntot) + '%')
print('Proportion of parsable sentences : ' + str(100*parsable/senttot) + '%')
end = time()
print('Total time : ' + str(end-start))

