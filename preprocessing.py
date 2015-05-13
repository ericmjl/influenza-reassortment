"""
This script performs data preprocessing.
"""

import pandas as pd
import sys

from Bio import SeqIO

class Preprocessor(object):
	"""docstring for Preprocessor"""
	def __init__(self, handle):
		super(Preprocessor, self).__init__()
		self.handle = handle
		self.df = None
		self.fasta = None

		# Curate a list if strain names to exclude from the analysis.
		self.strain_name_exclusions = ['little yellow-shouldered bat']

	def run(self):

		self.read_dataframe()
		self.clean_strain_names()
		self.remove_excluded_strains()
		self.clean_host_species()
		self.impute_location()
		self.remove_low_quality_accessions()
		self.impute_dates()
		self.get_complete_genome_isolates()
		self.save_full_isolates()

	def remove_excluded_strains(self):
		for name in self.strain_name_exclusions:
			self.df = self.df[self.df['Strain Name'].str.contains(name) == False]

	def read_dataframe(self):
		"""
		Reads the CSV file containing the data into memory.
		"""

		self.df = pd.read_csv('{0} Sequences.csv'.format(self.handle), parse_dates=['Collection Date'], na_filter=False)

	def read_fasta(self):
		self.fasta = SeqIO.to_dict(SeqIO.parse('{0} Sequences.fasta'.format(self.handle), 'fasta'))

	def clean_strain_names(self):
		"""
		This function removes parentheses from the strain names, leaving only the strain name without any other info.
		"""

		self.df['Strain Name'] = self.df['Strain Name'].str.replace("\\", "/")
   		self.df['Strain Name'] = self.df['Strain Name'].str.split("(").apply(lambda x: max(x, key=len))

	def clean_host_species(self):
		"""
		Host species are usually stored as IRD:hostname. 
		"""
		self.df['Host Species'] = self.df['Host Species'].str.split(':').str[-1]

	def impute_location(self):
		self.df['State/Province'] = self.df['Strain Name'].str.split("/").apply(lambda x: x[1] if len(x) == 4 else x[2])

	def impute_dates(self):
		self.df['Collection Date'] = pd.to_datetime(self.df['Collection Date'])

	def remove_low_quality_accessions(self):
		self.df = self.df[self.df['Sequence Accession'].str.contains('\*') == False]

	def get_complete_genome_isolates(self):
		rows_to_drop = []

		for name, df in self.df.groupby('Strain Name'):
			if len(df) == 8 and set(df['Segment'].values) == set(range(1,9)):
				pass
			else:
				rows_to_drop.extend(df.index)

		self.df = self.df.drop(rows_to_drop)

	def save_full_isolates(self):
		self.df.to_csv('{0} Full Isolates.csv'.format(self.handle))

	def write_segment_fasta(self, segnum):
		accessions = self.df.groupby('Segment').get_group(segnum)['Sequence Accession'].values

		if set(accessions).issubset(set(self.fasta.keys())):
			sequences = [record for accession, record in self.fasta.items() if accession in accessions]

			with open('{0} Segment {1}.fasta'.format(self.handle, segnum), 'w+') as f:
				SeqIO.write(sequences, f, 'fasta')

		else:
			raise Exception("Not all requested accessions in original download.")


if __name__ == '__main__':
	handle = sys.argv[1]

	p = Preprocessor(handle)
	p.run()
