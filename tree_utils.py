from collections import defaultdict
import numpy

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
            pcfg.lexicon[self.token][self.symbol] = 1/(n+1) + pcfg.lexicon[self.token].get(self.symbol, 0.)
            pcfg.term.add(self.symbol)
        else:
            pcfg.nterm.add(self.symbol)
            left = self.symbol
            right = tuple([child.symbol for child in self.children])
            n = len(pcfg.prod[left])
            for key in pcfg.prod[left].keys():
                pcfg.prod[left][key] = n*(pcfg.prod[left][key]) / (n+1)
            pcfg.prod[left][right] = 1/(n+1) + pcfg.prod[left].get(right, 0.)
            for child in self.children:
                child.addGrammar(pcfg)

    def computeProba(self, pcfg):
        p = 1.
        if len(self.children) > 0:
            p *= pcfg.prod[self.symbol][tuple([child.symbol for child in self.children])]
            p *= numpy.prod([child.computeProba(pcfg) for child in self.children])
        return p

    def sentence2bracketed(self):
        s = '('+self.symbol+' '+self.token
        for child in self.children:
            s += child.sentence2bracketed()
        s += ')'
        return s

                
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
        self.prod = defaultdict(dict)
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

    def printGrammar(self):
        for left, rights in self.prod.items():
            print(left, end=' -> ')
            for right, proba in rights.items():
                for c in right:
                    print(c, end=' ')
                print('p='+str(proba), end=' | ')
            print('')

    def Chomsky_term(self):
        # TERM phase in procedure to compute Chomsky normal form 
        replaced_char = set([])
        for left in self.prod.keys():
            new_rights = {}
            for right in self.prod[left].keys():
                proba = self.prod[left][right]
                new_right = list(right)
                for i, e in enumerate(right):
                    if e in self.term:
                        new_right[i] = 'TERM_'+e
                        self.nterm.add('TERM_'+e)
                        replaced_char.add(e)
                new_rights[tuple(new_right)] = proba
            self.prod[left] = new_rights
        for e in replaced_char:
            self.prod['TERM_'+e] = {tuple([e]) : 1.}

    def Chomsky_bin(self):
        # BIN phase in the procedure to compute Chomsky normal form
        added_rules = {}
        for left in self.prod.keys():
            new_rights = {}
            for i, right in enumerate(self.prod[left].keys()):
                proba = self.prod[left][right]
                if len(right) >= 3:
                    new_right = tuple([right[0], 'BIN_'+left+'_'+str(i)+'_1'])
                    new_rights[new_right] = proba
                    for l in range(1, len(right)-2):
                        added_rules['BIN_'+left+'_'+str(i)+'_'+str(l)] = tuple([right[l], 'BIN_'+left+'_'+str(i)+'_'+str(l+1)])
                    added_rules['BIN_'+left+'_'+str(i)+'_'+str(len(right)-2)] = tuple([right[len(right)-2], right[len(right)-1]])
                else:
                    new_rights[right] = proba
            self.prod[left] = new_rights
        for key, value in added_rules.items():
            self.prod[key][value] = 1.
            self.nterm.add(key)

    @staticmethod
    def Chomsky_unit_recu(pcfg, left, right):
        if right not in pcfg.prod[left].keys():
            return
        proba = pcfg.prod[left][right]
        for C in list(pcfg.prod[right[0]].keys())[:]:
            if len(C)==1 and C[0] in pcfg.nterm:
                PCFG.Chomsky_unit_recu(pcfg, right[0], C)
        for C in pcfg.prod[right[0]].keys():
            pcfg.prod[left][C] = proba * pcfg.prod[right[0]][C]
        del pcfg.prod[left][right]

    def Chomsky_unit(self):
        for left in list(self.prod.keys())[:]:
            for right in list(self.prod[left].keys())[:]:
                if len(right)==1 and right[0] in self.nterm:
                    PCFG.Chomsky_unit_recu(self, left, right)
