from collections import defaultdict
import numpy
import copy

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
        s = ''
        if self.token != '':
            s += self.token+' '
        for child in self.children:
            s += child.printSentence()
        return s

    def PoSlist(self):
        l = []
        if self.token != '':
            l.append(self.symbol)
        for child in self.children:
            l = l + child.PoSlist()
        return l
    
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
        if self.token != '':
            p *= pcfg.lexicon[self.token][self.symbol]
        if len(self.children) > 0:
            p *= pcfg.prod[self.symbol][tuple([child.symbol for child in self.children])]
            p *= numpy.prod([child.computeProba(pcfg) for child in self.children])
        return p

    def remove_BIN(self):
        to_treat = True
        while to_treat:
            to_treat = False
            new_children = []
            for child in self.children:
                if child.symbol[:3] == 'BIN':
                    for child_child in child.children:
                        new_children.append(child_child)
                    to_treat = True
                else:
                    new_children.append(child)
            self.children = new_children
        for child in self.children:
            child.remove_BIN()

    def remove_TERM(self):
        new_children = []
        for child in self.children:
            if child.symbol[:4] == 'TERM':
                new_children.append(child.children[0])
            else:
                new_children.append(child)
        self.children = new_children
        for child in self.children:
            child.remove_TERM()

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
        self.reverseprod = defaultdict(dict)
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
            # print(left, end=' -> ')
            for right, proba in rights.items():
                if len(right) == 1 and left[:4] != 'TERM':
                    print(left, end=' -> ')
                    for c in right:
                        print(c, end=' ')
                    print('p='+str(proba), end=' | ')
                    print('')
            # print('')

    def computeReverseProd(self):
        for left in self.prod.keys():
            for right in self.prod[left].keys():
                self.reverseprod[right][left] = self.prod[left][right]

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


    # @staticmethod
    # def Chomsky_unit_recu(pcfg, left, right):
        # if right not in pcfg.prod[left].keys():
            # return
        # proba = pcfg.prod[left][right]
        # for C in list(pcfg.prod[right[0]].keys())[:]:
            # if len(C)==1 and C[0] in pcfg.nterm:
                # PCFG.Chomsky_unit_recu(pcfg, right[0], C)
        # for C in pcfg.prod[right[0]].keys():
            # pcfg.prod[left][C] = proba * pcfg.prod[right[0]][C]
        # del pcfg.prod[left][right]

    # def Chomsky_unit(self):
        # for left in list(self.prod.keys())[:]:
            # for right in list(self.prod[left].keys())[:]:
                # if len(right)==1 and right[0] in self.nterm:
                    # PCFG.Chomsky_unit_recu(self, left, right)
    
    @staticmethod
    def Chomsky_unit_recu(pcfg):
        i = 0
        while i < len(pcfg.prod):
            left = list(pcfg.prod.keys())[i]
            j = 0
            while j < len(pcfg.prod[left]):
                right = list(pcfg.prod[left].keys())[j]
                if len(right)==1 and right[0] in pcfg.nterm:
                    # print('on traite '+left+' -> '+right[0])
                    proba = pcfg.prod[left][right]
                    # print(right[0] + ' -> ', end='')
                    for C in pcfg.prod[right[0]].keys():
                        # print(C, end = ' | ')
                        pcfg.prod[left][C] = proba * pcfg.prod[right[0]][C]
                    del pcfg.prod[left][right]
                    # if right in pcfg.prod[left].keys():
                        # print('ouuuups')
                    return pcfg, False
                j += 1
            i += 1
        return pcfg, True
            

