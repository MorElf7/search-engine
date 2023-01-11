import sys
import math

relevevance_values = 3

def NDCG(ranking, relevances, posNum):
    idealRank = []
    for (queryName, docId), relevance in relevances.items():
        if ranking[0][0] == queryName:
            idealRank.append((queryName, docId))

    idealRank = sorted(idealRank, key=lambda x : relevances[(x[0], x[1])] if (x[0],x[1]) in relevances else 0, reverse=True)
    ideal = relevances[(idealRank[0][0], idealRank[0][1])] if (idealRank[0][0], idealRank[0][1]) in relevances else 0
    for i in range(1, posNum):
        if i == len(idealRank): break
        queryName, docId = idealRank[i]
        relevance = relevances[(queryName, docId)] if (queryName, docId) in relevances else 0
        if relevance > 0:
            ideal += relevance / math.log(i + 1, 2) 
    
    if ideal == 0: return 0

    actual = relevances[(ranking[0][0], ranking[0][1])] if (ranking[0][0], ranking[0][1]) in relevances else 0
    for i in range(1, posNum):
        if i == len(ranking): break
        queryName, docId = ranking[i]
        relevance = relevances[(queryName, docId)] if (queryName, docId) in relevances else 0
        if relevance > 0:
            actual += relevance / math.log(i + 1, 2) 

    return actual / ideal

def RR(ranking, relevances):
    for i in range(len(ranking)):
        queryName, docId = ranking[i]
        relevance = relevances[(queryName, docId)] if (queryName, docId) in relevances else 0
        if relevance > 0:
            return float(1 / (i + 1))
    return 0

def P(ranking, relevances, posNum):
    cnt = 0
    for i in range(posNum):
        if i == len(ranking): break
        queryName, docId = ranking[i]
        relevance = relevances[(queryName, docId)] if (queryName, docId) in relevances else 0
        if relevance > 0:
            cnt += 1

    return float(cnt / posNum)

def R(ranking, relevances, posNum):
    query = ranking[0][0]
    totalRelevances = 0
    for (queryName, docId), relevance in relevances.items():
        if query == queryName and relevance > 0:
            totalRelevances += 1
    
    cnt = 0
    for i in range(posNum):
        if i == len(ranking): break
        queryName, docId = ranking[i]
        relevance = relevances[(queryName, docId)] if (queryName, docId) in relevances else 0
        if relevance > 0:
            cnt += 1
    
    return float(cnt / totalRelevances)

def F1(ranking, relevances, posNum):
    precision = P(ranking, relevances, posNum)
    recall = R(ranking, relevances, posNum)
    if precision + recall == 0: return 0
    return float(2 * recall * precision / (recall + precision))

def AP(ranking, relevances):
    suma = 0
    totalRelevances = 0
    for (queryName, docId), relevance in relevances.items():
        if ranking[0][0] == queryName and relevance > 0:
            totalRelevances += 1

    for i in range(len(ranking)):
        queryName, docId = ranking[i]
        relevance = relevances[(queryName, docId)] if (queryName, docId) in relevances else 0
        if relevance > 0:
            suma += P(ranking, relevances, i + 1)
    if totalRelevances == 0: return 0
    return float(suma / totalRelevances)

