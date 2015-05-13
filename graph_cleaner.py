import networkx as nx 
import numpy as np
import sys

class GraphCleaner(object):
	"""docstring for GraphCleaner"""
	def __init__(self, handle):
		super(GraphCleaner, self).__init__()
		self.handle = handle
		self.G = nx.read_gpickle('{0} Graph with PWIs.pkl'.format(self.handle))

	def run(self):
		self.remove_zero_pwi_edges()		
		self.remove_full_edges_diff_subtypes()
		self.remove_full_edges_with_nan()
		self.remove_reassortant_edges_with_nan()
		self.remove_reassortant_edges_with_subtype_mismatch()
		self.change_mixed_to_Mixed()
		self.save_output()


	def save_output(self):
		nx.write_gpickle(self.G, '{0} Final Graph.pkl'.format(self.handle))

	def change_mixed_to_Mixed(self):
		for n, d in self.G.nodes(data=True):
			if d['subtype'] == 'mixed':
				self.G.node[n]['subtype'] = 'Mixed'
				
	def remove_zero_pwi_edges(self):
		for sc, sk, d in self.G.edges(data=True):
			if d['pwi'] == 0 and (sc, sk) in self.G.edges():
				self.G.remove_edge(sc, sk)

	def remove_full_edges_diff_subtypes(self):
		for sc, sk, d in self.G.edges(data=True):
			if d['edge_type'] == 'full_complement':
				sc_subtype = self.G.node[sc]['subtype']
				sk_subtype = self.G.node[sk]['subtype']
				mixed = ['mixed', 'Mixed']
				if sc_subtype not in mixed and sk_subtype not in mixed:
					if sc_subtype != sk_subtype:
						self.G.remove_edge(sc, sk)

	def remove_full_edges_with_nan(self):
		for sc, sk, d in self.G.edges(data=True):
			if d['edge_type'] == 'full_complement':
				for seg, val in d['segments'].items():
					if np.isnan(val):
						self.G.remove_edge(sc, sk)
						break

	def has_nan(self, edge_with_data):
		has_nan = False
		_, _, d = edge_with_data
		for k, v in d['segments'].items():
			if np.isnan(v):
				has_nan = True
				break

		return has_nan

	def remove_in_edges(self, node):
		for sc, sk in self.G.in_edges(node):
			if (sc, sk) in self.G.edges():
				self.G.remove_edge(sc, sk)


	def remove_reassortant_edges_with_nan(self):
		for sc, sk, d in self.G.edges(data=True):
			if d['edge_type'] == 'reassortant' and self.has_nan((sc, sk, d)):
				if (sc, sk) in self.G.edges():
					self.remove_in_edges(sk)


	def remove_reassortant_edges_with_subtype_mismatch(self):
		
		def get_ha_subtype(node):
			mixed = ['mixed', 'Mixed']
			subtype = self.G.node[node]['subtype']
			if subtype not in mixed:
				return subtype.split('N')[0].split('H')[1]

			else:
				return subtype

		def get_na_subtype(node):
			mixed = ['mixed', 'Mixed']
			subtype = self.G.node[node]['subtype']
			if subtype not in mixed:
				return subtype.split('N')[1]
			else:
				return subtype

		for sc, sk, d in self.G.edges(data=True):

			sc_subtype = self.G.node[sc]['subtype']
			sk_subtype = self.G.node[sk]['subtype']

			sc_ha = get_ha_subtype(sc)
			sk_ha = get_ha_subtype(sk)

			sc_na = get_na_subtype(sc)
			sk_na = get_na_subtype(sk)

			mixed = ['mixed', 'Mixed']

			if 4 in d['segments'].keys():
				if sc_ha != sk_ha and sc_ha not in mixed and sk_ha not in mixed:
					self.remove_in_edges(sk)

			if 6 in d['segments'].keys():
				if sc_na != sk_na and sc_na not in mixed and sk_na not in mixed:
					self.remove_in_edges(sk)




if __name__ == '__main__':
	handle = sys.argv[1]

	gc = GraphCleaner(handle)
	gc.run()

