import scipy.io
import numpy as np
import random


def toNpArray(lst):
    return np.array(lst, dtype=np.float32)

def saveNpArrayToFile(filePath, arr):
    scipy.io.savemat(filePath, mdict={'data': arr}, oned_as='row')

def loadNpArrayFromFile(filePath):
    matdata = scipy.io.loadmat(filePath)
    return matdata['data']

def dice(probability):
    r = random.random()
    return r<=probability

# { {1,2}, {2, 3}, {3, 4}}
# width - number of columns = 3
# height - number of rows   = 2
def printCoordsArray(arr, elemIdx=None, printAsInt=False):
        width = len(arr)
        hasColumns = isinstance(arr[0], (list,)) or isinstance(arr[0], (np.ndarray,))
        height = len(arr[0]) if hasColumns else 1

        for i in reversed(range(height)):
            line = ""
            for j in range(width):
                val = 0
                if(elemIdx != None):
                    val = arr[j][i][elemIdx] if hasColumns else arr[j][elemIdx]
                else:
                    val = arr[j][i] if hasColumns else arr[j]

                if(not printAsInt and (isinstance(val, float) or isinstance(val, np.float32))):
                    line += "{0:6.2f} ".format(val) 
                else: 
                    if(not printAsInt and (isinstance(val, list))):
                        line += " " + str(val) + " "
                    else:
                        line += "{0:6.0f} ".format(val)
            print(line)
        print()     