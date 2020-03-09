from tree_utils import *
from oov import *
from collections import defaultdict
from operator import itemgetter


# def computeParents1(pcfg, N1):
    # parents = []
    # for left in pcfg.prod.keys():
        # if tuple([N1.symbol]) in pcfg.prod[left]:
            # parents.append(left)
    # return parents

# def computeParents2(pcfg, N1, N2):
    # parents = []
    # for left in pcfg.prod.keys():
        # if (N1.symbol, N2.symbol) in pcfg.prod[left]:
            # parents.append(left)
    # return parents

def computeParents(pcfg, nodes):
    parents = []
    right = tuple([N.symbol for N in nodes])
    # parents = [(left, pcfg.reverseprod[right][left]) for left in pcfg.reverseprod[right].keys()]
    # sorted_parents = sorted(parents, key=itemgetter(1))
    # return [sorted_parents[-i][0] for i in range(1, min(10, len(parents)+1))]
    return list(pcfg.reverseprod[right].keys())

def CYK(pcfg, nodeList):
    # nodeList is a list of leafs : each node has a token and its associated PoS
    # INIT
    n = len(nodeList)
    S = defaultdict(list)
    for i in range(n):
        for possible_symbol in pcfg.lexicon[nodeList[i].token].keys():
            N1 = Node()
            N1.symbol = possible_symbol
            N1.token = nodeList[i].token
            # for parent in most_prob_parent1(pcfg, N1):
            for parent in computeParents(pcfg, [N1]):
                N = Node()
                N.symbol = parent
                N.children = [N1]
                S[(i, i+1)].append(N)
    
    # COMPUTATION OF THE S[i,j]
    for k in range(2, n+1):
        for i in range(n-k+1):
            # we compute S[i,i+k] with the data of the pairs (S[i,i+l], S[i+l,i+k])
            for l in range(1,k):
                for N1 in S[(i,i+l)]:
                    for N2 in S[(i+l, i+k)]:
                        # for parent in most_prob_parent2(pcfg, N1, N2):
                        for parent in computeParents(pcfg, [N1, N2]):
                            N = Node()
                            N.symbol = parent
                            N.children = [N1, N2]
                            S[(i,i+k)].append(N)
            # we keep only the 10 best in S[i,i+k]
            if k < n:
                sorted_S = sorted([(N, N.computeProba(pcfg)) for N in S[(i, i+k)]], key=itemgetter(1))
                S[(i,i+k)] = [sorted_S[-i][0] for i in range(1,min(10, len(sorted_S)+1))]
            


    # Exploitation of S[0,n]
    candidates = []
    for N in S[(0,n)]:
        if N.symbol == pcfg.S:
            candidates.append((N, N.computeProba(pcfg)))
    if not candidates:
        print('THIS INPUT DOES NOT BELONG TO THE CFG')
        return None
    best_candidate = max(candidates, key=itemgetter(1))[0]
    return best_candidate

    

