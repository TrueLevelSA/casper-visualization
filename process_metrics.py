from os import listdir
from os.path import isfile, join
from collections import defaultdict

class ChainData:
    def __init__(self):
        pass

def main():
    directory = "../"
    onlyfiles = sorted([f for f in listdir(directory) if isfile(join(directory, f)) and f.startswith("stats") and f.endswith(".log")])
    data = []
    list_all = []
    for f in onlyfiles:
        list_all.extend(process_file(directory + f))
    print(list_all)
    with open("gen.csv", "w+") as f:
        f.write("nb_nodes;latency;overhead\n")
        for val in list_all:
            f.write("%d;%d;%d\n" %tuple(val))

def process_file(relative_path):
    print("file" + relative_path)
    list_files = []
    with open(relative_path, "r") as f:
        dic = defaultdict(list)
        for line in f.readlines():
            split = line.strip().split(';')
            if len(split) != 6:
                continue
            dic[split[2]].append(tuple([int(x) for x in split[3:]]))
        list_files.append(dic)

    list_values = []

    for dic in list_files:
        for (k, v) in dic.items():
            # reset variables
            last_consensus_height = -1
            last_nb_messages = v[0][2]
            # create new local value that will be updated
            local_values = [[len(dic),0,0]]
            for value in v:
                # value is a tuple (consensus_reached, total_chain_height, total_number of messages)
                # that can be used to derive latency and overhead

                (consensus_reached, total_chain_height, total_number_messages) = value
                # if the new consensus height reached is one more than the last we met
                # add a new point to the graphs
                if consensus_reached ==  last_consensus_height+1:
                    # once we reach a new consensus height, we can update the overhead from the previous point
                    local_values[-1][2] = total_number_messages - last_nb_messages

                    # we then add the new value with set nb_nodes and latency (which is the longest chain - consensus height that has been reachd
                    local_values.append([len(dic), total_chain_height - consensus_reached, 0])

                    # set loop variables for next iteration
                    last_consensus_height = consensus_reached
                    last_nb_messages = total_number_messages
                elif consensus_reached > last_consensus_height:
                    local_values[-1][2] = total_number_messages - last_nb_messages
                    for consensus_height in range(last_consensus_height +1, consensus_reached + 1):
                        local_values.append([len(dic), total_chain_height - consensus_height, 0])
                    last_consensus_height = consensus_reached
                    last_nb_messages = total_number_messages
            #print("local_values", local_values)
            list_values.extend(local_values[1:-1])
    return list_values

if __name__ == "__main__":
    main()
