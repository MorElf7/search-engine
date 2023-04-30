import sys, time, os
import math, utils

k1 = 1.8
k2 = 5
b = 0.75
mu = 300

def score_bm25(n, f, qf, r, R, N, dl, avdl):
    K = compute_k(dl, avdl)
    first = math.log(((r + 0.5) / (R - r + 0.5)) / ((n - r + 0.5) / (N - n - R + r + 0.5)))
    second = ((k1 + 1) * f) / (K + f)
    third = ((k2 + 1) * qf) / (k2 + qf)
    return first * second * third

def compute_k(dl, avdl):
    return k1 * ((1 - b) + b * (float(dl) / float(avdl)))


def score_ql(fqD, D, fqC, C):
    first = float(fqD + mu * fqC / C)
    second = float(D + mu)
    return math.log(first / second)
        
class Query(object):
    
    def boolean_query(self, idx, mode, phrases, is_scene):
        if is_scene:
            res = set(idx.get_scene_contain_phrase(phrases[0].strip()))
            for i in range(1, len(phrases)):
                if len(res) == 0:
                    return res
                temp = idx.get_scene_contain_phrase(phrases[i].strip())
                # Get intersection of 2 list
                if mode == "or":
                    res = set(list(res) + list(temp)) 
                elif mode == "and":
                    res = list(set(res) & set(temp)) 

            return set(res)
        else:
            res = set(utils.extract_play_list_from_scene_list(idx.get_scene_contain_phrase(phrases[0].strip())))

            for i in range(1, len(phrases)):
                if len(res) == 0:
                    return res

                temp = utils.extract_play_list_from_scene_list(idx.get_scene_contain_phrase(phrases[i].strip()))
                if mode == "or":
                    res = set(list(res) + list(temp)) 
                elif mode == "and":
                    res = list(set(res) & set(temp)) 

            return set(res)

    def bm25(self, idx, query, is_scene):
        res = {}
        
        if is_scene:
            avg_scene_len = idx.get_avg_scene_len()
            for term in set(query):
                if term in idx.inverted_list: 
                    posting_list = idx.inverted_list[term]
                    for scene in posting_list.keys():
                        score = score_bm25(n = len(posting_list.keys()), f=idx.get_TF_scene(term, scene), qf=query.count(term), r=0, R=0.0,
                                                    N=len(idx.scene_list), dl=idx.get_scene_len(scene), avdl=avg_scene_len)
                        
                        if scene in res:
                            res[scene] += score
                        else:
                            res[scene] = score
        else:
            avg_play_len = idx.get_avg_play_len()
            for term in set(query):
                if term in idx.inverted_list: 
                    posting_list = idx.inverted_list[term]
                    play_list = utils.extract_play_list_from_scene_list(posting_list.keys())

                    for play in play_list:
                        score = score_bm25(n = len(play_list), f=idx.get_TF_play(term, play), qf=query.count(term), r=0.0, R=0.0,
                                                    N=len(idx.play_list), dl=idx.get_play_len(play), avdl=avg_play_len)
                        
                        if play in res:
                            res[play] += score
                        else:
                            res[play] = score

        return dict(sorted(res.items(), key=lambda x : (-x[1], x[0])))

    def ql(self, idx, query, is_scene):
        res = {}
        scene_list = set()
        for term in query:
            if term in idx.inverted_list: 
                posting_list = idx.inverted_list[term]
                for scene in posting_list.keys():
                    scene_list.add(scene)

        if is_scene:
            doc_list = scene_list
            for term in query:
                if term in idx.inverted_list: 
                    for doc in doc_list:
                        score = score_ql(fqD=idx.get_TF_scene(term, doc), D=idx.get_scene_len(doc), fqC=idx.get_TF_collection(term), C=idx.collection_len)

                        if doc in res:
                            res[doc] += score
                        else:
                            res[doc] = score
        else: 
            doc_list = utils.extract_play_list_from_scene_list(scene_list)
            for term in query:
                if term in idx.inverted_list: 
                    for doc in doc_list:
                        score = score_ql(fqD=idx.get_TF_play(term, doc), D=idx.get_play_len(doc), fqC=idx.get_TF_collection(term), C=idx.collection_len)

                        if doc in res:
                            res[doc] += score
                        else:
                            res[doc] = score

        return dict(sorted(res.items(), key=lambda x : (-x[1], x[0])))
