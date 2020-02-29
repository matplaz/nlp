from collections import defaultdict

class Node:
    def __init__(self):
        self.children = []
        self.symbol = ''
        self.token = ''

    def computeChildren(self, sentence, iBegin):
        i = iBegin
        tokenWord = False
        while sentence[i] != ')':
            if sentence[i] != ' ':
                if sentence[i] == '(':
                    tokenWord = False
                    child = Node()
                    i = child.computeChildren(sentence, i+1)
                    self.children.append(child)
                elif not tokenWord:
                    self.symbol += sentence[i]
                else:
                    self.token += sentence[i]
            else :
                tokenWord = True
            i += 1
        return i

    def cleanHyphen(self):
        for i, char in enumerate(self.symbol):
            if char == '-':
                self.symbol = self.symbol[:i]
                break
        for child in self.children:
            child.cleanHyphen()

    def printSentence(self):
        if self.token != '':
            print(self.token, end = ' ')
        for child in self.children:
            child.printSentence()
    
    def addGrammar(self, pcfg):
        if not self.children:
            n = len(pcfg.lexicon[self.token])
            for key in pcfg.lexicon[self.token].keys():
                pcfg.lexicon[self.token][key] = n*(pcfg.lexicon[self.token][key]) / (n+1)
            pcfg.lexicon[self.token][self.symbol] = 1/(n+1) + pcfg.lexicon[self.token].get(self.symbol, 0.)/(n+1)
            pcfg.term.add(self.symbol)
        else:
            pcfg.nterm.add(self.symbol)
            rule = tuple([self.symbol, tuple([child.symbol for child in self.children])])
            pcfg.prod.add(rule)
            for child in self.children:
                child.addGrammar(pcfg)


                
class SentenceTree:
    def __init__(self, sentence):
        self.root = Node()
        self.sentence = sentence
    
    def extractStructure(self):
        self.root.computeChildren(self.sentence, 3)

    def cleanHyphen(self):
        # wrapper for the node method
        self.root.cleanHyphen()

    def printSentence(self):
        # wrapper for the node method
        self.root.printSentence()


class PCFG:
    def __init__(self):
        self.S = 'SENT'
        self.nterm = set([])
        self.term = set([])
        self.prod = set([])
        self.lexicon = defaultdict(dict)

    @staticmethod
    def generatePCFG(sentences):
        pcfg = PCFG()
        for sentence in sentences:
            st = SentenceTree(sentence)
            st.extractStructure()
            st.cleanHyphen()
            st.root.addGrammar(pcfg)
        return pcfg

