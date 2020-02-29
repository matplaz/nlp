from tree_utils import *

# sent = "(S (Suj Je) (Vb mange) (NP (Det des) (N pates)))"
# st = SentenceTree(sent)
# st.extractStructure()
# st.printSentence()

# FROM TXT TO LIST OF STRINGS
path_to_training = '/home/matthieu/Documents/Cours/NLP/HW2/sequoia-corpus+fct.mrg_strict'
with open(path_to_training, 'r') as file:
    sentences = file.readlines()

pcfg = PCFG.generatePCFG(sentences)

print(pcfg.nterm)





