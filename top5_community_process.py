import networkx as nx # pip install networkx
import community # pip install python-louvain
import csv

proposal_filename = "./config/top5_proposal.csv"

def check_import():
    print("Top5 community process module loaded successfully.")
    return
    
def get_community_name(nodes_list, proposal_list):
    # for each proposal in proposal_list
    for proposal_entry in proposal_list:
        # for each node in the nodes_list
        for node_entry in nodes_list:
            # get list of matching keywords
            key_list = proposal_entry[1].strip('][').split(',')
            # if there is at least one common
            if node_entry in key_list:
                # return proposed name
                return proposal_entry[0]
            
    # if no match found (new topic), return the node label with the highest degree
    return nodes_list[0]
    
def name_communities(community_info, proposal_list):
    community_map = []
    
    # sort community_info according to community number (ascending) and degree (descending)
    # community_info contains [0]community number, [1]node label, and [2]degree
    community_info.sort(key = lambda x: int(x[2]), reverse = True) # degree first
    community_info.sort(key = lambda x: int(x[0]))
    
    current_number = 0
    nodes_list = []
    # for each node in community_info
    for node in community_info:
    
        # if still in the same community number
        if current_number == node[0]:
            # store node label on the list
            nodes_list.append(node[1])
            
        else: # different community number
            # determine community name
            community_name = get_community_name(nodes_list, proposal_list)
            # count number of nodes in the community
            distinct_words = len(nodes_list)
            # store community name, possible community names, and number of distinct words to community_map
            max_iter = 5
            if distinct_words < 5: # if there are less than five nodes, adjust top nodes
                max_iter = distinct_words
            community_map.append([community_name,[nodes_list[i] for i in range(max_iter)],distinct_words])
            
            # move to next community
            current_number += 1
            nodes_list = []
            nodes_list.append(node[1])
            
            
    # settle last community
    # determine community name
    community_name = get_community_name(nodes_list, proposal_list)
    # count number of nodes in the community
    distinct_words = len(nodes_list)
    # store community name, possible community names, and number of distinct words to community_map
    max_iter = 5
    if distinct_words < 5: # if there are less than five nodes, adjust top nodes
        max_iter = distinct_words
    community_map.append([community_name, [nodes_list[i] for i in range(max_iter)], distinct_words])
    
    return community_map
    
def create_communities(GRAPHS, num_graphs, graph_header, input_mode, output_filename_prefix):
    # open community name proposal file
    proposal_file = open(proposal_filename, encoding='utf-8')
    proposal_reader = csv.reader(proposal_file, delimiter=',')
    next(proposal_reader)
    proposal_list = list(proposal_reader)
    
    # create community map output file
    map_filename = "./output/" + output_filename_prefix + "_community_map.csv"
    map_file = open(map_filename, mode='w', newline='\n', encoding='utf-8')
    map_writer = csv.writer(map_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    map_writer.writerow(["Modularity Class", graph_header, "Color Name", "Color Value", "Community Name", "Possible Community Names", "Distinct Words"])
    
    if input_mode == "twitter":
        import tweet_input as proj_input
    elif input_mode == "docu":
        import docu_input as proj_input
    else:
        print("Invalid input mode. Exiting...")
        exit()
        
    color_list = proj_input.load_color_list()
    
    cur_highest = -1 # first offset should be zero
    # for each graph
    for i in range(num_graphs):
        G = GRAPHS[i]
        community_info = []
        
        
        # compute for the communities
        community_dictionary = community.best_partition(G, partition=None, weight='weight', resolution=1.0, randomize=True, random_state=None)
        print("Done with best partition algorithm in graph \"" + G.graph['name'] + "\".")
        
        
        # get community information from the dictionary returned by community.best_partition()
        num_communities = 0
        # get the community number and degree for each node
        for node in G.nodes():
            # community number, node label, and degree (for top 5)
            community_info.append([community_dictionary[node], G.node[node]['label'], G.degree(node)])
            
            # take note of the last community number
            if community_dictionary[node] > num_communities:
                num_communities = community_dictionary[node]
                
        num_communities += 1 # total number of communities
        print("There are " + str(num_communities) + " communities in graph \"" + G.graph['name'] + "\".")
        
        
        # determine the community name (either by proposal or top 5)
        # community_map should contain [0]community name, [1]possible community names (top 5), [2]number of distinct words
        community_map = name_communities(community_info, proposal_list)
        community_map = proj_input.color_map(G.graph['name'], community_map, color_list)
        
        
        # store community number, community name, and color to the graph
        # adjust community number based on previous graph
        class_offset = cur_highest + 1
        
        # for each node in the graph
        for node in G.nodes():
            # adjust and add community number to the node as an attribute
            temp = community_dictionary[node] + class_offset
            G.node[node]['modularity_class'] = temp
            
            # add community name
            G.node[node]['community_name'] = community_map[community_dictionary[node]][0]
            
            # color the node
            G.node[node]['color_name'] = community_map[community_dictionary[node]][3]
            G.node[node]['color_value'] = community_map[community_dictionary[node]][4]
            
            # if it is the highest community number, take note (to be used on the next graph)
            if temp > cur_highest:
                cur_highest = temp
                
        # save community map
        map_size = len(community_map)
        for j in range(map_size):
            # Modularity Class, Graph Name, Color Name, Color Value, Community Name, Possible Community Names, Distinct Words
            map_writer.writerow([class_offset + j, G.graph['name'], community_map[j][3], community_map[j][4], community_map[j][0], community_map[j][1], community_map[j][2]])
            
        # store the graph back to the list
        GRAPHS[i] = G
        
    return GRAPHS
    