import json, gzip, sys, time, os
import math

k1 = 1.2
k2 = 1
b = 0.75
mu = 300

def extractPlayListFromSceneList(scenes):
    res = set()

    for scene in scenes:
        res.add(scene.split(":")[0])

    return list(res)

def scoreBM25(n, f, qf, r, R, N, dl, avdl):
    K = computeK(dl, avdl)
    first = math.log(((r + 0.5) / (R - r + 0.5)) / ((n - r + 0.5) / (N - n - R + r + 0.5)), 2)
    second = ((k1 + 1) * f) / (K + f)
    third = ((k2 + 1) * qf) / (k2 + qf)
    return first * second * third

def computeK(dl, avdl):
    return k1 * ((1 - b) + b * (float(dl) / float(avdl)))


def scoreQL(fqD, D, fqC, C):
    first = float(fqD + mu * fqC / C)
    second = float(D + mu)
    return math.log(first / second)

class Posting(object):
    def __init__(self, playId, sceneId, wordPos = None):
        self.playId = playId
        self.sceneId = sceneId
        self.positions = list(wordPos)

    def count(self):
        return len(self.positions)

class PostingList(object):
    def __init__(self):
        self.postings = dict()

    def insert(self, playId, sceneId, wordPos):
        if sceneId not in self.postings:
            self.postings[sceneId] = Posting(playId, sceneId, [wordPos])
        else:
            self.postings[sceneId].positions.append(wordPos)

    def getPostingList(self):
        return self.postings


class Indexer(object):
    def __init__(self, inputFile):
        with gzip.open(inputFile, 'r') as f:
            self.data = json.loads(f.read().decode('utf-8'))
        
        self.outputFile = outputFile
        self.queriesFile = queriesFile
        self.invertedList = dict()
        self.sceneList = dict()
        self.playList = dict()
        self.collectionLen = 0

        self.createInvertedList()

    def createInvertedList(self):
        for idx, s in enumerate(self.data["corpus"]):
            tokens = s["text"].split()
            self.collectionLen += len(tokens)

            if s["sceneId"] not in self.sceneList:
                self.sceneList[s["sceneId"]] = 0
            if s["playId"] not in self.playList:
                self.playList[s["playId"]] = 0
            
            self.sceneList[s["sceneId"]] += len(tokens)
            self.playList[s["playId"]] += len(tokens)

            for i, token in enumerate(tokens):
                if token not in self.invertedList:
                    self.invertedList[token] = PostingList()
                self.invertedList[token].insert(s["playId"], s["sceneId"], i)

    def getTermFreqCollection(self, term):
        postingList = self.invertedList[term].getPostingList()
        cnt = 0
        for scene, posting in postingList.items():
            cnt += posting.count()
        return cnt
    
    def getTfScene(self, term, scene):
        postingList = self.invertedList[term].getPostingList()
        return 0 if scene not in postingList else postingList[scene].count()

    def getSceneLen(self, scene):
        return self.sceneList[scene]

    def getAvgSceneLen(self):
        return float(self.collectionLen / len(self.sceneList))

    def getTfPlay(self, term, play):
        postingList = self.invertedList[term].getPostingList()
        cnt = 0
        for scene, posting in postingList.items():
            if play == posting.playId:
                cnt += posting.count()
        return cnt 

    def getPlayLen(self, play):
        return self.playList[play]

    def getAvgPlayLen(self):
        return float(self.collectionLen / len(self.playList))
        
