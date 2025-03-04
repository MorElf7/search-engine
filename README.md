# Shakespeare Search Engine

Hello, this is my implementation of a search engine for Shakespeare plays. All components are built from scratch.
It has both an API as well as a minimal webpage to demonstrate its capabilities. Clone the repo to your machine to see its capabilities for yourself.

## How to run
First clone the repo
```bash
cd ~
git clone https://github.com/MorElf7/search-engine.git
cd search-engine
```

Then ensure that you have Python 3.12.4. Install the neccessary packages 
```bash
pip install -r requirements.txt
```

Then download the database file from [here](https://drive.google.com/file/d/1kkE-_rxEDT0m8aXi4hZ8pW_ErFHlBsjo/view?usp=sharing). Put the database file to the root folder of the repo. 

> [!NOTE]
> You can choose not to download the database file, the application would auto generate one for you, but it could take a long time to create the full database.


Then just start the server with 
```bash
python application.py
```

<!-- Checkout the webpage [here](http://18.222.201.31/) -->
<!---->
<!-- Checkout the api [here](http://18.222.201.31/swagger) -->
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

There is also my own implementation of the famous PageRank algorithm. Download these [files](https://github.com/MorElf7/search-engine/tree/master/pagerank) to try it out.

To run, requires at least Python 3.7, execute the following command

```bash
python pagerank.py [input] [lambda] [tau] [inlinks_output] [pagerank_output] [k]
```

`input` is the input file, in this case is the file `links.srt.gz` which contains approximately 5.7 million links. `lambda` and `tau` are the constant values for the algorithm, the default value are 0.2 and 0.005 respectively. `inlinks_output` is the file which the would contain the inlinks number of the of the `k` links with the most inlinks. `pagerank_output` is the file which will contain the top `k` links with according to the PageRank algorithm.
