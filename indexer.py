import json, gzip, time


class Posting(object):
    def __init__(self, playId, sceneId, wordPos = None):
        self.playId = playId
        self.sceneId = sceneId
        self.positions = list(wordPos)

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

def find_indices(lst, condition):
    return [i for i, elem in enumerate(lst) if condition(elem)]

class Indexer(object):
    def __init__(self, input_file):
        self.input_file = input_file
        self.data = dict()
        self.outputFolder = ""
        self.queriesFile = ""
        self.invertedList = dict()
        self.sceneList = dict()
        self.playList = dict()

        self.createInvertedList()

    def load_data(self):
        self.data["corpus"] = list()
        with open(self.input_file, 'r') as f:
            for l in f:
                line = json.load(l.strip())
                play_name = line["play_name"]
                act_id, scene_num, line_number = line["line_number"].split(".")
                scene_id = play_name + ":" + act_id + "." + scene_num
                if len(find_indices(self.data["corpus"], lambda x : x["sceneId"] == scene_id)) == 0:
                    scene = dict()
                    scene["playId"] = line["play_name"]
                    scene["sceneId"] = scene_id






    def createInvertedList(self):
        for idx, s in enumerate(self.data["corpus"]):
            tokens = s["text"].split()

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
                
    def getAvgSceneLen(self):
        count = 0
        for k, v in self.sceneList.items():
            count += v
        return count / len(self.sceneList)

    def getMinLenScene(self):
        return min(self.sceneList, key = self.sceneList.get)

    def getMaxLenScene(self):
        return max(self.sceneList, key = self.sceneList.get)

    def getMinPlayScene(self):
        return min(self.playList, key = self.playList.get)

    def getMaxPlayScene(self):
        return max(self.playList, key = self.playList.get)

    def getScenceContainsPhrase(self, phrase):
        words = phrase.split()        
        res = list(self.invertedList[words[0]].getPostingList().keys())

        if len(res) == 0:
            return res

        for i in range(1, len(words), 1):
            curWord = words[i]
            prevWord = words[i - 1]
            postings = self.invertedList[curWord].getPostingList()
            prevWordPostings = self.invertedList[prevWord].getPostingList()
            temp = []
            for scene in res:
                if scene in postings:
                    check = 0
                    for prev in prevWordPostings[scene].positions:
                        if (prev + 1) in postings[scene].positions:
                            check += 1
                            break
                    
                    if check != 0:
                        temp.append(scene)
            
            res = temp
            
        return res

    def processAndQuery(self, phrases, isScene):
        if isScene:
            res = self.getScenceContainsPhrase(phrases[0].strip())
            for i in range(1, len(phrases)):
                if len(res) == 0:
                    return res

                temp = self.getScenceContainsPhrase(phrases[i].strip())
                res = list(set(res) & set(temp)) # Get intersection of 2 list

            return set(res)
        else:
            res = self.extractPlayListFromSceneList(self.getScenceContainsPhrase(phrases[0].strip()))

            for i in range(1, len(phrases)):
                if len(res) == 0:
                    return res

                temp = self.extractPlayListFromSceneList(self.getScenceContainsPhrase(phrases[i].strip()))
                res = list(set(res) & set(temp)) # Get intersection of 2 list

            return set(res)

    def processOrQuery(self, phrases, isScene):
        if isScene:
            res = set(self.getScenceContainsPhrase(phrases[0].strip()))
            for i in range(1, len(phrases)):
                if len(res) == 0:
                    return res

                temp = self.getScenceContainsPhrase(phrases[i].strip())
                res = set(list(res) + list(temp)) # Get intersection of 2 list

            return set(res)
        else:
            res = set(self.extractPlayListFromSceneList(self.getScenceContainsPhrase(phrases[0].strip())))

            for i in range(1, len(phrases)):
                if len(res) == 0:
                    return res

                temp = self.extractPlayListFromSceneList(self.getScenceContainsPhrase(phrases[i].strip()))
                res = set(list(res) + list(temp)) # Get intersection of 2 list

            return set(res)

    def extractPlayListFromSceneList(self, scenes):
        res = []

        for scene in scenes:
            res.append(scene.split(":")[0])

        return res

    def processQuery(self, query):
        queryName = query[0]
        isScene = query[1] == 'scene'
        if query[2].lower() == "and":
            results = list(self.processAndQuery(query[3:], isScene))
        elif query[2].lower() == "or":
            results = list(self.processOrQuery(query[3:], isScene))

        results.sort()

        with open(self.outputFolder + queryName + ".txt", "w") as f:
            for res in results:
                f.write(res + "\n")

        return

    def startQuery(self):
        with open(self.queriesFile, 'r') as f:
            maxTime = 0
            maxQuery = ""
            for line in f:
                l = line.split("\t")
                print("Start query " + l[0] + ": ")
                startTime = time.time()
                self.processQuery(l)
                endTime = time.time() - startTime
                if endTime > maxTime:
                    maxQuery = l[0]
                    maxTime = endTime
                print("Finish query: " + str(endTime))
            # print("Longest query: ", maxQuery)
        return 