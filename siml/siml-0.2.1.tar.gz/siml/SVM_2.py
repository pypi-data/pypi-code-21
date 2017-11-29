import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import random

def generate_data(no_points):
    X = np.zeros(shape=(no_points, 3))
    for ii in range(no_points):
        X[ii][0] = random.random()*10
        X[ii][1] = random.random()*10
        if ii % 2 == 0:
            X[ii][2] = 150 + (X[ii][0]-5)**4 - (X[ii][1]-5)*4
        else:
            X[ii][2] = - 150 - (X[ii][0]-5)**4 - (X[ii][1]-5)**4
    return X
    
def choose_color(y_i):
    return 'r' if y_i < 0 else 'b'

def choose_class(y_i):
    return 1 if y_i >0 else 0
    
X = generate_data(500)    
colors = [choose_color(elem) for elem in X[:,2]]
Y = np.array([choose_class(elem) for elem in X[:,2]])    

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(X[:,0], X[:,1], X[:,2], c=colors, marker='o', s = 50)
#plt.show()


####

# from sklearn.linear_model import LogisticRegression
# model = LogisticRegression()
# model = model.fit(X, Y)
# print(model.score(X, Y))
# print(model.coef_)

import logistic_regression as lr
from evaluators import *

print("training Logistic Regression Classifier")
lr2 = lr.LogisticRegression(max_iter = 20)
lr2.train(X, Y)
print("trained")
predicted_Y_test = lr2.classify(X)
f1 = f1_score(predicted_Y_test, Y, 1)
print("F1-score on the test-set for class %s is: %s" % (1, f1))

