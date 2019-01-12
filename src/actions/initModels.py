from field.Field import Field
from numpy.random import randint
import numpy as np
from settings import fieldW, fieldH, FoxN, RabitN, vr
from Trainer import train


def generateDummyLabels(populationSize):
    labels=[]
    for j in range(populationSize): 
        label=[.0, .0, .0, .0, .0, .0, .0, .0, .0]
        direction = randint(9)
        label[direction] = .3
        labels.append(label)

    npLabels = np.array(labels, dtype=np.float32)
    return npLabels

def initModels():
    field = Field(fieldW, fieldH, RabitN, FoxN, vr)

    dataR = field.getStatesR()
    labelR = generateDummyLabels(RabitN)

    dataF = field.getStatesF()
    labelF = generateDummyLabels(FoxN)

    train(dataR, labelR, True, True)
    train(dataF, labelF, False, True)
    return None