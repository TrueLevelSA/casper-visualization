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
            #print(split)
            dic[split[2]].append([int(x) for x in split[3:]])

        list_files.append(dic)
    list_values = []
    for dic in list_files:

        for (k, v) in dic.items():
            #print(k,v)
            last_consensus_height = -1
            last_nb_messages = 0
            local_values = [[len(dic),0,0]]
            for value in v:
                # TODO maybe instead of forcing the 1 step on the consensus
                # divide nb messages by nb of consensus steps?
                if value[0] ==  last_consensus_height+1:
                    #print("in", value)
                    local_values[-1][2] = value[2] - last_nb_messages
                    local_values.append([len(dic), value[1]-value[0],0])
                    last_consensus_height = value[0]
                    last_nb_messages = value[2]
                elif value[0] > last_consensus_height:
                    last_consensus_height = value[0]
                    last_nb_messages = value[2]
            list_values.extend(local_values[1:-1])
    return list_values

if __name__ == "__main__":
    main()
