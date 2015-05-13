import pandas as pd
import sys

class FullAffmatCompiler(object):
	"""docstring for FullAffmatCompiler"""
	def __init__(self, handle):
		super(FullAffmatCompiler, self).__init__()
		self.handle = handle
		self.summed_affmat = pd.DataFrame()
		self.current_df = None

	def run(self):
		for segment in range(1,9):
			print('Currently processing segment {0}'.format(segment))
			if segment == 1:
				self.read_affmat(segment)
				self.summed_affmat = self.current_df
			else:
				self.read_affmat(segment)
				self.summed_affmat = self.summed_affmat + self.current_df

		self.summed_affmat.to_hdf(path_or_buf='{0} Summed Affmats.h5'.format(self.handle), key='full', mode='w')

	def read_affmat(self, segment):
		key = 'segment{0}'.format(segment)
		self.current_df = pd.read_hdf('{0} Segment Affmats.h5'.format(self.handle), key=key)

if __name__ == '__main__':
	handle = sys.argv[1]

	fac = FullAffmatCompiler(handle)
	fac.run()