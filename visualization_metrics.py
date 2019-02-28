import math
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix
import pandas as pd
from sklearn import linear_model
from scipy import stats
from scipy.linalg import lstsq
import os
import seaborn as sns


class RegrParams(object):
    def __init__(self):
        self.is_latency_node_vertical = False
        self.is_overhead_node_vertical = False
        self.is_latency_overhead_vertical = False
        self.is_latency_node_linear = True
        self.is_overhead_node_linear = True
        self.is_latency_overhead_linear = True

def main(filename, undersample=False, oversample=False, plot=True, regr_params=None):
    sns.set()
    if regr_params is None:
        regr_params = RegrParams()

    df = pd.read_csv(filename, sep=';')
    df = df.query("nb_nodes>1")

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
    maxima = {'nb_nodes': 19, 'overhead': 55, 'latency': 52}
    for x in df.columns:
        value_counts = df[x].value_counts().copy()
        arg_min = value_counts.index.min()
        arg_max = maxima[x]
        print(value_counts.index)
        for i in range(arg_min, arg_max):
            if i not in value_counts.index:
                value_counts.at[i] = 0
        s = value_counts.sum()
        value_counts= value_counts.apply(lambda x: float(x)/s*100.0)
        bar = pd.DataFrame(value_counts)
        bar = bar.sort_index()
        ax = bar.plot(kind='bar')
        ax.get_legend().remove()
        plt.title("Distribution of %s" % pretty[x])
        plt.xlabel(pretty[x])
        plt.ylabel("%")

        if arg_max - arg_min < 20:
            plt.xticks(np.arange(arg_min - 2, arg_max - 1))
            ax.set_xticklabels(np.arange(arg_min, arg_max + 1))
        elif arg_max - arg_min < 50:
            plt.xticks(np.arange(arg_min - 2, arg_max - 1, 2))
            ax.set_xticklabels(np.arange(arg_min, arg_max + 1, 2))
        else:
            plt.xticks(np.arange(arg_min - 2, arg_max -1, 3))
            ax.set_xticklabels(np.arange(arg_min, arg_max + 1, 3))

        if plot:
            plt.show()
        plt.savefig(save_path + "hist_" + x + "_" + filename_suffix, dpi=600)

    for (x, y, is_linear, is_vertical) in [
            ('nb_nodes', 'latency', regr_params.is_latency_node_linear, regr_params.is_latency_node_vertical),
            ('nb_nodes', 'overhead', regr_params.is_overhead_node_linear, regr_params.is_overhead_node_vertical),
            ('overhead', 'latency', regr_params.is_latency_overhead_linear, regr_params.is_latency_overhead_vertical)]:
        plot_df = df.groupby([x, y]).size().reset_index(name='Distribution (%)')
        s = plot_df['Distribution (%)'].sum()
        plot_df['Distribution (%)'] = plot_df['Distribution (%)'].apply(lambda x: 100.0*x/s)
        ax = plot_df.plot.scatter(x=x, y=y, c='Distribution (%)', cmap='copper_r')# cmap='jet')#,)
        occurences = df[x].value_counts()

        arg_min = plot_df[x].min()
        arg_max = plot_df[x].max()
        plt.title("%s as function of %s" % (pretty[y],pretty[x]))
        plt.xlabel(pretty[x])
        plt.ylabel(pretty[y])

        if arg_max - arg_min < 20:
            plt.xticks(np.arange(arg_min, arg_max + 1))
        elif arg_max - arg_min < 50:
            plt.xticks(np.arange(arg_min, arg_max + 1, 2))
        else:
            plt.xticks(np.arange(arg_min, arg_max + 1, 3))
        plt.xlim([arg_min - 1, arg_max + 1])
        xi = plot_df[x]
        yi = plot_df[y]
        s = 0
        i = 0
        flipped = False
        if is_vertical:
            #TODO: sp -> numpy
            s, i, err, _, _ = stats.linregress(yi, xi)
            plot_line(y, x, plot_df, s, i, flip=True)
            print("err:", err)
        elif is_linear:
            Ai = np.vstack([xi, np.zeros(len(xi))]).T
            result = np.linalg.lstsq(Ai, yi, rcond=None)
            s, i = result[0]
            err = result[1]
            plot_line(x, y, plot_df, s, i, flip=False)
            print("err:", err)
        else:
            Ai = np.vstack([xi, np.ones(len(xi))]).T
            result = np.linalg.lstsq(Ai, yi, rcond=None)
            s, i = result[0]
            err = result[1]
            plot_line(x, y, plot_df, s, i, flip=False)
            print("err:", err)

        if plot:
            plt.show()
        plt.savefig(save_path + "relation_" + x + "_" + y + "_" + filename_suffix, dpi=600)

    regr_df = df.copy()
    regr_df_new = df.copy()
    regr_df['nb_nodes'] = regr_df['nb_nodes'].apply(lambda x: 1.0/x)
    regr_y = np.ones((regr_df.shape[0], 1))
    values, err, _, _ = np.linalg.lstsq(regr_df, regr_y, rcond=None)
    values = tuple([v[0] for v in values])
    print("1 = %f / nb_nodes + %f * latency + %f * overhead" % values)
    print(values)
    print("err:", err)
    regr_df = df.copy()
    EXPONENT_OVERHEAD= 1/2.6255
    EXPONENT_LATENCY = 1/0.9825
    FACTOR_LATENCY = 1/2.0
    FACTOR_NODES = 2.5563246430404476

    regr_df_new['overhead'] = regr_df_new['overhead'].apply(lambda x: x**EXPONENT_OVERHEAD)
    regr_df_new['latency'] = regr_df_new['latency'].apply(lambda x: FACTOR_LATENCY * x**EXPONENT_LATENCY)
    regr_df_new['nb_nodes'] = regr_df_new['nb_nodes'].apply(lambda x: FACTOR_NODES/x)
    regr_y = np.ones((regr_df_new.shape[0], 1))
    values2, err2 , _, _ = np.linalg.lstsq(regr_df_new, regr_y, rcond=None)
    values2 = tuple([v[0] for v in values2])
    print(values2)
    print("err2:", err2)
    return values, values2

def plot_line(x, y, df, s, i, flip):
    arg_min = df[x].min()
    arg_max = df[x].max()
    ran = np.arange(arg_min, arg_max + 1)
    line = i + s * ran
    if flip:
        plt.plot(line, ran, alpha=0.7)
    else:
        plt.plot(ran, line, alpha=0.7)
    print("%s = %f * %s + %f" %(y, s, x, i))


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
