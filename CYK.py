from tree_utils import *
from oov import *
from collections import defaultdict
from operator import itemgetter


def computeParents1(pcfg, N1):
    parents = []
    for left in pcfg.prod.keys():
        if tuple([N1.symbol]) in pcfg.prod[left]:
            parents.append(left)
    return parents

def computeParents2(pcfg, N1, N2):
    parents = []
    for left in pcfg.prod.keys():
        if (N1.symbol, N2.symbol) in pcfg.prod[left]:
            parents.append(left)
    return parents

def CYK(pcfg, nodeList):
    # nodeList is a list of leafs : each node has a token and its associated PoS
    # INIT
    n = len(nodeList)
    S = defaultdict(list)
    for i in range(n):
        N1 = nodeList[i]
        parents = computeParents1(pcfg, N1)
        for parent in parents:
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
                        parents = computeParents2(pcfg, N1, N2)
                        for parent in parents:
                            N = Node()
                            N.symbol = parent
                            N.children = [N1, N2]
                            S[(i,i+k)].append(N)

    # Exploitation of S[0,n]
    candidates = []
    for N in S[(0,n)]:
        if N.symbol == pcfg.S:
            candidates.append((N, N.computeProba(pcfg)))
    if not candidates:
        print('THIS INPUT DOES NOT BELONG TO THE CFG')
        return
    best_candidate = max(candidates, key=itemgetter(1))[0]
    return best_candidate.sentence2bracketed()

    

