import csv
import re
import networkx as nx # pip install networkx

stopwords_filename = "./config/tweet_stopwords.txt"
color_list_filename = "./config/tweet_colors.csv"

def check_import():
    print("Tweet input module loaded successfully.")
    return
    
def load_file(filename, graph_name):
    input_entries = []
   
    for name in filename:
        # open each file
        input_file = open(name, encoding='utf-8')
        input_reader = csv.reader(input_file, delimiter=',')
       
        # for each tweet record
        for tweet in input_reader:
            tweet_dim = len(tweet) # check how many dimensions are there
            if tweet_dim == 4: # if correct dimensions, save as is
                if tweet[2] in graph_name:
                    input_entries.append(tweet)
            elif tweet_dim > 4: # if incorrect dimensions, adjust data
                temp = [w for w in tweet if w != ""] # get all elements that is not blank
                temp_dim = len(temp)
                if temp[temp_dim - 2] in graph_name:
                    tweet_text = " ".join([temp[i] for i in range(1,temp_dim - 2)]) # join all elements that are part of text
                    input_entries.append([temp[0], tweet_text, temp[temp_dim - 2], temp[temp_dim - 1]])
                   
        input_file.close()
    
    input_entries.sort(key = lambda x: x[2])
   
    return input_entries
    
def clean_data(input_entries):
    cleaned_entries = []
    
    # open stopwords file
    stopwords_file = open(stopwords_filename, encoding='utf-8')
    stopwords_reader = set(stopwords_file.readlines())
    stopwords_list = [x.strip() for x in stopwords_reader]
    
    # remove special characters and stopwords
    # for each tweet
    for tweet in input_entries:
        # remove special characters
        temp = re.sub(r"[^a-zñ0-9#@ ]+", "", tweet[1].lower())
        
        # TODO: CREATE A REGEX LOOKUP FILE
        #temp = re.sub(r"@[a-zñ0-9]+", "<user_tag>", temp) # substitute user tag as <user_tag>
        temp = re.sub(r"http[a-zñ0-9]+", " ", temp) # substitute http as <url>
        temp = re.sub(r"pictwitter[a-zñ0-9]+", " ", temp) # substitute pictwitter as <twitter_pic>
        #temp = re.sub(r"\b(?:a*(?:ha)+h?|h*ha+h[ha]*|(?:l+o+)+l+|o?l+o+l+[ol]*)\b", "<laugh_text>", temp) # substitute haha and lol as <laugh_text>
        
        # if non-empty result
        if temp != "":
            # tokenize
            words = temp.split()
            # select words that are not in the stopwords list
            temp2 = [w for w in words if not w in stopwords_list]
            # save if not empty
            if temp2 != []:
                cleaned_entries.append([tweet[0], " ".join(temp2), tweet[2], tweet[3]]) # id, text, city, province
                
    return cleaned_entries

def consolidate_entries(entries):
    #new_entries = []
   
    #graph_name = entries[0][2]
    #text_entry = []
   
    # for each entries
    #for tweet in entries:
        #if graph_name == tweet[2]: # if same graph, append text
            #text_entry.append(tweet[1])
        #else: # if different graph
            # create new entry for the current graph
            #new_entries.append([" ".join(text_entry), graph_name])
           
            # initialize next graph
            #graph_name = tweet[2]
            #text_entry = [tweet[1]]
           
    # create entry for the last graph
    #new_entries.append([" ".join(text_entry), graph_name])
   
    #return new_entries
    return entries
    
def add_nodes(data, G):
    # initialize graphs
    H = []
    G_prev = None
    
    # tokenize
    words = data[1].split()
    
    # count the number of words for each entry
    num_words = len(words)
    
    # add city as prefix of ID
    prefix = re.sub(r" ", "_", data[2].lower())
    
    # if new graph
    if G is None:
        # create a graph with the city name as an attribute
        G = nx.Graph(name=data[2])
        
    # if the current data is for new graph
    if data[2] != G.graph['name']:
        G_prev = G
        G = nx.Graph(name=data[2])
        
    # for each word
    for i in range(num_words):
        # add node to main graph
        G.add_node(prefix+"_"+words[i], label=words[i], graph_name=data[2])
        
        # add node to temp graph
        H.append(prefix+"_"+words[i])
        
    return G_prev, G, H
    
def get_nodes_header(graph_header):
    return ["ID", "Label", "Degree", "modularity_class", "Community Name", "Colrname", "Color", graph_header]
    
def get_edges_header():
    return ["ID", "Source", "Target", "Type", "Label", "Weight"]
    
def get_node_save_data(G, node):
    return [
        node, G.node[node]['label'], # ID, Label
        G.degree(node), # Degree
        G.node[node]['modularity_class'], # modularity_class
        G.node[node]['community_name'], # Community Name
        G.node[node]['color_name'], # Color Name
        G.node[node]['color_value'], # Color Value
        G.node[node]['graph_name'] # graph_header = City
    ]
    
def get_edge_save_data(G, edge):
    return [
        G[edge[0]][edge[1]]['id'], # ID
        edge[0], edge[1], # Source, Target
        G[edge[0]][edge[1]]['type'], # Type
        G[edge[0]][edge[1]]['label'], # Label
        G[edge[0]][edge[1]]['weight'] # Weight
    ]
    
def load_color_list():
    color_list_file = open(color_list_filename, encoding='utf-8')
    color_list_reader = csv.reader(color_list_file, delimiter=',')
    next(color_list_reader)
    
    return list(color_list_reader)
    
def color_map(graph_name, community_map, color_list):
    color_name = "Black"
    color_value = "#333333"
    new_map = []

    # check if graph name is in the color list
    for color_entry in color_list:
        # if yes, then assign color name and value for each entry in the community map
        if color_entry[2] == graph_name:
            color_name = color_entry[0]
            color_value = color_entry[1]
            for community_entry in community_map:
                new_map.append([community_entry[0], community_entry[1], community_entry[2], color_name, color_value])
            return new_map
            
    # if not in color list, use default colors
    for community_entry in community_map:
        new_map.append([community_entry[0], community_entry[1], community_entry[2], color_name, color_value])
    return new_map
    
