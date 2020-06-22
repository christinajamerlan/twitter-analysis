import networkx as nx

def check_import():
    print("Bigrams-graph process module loaded successfully.")
    return
    
def create_graph(entries, input_mode):
    # initialize list of graphs
    GRAPHS = []
    
    # align with type of input
    if input_mode == "twitter":
        import tweet_input as proj_input
    elif input_mode == "docu":
        import docu_input as proj_input
    else:
        print("Invalid input mode. Exiting...")
        exit()
    
    # connect all entries of the same graph
    # resolves sparsity of the graphs
    entries = proj_input.consolidate_entries(entries)
    # 1 entry = 1 graph
    
    G = None
    edge_id = 0
    # for each entries
    for data in entries:
        # add nodes
        G_prev, G, nodes = proj_input.add_nodes(data, G)
        
        # if it is a new graph, append the previous graph to the graphs list
        if G_prev is not None:
            print("\"" + G_prev.graph['name'] + "\" graph created.")
            print("Number of nodes: " + str(G_prev.number_of_nodes()))
            print("Number of edges: " + str(G_prev.number_of_edges()))
            GRAPHS.append(G_prev)
            
        nodes_length = len(nodes)
        # for each nodes in temp graph, create an edge per pair of consecutive nodes and add to main graph
        for i in range(nodes_length - 1):
        
            # if edge already exists, then increase weight
            if G.has_edge(nodes[i], nodes[i+1]):
                weight = G[nodes[i]][nodes[i+1]]['weight']
                G[nodes[i]][nodes[i+1]]['weight'] = weight + 1
                
            elif G.has_edge(nodes[i+1], nodes[i]): # reverse
                weight = G[nodes[i+1]][nodes[i]]['weight']
                G[nodes[i+1]][nodes[i]]['weight'] = weight + 1
                
            else: # new edge
                # edges should contain (ID, Source, Target, Type, Label, Weight)
                G.add_edge(nodes[i], nodes[i+1], id=edge_id, type="Undirected", label="", weight=1)
                edge_id += 1
                
    # add the last graph created to the graphs list
    print("\"" + G.graph['name'] + "\" graph created.")
    print("Number of nodes: " + str(G.number_of_nodes()))
    print("Number of edges: " + str(G.number_of_edges()))
    GRAPHS.append(G)
    
    return GRAPHS
    
