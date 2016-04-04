Insight Data Engineering - Coding Challenge
===========================================================

## Packages Used 

* iGraph -- For HashTag Graph.
* Pandas 
* Numpy

## Algorithm 

* First I extracted hashtags and created_at fields from each tweet. Also I ignored the rate limit messages
* For each tweet, I have created hashtag graph and written the average degree to the output file. It is implemented using 2 methods.In the first method
	1. For each tweet processed, I maintained two lists. t_stamps store the current timestamp. t_stamps_hashtags store the coresponding hashtags. This list is used to maintain all the timestamps corresponding to 60 second window of maximum timestamp tweet processed. I could have used dictionary in this step, but I need to maintain order of timestamp processed and need to sort them when a tweet with out of order in time arrives.
	2. Also I maintained another list to store  unique vertices and a dictionary for storing unique edges and their counts. This dictionary is helpful while evicting the out of window tweets. 
	3. While building the graph, I have maximum_timestamp_processed variable which is updated each time, if new tweet has higher timestamp than previous step. The following steps are taken while building the graph.
	- If the current tweet falls within the 60 second window of t_stamps list and if size of hashtags set is greater than or equal to 2, then new edges are created using add_edges() method and these new edges are added to the existing graph.
	- Else if the current_tweet doesn't fall in the 60 second window of t_stamps list, then a tweet is evicted from the list each time until current tweet falls within the 60 second window of t_stamps. 
	- Also, if the new tweet processed falls out of the window of maximum time stamp processed, then new graph is created and all other lists and dictionary are initialized. This is becauseI dont want to delete every edge and every element in the list.

* In the second method, I used Pandas Datafame to store "created_at" and "hashtags" fields. Then I used map function to process each tweet. The implementation part is same as descrived above. Also, the run time of first method is better than second method. It has taken roughly 7 seconds to process 10000 tweets via first method and 9 seconds via using Pandas dataframes. 
* The first method is stored in average_degree.py and second method is in average_degree_1.py
* My 60-second window is inclusive. 
