#!/usr/bin/env python
import sys
import numpy as np
import os.path
import codecs
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

encoding = 'cp932'
THRESHOLD = 0

tfidf_transformer = TfidfTransformer()
count_vect = CountVectorizer(ngram_range=(2,2), analyzer="char_wb")

all_filenames = []
out_dir = sys.argv[2]
out_name = 'UniqueNGrams.txt'
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

def visitor(filters, dirname, names):
    global all_filenames
    all_documents = []
    mynames = filter(lambda n : os.path.splitext(n)[1].lower() in filters, names)
    for name in mynames:
        fname = os.path.join(dirname, name)
        if not os.path.isdir(fname):
            all_documents.append(read_file (fname))
            all_filenames.append(name)
    compareNgram(all_documents)

def compareNgram(all_documents):
    bags_of_strings = getNgram(all_documents)
    tfidf = TFIDF(bags_of_strings)
    strings = count_vect.get_feature_names()
    zippedMatrix = zip(*tfidf.nonzero())

    uniqueStrings = []

    # unique strings is an array with tuples containing document id, strings, and tfidf rating
    for docId,stringsID in zippedMatrix :
        if (tfidf[docId, stringsID] > THRESHOLD ):
            uniqueStrings.append([docId, strings[stringsID], tfidf[docId, stringsID]])

    writeToFile(uniqueStrings)

def writeToFile(uniqueStrings) :
    output_file = codecs.open(out_dir+'/'+out_name,'a', encoding)

    for data in uniqueStrings :
        string_to_write = all_filenames[data[0]] + " : " + data[1] + " " + str(data[2])
        output_file.write(string_to_write)
        output_file.write(os.linesep)

    output_file.close()

def getNgram(all_documents):
    return count_vect.fit_transform(all_documents)


def TFIDF(bags_of_strings):
    return tfidf_transformer.fit_transform(bags_of_strings)

def read_file (filename):
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
