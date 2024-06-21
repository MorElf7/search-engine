import sys, gzip, datetime
import utils

class PageRank:
    def __init__(self, lb, tau, filename):
        self.lb = lb
        self.tau = tau
        self.pages = set()
        self.inlinks = dict()
        self.outlinks = dict()
        f = gzip.open(filename, "rb")
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

def writeOutput(out, filename, k):
    f = open(filename, "w")
    index = 1
    for page, rank in out.items():
        f.write(str(page) + "\t" + str(index) + "\t" + str(rank) + "\n")
        if index == k: 
            break
        index += 1

    f.close()
    return None

if __name__ == "__main__":
    argv_len = len(sys.argv)
    inputFile = sys.argv[1] if argv_len >= 2 else "links.srt.gz"
    lambda_val = float(sys.argv[2]) if argv_len >=3 else 0.2
    tau = float(sys.argv[3]) if argv_len >=4 else 0.005
    inLinksFile = sys.argv[4] if argv_len >= 5 else "inlinks.txt"
    pagerankFile = sys.argv[5] if argv_len >= 6 else "pagerank.txt"
    k = int(sys.argv[6]) if argv_len >= 7 else 100

    start_time = datetime.datetime.now()
    pr = PageRank(lambda_val, tau, inputFile)
    print("Finish processing input: " + utils.get_elapsed_time(start_time, datetime.datetime.now()))
    start_time = datetime.datetime.now()
    writeOutput(pr.countInlinks(), inLinksFile, k)
    print("Finish counting links: " + utils.get_elapsed_time(start_time, datetime.datetime.now()))
    start_time = datetime.datetime.now()
    writeOutput(pr.getPageRank(), pagerankFile, k)
    print("Finish PageRank: " + utils.get_elapsed_time(start_time, datetime.datetime.now()))
    exit(1)
    