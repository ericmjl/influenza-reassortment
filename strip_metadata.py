import os

from PyPDF2 import PdfFileReader, PdfFileMerger

files_dir = os.getcwd()

for f in os.listdir(files_dir):
	if f.split('.')[-1] == 'pdf':
		merger = PdfFileMerger()
		merger.append(PdfFileReader(f, 'rb'))
		merger.write('{0}'.format(f))