import networkx as nx
import numpy as np
import pandas as pd
import pickle as pkl
import sys
import os

from collections import Counter, defaultdict
from random import sample


class MedianDownsampler(object):
    """
    Downsamples the isolates to the median number of isolates per subtype.

    Input:    A CSV file with all of the isolates present.
    Output:   A CSV file with isolates downsampled to the median number of
              isolates per subtype.
    """
    def __init__(self, handle, n_samples):
        super(MedianDownsampler, self).__init__()
        self.handle = handle
        self.df = None
        self.G = nx.Graph()
        self.n_samples = n_samples

    def run(self):
        self.read_data()
        self.initialize_graph()
        for n in range(self.n_samples):
            self.write_downsampled_isolates(n)

    def read_data(self):
        self.df = pd.read_csv('{0} Full Isolates.csv'.format(self.handle),
                              index_col=0,
                              parse_dates=['Collection Date'],
                              na_filter=False)

    def initialize_graph(self):
        for g, d in self.df.groupby(['Strain Name', 'Subtype']):
            strain_name, subtype = g

            self.G.add_node(strain_name, subtype=subtype)

    @property
    def median_class_size(self):
        counts = Counter([d['subtype'] for n, d in self.G.nodes(data=True)])
        med = np.median([i for i in counts.values()])
        return med

    @property
    def median_downsampled_isolates(self):
        subtypes_nodes = defaultdict(list)
        for n, d in self.G.nodes(data=True):
            subtype = d['subtype']
            subtypes_nodes[subtype].append(n)

        downsampled = set()

        for subtype, isolates in subtypes_nodes.items():
            if len(isolates) > self.median_class_size:
                downsampled.update(sample(isolates, int(median)))
            else:
                downsampled.update(isolates)

        downsampled_df = self.df[self.df['Strain Name'].isin(downsampled)]

        return downsampled_df

    def checkdir(self, dirname):
        if dirname not in os.listdir(os.getcwd()):
            os.mkdir(dirname)

    def write_downsampled_isolates(self, n):
        self.checkdir('run{0}'.format(n))
        self.median_downsampled_isolates.to_csv(
            'run{0}/{1} Full Isolates.csv'.format(n, sample))

if __name__ == '__main__':

    handle = sys.argv[1]
    n_samples = sys.argv[2]
    md = MedianDownsampler(handle)
    md.run()
