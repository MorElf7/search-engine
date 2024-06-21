import json
import math
import os
import re
import sqlite3
from uuid import uuid4

from tqdm import tqdm

from utils import get_num_lines


# Tokenizer
class PorterStemmer:
    def __init__(self):
        self.vowels = "aeiou"

    def is_consonant(self, word, i):
        if word[i] in self.vowels:
            return False
        if word[i] == "y":
            if i == 0:
                return True
            else:
                return not self.is_consonant(word, i - 1)
        return True

    def measure(self, word):
        m = 0
        i = 0
        while i < len(word):
            while i < len(word) and not self.is_consonant(word, i):
                i += 1
            if i >= len(word):
                break
            i += 1
            while i < len(word) and self.is_consonant(word, i):
                i += 1
            m += 1
        return m

    def contains_vowel(self, word):
        for i in range(len(word)):
            if not self.is_consonant(word, i):
                return True
        return False

    def ends_double_consonant(self, word):
        if len(word) < 2:
            return False
        return word[-1] == word[-2] and self.is_consonant(word, len(word) - 1)

    def ends_cvc(self, word):
        if len(word) < 3:
            return False
        return (
            self.is_consonant(word, len(word) - 1)
            and not self.is_consonant(word, len(word) - 2)
            and self.is_consonant(word, len(word) - 3)
            and word[-1] not in "wxy"
        )

    def step1a(self, word):
        if word.endswith("sses"):
            return word[:-2]
        elif word.endswith("ies"):
            return word[:-2]
        elif word.endswith("ss"):
            return word
        elif word.endswith("s"):
            return word[:-1]
        return word

    def step1b(self, word):
        if word.endswith("eed"):
            if self.measure(word[:-3]) > 0:
                return word[:-1]
        elif word.endswith("ed"):
            if self.contains_vowel(word[:-2]):
                word = word[:-2]
                return self.step1b_helper(word)
        elif word.endswith("ing"):
            if self.contains_vowel(word[:-3]):
                word = word[:-3]
                return self.step1b_helper(word)
        return word

    def step1b_helper(self, word):
        if word.endswith("at") or word.endswith("bl") or word.endswith("iz"):
            return word + "e"
        elif (
            self.ends_double_consonant(word)
            and not word.endswith("l")
            and not word.endswith("s")
            and not word.endswith("z")
        ):
            return word[:-1]
        elif self.measure(word) == 1 and self.ends_cvc(word):
            return word + "e"
        return word

    def step1c(self, word):
        if word.endswith("y") and self.contains_vowel(word[:-1]):
            return word[:-1] + "i"
        return word

    def step2(self, word):
        suffixes = {
            "ational": "ate",
            "tional": "tion",
            "enci": "ence",
            "anci": "ance",
            "izer": "ize",
            "bli": "ble",
            "alli": "al",
            "entli": "ent",
            "eli": "e",
            "ousli": "ous",
            "ization": "ize",
            "ation": "ate",
            "ator": "ate",
            "alism": "al",
            "iveness": "ive",
            "fulness": "ful",
            "ousness": "ous",
            "aliti": "al",
            "iviti": "ive",
            "biliti": "ble",
            "logi": "log",
        }
        for suffix, replacement in suffixes.items():
            if word.endswith(suffix):
                if self.measure(word[: -len(suffix)]) > 0:
                    return word[: -len(suffix)] + replacement
        return word

    def step3(self, word):
        suffixes = {
            "icate": "ic",
            "ative": "",
            "alize": "al",
            "iciti": "ic",
            "ical": "ic",
            "ful": "",
            "ness": "",
        }
        for suffix, replacement in suffixes.items():
            if word.endswith(suffix):
                if self.measure(word[: -len(suffix)]) > 0:
                    return word[: -len(suffix)] + replacement
        return word

    def step4(self, word):
        suffixes = [
            "al",
            "ance",
            "ence",
            "er",
            "ic",
            "able",
            "ible",
            "ant",
            "ement",
            "ment",
            "ent",
            "ou",
            "ism",
            "ate",
            "iti",
            "ous",
            "ive",
            "ize",
        ]
        for suffix in suffixes:
            if word.endswith(suffix):
                if self.measure(word[: -len(suffix)]) > 1:
                    return word[: -len(suffix)]
        if (
            word.endswith("ion")
            and len(word) > 3
            and (word[-4] == "s" or word[-4] == "t")
        ):
            if self.measure(word[:-3]) > 1:
                return word[:-3]
        return word

    def step5a(self, word):
        if word.endswith("e"):
            if self.measure(word[:-1]) > 1:
                return word[:-1]
            elif self.measure(word[:-1]) == 1 and not self.ends_cvc(word[:-1]):
                return word[:-1]
        return word

    def step5b(self, word):
        if (
            self.measure(word) > 1
            and self.ends_double_consonant(word)
            and word.endswith("l")
        ):
            return word[:-1]
        return word

    def stem(self, word):
        word = word.lower()
        word = self.step1a(word)
        word = self.step1b(word)
        word = self.step1c(word)
        word = self.step2(word)
        word = self.step3(word)
        word = self.step4(word)
        word = self.step5a(word)
        word = self.step5b(word)
        return word

    def tokenize_paragraph(self, paragraph):
        words = paragraph.split()
        return [self.stem(word) for word in words]


