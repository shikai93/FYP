import shutil
import os

dirName = os.path.dirname(__file__)
filename = os.path.join(dirName, 'result')

shutil.rmtree(filename) 