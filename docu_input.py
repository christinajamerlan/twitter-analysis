import docx
import csv
import re
import networkx as nx # pip install networkx

stopwords_filename = "./config/docu_stopwords.txt"
color_list_filename = "./config/docu_colors.csv"

def check_import():
    print("Document input module loaded successfully.")
    return
    
def load_file(filename, graph_name):
    input_entries = []
    
    num_graph = len(filename) # count number of files (1 file = 1 graph)
    for i in range(num_graph): # for each file
        doc = docx.Document(filename[i]) # open document
        for para in doc.paragraphs: # for each paragraph
            input_entries.append([para.text, graph_name[i]]) # add text and corresponding file source
            
    return input_entries
    
def clean_data(input_entries):
    cleaned_entries = []
    
    # open stopwords file
    stopwords_file = open(stopwords_filename, encoding='utf-8')
    stopwords_reader = set(stopwords_file.readlines())
    stopwords_list = [x.strip() for x in stopwords_reader]
    
    # remove special characters and stopwords
    # for each paragraph
    for para in input_entries:
        # remove special characters
        temp = re.sub(r"[^a-zñ0-9 ]+", "", para[0].lower())
        
        # if non-empty result
        if temp != "":
            # tokenize
            words = temp.split()
            # select words that are not in the stopwords list
            temp2 = [w for w in words if not w in stopwords_list]
            # save if not empty
            if temp2 != []:
                cleaned_entries.append([" ".join(temp2), para[1]]) # text, show
                
    return cleaned_entries
    
def consolidate_entries(entries):
    new_entries = []
    
    graph_name = entries[0][1]
    text_entry = []
    
    # for each entries
    for para in entries:
        if graph_name == para[1]: # if same graph, append text
            text_entry.append(para[0])
        else: # if different graph
            # create new entry for the current graph
            new_entries.append([" ".join(text_entry), graph_name])
            
            # initialize next graph
            graph_name = para[1]
            text_entry = [para[0]]
            
    # create entry for the last graph
    new_entries.append([" ".join(text_entry), graph_name])
    
    return new_entries
    
def add_nodes(data, G):
    # initialize graphs
    H = []
    G_prev = None
    
    # tokenize
    words = data[0].split()
    
    # count the number of words for each entry
    num_words = len(words)
    
    # add show as prefix of ID
    prefix = re.sub(r" ", "_", data[1].lower())
    
    # if new graph
    if G is None:
        # create a graph with the show name as an attribute
        G = nx.Graph(name=data[1])
        
    # if the current data is for new graph
    if data[1] != G.graph['name']:
        G_prev = G
        G = nx.Graph(name=data[1])
        
    # for each word
    for i in range(num_words):
        # add node to main graph
        G.add_node(prefix+"_"+words[i], label=words[i], graph_name=data[1])
        
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
        G.node[node]['graph_name'] # graph_header = Show
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
    
    # for each entry in community map
    for community_entry in community_map:
        # check for each entry in the color list
        in_list = False
        for color_entry in color_list:
            # if same community name and matching word
            if community_entry[0] == color_entry[2]:
                new_map.append([community_entry[0], community_entry[1], community_entry[2], color_entry[0], color_entry[1]])
                in_list = True
                break
                
        # if not in list, use default value
        if not in_list:
            new_map.append([community_entry[0], community_entry[1], community_entry[2], color_name, color_value])
            
    return new_map
    