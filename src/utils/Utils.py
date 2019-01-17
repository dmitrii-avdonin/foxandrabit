import scipy.io
import numpy as np


def toNpArray(lst):
    return np.array(lst, dtype=np.float32)

def saveNpArrayToFile(filePath, arr):
    scipy.io.savemat(filePath, mdict={'data': arr}, oned_as='row')

def loadNpArrayFromFile(filePath):
    matdata = scipy.io.loadmat(filePath)
    return matdata['data']