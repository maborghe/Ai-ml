# exec(open("./hw1.py").read())

from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.model_selection import PredefinedSplit
from sklearn.model_selection import GridSearchCV

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

X, y = load_wine(True)
x = X[:,:2]
xNotTest, xTest, yNotTest, yTest = train_test_split(x, y, test_size=0.3)
xTrain, xVal, yTrain, yVal = train_test_split(xNotTest, yNotTest, test_size=0.28)

scaler = StandardScaler()
scaler.fit(xTrain)
xTrain = scaler.transform(xTrain)
xVal = scaler.transform(xVal)
xTest = scaler.transform(xTest)
xNotTest = scaler.transform(xNotTest)

# Setup plot
x_min, x_max = xTest[:, 0].min() - 1, xTest[:, 0].max() + 1
y_min, y_max = xTest[:, 1].min() - 1, xTest[:, 1].max() + 1
xx, yy = np.meshgrid(np.arange(x_min, x_max, .02),
                         np.arange(y_min, y_max, .02))
cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA', '#AAAAFF'])
cmap_bold = ListedColormap(['#FF0000', '#00FF00', '#0000FF'])

KNN = 1
SVM = 1                            
                            
# 1. KNN
if KNN:
    K = [1,3,5,7]
    Kscore = [None]*len(K)
    plt.figure()
    for i, k in enumerate(K):    
        clf = KNeighborsClassifier(n_neighbors=k).fit(xTrain, yTrain)  
        #accuracy = accuracy_score(Kpred[i], yVal)
        Kscore[i] = clf.score(xVal, yVal)
        
        # Create plot        
        Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)        
    
        plt.subplot(2, 2, i + 1)    
        plt.pcolormesh(xx, yy, Z, cmap=cmap_light)
        plt.scatter(xTrain[:, 0], xTrain[:, 1], c=yTrain, cmap=cmap_bold,
                    edgecolor='k', s=20)
        plt.xlim(xx.min(), xx.max())
        plt.ylim(yy.min(), yy.max())
        #plt.title("Wine classification (k = %i)"
        #          % (K[i]))    
        #filename = 'wine%d' % (K[i])        
    
    #plt.show()
    plt.savefig('knnPredPlot', dpi=250)
    
    # plot Kscores
    plt.figure()
    plt.scatter(K, Kscore)
    #plt.show()
    plt.savefig('knnScorePlot', dpi=250)
    
    # evaluate the best K on the test set
    bestK = np.asarray(Kscore).argmax()
    clf = KNeighborsClassifier(n_neighbors=K[bestK]).fit(xTrain, yTrain)
    KNNtestScore = clf.score(xTest, yTest)
    print("KNN test score: %f" % (KNNtestScore))

# 2. and 3. linear and rbf SVM
C = [0.001, 0.01, 0.1, 1, 10, 100, 1000]
SVMscore = [None]*len(C)        
if SVM:    
    for c, ker in enumerate(["linear", "rbf"]):               
                
        plt.figure()
        plt.subplots_adjust(hspace=0.4, wspace=1.5)
        for i, cc in enumerate(C):
            clf = SVC(C=cc, gamma='scale', kernel=ker).fit(xTrain, yTrain)
            SVMscore[i] = clf.score(xVal, yVal)
            plt.subplot(3, 3, i+1)    
            plt.xlim(xx.min(), xx.max())
            plt.ylim(yy.min(), yy.max())
            Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
            Z = Z.reshape(xx.shape)
            plt.contourf(xx, yy, Z, cmap=cmap_light)
            plt.scatter(xTrain[:, 0], xTrain[:, 1], c=yTrain, cmap=cmap_bold,
                        edgecolor='k', s=20)        
            #plt.title("(C = %g)"
            #        % (C[i]))            
                        
        plt.savefig(ker+'PredPlot', dpi=250)
        
        # plot Kscores
        plt.figure()
        plt.xlim(0.0001, 10000)
        plt.xscale("log")        
        plt.scatter(C, SVMscore)
        plt.show()
        plt.savefig(ker+'ScorePlot', dpi=250)
        
        # evaluate the best C on the test set
        bestC = np.asarray(SVMscore).argmax()
        #print("bestC: %d - %f" % (bestC, SVMscore[bestC]))
        clf = SVC(C=C[bestC], gamma='scale', kernel=ker).fit(xTrain, yTrain)
        SVMtestScore = clf.score(xTest, yTest)
        print(ker + " test score: %f" % (SVMtestScore))
        print()
                           
        
#4. Grid search
GridScore = [SVMscore, [None]*len(C)]
for i, cc in enumerate(C):
    clf = SVC(C=cc, gamma='auto', kernel='rbf').fit(xTrain, yTrain)
    GridScore[1][i] = clf.score(xVal, yVal)

bestVal = np.asmatrix(GridScore).argmax()
bestC = C[bestVal % len(C)]
bestGamma = 'scale' if bestVal//len(C) == 0 else 'auto'
clf = SVC(C=bestC, gamma=bestGamma, kernel='rbf').fit(xTrain, yTrain)
plt.figure()
plt.xlim(xx.min(), xx.max())
plt.ylim(yy.min(), yy.max())
Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)
plt.contourf(xx, yy, Z, cmap=cmap_light)
plt.scatter(xTrain[:, 0], xTrain[:, 1], c=yTrain, cmap=cmap_bold,
            edgecolor='k', s=20)    
plt.show()
plt.savefig('gridPredPlot', dpi=250)
gridTestScore = clf.score(xTest, yTest)
print("best params: C=%f, gamma=%s" %(bestC, bestGamma))
print("grid test score: %f" % (gridTestScore))
print()    


# 5. Grid search with 5-Fold CV
# Merge train and validation sets         
xTrain = xNotTest
yTrain = yNotTest
parameters = {'gamma':('auto', 'scale'), 'C':C}
clf = GridSearchCV(SVC(kernel="rbf"), parameters, cv=5, iid='false').fit(xTrain, yTrain)
plt.figure()
plt.xlim(xx.min(), xx.max())
plt.ylim(yy.min(), yy.max())
Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)
plt.contourf(xx, yy, Z, cmap=cmap_light)
plt.scatter(xTrain[:, 0], xTrain[:, 1], c=yTrain, cmap=cmap_bold,
            edgecolor='k', s=20)    
plt.show()
plt.savefig('cvGridPredPlot', dpi=250)
gridTestScore = clf.score(xTest, yTest)
bestParams = ', '.join("{!s}={!r}".format(key,val) for (key,val) in clf.best_params_.items())    
print("CV best params: " + bestParams)
print("CV grid test score: %f" % (gridTestScore))