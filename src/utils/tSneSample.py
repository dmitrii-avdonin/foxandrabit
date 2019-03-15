from Utils import printCoordsArray, loadNpArrayFromFile
from matplotlib.ticker import NullFormatter  # useful for `logit` scale
import matplotlib.pyplot as plt
import numpy as np
import sys

from time import time
from sklearn import (manifold, datasets, decomposition, ensemble,
             discriminant_analysis, random_projection)

sys.path.append('.\src')
from settings import pathToDataR, pathToDataF, pathToLabelR, pathToLabelF

#np.random.seed(19680801)

# loading existing training data from files
dataR = loadNpArrayFromFile(pathToDataR)
labelR = loadNpArrayFromFile(pathToLabelR)


labelsTmp = np.array([a for a in labelR if sum(a[2])>1 ])
labels = labelsTmp[:, 0, :]
idx = np.random.randint(labels.shape[0], size=2000)
labels = labels[idx, :]

delta = labelR[:, 1, :]
count = labelR[:, 2, :]

def analyzeRabitsData():
    plt.figure(1)

    tSNE(plt)

    plt.gca().yaxis.set_minor_formatter(NullFormatter())
    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
                    wspace=0.35)
    plt.show()


## Function to Scale and visualize the embedding vectors
def plot_embedding(X, plt, title=None):
    x_min, x_max = np.min(X, 0), np.max(X, 0)
    X = (X - x_min) / (x_max - x_min)     
    #plt.figure()
    ax = plt.subplot(111)
    for i in range(X.shape[0]):
        plt.text(X[i, 0], X[i, 1], "o",
                 color=plt.cm.Set1(np.argmax(labels[i]) / 10.),
                 fontdict={'weight': 'bold', 'size': 9})
#     if hasattr(offsetbox, 'AnnotationBbox'):
#         ## only print thumbnails with matplotlib > 1.0
#         shown_images = np.array([[1., 1.]])  # just something big
#         for i in range(digits.data.shape[0]):
#             dist = np.sum((X[i] - shown_images) ** 2, 1)
#             if np.min(dist) < 4e-3:
#                 ## don't show points that are too close
#                 continue
#             shown_images = np.r_[shown_images, [X[i]]]
#             imagebox = offsetbox.AnnotationBbox(
#                 offsetbox.OffsetImage(digits.images[i], cmap=plt.cm.gray_r),
#                 X[i])
#             ax.add_artist(imagebox)
    plt.xticks([]), plt.yticks([])
    if title is not None:
        plt.title(title)

def tSNE(plt):
        print("Computing t-SNE embedding")
        tsne = manifold.TSNE(n_components=2, init='pca', random_state=0)
        t0 = time()
        X_tsne = tsne.fit_transform(labels)
        plot_embedding(X_tsne, plt,
                "t-SNE embedding of the labels (time %.2fs)" % (time() - t0))


if __name__ == "__main__":
    analyzeRabitsData()