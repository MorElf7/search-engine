import os, sys, re
from indexer import Indexer
from tokenization import Tokenizer
from query import Query


if __name__ == '__main__':
    argv_len = len(sys.argv)
    mode = sys.argv[1] if argv_len >= 2 else "bm25"
    output_file = sys.argv[2] if argv_len >= 3 else "queries.result"

    if mode not in ["bm25", "ql"]:
        raise Exception("Query mode not recognized")

    print("Welcome to the Shakespeare database search engine!")
    print("Checking if the inverted list exists ...")
    if not os.path.exists("database.json.gz"):
        idx = Indexer(raw_data_file="shakespeare-data")
    else:
        while True:
            inp = input("Found existing inverted list 'database.json.gzip', do you want to use it? (y/n)") or "y"
            if inp.lower() == "y":
                idx = Indexer(database="database.json.gz")
                break
            elif inp.lower() == "n":
                idx = Indexer(raw_data_file="shakespeare-data")
                break
            else:
                continue
    
    tokenizer = Tokenizer()
    engine = Query()
    while True:
        print("Type 'quit' to exit")
        query = input("Enter your search: ")
        if query == "quit":
            exit()
        query = tokenizer.tokenize(query)
        if mode == "bm25":
            res = engine.bm25(idx, query, True)
        elif mode == "ql":
            res = engine.ql(idx, query, True)
        
        with open("self.outputFile", "a") as f:
            index = 1
            for key, value in res.items():
                play, act, scene = re.split("[:.]", key)
                if index <= 10:
                    print("Rank {}: {} Act {} Scene {}".format(index, play, act, scene))
                f.write(str(key) + " ")
                f.write(str(index) + " ")
                f.write(str("{0:.6f}".format(value)) + " ")
                f.write("\n")
                index += 1
                if index > 100:
                    break
