from Utils import printCoordsArray, loadNpArrayFromFile
from matplotlib.ticker import NullFormatter  # useful for `logit` scale
import matplotlib.pyplot as plt
import numpy as np
import sys

sys.path.append('.\src')
from settings import pathToDataR, pathToDataF, pathToLabelR, pathToLabelF

np.random.seed(19680801)

# loading existing training data from files
dataR = loadNpArrayFromFile(pathToDataR)
labelR = loadNpArrayFromFile(pathToLabelR)

delta = labelR[:, 1, :]
count = labelR[:, 2, :]

def analyzeRabitsData():
    plt.figure(1)

    updatesCount(plt)

    updateSize(plt)

    plt.gca().yaxis.set_minor_formatter(NullFormatter())
    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
                    wspace=0.35)
    plt.show()


def updatesCount(plt):
    # Reinforcement eficiency investigation
    unique, counts = np.unique(np.array([a.sum() for a in count]), return_counts=True)

    plt.subplot(211)
    plt.bar(range(len(unique)), counts, tick_label=unique.astype(int))
    plt.yscale('log')
    plt.title('Update Count')
    plt.xlabel('Number of times label was updated')
    plt.ylabel('Number of Labels')
    plt.grid(True)    

    for i, v in enumerate(counts):
        plt.text(i , 1.5 , str(v), color='black', verticalalignment='bottom', rotation=90)


def updateSize(plt):
    avgAbsDelta =  np.array([ np.sum(np.abs(a))/len(a) for a in delta if np.any(a)])
    bins =  [i * 0.005 for i in range(41)]
    digitized = np.digitize(avgAbsDelta, bins)
    unique, counts = np.unique(digitized, return_counts=True)
    labels =  ["<" + str(bins[u]) for u in unique]

    plt.subplot(212)
    plt.bar(range(len(unique)), counts, tick_label=labels)
    plt.yscale('log')
    plt.title('Update Amount')
    plt.xlabel('Label average absolute update amount ')
    plt.ylabel('Number of Labels')
    plt.grid(True)

    for i, v in enumerate(counts):
        plt.text(i , 3.5 , str(v), color='black', verticalalignment='bottom', rotation=90)



if __name__ == "__main__":
    analyzeRabitsData()