# Parser
# Insert 'OR' between consecutive terms where no explicit operator is present
def insert_default_operators(tokens):
    new_tokens = []
    prev_was_term = False
    for token in tokens:
        if token.upper() not in ["AND", "OR", "NOT"]:
            if prev_was_term and token not in [")"]:
                new_tokens.append("OR")
            prev_was_term = token not in ["("]
        else:
            prev_was_term = False
        new_tokens.append(token)
    return new_tokens


# Parsing the query into a structured format (AST)
class QueryParser:
    def __init__(self, query):
        self.raw_tokens = re.findall(r"\"[^\"]*\"|\w+|AND|OR|NOT|\(|\)", query)
        self.raw_tokens = insert_default_operators(self.raw_tokens)
        self.tokens = []
        self.pos = 0

    def parse_ast(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while (
            self.pos < len(self.raw_tokens)
            and self.raw_tokens[self.pos].upper() == "OR"
        ):
            self.pos += 1
            right = self.parse_and()
            left = ("OR", left, right)
        return left

    def parse_and(self):
        left = self.parse_term()
        while (
            self.pos < len(self.raw_tokens)
            and self.raw_tokens[self.pos].upper() == "AND"
        ):
            self.pos += 1
            right = self.parse_term()
            left = ("AND", left, right)
        return left

    def parse_term(self):
        if self.raw_tokens[self.pos].upper() == "NOT":
            self.pos += 1
            term = self.parse_term()
            return ("NOT", term)
        elif self.raw_tokens[self.pos] == "(":
            self.pos += 1
            expr = self.parse_or()
            self.pos += 1  # Skip ')'
            return expr
        else:
            term = self.raw_tokens[self.pos]
            self.pos += 1
            self.tokens.append(term)
            return term.strip('"')


# Indexer
def setup_db():
    con = sqlite3.connect("shakespeares.db", check_same_thread=False)
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute(
        """CREATE TABLE token_pos(
            id TEXT PRIMARY KEY, 
            scene_id TEXT NOT NULL,
            token TEXT NOT NULL,
            value INTEGER,
            play_id TEXT, 
            act_id TEXT,
            scene_num TEXT
        );"""
    )
    cur.execute(
        """
        CREATE INDEX scene_token_idx on token_pos(scene_id, token);
    """
    )
    con.commit()
    return con


def connect_db():
    con = sqlite3.connect("shakespeares.db", check_same_thread=False)
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    print("Database connected")
    return con


def select_query(con, columns, conditions=None, condition_values=None):
    cur = con.cursor()
    query = f"SELECT {', '.join(columns)} FROM token_pos"
    if conditions:
        query += f" WHERE {' AND '.join(conditions)}"
    res = cur.execute(query, condition_values or [])
    return res.fetchall()


def count_query(con, columns, conditions=None, condition_values=None):
    cur = con.cursor()
    query = f"SELECT COUNT({', '.join(columns)}) FROM token_pos"
    if conditions:
        query += f" WHERE {' AND '.join(conditions)}"
    res = cur.execute(query, condition_values or [])
    return res.fetchone()[0]


def insert_query(con, data):
    cur = con.cursor()
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?" for _ in range(len(data))])
    query = f"INSERT INTO token_pos ({columns}) VALUES ({placeholders})"

    cur.execute(query, tuple(data.values()))
    con.commit()
    return True


def exists(con, conditions, condition_values):
    cur = con.cursor()
    query = "SELECT COUNT(*) FROM token_pos"
    query += f" WHERE {' AND '.join(conditions)}"
    res = cur.execute(query, condition_values)
    count = res.fetchone()[0]
    return count > 0


class Indexer:
    def handle_data_one_line(
        self, con, tokenizer, data, scene_id, play_id, act_id, scene_num
    ):
        # Tokenize the text
        text = f'{data["speaker"]} {data["text_entry"]}'
        tokens = tokenizer.tokenize_paragraph(text)

        # Add entry to database
        for i, token in enumerate(tokens):
            insert_query(
                con,
                {
                    "id": uuid4().urn,
                    "scene_id": scene_id,
                    "value": i,
                    "token": token,
                    "play_id": play_id,
                    "act_id": act_id,
                    "scene_num": scene_num,
                },
            )

    def build_inverted_list(self):
        # Init tokenizer
        tokenizer = PorterStemmer()

        # Set up database
        con = setup_db()

        # Check for raw data
        if os.path.exists("shakespeare-data"):
            with open("shakespeare-data", "r") as f:
                act_id, scene_num = None, None
                queue = []
                # Process raw data
                for line in tqdm(f, total=get_num_lines("shakespeare-data")):
                    data = json.loads(line.strip())
                    if len(data["line_number"]) != 0:
                        play_id = data["play_name"]
                        act_id, scene_num, _ = data["line_number"].split(".")
                        scene_id = f"{play_id}:{act_id}:{scene_num}"
                    else:
                        queue.append(data)
                        continue

                    while len(queue) > 0:
                        queue_data = queue.pop(0)
                        self.handle_data_one_line(
                            con,
                            tokenizer,
                            queue_data,
                            scene_id,
                            play_id,
                            act_id,
                            scene_num,
                        )

                    self.handle_data_one_line(
                        con, tokenizer, data, scene_id, play_id, act_id, scene_num
                    )

        # Close database connection
        print("Database setup completed")
        con.close()

    def get_TF_scene(self, con, token, scene_id):
        count = count_query(
            con, ["*"], ["scene_id = ?", "token = ?"], [scene_id, token]
        )
        return count

    def get_scene_len(self, con, scene_id):
        count = count_query(con, ["*"], ["scene_id = ?"], [scene_id])
        return count

    def get_total_scenes(self, con):
        count = count_query(con, ["DISTINCT scene_id"])
        return count

    def get_avg_scene_len(self, con):
        count = count_query(con, ["*"])
        scene_count = count_query(con, ["DISTINCT scene_id"])
        return float(count / scene_count)

    def get_scene_contain_phrase(self, con, phrase):
        tokenizer = PorterStemmer()
        tokens = tokenizer.tokenize_paragraph(phrase)
        num_tokens = len(tokens)
        if num_tokens == 0:
            return []

        cur = con.cursor()
        query = "SELECT DISTINCT tp1.scene_id FROM token_pos tp1 "

        # Add joins for each subsequent token
        for i in range(1, num_tokens):
            query += f"JOIN token_pos tp{i + 1} ON tp{i}.scene_id = tp{i + 1}.scene_id AND tp{i + 1}.value = tp{i}.value + 1 "

        # Add the WHERE clause for each token
        query += "WHERE "
        for i in range(num_tokens):
            if i > 0:
                query += "AND "
            query += f"tp{i + 1}.token = ? "

        query += ";"
        res = cur.execute(query, tokens)
        res = res.fetchall()
        return [row[0] for row in res]

    def get_scene_not_contain_phrase(self, con, phrase):
        tokenizer = PorterStemmer()
        tokens = tokenizer.tokenize_paragraph(phrase)
        num_tokens = len(tokens)
        if num_tokens == 0:
            return []

        cur = con.cursor()
        subquery = "SELECT DISTINCT tp1.scene_id FROM token_pos tp1 "

        # Add joins for each subsequent token
        for i in range(1, num_tokens):
            subquery += f"JOIN token_pos tp{i + 1} ON tp{i}.scene_id = tp{i + 1}.scene_id AND tp{i + 1}.value = tp{i}.value + 1 "

        # Add the WHERE clause for each token
        subquery += "WHERE "
        for i in range(num_tokens):
            if i > 0:
                subquery += "AND "
            subquery += f"tp{i + 1}.token_id = ? "

        query = f"SELECT scene_id from token_pos WHERE scene_id NOT IN ({subquery});"
        res = cur.execute(query, tokens)
        res = res.fetchall()
        return [row[0] for row in res]


k1 = 1.8
k2 = 5
b = 0.75
mu = 300


def score_bm25(n, f, qf, r, R, N, dl, avdl):
    K = compute_k(dl, avdl)
    first = math.log(
        ((r + 0.5) / (R - r + 0.5)) / ((n - r + 0.5) / (N - n - R + r + 0.5))
    )
    second = ((k1 + 1) * f) / (K + f)
    third = ((k2 + 1) * qf) / (k2 + qf)
    return first * second * third


def compute_k(dl, avdl):
    return k1 * ((1 - b) + b * (float(dl) / float(avdl)))


def score_ql(fqD, D, fqC, C):
    first = float(fqD + mu * fqC / C)
    second = float(D + mu)
    return math.log(first / second)


# Ranking
class Query(object):
    def boolean_filter(self, con, idx, query_ast):
        if isinstance(query_ast, str):
            return idx.get_scene_contain_phrase(con, query_ast)
        elif isinstance(query_ast, tuple) and query_ast[0] == "NOT":
            return idx.get_scene_not_contain_phrase(con, query_ast[1])

        op, left, right = query_ast
        if op is None or left is None or right is None:
            return []
        if op == "AND":
            return list(
                set(self.boolean_filter(con, idx, left))
                & set(self.boolean_filter(con, idx, right))
            )
        else:
            return list(
                set(
                    self.boolean_filter(con, idx, left)
                    + self.boolean_filter(con, idx, right)
                )
            )

    def bm25(self, con, idx, query, filter_scenes=None):
        res = {}

        avg_scene_len = idx.get_avg_scene_len(con)
        total_scenes_num = idx.get_total_scenes(con)
        for term in set(query):
            if exists(con, ["token = ?"], [term]):
                if filter_scenes:
                    scenes = filter_scenes
                else:
                    scenes = select_query(
                        con, ["DISTINCT scene_id"], ["token = ?"], [term]
                    )
                for scene in scenes:
                    score = score_bm25(
                        n=len(scenes),
                        f=idx.get_TF_scene(con, term, scene),
                        qf=query.count(term),
                        r=0,
                        R=0.0,
                        N=total_scenes_num,
                        dl=idx.get_scene_len(con, scene),
                        avdl=avg_scene_len,
                    )

                    if scene in res:
                        res[scene] += score
                    else:
                        res[scene] = score
        return dict(sorted(res.items(), key=lambda x: (-x[1], x[0])))
