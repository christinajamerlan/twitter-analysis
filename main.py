import networkx as nx # pip install networkx
import time


start_time = time.time() # take note of start time
#=============================================================================
# Set control variables
#=============================================================================
# single docu example
#input_filename = ["./input/24 Oras 05.04.2020.docx"]
#output_filename_prefix = "24O.05.04.2020" # common prefix of your output filename
#input_mode = "docu"
#graph_header = "Show" # custom cell header of output csv
#graph_name = ["24 Oras"] # custom cell value of output csv


# single docu example
#input_filename = ["./input/TV Patrol 05.04.2020.docx"]
#output_filename_prefix = "TV Patrol 05.04.2020" # common prefix of your output filename
#input_mode = "docu"
#graph_header = "Show" # custom cell header of output csv
#graph_name = ["TV Patrol"] # custom cell value of output csv


# multiple docu example (TVP vs 24Oras)
#input_filename = ["./input/24 Oras 06.01-05.2020.docx", "./input/TV Patrol 06.01-05.2020.docx"]
#output_filename_prefix = "TVPvs24Oras_06.01-05.2020" # common prefix of your output filename
#input_filename = ["./input/sample1.docx", "./input/sample2.docx"]
#output_filename_prefix = "sample" # common prefix of your output filename
#input_mode = "docu"
#graph_header = "Show" # custom cell header of output csv
#graph_name = ["24 Oras", "TV Patrol"] # custom cell value of output csv


# Twitter example
input_filename = ["./input/city_tweets_2020-06-17.csv"]
output_filename_prefix = "city_tweets_2020-06-17" # common prefix of your output filename
input_mode = "twitter"
graph_header = "City" # custom cell header of output csv
graph_name = ["Caloocan City", "City Of Makati", "Manila", "Quezon City", "Taguig City", "Cebu City", "Davao City"]

output_folder = "./output/" # output folder
graph_mode = "bigrams"
community_mode = "top5"
output_mode = "gephi"


#=============================================================================
# Load and clean the data
#=============================================================================
# change input mode
if input_mode == "twitter":
    import tweet_input as proj_input
elif input_mode == "docu":
    import docu_input as proj_input
else:
    print("Invalid input mode. Exiting...")
    exit()

# check if successful
proj_input.check_import()


# load file
# note: twitter = csv file, docu = docx file
# returns list of entries (tweets/sentences)
print("Loading files...")
input_entries = proj_input.load_file(input_filename, graph_name)
print("Done. There are " + str(len(input_entries)) + " total entries.\n")

# clean data (depends on the input mode)
print("Cleaning data...")
input_entries = proj_input.clean_data(input_entries)
print("Done.\n")


#=============================================================================
# Create graph
#=============================================================================
# change process mode
if graph_mode == "bigrams":
    import bigram_graph_process as graph_process
else:
    print("Invalid process mode. Exiting...")
    exit()

# check if successful
graph_process.check_import()

# create a graph using the input entries (returns networkx graph object)
print("Creating graphs...")
GRAPHS = graph_process.create_graph(input_entries, input_mode)
num_graphs = len(GRAPHS)
print("Done. " + str(num_graphs) + " graphs created.\n")


#=============================================================================
# Create communities and color the graph
#=============================================================================
# change process mode
if community_mode == "top5":
    import top5_community_process as community_process
elif community_mode == "cities":
    import cities_coloring_process as community_process
else:
    print("Invalid process mode. Exiting...")
    exit()

# check if successful
community_process.check_import()

# create communities and color the graph
print("Detecting communities...")
GRAPHS = community_process.create_communities(GRAPHS, num_graphs, graph_header, input_mode, output_filename_prefix)
print("Done.\n")


#=============================================================================
# Export
#=============================================================================
# set output mode
if output_mode == "gephi":
    import gephi_output as proj_output
else:
    print("Invalid process mode. Exiting...")
    exit()

# check if successful
proj_output.check_import()

# export graph
print("Exporting graph...")
proj_output.export_graph(GRAPHS, output_folder, output_filename_prefix, graph_header, input_mode)
print("Done.\n")


#=============================================================================
# End
#=============================================================================
# display time elapsed
print("Program finished after " + str(time.time() - start_time) + " seconds.")
