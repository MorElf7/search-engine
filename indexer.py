import json, gzip, datetime, os
from tokenization import Tokenizer
import utils

class Posting(object):
    def __init__(self, play_id, scene_id, word_pos = None):
        self.play_id = play_id
        self.scene_id = scene_id
        self.positions = list(word_pos)
        self.count = len(self.positions)

class PostingList(object):
    def __init__(self):
        self.postings = dict()

def insert_posting(posting_list, play_id, scene_id, word_pos):
    if scene_id not in posting_list:
        posting_list[scene_id] = Posting(play_id, scene_id, [word_pos])
    else:
        posting_list[scene_id]["positions"].append(word_pos)
        posting_list[scene_id]["count"] += 1

class Indexer(object):
    def __init__(self, raw_data_file=None, database=None):
        self.data = list()
        if raw_data_file is not None and os.path.exists(raw_data_file):
            with open(raw_data_file, 'r') as f:
                for l in f:
                    line = json.loads(l.strip())
                    self.data.append(line)
            
            self.inverted_list = dict()
            self.scene_list = dict()
            self.play_list = dict()
            self.collection_len = 0
            self.create_IL()
            
        elif database is not None and os.path.exists(database):
            with gzip.open(database, "r") as f:
                save_data = json.loads(f.read().decode('utf-8'))
                self.inverted_list = save_data["inverted_list"]
                self.scene_list = save_data["scene_list"]
                self.collection_len = save_data["collection_len"]
                self.play_list = save_data["play_list"]


    def create_IL(self, save=True):
        start_time = datetime.datetime.now()
        tokenizer = Tokenizer()
        prev_scene = ""
        print("Start constructing the inverted list")
        for line in self.data:
            tokens = tokenizer.tokenize(line["text_entry"]).split()
            self.collection_len += len(tokens)
            play_name = line["play_name"]
            if len(line["line_number"]) != 0:
                act_id, scene_num, line_number = line["line_number"].split(".")
                scene_id = play_name + ":" + act_id + "." + scene_num
                if scene_id != prev_scene:
                    prev_scene = scene_id
            else:
                scene_id = prev_scene
            
            if scene_id not in self.scene_list:
                self.scene_list[scene_id] = 0
            if play_name not in self.play_list:
                self.play_list[play_name] = 0
            
            self.scene_list[scene_id] += len(tokens)
            self.play_list[play_name] += len(tokens)

            for i, token in enumerate(tokens):
                if token not in self.inverted_list:
                    self.inverted_list[token] = dict()
                insert_posting(self.inverted_list[token], play_name, scene_id, i)
        
        if save:
            with gzip.open("database.json.gz", "wb") as f:
                save_data = dict()
                save_data["inverted_list"] = self.inverted_list
                save_data["scene_list"] = self.scene_list
                save_data["play_list"] = self.play_list
                save_data["collection_len"] = self.collection_len
                f.write(json.dumps(save_data, default=lambda x: x.__dict__).encode("utf-8"))

        print("Finish constructing the inverted list")
        print("Time elapsed: {}".format(utils.get_elapsed_time(start_time, datetime.datetime.now())))

    def get_TF_collection(self, term):
        posting_list = self.inverted_list[term]
        cnt = 0
        for scene, posting in posting_list.items():
            cnt += posting["count"]
        return cnt
    
    def get_TF_scene(self, term, scene):
        posting_list = self.inverted_list[term]
        return 0 if scene not in posting_list else posting_list[scene]["count"]

    def get_scene_len(self, scene):
        return self.scene_list[scene]

    def get_avg_scene_len(self):
        return float(self.collection_len / len(self.scene_list))

    def get_TF_play(self, term, play):
        posting_list = self.inverted_list[term]
        cnt = 0
        for scene, posting in posting_list.items():
            if play == posting.play_id:
                cnt += posting["count"]
        return cnt 

    def get_play_len(self, play):
        return self.play_list[play]

    def get_avg_play_len(self):
        return float(self.collection_len / len(self.play_list))           

    def get_scene_contain_phrase(self, phrase):
        words = phrase.split()        
        res = list(self.inverted_list[words[0]].keys())

        if len(res) == 0:
            return res

        for i in range(1, len(words), 1):
            cur_word = words[i]
            prev_word = words[i - 1]
            postings = self.inverted_list[cur_word]
            prev_word_postings = self.inverted_list[prev_word]
            temp = []
            for scene in res:
                if scene in postings:
                    check = 0
                    for prev in prev_word_postings[scene].positions:
                        if (prev + 1) in postings[scene].positions:
                            check += 1
                            break
                    
                    if check != 0:
                        temp.append(scene)
            
            res = temp
            
        return res

    
