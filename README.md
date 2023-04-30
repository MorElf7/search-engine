# Shakespeare Scenes search engine

Hello, this is my implementation of a search engine for Shakespeare plays. Processes like tokenization, indexing, and querying are my own implementation.

In this implementation, I regard scenes of each plays as the document, and the inverted list is constructed using data from `shakespeare-data` file. There are 2 models of information retrieval available: BM25 and QL(Query Likelihood). You can choose either for your search.

Running on Python 3.10. Make sure that you have `shakespeare-data` file in the same directory as `shakespeare.py`. To run, execute the following command

```bash
python shakespeare.py [mode] [output_file]
```

The default mode is BM25

```bash
python shakespeare.py bm25
```

but you can run the following command to query with QL

```bash
python shakespeare.py ql
```

When querying, the program would return the top 10 results as well as saving the top 100 results to a file of your choosing. Default output file is `queries.result`. It is in the format

```bash
key     rank    score
```

The key is `[play name]:[act].[scene]`, rank is the the rank according to the score, from high to low.

## PageRank Implementation

There is also my own implementation of the famous PageRank algorithm. To run, execute the following command

```bash
python pagerank.py [input] [lambda] [tau] [inlinks_output] [pagerank_output] [k]
```

`input` is the input file, in this case is the file `links.srt.gz` which contains approximately 5.7 million links. `lambda` and `tau` are the constant values for the algorithm, the default value are 0.2 and 0.005 respectively. `inlinks_output` is the file which the would contain the inlinks number of the of the `k` links with the most inlinks. `pagerank_output` is the file which will contain the top `k` links with according to the PageRank algorithm.
