import json
import gzip
import math
import time
import numpy as np
#import tkinter as tk
from tkinter import ttk as tk
from tkinter import *
from tkinter.messagebox import askyesno 
from numpy.linalg import norm
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

class RetreivalAugmentation:
    def __init__(self, threshold):
        self.ps = PorterStemmer()
        self.inverted_index = {}
        self.pagerank = {}
        self.query = ''
        self.tfidf_table  = {}
        self.query_token_docs = set()
        self.inverted_index_dict= {}
        self.pagerank_scores = {}
        self.results = []
        


    def tokenize(self, text, corpus_tokens):
        token_to_count = defaultdict(int)
        tokens = word_tokenize(text)
        for t in tokens:
            stem_token = self.ps.stem(t.lower())
            if stem_token in corpus_tokens:
                token_to_count[stem_token] += 1
        return token_to_count
        
    def start(self):
        """
        Called on Each query
        """
        currTime = time.perf_counter()
        query_token_count =  self.tokenize(self.query, self.tokens)
        query_idf_weights = {term: 1+ math.log10(query_token_count[term])
                             for term in query_token_count.keys()}
        
        query_tfidf_relevance_score = defaultdict(float)




        #Cosine similarity calculations
        for term in query_token_count:
            for url in self.inverted_index[term]:
                tfidf = self.tfidf_table[term][url]  
                tfidf_score = query_idf_weights[term] * tfidf   
                query_tfidf_relevance_score[url] += tfidf_score
        
        # Calculate relevance score based on cosine similarity and pagerank
        for url, score in query_tfidf_relevance_score.items():
            query_tfidf_relevance_score[url] = 0.8*score + 0.2*self.pagerank[url] 

        sorted_query_tfidf_relevance_score = dict(sorted(query_tfidf_relevance_score.items(), key=lambda item: item[1]))
        top_results = list(sorted_query_tfidf_relevance_score.keys())[-5:]
        
        for result in reversed(top_results):
            print(f"- {result, sorted_query_tfidf_relevance_score[result]} \n")

        endTime = time.perf_counter()
        print('Time taken to run this query - ', endTime-currTime)
        print('-'*100)
        return top_results

    def query_call(self, inp): 
        self.query = inp
        self.results = self.start()
        # while True:
        #   permission = input("Do you want to run another query: (y/n) ")
        #   if permission == "y":
        #     query = input("Enter your new Query: ")
        #     print("--- Processing this query ---")
        #     self.query = query
        #     self.results = self.start()
        #   else:
        #     break
          
    def calculate_page_rank(self):
        url_graph = nx.DiGraph()
        for token , url_dict in self.inverted_index.items():     
            for url, count in url_dict.items():
                url_graph.add_node(url)
            url_graph.add_edges_from([(url, terms[0]) for terms in url_dict])

        self.pageScores = nx.pagerank(url_graph)
        return 
    
    def show_results(self):
        root1 = Tk()
        root1.geometry('500x700') 
        frm = tk.Frame(root1, padding=10)
        frm.grid()
        tk.Label(frm, text=self.results[0], justify = CENTER).grid(column=0, row=0)
        tk.Label(frm, text=self.results[1]).grid(column=0, row=1)
        tk.Label(frm, text=self.results[2]).grid(column=0, row=2)
        tk.Label(frm, text=self.results[3]).grid(column=0, row=3)
        tk.Label(frm, text=self.results[4]).grid(column=0, row=4)
        tk.Button(frm, text="Quit", command=root1.destroy).grid(column=0, row=7)
        root1.mainloop()
        
        
    def initate_call(self):
        print('--- Reading PageRank, Inverted Index and TfIdf Json ---- ')
               
        with gzip.open('compressed_pagerank.json.gz', 'rb') as pagerank_file:
            compressed_pagerank_file = pagerank_file.read()
            decompressed_pagerank_file = gzip.decompress(compressed_pagerank_file)
            self.pagerank = json.loads(decompressed_pagerank_file.decode('utf-8'))
        
        with gzip.open('compressed_inverted_index.json.gz', 'rb') as inverted_index_file:
            compressed_inverted_index_file = inverted_index_file.read()
            decompressed_inverted_index_file = gzip.decompress(compressed_inverted_index_file)
            self.inverted_index = json.loads(decompressed_inverted_index_file.decode('utf-8'))
            self.inverted_index_dict = {key: index for index, key in enumerate(self.inverted_index.keys())}
            self.tokens = self.inverted_index_dict.keys()

        with gzip.open('compressed_tfidf.json.gz', 'rb') as tfidf_file:
            compressed_tfidf_file = tfidf_file.read()
            decompressed_tfidf_file = gzip.decompress(compressed_tfidf_file) 
            self.tfidf_table = json.loads(decompressed_tfidf_file.decode('utf-8'))

        def search_query():
            inp = entry.get()  # Get the search query from the entry widget
            # Perform the search (replace this with your actual search function)
            self.query_call(inp)
            self.show_results()

        root = Tk()
        root.geometry('500x700') 
        entry = tk.Entry(root, textvariable = 'Search Engine', justify = CENTER) 
  
        # focus_force is used to take focus 
        # as soon as application starts 
        entry.focus_force() 
        entry.pack(side = TOP, ipadx = 30, ipady = 6) 
        
        search = tk.Button(root, text = 'Search', command = lambda : search_query()) 
        search.pack(side = TOP, pady = 10) 
        
        root.mainloop()
                              
        #GUI partially taken from https://www.geeksforgeeks.org/how-to-get-the-input-from-tkinter-text-box/
        
        
if __name__ == "__main__":
    rag = RetreivalAugmentation(200)
    rag.initate_call()











