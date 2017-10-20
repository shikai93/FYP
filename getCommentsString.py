#!/usr/bin/env python

import sys
import re
import os.path
import codecs
import os

encoding = 'cp932'
currProjDir = ''
out_dir = sys.argv[2]
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

def visitor(filters, dirname, names):
    mynames = filter(lambda n : os.path.splitext(n)[1].lower() in filters, names)
    for name in mynames:
        fname = os.path.join(dirname, name)
        if not os.path.isdir(fname):
            print_command(fname, 'parsed' + name)

def combineFiles(filters, dirname, names):
    mynames = filter(lambda n : os.path.splitext(n)[1].lower() in filters, names)
    for name in mynames:
        fname = os.path.join(dirname, name)
        if not os.path.isdir(fname):
            combineStrings(fname)

def print_command(filename, outfile):
    global currProjDir

    code = read_file (filename)
    outname = os.path.splitext(outfile)[0]
    if not os.path.exists(out_dir+'/'+currProjDir):
        os.makedirs(out_dir+'/'+currProjDir)
    # commentfile = codecs.open(out_dir+'/'+outfile+".cmt",'a', encoding)
    output_file = codecs.open(out_dir+'/'+currProjDir+'/'+outname+'.txt','a', encoding)

    list_of_strings = finder(code)
    for string in list_of_strings:
        string_to_write = ' '.join(trim_string(string).split())+'\n'

        if len(string_to_write)!=0:

            output_file.write(string_to_write)
            output_file.write(os.linesep)

    output_file.close()

def finder(text):
    result = matchCommentMultiline(text)
    result += matchCommentSingleline(text)
    result += matchString(text)
    result += matchBytes(text)
    return result

def matchCommentMultiline (text) :
    # matches /* */
    pattern_with_lf = re.compile( r'\/\*.*?\*\/', re.DOTALL | re.MULTILINE)
    return pattern_with_lf.findall(text)

def matchCommentSingleline (text) :
    #matches //
    pattern = re.compile( r'\/\/.*')
    return pattern.findall(text)

def matchString (text) :
     # matches " " ' '
    string_pattern = re.compile( r'(([\"\'])(?:(?=(\\?))\3.)*?\2)', re.DOTALL | re.MULTILINE)
    result = []
    string_matched_groups = string_pattern.findall(text)
    # remove 2nd and 3rd group matched
    for match in string_matched_groups:
        result.append(match[0])
    return result

# match magic byte - 0x
def matchBytes (text) :
    byte_pattern = re.compile( r'0[xX]\S*')
    return byte_pattern.findall(text)

def read_file (filename) :
    global encoding
    try:
        encoding = 'cp932'
        codefile = codecs.open(filename,'r', encoding)
        lines=codefile.read()
        codefile.close()
    except UnicodeDecodeError, err:
        return ''
    return lines

def trim_string (string) :
    trimmed_string = string
    if string[0:2] == "//":
            trimmed_string = string[2:]

    if string[0:2] == "/*":
        string = string.replace('\n', ' ')
        string = removeSpecials(['\r','\t','*'],string)
        trimmed_string = string[2:-2]

    if string[0:1] == "'" or string[0:1] == '"':
        trimmed_string = string[1:-1]
    return trimmed_string

def removeSpecials(characters,string):
    for unwantedSpecial in characters :
        string = string.replace(unwantedSpecial,'')
    return string

def combineStrings(fname):
    global currProjDir
    if not os.path.exists(out_dir+'/'+'combined'):
        os.makedirs(out_dir+'/'+'combined')
    code = read_file(fname)
    output_file = codecs.open(out_dir+'/'+'combined'+'/'+'combined'+currProjDir+'.txt','a', 'cp932')
    output_file.write(code)
    output_file.write(os.linesep)
    output_file.close()

'''
Usage:
    python srj-string_comments.py src_dir/ output_dir/
    src_dir is the dir that stores all the different open source codes in folders.
    out_dir/combined contains all combined strings of all open source libraries compared as 'combined'+libname.txt
'''

if __name__ == "__main__":
    topdir = sys.argv[1]
    filters = ['.c', '.cc', '.cpp', '.cxx', '.c++', '.h', '.hxx', '.hh', '.hpp', '.h++', '.txt']
    # combine results of each directories axtracted under the topdir (dir of open source lib)
    for subdir in os.listdir(topdir):
        if (subdir == '.DS_Store') :
            continue
        currProjDir = subdir
        os.path.walk(topdir+'/'+currProjDir, visitor, filters)
        os.path.walk(topdir+'/'+currProjDir, combineFiles, filters)
