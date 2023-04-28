import os
from indexer import Indexer

def create_index(input_file):
    Index = Indexer(input_file)

if __name__ == '__main__':
    print("Welcome to the Shakespeare database search engine")
    if not os.path.exist("shakespeare_index.json"):
        create_index("shakespeare-data")