import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix
import pandas as pd

def main():
    df = pd.read_csv("gen.csv", sep=';')
    scatter_matrix(df, alpha=0.2, diagonal='kde')
    plt.show()

if __name__ == "__main__":
    main()
