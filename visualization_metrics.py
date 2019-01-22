import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix
import pandas as pd

def main(filename, undersample=False, oversample=False):
    df = pd.read_csv(filename, sep=';')

    if oversample and undersample:
        print("Can't both over and undersample")
        exit()

    if undersample or oversample:
        indices = []
        nb_min = df.min(axis=0)[0]
        nb_max = df.max(axis=0)[0]
        arg_min = 0
        arg_max = len(df)

        occurences = df['nb_nodes'].value_counts()

        #print(occurences)

        arg_min = occurences.min(axis=0)
        arg_max = occurences.max(axis=0)

        nb_to_pick = int((arg_max + arg_min)/2) if oversample else arg_min
        replace = oversample

        print("Undersampling" if undersample else "Oversampling")
        print("Using %d samples for each" %nb_to_pick)

        for nb_nodes in range(nb_min, nb_max+1):
            nodes_indices = df[df.nb_nodes == nb_nodes].index
            if len(nodes_indices) <= 0:
                continue
            random_indices = np.random.choice(nodes_indices, nb_to_pick, replace=replace)
            indices.extend(random_indices)

        df = df.loc[indices]

    #scatter_matrix(df, alpha=0.2)#, diagonal='kde')
    #plt.suptitle("Inter-dependency and KDE of the main metrics")
    #plt.show()

    pretty = {'nb_nodes': 'Number of nodes', 'overhead': 'Overhead', 'latency': 'Latency'}
    for x in df.columns:
        bar = pd.DataFrame(df[x].value_counts())
        print(bar.columns)
        bar = bar.sort_index()
        ax = bar.plot(kind='bar')
        ax.get_legend().remove()
        plt.title("Histogram of %s" % pretty[x])
        plt.xlabel(pretty[x])
        plt.ylabel("Counts")
        plt.show()

    for (x, y) in [('nb_nodes', 'latency'), ('nb_nodes', 'overhead'), ('latency', 'overhead')]:
        plot_df = df.groupby([x, y]).size().reset_index(name='Count')
        ax = plot_df.plot.scatter(x=x, y=y, c='Count', cmap='gist_rainbow')# cmap='jet')#,)
        occurences = df[x].value_counts()
        print(occurences)
        arg_min = plot_df[x].min()
        arg_max = plot_df[x].max()
        plt.title("%s as function of %s" % (pretty[y],pretty[x]))
        plt.xlabel(pretty[x])
        plt.ylabel(pretty[y])
        plt.show()
        print(x,'[', plot_df[x].min(),',', plot_df[x].max(),']')
        print("x axis will be fixed in pandas 0.24.0 (31.01.19)")


if __name__ == "__main__":
    import sys
    filename = "gen.csv"
    if "--undersample" in sys.argv:
        main(filename, undersample=True)
    elif "--oversample" in sys.argv:
        main(filename, oversample=True)
    else:
        main(filename)
