import tables as tb 
import pandas as pd 
import sys

class AffmatCompiler(object):
	"""docstring for AffmatCompiler"""
	

	def __init__(self, handle):
		super(AffmatCompiler, self).__init__()
		self.handle = handle
		self.distmat = None
		self.thresholds = None

	def run(self):
		print('Reading thresholds...')
		self.read_thresholds()
		
		for segment in range(1,9):
			print('Segment: {0}'.format(segment))

			print('Reading Distmat...')
			self.read_distmat(segment)

			print('Saving affmat...')
			self.save_affmat(segment)

			print('Removing intermediate distmat...')
			self.remove_intermediate_distmat(segment)

	def read_thresholds(self):
		self.thresholds = pd.read_csv('thresholds.csv', header=None)
		self.thresholds = dict(zip(self.thresholds[0], self.thresholds[1]))

	def read_distmat(self, segment):
		"""
		Reads the distmat into memory.
		"""
		self.distmat = pd.read_csv('distmats/{0} Segment {1} Distmat Renamed.txt'.format(self.handle, segment), index_col=0, delimiter=',', skiprows=1, header=None)
		self.distmat.columns = self.distmat.index

	def save_affmat(self, segment):
		"""
		Saves the affmat to an HDF5 store.
		"""
		self.distmat = (1 - self.distmat)

		threshold_value = self.thresholds[segment]
		self.distmat = self.distmat[self.distmat > threshold_value]

		self.distmat.to_hdf('{0} Segment Affmats.h5'.format(self.handle), mode='a', key='segment{0}'.format(segment))

	def remove_intermediate_distmat(self, segment):
		import os
		os.remove('distmats/{0} Segment {1} Distmat Renamed.txt'.format(self.handle, segment))



if __name__ == '__main__':

	handle = sys.argv[1]

	ac = AffmatCompiler(handle)
	ac.run()





