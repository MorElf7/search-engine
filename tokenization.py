from typing import *
import re

vowels = "aeoiu"

class Tokenizer(object):
    def __init__(self, inputFile = None):
        if inputFile is not None:
            with open(inputFile, "r") as f:
                self.preProcessDoc = f.read()
                self.document = self.textProcessing(self.preProcessDoc)
    
    def readInput(self, doc):
        self.preProcessDoc = doc
        self.document = self.textProcessing(self.preProcessDoc)

    def getProcessDoc(self):
        return self.document

    def getPreProcessDoc(self):
        return self.preProcessDoc

    # Helper functions for tokenization, stemming
    def isAbbreviation(self, word : str) -> bool:
        check : bool = True
        if len(word) == 1 or len(word) == 0: return False
        l : int = 0
        while not word[l].isalnum() and l < len(word) - 1:
            l += 1
        j : int = len(word) - 1
        while not word[j].isalnum() and j >= 0:
            j -= 1
        for i in range(l, j):
            if not ((word[i] == "." and word[i + 1].isalnum()) 
                or (word[i + 1] == "." and word[i].isalnum())):
                check = False
        return check

    def isTitle(self, word : str) -> bool:
        titles = ["mr.", "mrs."]
        for title in titles:
            if word.lower() in title:
                return True
        return False

    def findNonVowelFollowedVowel(self, stem : str) -> int:
        if len(stem) <= 1: return -1
        for i in range(len(stem) - 1):
            if stem[i] in vowels and stem[i + 1] not in vowels:
                return i + 1
        return -1

    def haveVowelPreceed(self, stem : str, index : int) -> int:
        while index >= 0:
            if stem[index] in vowels:
                return index
            index -= 1
        return -1

    # Helper function for step 1b of Porter Stemmer
    def step1b2(self, stem : str) -> str:
        suffix = stem[:-3:-1][::-1]
        if len(suffix) == 2 and suffix in ["at", "bl", "iz"]:
            stem = stem + "e"
        elif (len(suffix) == 2 
            and suffix[0] == suffix[1] 
            and suffix not in ["ll", "ss", "zz"]):
            stem = stem[:-1]
        elif self.isShortWord(stem):
            stem = stem + "e"

        return stem

    def isShortWord(self, stem : str) -> bool:
        flag = False
        count = 0
        for i in range(len(stem)):
            if stem[i] in vowels:
                flag = True
            else:
                if flag:
                    count += 1
                flag = False
        return count == 1
        
    # Tokenization helper function
    def tokenization(self, document: str) -> List[str]:
        wordList : List[str] = document.split()
        i : int = 0
        while (i < len(wordList)):
            wordList[i] = wordList[i].replace("'", "") #Consider contractions

            if self.isAbbreviation(wordList[i]):
                wordList[i] = wordList[i].replace(".", "") #Consider abbreviations

            if self.isTitle(wordList[i]) and i < len(wordList) - 1:
                wordList[i] = wordList[i].replace(". ", "") + wordList.pop(i + 1) #Consider titles

            if not wordList[i].isalnum(): #Consider all other non alphanumeric characters as word separators
                temp = list(filter(None, re.split("[^a-zA-Z0-9]+", wordList[i])))
                wordList.pop(i)
                wordList[i:i] = temp
                if len(temp) == 0:
                    wordList[i] = wordList[i].lower()
                    continue

            wordList[i] = wordList[i].lower()
            i += 1
        return wordList

    # Stopping helper function
    def stopping(self, tokens : List[str]) -> None:
        f = open("stopwords.txt", "r")
        stopwordsDoc = f.read()
        stopwords = stopwordsDoc.split()
        f.close()
        i : int = 0
        while i < len(tokens):
            if tokens[i] in stopwords:
                tokens.pop(i)
                continue
            i += 1
        return None

    # Stemming helper function
    def stemming(self, stem : str) -> None:
        # Step 1a
        suffix : str = stem[:-5:-1][::-1]
        if "sses" in suffix:
            stem = stem[:-2]
        elif "ied" in suffix or "ies" in suffix:
            if len(stem) - 3 == 1:
                stem = stem[:-1]
            elif len(stem) - 3 > 1:
                stem = stem[:-2]
        elif "us" in suffix or "ss" in suffix:
            pass
        elif (len(suffix) > 1 and stem[-1] == "s" 
            and stem[-2] not in vowels 
            and self.haveVowelPreceed(stem, len(stem) - 3) >= 0):
            stem = stem[:-1]

        # Step 1b
        suffix = stem[:-6:-1][::-1]
        nonVowelVowelIndex = self.findNonVowelFollowedVowel(stem)
        if ("eedly" in suffix 
            and nonVowelVowelIndex != -1 
            and nonVowelVowelIndex < len(stem) - 6):
            stem = stem[:-3]
        elif ("ingly" in suffix and self.haveVowelPreceed(stem, len(stem) - 6)):
            stem = stem[:-5]
            stem = self.step1b2(stem)
        elif ("edly" in suffix and self.haveVowelPreceed(stem, len(stem) - 5)):
            stem = stem[:-4]
            stem = self.step1b2(stem)
        elif ("ing" in suffix and self.haveVowelPreceed(stem, len(stem) - 4)):
            stem = stem[:-3]
            stem = self.step1b2(stem)
        elif ("eed" in suffix 
            and nonVowelVowelIndex != -1 
            and nonVowelVowelIndex < len(stem) - 4):
            stem = stem[:-1]
        elif ("ed" in suffix and self.haveVowelPreceed(stem, len(stem) - 3)):
            stem = stem[:-2]
            stem = self.step1b2(stem)

        return stem

    # The whole tokenization system, in order, tokenization, stopping, stemming
    def textProcessing(self, document : str) :
        result = self.tokenization(document)
        self.stopping(result)
        for i in range(len(result)):
            result[i] = self.stemming(result[i])
        return " ".join(result)

    # Helper function to return the list of k most frequent terms
    def frequentTerms(terms : List[str], k) -> List[str]:
        store = {}
        x, y = 0, 0 # Variables to plot Heape's Law graph
        xPoints, yPoints = [], []
        for term in terms:
            if term not in store:
                store[term] = 0
                y += 1
            store[term] += 1
            x += 1
            xPoints.append(x)
            yPoints.append(y)
        
        store = dict(sorted(store.items(), key = lambda x: x[1], reverse = True))
        count = 0
        result = []
        for key, value in store.items():
            if count == k:
                break
            result.append(key + " " + str(value))
            count += 1
        return result
    