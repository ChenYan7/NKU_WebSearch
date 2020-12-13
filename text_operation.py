# -*- coding: utf-8 -*-
# @时间：2020/12/9 16:32
# @作者：陈燕
# @项目名：hw5
# @文件名：text_operation.py

import jieba
import sqlite3
from collections import defaultdict
import math
import time

class Indexer:
    page_dict = {}
    page_cut = {}
    N = 0
    postings = defaultdict(dict)  # 单词出现在哪些文档中
    corups = set()  # 词袋，保存所有词
    page_frequency = defaultdict(int)
    length = defaultdict(float)  # 文章长

    def __init__(self,db_path):
        # self.page_dict = {}
        # self.page_cut = {}
        # self.N = 0 # 总page数


        self.page2dict(db_path)
        self.jieba_cut()
        self.terms_postings()
        self.page_frequencies()
        self.doc_lengths()

    def page2dict(self, db_path):
        db = sqlite3.connect(db_path)
        cursor = db.cursor()

        try:
            cursor.execute("select pageid,raw_html from page where is_text=1")
            result = cursor.fetchall()
            self.N = len(result)
            for re in result:
                id=re[0]
                page_text=re[1]
                self.page_dict[id] = page_text

        except Exception as e:
            print(e)
        finally:
            db.commit()
            db.close()


    def jieba_cut(self):
        with open('stoplist.txt', 'r', encoding='utf-8') as fp:
            stopwords = fp.readlines()
            stopwords = [stopword.replace('\n', '') for stopword in stopwords]

        term_list = []
        for id,text in self.page_dict.items():
            #print(id,text)
            seg_list = list(jieba.cut_for_search(text))
            for word in seg_list:
                if word not in stopwords:
                    term_list.append(word)
            self.page_cut[id] = term_list
            #self.page_cut[id] = seg_list
            #print(term_list)
        print("jiaba_cut finish")

    def terms_postings(self):
        #global corups, postings
        words = []
        for id,terms in self.page_cut.items():
            print(id)
            #unique_terms = set(terms)
            #print(unique_terms)
            #self.corups = self.corups.union(unique_terms)
            #beg2 = time.time()
            for term in terms:
                words.append(term)
                if term in self.postings:
                    if id not in self.postings[term]:
                        self.postings[term][id] = 1
                    else:
                        self.postings[term][id] += 1
                else:
                    self.postings[term] = {id:1}

                # if term not in self.postings.keys():
                #     self.postings[term][id] = 1
                # elif id
                # words.append(term)
                # self.postings[term][id] = terms.count(term) #每个词在文档中的词频
            # fin2 = time.time()
            # print("2:",fin2 - beg2)
        self.corups = set(words)
        #print(self.postings)
        print("terms_postings finish")

    # 每个词出现的文档数 df
    def page_frequencies(self):
        #global corups, page_frequency, postings
        for term in self.corups:
            self.page_frequency[term] = len(self.postings[term])
        print("page_frequencies finish")

    # 求 idf
    def inverse_page_frequencies(self, term):
        #global corups, page_frequency
        if term in self.corups:
            return math.log(self.N / self.page_frequency[term], 2)
        else:
            return 0.0

    # 求词在每个文档中的权重
    def term_importance(self,term,id):
        #global postings
        if id in self.postings[term]:
            return self.postings[term][id] * self.inverse_page_frequencies(term)
        else:
            return 0.0

    # 求文档向量
    def doc_lengths(self):
        #global length, corups
        for id in self.page_cut:
            l = 0
            for term in self.corups:
                l += self.term_importance(term, id) ** 2
            self.length[id] = math.sqrt(l)
        print("doc_lengths finish")

if __name__=='__main__':
    db_path = "searchengine.sqlite"
    index = Indexer(db_path)
    # index.page2dict(db_path)
    # jieba_cut()
    #
    # # 对文本进行处理，获取tf，idf
    # terms_postings()
    # page_frequencies()
    # doc_lengths()
    # print(corups)
    # print(postings)
    # print(page_frequency)

