import shutil
import os

dirName = os.path.dirname(__file__)
filename = os.path.join(dirName, 'result')
comparedResults = os.path.join(dirName, 'comparedResults')

shutil.rmtree(filename)
shutil.rmtree(comparedResults) 
