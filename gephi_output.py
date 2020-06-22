import csv
import networkx as nx # pip install networkx

def check_import():
    print("Gephi output module loaded successfully.")
    return
    
def export_graph(GRAPHS, output_folder, output_filename_prefix, graph_header, input_mode):
    # change method of saving according to the input type
    if input_mode == "twitter":
        import tweet_input as proj_input
    elif input_mode == "docu":
        import docu_input as proj_input
    else:
        print("Invalid input mode. Exiting...")
        exit()
        
    nodes_filename = output_folder + output_filename_prefix + "_nodes.csv"
    edges_filename = output_folder + output_filename_prefix + "_edges.csv"
    
    nodes_file = open(nodes_filename, mode='w', newline='\n', encoding='utf-8')
    edges_file = open(edges_filename, mode='w', newline='\n', encoding='utf-8')
    
    # initialize nodes and edges file writer
    nodes_writer = csv.writer(nodes_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    edges_writer = csv.writer(edges_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
    # write nodes on nodes file
    print("Writing on " + nodes_filename + "...")
    nodes_writer.writerow(proj_input.get_nodes_header(graph_header))
    
    # for each graph
    for G in GRAPHS:
        # for each nodes
        for node in G.nodes():
            nodes_writer.writerow(proj_input.get_node_save_data(G, node))
            
    # write edges on edges file
    print("Writing on " + edges_filename + "...")
    edges_writer.writerow(proj_input.get_edges_header())
    
    # for each graph
    for G in GRAPHS:
        # for each edges
        for edge in G.edges():
            edges_writer.writerow(proj_input.get_edge_save_data(G, edge))
            
    # close files    
    nodes_file.close()
    edges_file.close()
    
    return