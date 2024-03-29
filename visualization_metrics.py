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
from mpl_toolkits.mplot3d import Axes3D

class RegrParams(object):
    def __init__(self):
        self.is_latency_node_vertical = False
        self.is_overhead_node_vertical = False
        self.is_latency_overhead_vertical = False
        self.is_latency_node_linear = True
        self.is_overhead_node_linear = True
        self.is_latency_overhead_linear = True

def main(filename, undersample=False, oversample=False, plot=True, regr_params=None, filter_overhead=False):
    # set seaborn style
    sns.set()

    # parameter parsing
    if regr_params is None:
        regr_params = RegrParams()

    df = pd.read_csv(filename, sep=';')
    df = df.query("nb_nodes>1")
    if filter_overhead:
        df = df.query("overhead>0")

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
    # end parameter parsing

    # over/undersampling in order to balance the samples and have the same amount of samples
    # for each nunmber of nodes
    # in case of over sampling, we take the mean amount of samples
    # in case of under sampling, we take the min amount of samples across the number of nodes
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

        # pick the same amount of samples for each number of nodes
        for nb_nodes in range(nb_min, nb_max+1):
            nodes_indices = df[df.nb_nodes == nb_nodes].index
            if len(nodes_indices) <= 0:
                continue
            random_indices = np.random.choice(nodes_indices, nb_to_pick, replace=replace)
            indices.extend(random_indices)

        df = df.loc[indices]

    # 3D plot
    fig_3d = plt.figure()
    ax_3d = fig_3d.add_subplot(111, projection='3d')
    x_3d = df['nb_nodes']
    y_3d = df['latency']
    z_3d = df['overhead']
    ax_3d.scatter(x_3d, y_3d, z_3d, c='r', marker='o')
    ax_3d.set_xlabel('nb_nodes')
    ax_3d.set_ylabel('latency')
    ax_3d.set_zlabel('overhead')
    plt.show()
    # end 3D plot

    # histograms
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
    # end histograms

    # variable against variable

    # generate all combinations of 1-by-1 comparisons between nb_node, latency, and overhead
    # use parameters contained in regr_params
    for (x, y, is_linear, is_vertical) in [
            ('nb_nodes', 'latency', regr_params.is_latency_node_linear, regr_params.is_latency_node_vertical),
            ('nb_nodes', 'overhead', regr_params.is_overhead_node_linear, regr_params.is_overhead_node_vertical),
            ('overhead', 'latency', regr_params.is_latency_overhead_linear, regr_params.is_latency_overhead_vertical)]:

        # group by variables 1-by-1
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
    # end variable against variable

    test_df = df.groupby(["nb_nodes"])

    # fitting to model
    regr_df = df.copy()
    regr_df_new = df.copy()
    regr_df['nb_nodes'] = regr_df['nb_nodes'].apply(lambda x: 1.0/x)
    regr_y = np.ones((regr_df.shape[0], 1))
    values, err, _, _ = np.linalg.lstsq(regr_df, regr_y, rcond=None)
    values = tuple([v[0] for v in values])
    print("1 = %f / nb_nodes + %f * latency + %f * overhead" % values)
    print(values)
    print("err:", err)

    s = err / regr_df.shape[0]
    s = math.sqrt(s)
    print("rmse=", s)

    (a, b, c) = values
    values = (a, b, c, s)
    # end fitting to model

    # fitting to updated model
    regr_df = df.copy()
    EXPONENT_OVERHEAD= 1.0/2.0 #1/2.6255
    EXPONENT_LATENCY = 1.0 #1/0.9825
    FACTOR_LATENCY = 1/2.0
    FACTOR_NODES = 2.556324643040449

    regr_df_new['overhead'] = regr_df_new['overhead'].apply(lambda x: x**EXPONENT_OVERHEAD)
    regr_df_new['latency'] = regr_df_new['latency'].apply(lambda x: FACTOR_LATENCY * x**EXPONENT_LATENCY)
    regr_df_new['nb_nodes'] = regr_df_new['nb_nodes'].apply(lambda x: FACTOR_NODES/x)
    regr_y = np.ones((regr_df_new.shape[0], 1))
    values2, err2 , _, _ = np.linalg.lstsq(regr_df_new, regr_y, rcond=None)
    values2 = tuple([v[0] for v in values2])
    print(values2)
    print("err2:", err2)
    s = err2 / regr_df.shape[0]
    s = math.sqrt(s)
    print("rmse2=", s)

    (a, b, c) = values2
    values2 = (a, b, c, s)
    #end fitting to new model

    return values, values2, test_df

# plot the lins od df[y] = s*df[x] + i
# if flip is true then invert x and y
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

# returns truf when we second regression is better than first
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
