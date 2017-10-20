#!/usr/bin/env python
import sys, time
import numpy as np
import os.path
import codecs
import os
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

encoding = 'cp932'
THRESHOLD = 0

conn = sqlite3.connect('comparedResults.db')
c = conn.cursor()

tfidf_transformer = TfidfTransformer()
tfidf_vector = TfidfVectorizer(ngram_range=(2,2), analyzer="word")
tfidf_tri_vector = TfidfVectorizer(ngram_range=(3,3), analyzer="word")

all_filenames = []
out_dir = sys.argv[2]
out_name = 'UniqueNGrams.txt'
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

def visitor(filters, dirname, names):
    global all_filenames
    initDB()
    all_documents = []
    mynames = filter(lambda n : os.path.splitext(n)[1].lower() in filters, names)
    id = 0;
    for name in mynames:
        fname = os.path.join(dirname, name)
        if not os.path.isdir(fname):
            all_documents.append(read_file (fname))
            all_filenames.append(name)
            c.execute("INSERT INTO Project VALUES (?,?)",(id, name))
            id += 1
    compareNgram(all_documents)
    conn.commit()
    conn.close()

def initDB():
    c.execute('DROP TABLE IF EXISTS Project')
    c.execute('DROP TABLE IF EXISTS Bigram')
    c.execute('DROP TABLE IF EXISTS Trigram')
    c.execute('DROP TABLE IF EXISTS BigramStrings')
    c.execute('DROP TABLE IF EXISTS TrigramStrings')
    c.execute('CREATE TABLE Project (Id Int, filename text)')
    c.execute('CREATE TABLE Bigram (Pid Int, Bid Int, Prob Float)')
    c.execute('CREATE TABLE BigramStrings (Bid Int, Message text)')
    c.execute('CREATE TABLE TrigramStrings (Tid Int, Message text)')
    c.execute('CREATE TABLE Trigram (Pid Int, Tid Int, Prob Float)')

def compareNgram(all_documents):
    bigrams = getNgram(all_documents,2)
    trigrams = getNgram(all_documents, 3)

    tfidf = TFIDF(bigrams)
    tfidf_tri = TFIDF(trigrams)
    print "******** TFIDF Done **********"

    bi_strings = tfidf_vector.get_feature_names()
    tri_strings = tfidf_tri_vector.get_feature_names()

    zippedMatrix = zip(*tfidf.nonzero())
    zippedTriMatrix = zip(*tfidf_tri.nonzero())

    index = 0
    for string in bi_strings:
        c.execute('INSERT INTO BigramStrings VALUES (?,?)',(index,string))
        index += 1
    index = 0
    for string in tri_strings:
        c.execute('INSERT INTO TrigramStrings VALUES (?,?)',(index,string))
        index += 1

    counter = 0
    for docId,stringsID in zippedTriMatrix:
        if (counter%10000 == 0):
            print'\t...'
        counter += 1
        c.execute('INSERT INTO Trigram VALUES (?,?,?)',(int(docId),int(stringsID),tfidf_tri[docId, stringsID]))
    # unique strings is an array with tuples containing document id, strings, and tfidf rating
    print 'Trigram Done!'

    for docId,stringsID in zippedMatrix:
        if (counter%10000 == 0) :
            print '\t...'
        counter += 1
        if (tfidf[docId, stringsID] > THRESHOLD ):
            # insert into bigram table
            c.execute('INSERT INTO Bigram VALUES (?,?,?)',(int(docId),int(stringsID),tfidf[docId, stringsID]))
    print 'Bigram Done!'

    # writeToFile(uniqueStrings)

def writeToFile(uniqueStrings):
    output_file = codecs.open(out_dir+'/'+out_name,'a', encoding)

    for data in uniqueStrings :
        string_to_write = all_filenames[data[0]] + " : " + data[1] + " " + str(data[2])
        output_file.write(string_to_write)
        output_file.write(os.linesep)

    output_file.close()

def getNgram(all_documents,no_of_words):
    if (no_of_words == 2) :
        return tfidf_vector.fit_transform(all_documents)
    if (no_of_words == 3):
        return tfidf_tri_vector.fit_transform(all_documents)
    return tfidf_vector.fit_transform(all_documents)


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
