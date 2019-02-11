import math
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix
import pandas as pd
from sklearn import linear_model
from scipy import stats
from scipy.linalg import lstsq
import os

def main(filename, undersample=False, oversample=False, plot=True):
    df = pd.read_csv(filename, sep=';')

    if oversample and undersample:
        print("Can't both over and undersample")
        exit()

    filename_suffix = filename.split("/")[-1] + ".png"
    save_path = "generated/imgs/"
    try:
        os.mkdir(save_path)
    except FileExistsError as e:
        pass
    except BaseException as e:
        raise e

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
        #print(bar.columns)
        bar = bar.sort_index()
        ax = bar.plot(kind='bar')
        ax.get_legend().remove()
        plt.title("Histogram of %s" % pretty[x])
        plt.xlabel(pretty[x])
        plt.ylabel("Counts")
        if plot:
            plt.show()
        plt.savefig(save_path + "hist_" + x + "_" + filename_suffix, dpi=600)

    for (x, y) in [('nb_nodes', 'latency'), ('nb_nodes', 'overhead'), ('overhead', 'latency')]:
        plot_df = df.groupby([x, y]).size().reset_index(name='Count')
        ax = plot_df.plot.scatter(x=x, y=y, c='Count', cmap='jet')# cmap='jet')#,)
        occurences = df[x].value_counts()
        #print(plot_df)
        arg_min = plot_df[x].min()
        arg_max = plot_df[x].max()
        plt.title("%s as function of %s" % (pretty[y],pretty[x]))
        plt.xlabel(pretty[x])
        plt.ylabel(pretty[y])
        xi = plot_df[x]
        yi = plot_df[y]
        s1, i1, r1, p1, std1 = stats.linregress(xi, yi)
        s2, i2, r2, p2, std2 = stats.linregress(yi, xi)
        if should_select_second(r1, p1, std1, r2, p2, std2):
            plot_line(y, x, plot_df, s2, i2, flip=True)
        else:
            plot_line(x, y, plot_df, s1, i1, flip=False)

        if plot:
            plt.show()
        plt.savefig(save_path + "relation_" + x + "_" + y + "_" + filename_suffix, dpi=600)

    regr_df = df.copy()
    regr_df['nb_nodes'] = regr_df['nb_nodes'].apply(lambda x: 1.0/x)
    regr_y = np.ones((regr_df.shape[0], 1))
    values, residues, rank, s = lstsq(regr_df, regr_y, overwrite_a=True, overwrite_b=True)
    values = tuple([v for v in values.flat])
    print("1 = %f / nb_nodes + %f * latency + %f * overhead" % values)
    print(values)
    return values

def plot_line(x, y, df, s, i, flip):
    arg_min = df[x].min()
    arg_max = df[x].max()
    ran = np.arange(arg_min, arg_max + 1)
    line = i + s * ran
    if flip:
        plt.plot(line, ran, color='red')
    else:
        plt.plot(ran, line, color='red')
    print("%s = %f * %s + %f" %(x, s, y, i))


def should_select_second(r1, p1, std1, r2, p2, std2):
    return std2 < std1

if __name__ == "__main__":
    import sys
    filename = "gen_averages.csv"
    if "--undersample" in sys.argv:
        main(filename, undersample=True)
    elif "--oversample" in sys.argv:
        main(filename, oversample=True)
    else:
        main(filename)