class Query(object):
    def __init__(self, outputFile, queriesFile):
        self.outputFile = outputFile
        self.queriesFile = queriesFile

    def runBM25(self, idx, query, isScene):
        res = {}
        # sceneLst = set()
        # for term in query:
        #     if term in idx.invertedList: 
        #         postingList = idx.invertedList[term].getPostingList()
        #         for scene in postingList.keys():
        #             sceneLst.add(scene)

        # if isScene:
        #     averageSceneLength = idx.getAvgSceneLen()
        #     for scene in sceneLst:
        #         for term in query:
        #             if term in idx.invertedList: 
        #                 postingList = idx.invertedList[term].getPostingList()

        #                 score = scoreBM25(n = len(postingList.keys()), f=idx.getTfScene(term, scene), qf=query.count(term), r=0, R=0.0,
        #                                             N=len(idx.sceneList), dl=idx.getSceneLen(scene), avdl=averageSceneLength)
                        
        #                 if scene in res:
        #                     res[scene] += score
        #                 else:
        #                     res[scene] = score
        # else:
        #     averagePlayLength = idx.getAvgPlayLen()
        #     playLst = idx.extractPlayListFromSceneList(sceneLst.keys())
        #     for play in playLst:
        #         for term in query:
        #             if term in idx.invertedList: 
        #                 postingList = idx.invertedList[term].getPostingList()

        #                 score = scoreBM25(n = len(idx.extractPlayListFromSceneList(postingList.keys())), 
        #                                             f=idx.getTfPlay(term, play), qf=query.count(term), r=0.0, R=0.0,
        #                                             N=len(idx.playList), dl=idx.getPlayLen(play), avdl=averagePlayLength)
                        
        #                 if play in res:
        #                     res[play] += score
        #                 else:
        #                     res[play] = score
        
        if isScene:
            averageSceneLength = idx.getAvgSceneLen()
            for term in set(query):
                if term in idx.invertedList: 
                    postingList = idx.invertedList[term].getPostingList()
                    for scene in postingList.keys():
                        score = scoreBM25(n = len(postingList.keys()), f=idx.getTfScene(term, scene), qf=query.count(term), r=0, R=0.0,
                                                    N=len(idx.sceneList), dl=idx.getSceneLen(scene), avdl=averageSceneLength)
                        
                        if scene in res:
                            res[scene] += score
                        else:
                            res[scene] = score
        else:
            averagePlayLength = idx.getAvgPlayLen()
            for term in set(query):
                if term in idx.invertedList: 
                    postingList = idx.invertedList[term].getPostingList()
                    playLst = extractPlayListFromSceneList(postingList.keys())

                    for play in playLst:
                        score = scoreBM25(n = len(playLst), f=idx.getTfPlay(term, play), qf=query.count(term), r=0.0, R=0.0,
                                                    N=len(idx.playList), dl=idx.getPlayLen(play), avdl=averagePlayLength)
                        
                        if play in res:
                            res[play] += score
                        else:
                            res[play] = score

        return dict(sorted(res.items(), key=lambda x : (-x[1], x[0])))

    def runQL(self, idx, query, isScene):
        res = {}
        sceneLst = set()
        for term in query:
            if term in idx.invertedList: 
                postingList = idx.invertedList[term].getPostingList()
                for scene in postingList.keys():
                    sceneLst.add(scene)

        if isScene:
            docLst = sceneLst
            for term in query:
                if term in idx.invertedList: 
                    for doc in docLst:
                        score = scoreQL(fqD=idx.getTfScene(term, doc), D=idx.getSceneLen(doc), fqC=idx.getTermFreqCollection(term), C=idx.collectionLen)

                        if doc in res:
                            res[doc] += score
                        else:
                            res[doc] = score
        else: 
            docLst = extractPlayListFromSceneList(sceneLst)
            for term in query:
                if term in idx.invertedList: 
                    for doc in docLst:
                        score = scoreQL(fqD=idx.getTfPlay(term, doc), D=idx.getPlayLen(doc), fqC=idx.getTermFreqCollection(term), C=idx.collectionLen)

                        if doc in res:
                            res[doc] += score
                        else:
                            res[doc] = score

        return dict(sorted(res.items(), key=lambda x : (-x[1], x[0])))

    def processQuery(self, idx, query):
        queryName = query[0]
        isScene = query[1] == 'scene'
        if query[2].lower() == "bm25":
            results = self.runBM25(idx, query[3:], isScene)
        elif query[2].lower() == "ql":
            results = self.runQL(idx, query[3:], isScene)
        
        with open(self.outputFile, "a") as f:
            index = 1
            for key, value in results.items():
                f.write(str(queryName) + " ")
                f.write("skip" + " ")
                f.write(str(key) + " ")
                f.write(str(index) + " ")
                f.write(str("{0:.6f}".format(value)) + " ")
                f.write("bcao" + "\n")
                index += 1
                if index > 100:
                    break

    def runQuery(self, idx):
        if os.path.exists(self.outputFile):
            os.remove(self.outputFile)
        with open(self.queriesFile, 'r') as f:
            for line in f:
                l = line.split()
                print("Start query " + l[0] + ": ")
                startTime = time.time()
                self.processQuery(idx, l)
                endTime = time.time() - startTime
                print("Finish query: " + str(endTime))
        return 


if __name__ == "__main__":
    # argv_len = len(sys.argv)
    # inputFile = sys.argv[1] if argv_len >= 2 else 'shakespeare-scenes.json.gz'
    # queriesFile = sys.argv[2] if argv_len >= 3 else 'trainQueries.tsv'
    # outputFile = sys.argv[3] if argv_len >= 4 else 'train.results'
    # # queriesFile = sys.argv[2] if argv_len >= 3 else 'playQueries.tsv'
    # # outputFile = sys.argv[3] if argv_len >= 4 else 'playQueries.results'
    
    # starttime = time.time()
    # idx = Indexer(inputFile)
    # print("Finish building inverted list: " + str(time.time() - starttime))
    # query = Query(outputFile, queriesFile)
    # query.runQuery(idx)
    t1 = scoreBM25(6, 4, 0, 0, 0, 1000, 20, 20)
    t2 = scoreBM25(6, 3, 2, 0, 0, 1000, 20, 20)
    t3 = scoreBM25(6, 5, 0, 0, 0, 1000, 20, 20)
    t4 = scoreBM25(6, 2, 0, 0, 0, 1000, 20, 20)
    t5 = scoreBM25(6, 1, 1, 0, 0, 1000, 20, 20)
    t6 = scoreBM25(6, 5, 0, 0, 0, 1000, 20, 20)
    print(t1 + t2 + t3 + t4 + t5)
