#!/usr/bin/env python

import sys
import re
import os.path
import codecs
import os

encoding = 'cp932'
out_dir = sys.argv[2]
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

def comment_finder(text):
    pattern = re.compile( r'//.*?$|/\*.*?\*/', re.DOTALL | re.MULTILINE)
    result = pattern.findall(text)
    return result

def print_command(filename, outfile):

    codefile = codecs.open(filename,'r', encoding)
    commentfile = codecs.open(out_dir+'/'+outfile+".cmt",'a', encoding)
    lines=codefile.read()
    codefile.close()
    #the list of comments
    list_of_comments = comment_finder(lines)
    for comment in list_of_comments:
        #print comment[0:2]
        if comment[0:2] == "//":
                comment_to_write = comment[2:]
        else:
            comment_to_write = comment[2:-2]
        if comment_to_write.endswith("\r"):
            comment_to_write = comment_to_write[0:-1]
        if len(comment_to_write)!=0:
            commentfile.write(comment_to_write)
            commentfile.write(os.linesep)
    commentfile.close()

def visitor(filters, dirname, names):
	mynames = filter(lambda n : os.path.splitext(n)[1].lower() in filters, names)
	for name in mynames:
		fname = os.path.join(dirname, name)
		if not os.path.isdir(fname):
			print_command(fname, name)
'''
Usage:
    python srj-string_comments.py src_dir/ output_dir/
'''

if __name__ == "__main__":
    topdir = sys.argv[1]

    filters = ['.c', '.cc', '.cpp', '.cxx', '.c++', '.h', '.hxx', '.hh', '.hpp', '.h++']

    os.path.walk(topdir, visitor, filters)

