import gzip

class PageRank:
    def __init__(self, lb, tau, filename = None):
        self.lb = lb
        self.tau = tau
        self.pages = set()
        self.inlinks = dict()
        self.outlinks = dict()
        if filename is not None:
            with gzip.open(filename, "rb") as f:
                while True:
                    line = f.readline()
                    if line == b'':
                        break
                    link = str(line, "utf-8")
                    src, des = link.split()
                    self.pages.add(src)
                    self.pages.add(des)
                    if src not in self.outlinks:
                        self.outlinks[src] = set()
                    if des not in self.inlinks:
                        self.inlinks[des] = set()
                    self.outlinks[src].add(des)
                    self.inlinks[des].add(src)

    def readInput(self, inp):
        self.pages = set()
        self.inlinks = dict()
        self.outlinks = dict()
        lines = inp.split("\n")
        for line in lines:
            link = str(line, "utf-8")
            src, des = link.split()
            self.pages.add(src)
            self.pages.add(des)
            if src not in self.outlinks:
                self.outlinks[src] = set()
            if des not in self.inlinks:
                self.inlinks[des] = set()
            self.outlinks[src].add(des)
            self.inlinks[des].add(src)

    def countInlinks(self):
        lst = dict()
        for page in self.pages:
            if page not in self.inlinks:
                lst[page] = 0
            else:
                lst[page] = len(self.inlinks[page])
        return dict(sorted(lst.items(), key = lambda x : x[1], reverse = True))

    def getPageRank(self):
        currentPR, resultPR = dict(), dict()
        P = len(self.pages)
        delta_x = dict()
        delta_y = float((1 - self.lb) / P)
        count = 0
        res = float(self.lb / P)
        initialPR = float(1 / P)
        for page in self.pages:
            if len(self.outlinks.get(page, set())) > 0:
                delta_x[page] = float((1 - self.lb) / len(self.outlinks[page]))
            currentPR[page] = initialPR
        
        while True:
            count += 1
            for page in self.pages:
                resultPR[page] = res
            delta = 0
            for page in self.pages:
                if page not in self.outlinks:
                    desLst = set()
                else:
                    desLst = self.outlinks[page]
                if len(desLst) > 0:
                    for q in desLst:
                        resultPR[q] += delta_x[page] * currentPR[page]
                else:
                    delta += delta_y * currentPR[page]
            check = True
            for page, rank in resultPR.items():
                resultPR[page] += delta
                if check and abs(resultPR[page] - currentPR[page]) >= self.tau:
                    check = False
                currentPR[page] = resultPR[page]
        
            if check:
                return dict(sorted(resultPR.items(), key = lambda x: x[1], reverse = True))