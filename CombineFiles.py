#!/usr/bin/env python

import sys
import re
import os.path
import codecs
import os

encoding = 'cp932'
out_dir = 'combinedFiles'
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

def visitor(filters, dirname, names):
	mynames = filter(lambda n : os.path.splitext(n)[1].lower() in filters, names)
	for name in mynames:
		fname = os.path.join(dirname, name)
		if not os.path.isdir(fname):
			combineStrings(fname)

def combineStrings(fname):
    code = read_file(fname)
    output_file = codecs.open(out_dir+'/'+'combined'+sys.argv[1]+'.txt','a', 'cp932')
    output_file.write(code)
    output_file.write(os.linesep)
    output_file.close()

def read_file (filename) :
    global encoding
    try:
        encoding = 'cp932'
        codefile = codecs.open(filename,'r', encoding)
        lines=codefile.read()
        codefile.close()
    except UnicodeDecodeError, err:
        encoding = 'utf8'
        codefile = codecs.open(filename,'r',encoding)
        lines=codefile.read()
        codefile.close()
        return lines
    return lines

'''
Usage:
    python srj-string_comments.py src_dir/ output_dir/
'''

if __name__ == "__main__":
    topdir = sys.argv[1]

    filters = ['.txt']

    os.path.walk(topdir, visitor, filters)
