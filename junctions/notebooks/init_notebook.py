import os, sys
currentFolder = os.path.abspath('')
try:
    sys.path.remove(str(currentFolder))
except ValueError: # Already removed
    pass

<<<<<<< HEAD
projectFolder = '/home/exx/muktadir/earthquakePrediction/'
projectFolder = 'C:/Users/abjaw/Documents/GitHub/junction-art'
projectFolder = 'f:/myProjects/av/junction-art'
=======
projectFolder = 'C:\\Users\\ishaa\\source\\repos\\junction-art'
>>>>>>> signals-feature-ishaan
sys.path.append(str(projectFolder))
os.chdir(projectFolder)
print( f"current working dir{os.getcwd()}")