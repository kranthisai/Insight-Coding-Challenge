'''
Created on Mar 29, 2016

@author: system
'''
import sys
import os
import json
import time
import igraph
from igraph import *
from datetime import datetime
import pandas as pd
import numpy as np
start_time=time.time()
class average_deg:
    def __init__(self):
        self.args=sys.argv
        if(len(self.args)!=3):
            print("Incorrect number of argument")
            sys.exit(1)
        inputpath=self.args[1]
        #preprocessing tweets 
        self.max_timestamp_processed=0 
        ### Maintaining count of edges and unique vertices
        self.unique_hashtags=set()  # Unique set of vertices/nodes      
        self.unique_edges={} # Useful while deleting edges.
        ### For maintaining 60 second window
        self.t_stamps=[]
        self.t_stamp_hashtags=[]
        self.g=Graph() # Hashtag graph
        self.preprocess(inputpath)
        print("---Final time %.2f seconds----"%(time.time()-start_time))
        pass
  
    def hashtag_graph(self,current_timestamp,hashtag):
        '''
           This function build the Hashtag Graph. It appends the edges to the graphs each time
           a processing tweet falls within the 60 second window of maximum timestamp processed
           tweet. It also ignores the tweet that is not ordered in time and is 60 second older
           than maximum timestamp tweet processed. This function also removes the edges when
           the tweet should be evicted. Finally it returns the average degree of the graph for
           each tweet. 
        
        '''
        # Difference between current tweet and max_timestamp_processed_tweet    
        current_diff=round(time.mktime(current_timestamp)-time.mktime(self.max_timestamp_processed),2)
        #Maintaining Data within the 60 second window
        if(current_diff>=-60 and current_diff<=60 ):
            if(current_diff>=0):    # Update max_timestamp_processed 
                self.max_timestamp_processed=current_timestamp 
                self.t_stamps.append(current_timestamp)
                self.t_stamp_hashtags.append(hashtag)
            
            # Finding if tweet should be evicted or not.
            current_window=round(time.mktime(current_timestamp)-time.mktime(self.t_stamps[0]),2) 
            #current_window=round((current_timestamp-self.t_stamps[0]).total_seconds(),2)
            if(current_window<=60 and len(hashtag)>1):
                    self.add_edges(hashtag)
            # Evict all tweets that fall outside the window of current tweet                
            elif(current_window>60):
                while(current_window>60):
                    out_of_window_hashtags=self.t_stamp_hashtags[0]
                    if(len(out_of_window_hashtags)>1):
                        self.remove_edges(out_of_window_hashtags)
                    self.t_stamps.pop(0)
                    self.t_stamp_hashtags.pop(0)
                    current_window=round(time.mktime(current_timestamp)-time.mktime(self.t_stamps[0]),2)
                if(len(hashtag)>1):
                    self.add_edges(hashtag)                 
            #Dealing with tweets which arrive out of order in time 
            if(current_diff<0):
                self.t_stamps.append(current_timestamp)
                self.t_stamp_hashtags.append(hashtag)
                self.t_stamp_hashtags=[x for (y,x) in sorted(zip(self.t_stamps,self.t_stamp_hashtags))]
                self.t_stamps=[y for (y,x) in sorted(zip(self.t_stamps,self.t_stamp_hashtags))]
        
        ## Creating new window if the tweet falls outside 60 second window of maximum timestamp processed
        elif(current_diff>60): 
            self.max_timestamp_processed=current_timestamp
            self.g=Graph()
            self.t_stamp_hashtags=[]
            self.t_stamps=[]
            self.t_stamps.append(current_timestamp)
            self.t_stamp_hashtags.append(hashtag)
            self.unique_edges={}
            self.unique_hashtags=set()
            self.add_edges(hashtag)
        
        try:
            number_of_vertices=len([vertex for vertex in self.g.degree() if vertex!=0])
            res='%.2f' %round(float(sum(self.g.degree()))/number_of_vertices,2)
            return res
        except:
            return '%.2f' %0.00
        pass      
        
    def add_edges(self,hashtag):
        ''' This function add edges to the graph '''
        for tag in hashtag:
            if tag not in self.unique_hashtags:
                self.unique_hashtags.add(tag)
                self.g.add_vertex(tag)

        for i in range(0,len(hashtag)-1):
            for j in range(i+1,len(hashtag)):
                if ((hashtag[i],hashtag[j]) and (hashtag[j],hashtag[i])) not in self.unique_edges:
                    self.unique_edges[(hashtag[i],hashtag[j])]=1
                    self.unique_edges[(hashtag[j],hashtag[i])]=1
                    self.g.add_edge(hashtag[i],hashtag[j]) 
                else: 
                    self.unique_edges[(hashtag[i],hashtag[j])]+=1
                    self.unique_edges[(hashtag[j],hashtag[i])]+=1
        
        pass
    
    def remove_edges(self,out_of_window_hashtags):
        ''' This function remove edges from the graph '''
        for i in range(0,len(out_of_window_hashtags)-1):
            for j in range(i+1,len(out_of_window_hashtags)):
                self.unique_edges[(out_of_window_hashtags[i],out_of_window_hashtags[j])]-=1
                self.unique_edges[(out_of_window_hashtags[j],out_of_window_hashtags[i])]-=1
                if self.unique_edges[(out_of_window_hashtags[j],out_of_window_hashtags[i])]==0:
                    del self.unique_edges[(out_of_window_hashtags[j],out_of_window_hashtags[i])]
                    del self.unique_edges[(out_of_window_hashtags[i],out_of_window_hashtags[j])]
                    self.g.delete_edges([(out_of_window_hashtags[i],out_of_window_hashtags[j])])

        
        pass
    
    def preprocess(self,path):
        ''' In preproceesing step, I extracted unique_hashtags and Timestamp. 
            Also rate limiting messages are removed.
        '''
        tweet_file=''
        f=open(self.args[2],'w')
        try:
            tweet_file=open(path,"r")
        except: 
            print(" Could not open the file ")
            sys.exit(1) 
        for tweet in tweet_file:
            tweet=json.loads(tweet)
            if tweet.get('created_at') is not None:
                hashtags=set([item.get('text') for item in tweet.get('entities').get('hashtags')])
                current_timestamp=tweet.get('created_at')
                current_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(current_timestamp,'%a %b %d %H:%M:%S +0000 %Y'))
                current_timestamp=time.strptime(current_timestamp,"%Y-%m-%d %H:%M:%S")
                hashtags=[item for item in hashtags]
                if self.max_timestamp_processed==0:
                    self.max_timestamp_processed=current_timestamp
                res=self.hashtag_graph(current_timestamp, hashtags)
                f.write(res)
                f.write('\n')
        f.close()
        pass
avg=average_deg() 