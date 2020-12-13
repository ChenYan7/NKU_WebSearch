# -*- coding: utf-8 -*-
# @时间：2020/12/8 22:05
# @作者：陈燕
# @项目名：hw5
# @文件名：vsm.py

from text_operation import Indexer
import sqlite3
from collections import defaultdict
import jieba
import math



class VSM_Searcher:
    def __init__(self,index):
        self.index = index

    def search(self,query):
        token_list = []
        query = query.split()
        for entry in query:
            token_list = list(jieba.cut_for_search(entry))
        #print(token_list)
        relevant_docIds = self.intersect([set(self.index.postings[term].keys()) for term in token_list])
        #print(relevant_docIds)
        if not relevant_docIds:
            return ' '
        else:
            scores = sorted([(id, self.similarity(id,token_list))
                             for id in relevant_docIds],
                            key=lambda x: x[1],
                            reverse=True)
        return  scores

    def intersect(self,sets):
        result = sets[0]
        for s in sets[1:]:
            result = result.intersection(s)
        return result

    # 求相似度
    def similarity(self,id,token_list):
        similarity = 0.0
        for term in token_list:
            if term in self.index.corups:
                similarity += self.index.inverse_page_frequencies(term)*self.index.term_importance(term,id)
        #print(self.index.length[id])
        similarity = similarity / self.index.length[id]
        return similarity



if __name__=='__main__':
    db_path = "searchengine.sqlite"
    index = Indexer(db_path)
    print("文本处理成功")
    searcher = VSM_Searcher(index)
    while True:
        query = input("请输入query：")
        id_score = searcher.search(query)
        print(id_score)