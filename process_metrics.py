from os import listdir
from os.path import isfile, join
from collections import defaultdict

def main():
    directory = "../"
    onlyfiles = sorted([f for f in listdir(directory) if isfile(join(directory, f)) and "stats" in f and f.endswith(".log")])
    data = []
    list_all = []
    list_averages = []
    for f in onlyfiles:
        print(f)
        raw, averages = process_file(directory + f)
        list_all.extend(raw)
        list_averages.extend(averages)
    print(list_all)
    with open("gen.csv", "w+") as f:
        f.write("nb_nodes;latency;overhead\n")
        for val in list_all:
            f.write("%d;%d;%d\n" %tuple(val))

    with open("gen_averages.csv", "w+") as f:
        f.write("nb_nodes;latency;overhead\n")
        for val in list_averages:
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
    list_averages = []

    for dic in list_files:
        local_averages = []
        for (k, v) in dic.items():
            # reset variables
            last_consensus_height = -1
            last_nb_messages = v[0][2]
            # create new local value that will be updated
            local_values = []
            for value in v:
                # value is a tuple (consensus_reached, total_chain_height, total_number of messages)
                # that can be used to derive latency and overhead
                (consensus_reached, total_chain_height, total_number_messages) = value
                # if the new consensus height reached is one more than the last we met
                # add new points to the graphs
                if consensus_reached > last_consensus_height:
                    for consensus_height in range(last_consensus_height, consensus_reached):
                        local_values.append((len(dic), total_chain_height - consensus_height, total_number_messages-last_nb_messages))
                        last_nb_messages = total_number_messages
                    last_consensus_height = consensus_reached

            list_values.extend(local_values)
            local_averages.extend(local_values)
        average = tuple(map(lambda y: sum(y)/float(len(y)), zip(*local_averages)))
        list_averages.append(average)
    return list_values, list_averages

if __name__ == "__main__":
    main()
