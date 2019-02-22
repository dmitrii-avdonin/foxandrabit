from Utils import printCoordsArray, loadNpArrayFromFile
from matplotlib.ticker import NullFormatter  # useful for `logit` scale
import matplotlib.pyplot as plt
import numpy as np
import sys

sys.path.append('.\src')
from settings import pathToDataR, pathToDataF, pathToLabelR, pathToLabelF

np.random.seed(19680801)

def analyzeRabitsData():
    # loading existing training data from files
    dataR = loadNpArrayFromFile(pathToDataR)
    labelR = loadNpArrayFromFile(pathToLabelR)

    delta = labelR[:, 1, :]
    count = labelR[:, 2, :]


    unique, counts = np.unique(np.array([a.sum() for a in count]), return_counts=True)
    r = dict(zip(unique, counts))

    plt.figure(1)

    # Reinforcement eficiency investigation
    plt.subplot(221)
    plt.bar(range(len(unique)), counts, tick_label=unique.astype(int))
    plt.yscale('log')
    plt.title('Reinforcement eficiency')
    plt.xlabel('Number of times label was updated')
    plt.ylabel('Number of Labels')
    plt.grid(True)    

    plt.gca().yaxis.set_minor_formatter(NullFormatter())
    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
                    wspace=0.35)
    
    for i, v in enumerate(counts):
        plt.text(i , 1.5 , str(v), color='black', verticalalignment='bottom', rotation=90)

    plt.show()





if __name__ == "__main__":
    analyzeRabitsData()