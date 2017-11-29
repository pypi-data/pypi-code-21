import random
import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt

def func1(x_i):
  return 1 if x_i > 2.5 else -1


# X = [-3, -1,  0,  1, 4, 5, 6, 8, 9]
# #if x_i > 2, this datapoint belongs to the positive class and y_i is +1.
# Y = [-1, -1, -1, -1, 1, 1, 1, 1, 1]
# print X
# print Y

def generate_data(no_points):
    X = np.zeros(shape=(no_points, 2))
    Y = np.zeros(shape=no_points)
    for ii in range(no_points):
        X[ii][0] = random.randint(1,9)+0.5
        X[ii][1] = random.randint(1,9)+0.5
        Y[ii] = 1 if X[ii][0]+X[ii][1] >= 12 else -1
    return X, Y

def generate_polynomial_data(no_points):
    X = np.zeros(shape=(no_points, 2))
    Y = np.zeros(shape=no_points)
    for ii in range(no_points):
        X[ii][0] = random.randint(1,9)+0.5
        X[ii][1] = random.randint(1,9)+0.5
        Y[ii] = 1 if (X[ii][0]*X[ii][1]) >= 14 else -1
    return X, Y
    
X,Y = generate_polynomial_data(100)
print(Y)


x_1_pass, x_2_pass, x_1_fail, x_2_fail, wrong_guess_1, wrong_guess_2 = [], [], [], [], [], []
for ii in range(0,len(Y)):
    if Y[ii] == -1:
        x_1_fail.append(X[ii][0])
        x_2_fail.append(X[ii][1])
    else:
        x_1_pass.append(X[ii][0])
        x_2_pass.append(X[ii][1])
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
ax.scatter(x_1_fail, x_2_fail, c='r', s=50)
ax.scatter(x_1_pass, x_2_pass, c='g', s=50)
#ax.scatter(wrong_guess_1, wrong_guess_2, c='k', s=200, marker="x")
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=20)
#ax.set_xlim([0,10])
#ax.set_ylim([0,10])
ax.set_xlabel('hours of studying time', fontsize=20)
ax.set_ylabel('hours of sleep', fontsize=20)
fig.show()
plt.show()




def plot_figure(X,Y,iteration_no,example_no,w,b):
    x_1_pass, x_2_pass, x_1_fail, x_2_fail = [], [], [], []
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    #ax.add_patch(patches.Rectangle((X[jj][0]-0.25, X[jj][1]-0.25), 0.5, 0.5, fill=False))
    for ii in range(0,len(Y)):
        if Y[ii] == -1:
            x_1_fail.append(X[ii][0])
            x_2_fail.append(X[ii][1])
        else:
            x_1_pass.append(X[ii][0])
            x_2_pass.append(X[ii][1])        
    ax.scatter(x_1_fail, x_2_fail, c='r', s=50)
    ax.scatter(x_1_pass, x_2_pass, c='g', s=50)
    ax.tick_params(axis='x', labelsize=20)
    ax.tick_params(axis='y', labelsize=20)
    ax.set_xlim([0,10])
    ax.set_ylim([0,10])
    ax.set_xlabel('x_1', fontsize=20)
    ax.set_ylabel('x_2', fontsize=20)
    plt.title('The perceptron algorithm: \n iteration %s - training example %s' % (iteration_no,example_no))
    plt.plot([0, 10], [-b/float(w[1]), (-b/float(w[1])-10.0*float(w[0])/float(w[1]))], 'k-')
    plt.tight_layout()
    name = str(iteration_no) + '_' + str(example_no) + '.png'
    plt.savefig(name, dpi=50)

# b = 0 
# max_iter = 10
# weight_factor = 0
# diff = 1
# for ii in range(0,max_iter):
  # #random.shuffle(X)
  # for jj in xrange(len(X)):
    # x_i = X[jj]
    # y_i = Y[jj]
    # a = b + weight_factor*x_i
    # #print "y_i, --- b, weight_factor, x_i --- a, y_i*a         -->          ", y_i, "----", b, weight_factor, x_i, "----", a, y_i*a
    # if y_i*a <= 0:
      # weight_factor += y_i*x_i
      # b = b + y_i
      # print "iteration no: %s ; new weight_factor, bias: %s %s " % (ii, weight_factor, b)
      
b = 0 #bias
n,m = np.shape(X) #n is the number of training examples, m the number of dimensions
max_iter = 200
weight_vector = np.zeros(m);
for ii in range(0,max_iter):
  #random.shuffle(X)
  for jj in xrange(n):
    x_i = X[jj]
    y_i = Y[jj]
    #a = b + weight_vector[0]*x_i[0]+weight_vector[1]*x_i[1]
    a = b + np.dot(weight_vector, x_i)
    #print "y_i, --- b, weight_factor, x_i --- a, y_i*a         -->          ", y_i, "----", b, weight_vector, x_i, "----", a, y_i*a
    if np.sign(y_i*a) != 1:
      weight_vector += y_i*x_i
      b += y_i
      print("iteration %s; new weight_vector: %s - new b: %s" % (ii, weight_vector, b))
      #if weight_vector[1] != 0: plot_figure(X,Y,ii,jj,weight_vector,b) 

def linear_kernel(x1, x2):
    return np.dot(x1, x2)

def polynomial_kernel(x, y, p=3):
    return (1 + np.dot(x, y)) ** p

def gaussian_kernel(x, y, sigma=5.0):
    return np.exp(-linalg.norm(x-y)**2 / (2 * (sigma ** 2)))