class Eval(object):
    def __init__(self, outputFile, qrelsFile, runFile):
        self.outputFile = outputFile
        self.runFile = runFile

        self.qrels = {}
        with open(qrelsFile, "r") as f:
            for line in f:
                l = line.split()
                queryName, docId, relevance = l[0], l[2], int(l[3])
                self.qrels[(queryName, docId)] = relevance

    def runEval(self):
        with open(self.runFile, "r") as fin, open(self.outputFile, "w") as fout:
            ranking = []
            curQuery = ""
            ndcgList, rrList, apList, pList, rList, f1List = [], [], [], [], [], []
            for line in fin:
                l = line.split()
                if curQuery == "":
                    ranking.append((l[0], l[2]))
                    curQuery = l[0]
                elif curQuery != l[0]:
                    ndcg75 = NDCG(ranking, self.qrels, 75)
                    rr = RR(ranking, self.qrels)
                    p = P(ranking, self.qrels, 15)
                    r = R(ranking, self.qrels, 20)
                    f1 = F1(ranking, self.qrels, 25)
                    ap = AP(ranking, self.qrels)
                    rrList.append(rr)
                    apList.append(ap)
                    ndcgList.append(ndcg75)
                    rList.append(r)
                    pList.append(p)
                    f1List.append(f1)
                    fout.write("NDCG@75" + "\t" + curQuery + "\t" + str("{0:.4f}".format(ndcg75)) + "\n")
                    fout.write("RR" + "\t" + curQuery + "\t" + str("{0:.4f}".format(rr)) + "\n")
                    fout.write("P@15" + "\t" + curQuery + "\t" + str("{0:.4f}".format(p)) + "\n")
                    fout.write("R@20" + "\t" + curQuery + "\t" + str("{0:.4f}".format(r)) + "\n")
                    fout.write("F1@25" + "\t" + curQuery + "\t" + str("{0:.4f}".format(f1)) + "\n")
                    fout.write("AP" + "\t" + curQuery + "\t" + str("{0:.4f}".format(ap)) + "\n")
                    ranking = [(l[0], l[2])]
                    curQuery = l[0]
                else:
                    ranking.append((l[0], l[2]))
            

            ndcg75 = NDCG(ranking, self.qrels, 75)
            rr = RR(ranking, self.qrels)
            p = P(ranking, self.qrels, 15)
            r = R(ranking, self.qrels, 20)
            f1 = F1(ranking, self.qrels, 25)
            ap = AP(ranking, self.qrels)
            rrList.append(rr)
            apList.append(ap)
            ndcgList.append(ndcg75)
            rList.append(r)
            pList.append(p)
            f1List.append(f1)
            fout.write("NDCG@75" + "\t" + curQuery + "\t" + str("{0:.4f}".format(ndcg75)) + "\n")
            fout.write("RR" + "\t" + curQuery + "\t" + str("{0:.4f}".format(rr)) + "\n")
            fout.write("P@15" + "\t" + curQuery + "\t" + str("{0:.4f}".format(p)) + "\n")
            fout.write("R@20" + "\t" + curQuery + "\t" + str("{0:.4f}".format(r)) + "\n")
            fout.write("F1@25" + "\t" + curQuery + "\t" + str("{0:.4f}".format(f1)) + "\n")
            fout.write("AP" + "\t" + curQuery + "\t" + str("{0:.4f}".format(ap)) + "\n")

            fout.write("NDCG@75" + "\t" + "all" + "\t" + str("{0:.4f}".format(sum(ndcgList) / len(ndcgList))) + "\n")
            fout.write("MRR" + "\t" + "all" + "\t" + str("{0:.4f}".format(sum(rrList) / len(rrList))) + "\n")
            fout.write("P@15" + "\t" + "all" + "\t" + str("{0:.4f}".format(sum(pList) / len(pList))) + "\n")
            fout.write("R@20" + "\t" + "all" + "\t" + str("{0:.4f}".format(sum(rList) / len(rList))) + "\n")
            fout.write("F1@25" + "\t" + "all" + "\t" + str("{0:.4f}".format(sum(f1List) / len(f1List))) + "\n")
            fout.write("MAP" + "\t" + "all" + "\t" + str("{0:.4f}".format(sum(apList) / len(apList))))



if __name__ == "__main__":
    argv_len = len(sys.argv)
    runFile = sys.argv[1] if argv_len >= 2 else 'simple.trecrun'
    qrelsFile = sys.argv[2] if argv_len >= 3 else 'qrels'
    outputFile = sys.argv[3] if argv_len >= 4 else 'simple.eval'
    
    evalObject = Eval(outputFile, qrelsFile, runFile)
    evalObject.runEval()
    