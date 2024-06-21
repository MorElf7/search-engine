# Shakespeare Search Engine

Hello, this is my implementation of a search engine for Shakespeare plays. All components are built from scratch.
It has both an API as well as a minimal webpage to demonstrate its capabilities

## How it works

First, using the data from the file `shakespeare-data`, each is parsed and process to construct an Inverted List stored using SQLite. All calculations would be used along with this database.

### What happens when a query is passed in
First the query is parsed and tokenized. Then running the preprocessed query through a Boolean filter, we got a list of filtered documents. From that list of filtered documents, we use [BM25](https://en.wikipedia.org/wiki/Okapi_BM25#:~:text=5%20General%20references-,The%20ranking%20function,slightly%20different%20components%20and%20parameters.)
algorithm to score and rank each document. In this cases, each scene of each play and act is considered a document. The results are a sorted list of scenes based on the calculated score. 

## Features

- Parse and tokenize the query using AST and PorterStemmer
- Boolean filter supports `AND`, `OR`, and `NOT`
- Should respects parentheses order and priority, does not support nested parentheses yet
- Exact phrasing with double quotes, eg. "something here" is considered one word
- The database consists of around 800 unique scenes and 900,000 individual words


## Extras

### Plan for the future

- Implement an evaluation system to get data to better improve the search algorithm
- Expands to other databases, optimize the way data is stored and retrieved for better performance

### PageRank Implementation

There is also my own implementation of the famous PageRank algorithm. To run, execute the following command

```bash
python pagerank.py [input] [lambda] [tau] [inlinks_output] [pagerank_output] [k]
```

`input` is the input file, in this case is the file `links.srt.gz` which contains approximately 5.7 million links. `lambda` and `tau` are the constant values for the algorithm, the default value are 0.2 and 0.005 respectively. `inlinks_output` is the file which the would contain the inlinks number of the of the `k` links with the most inlinks. `pagerank_output` is the file which will contain the top `k` links with according to the PageRank algorithm.
