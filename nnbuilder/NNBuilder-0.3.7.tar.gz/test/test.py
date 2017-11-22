from nnbuilder import *

### Global Config ###
config.set(name='planet', max_epoch=1000, batch_size=1024, valid_batch_size=128, verbose=5)

### Optimizer Config ###
gradientdescent.adam.learning_rate=0.001

### Extension Config ###
earlystop.set(epoch=True)
saveload.set(load=False)

### Build Model ###
VGG19 = Model(X=X.Img2D((1, 28, 28)), Y=Y.OneHot(10), metrics=[metrics.accuracy, metrics.f2],
              lossfunction=lossfunctions.onehot_crossentropy)
VGG19.add(EncodeY(10))
VGG19.add(ImArgument2D((26, 26), tencrop, 10))
VGG19.add(Conv(64, (3, 3), bias=True, activation=T.relu, mode='same'))
VGG19.add(Conv(64, (3, 3), bias=True, activation=T.relu, mode='same'))
VGG19.add(Pool((2, 2), autopad=True))
VGG19.add(Conv(128, (3, 3), bias=True, activation=T.relu, mode='same'))
VGG19.add(Conv(128, (3, 3), bias=True, activation=T.relu, mode='same'))
VGG19.add(Pool((2, 2), autopad=True))
VGG19.add(Conv(256, (3, 3), bias=True, activation=T.relu, mode='same'))
VGG19.add(Conv(256, (3, 3), bias=True, activation=T.relu, mode='same'))
VGG19.add(Conv(256, (3, 3), bias=True, activation=T.relu, mode='same'))
VGG19.add(Conv(256, (3, 3), bias=True, activation=T.relu, mode='same'))
VGG19.add(Pool((2, 2), autopad=True))
VGG19.add(Conv(512, (3, 3), bias=True, activation=T.relu, mode='same'))
VGG19.add(Conv(512, (3, 3), bias=True, activation=T.relu, mode='same'))
VGG19.add(Conv(512, (3, 3), bias=True, activation=T.relu, mode='same'))
VGG19.add(Conv(512, (3, 3), bias=True, activation=T.relu, mode='same'))
VGG19.add(Pool((2, 2), autopad=True))
VGG19.add(Conv(512, (3, 3), bias=True, activation=T.relu, mode='same'))
VGG19.add(Conv(512, (3, 3), bias=True, activation=T.relu, mode='same'))
VGG19.add(Conv(512, (3, 3), bias=True, activation=T.relu, mode='same'))
VGG19.add(Conv(512, (3, 3), bias=True, activation=T.relu, mode='same'))
VGG19.add(Pool((2, 2), autopad=True))
VGG19.add(Flatten())
VGG19.add(Hidden(4096, activation=T.relu))
VGG19.add(Dropout(0.5))
VGG19.add(Hidden(4096, activation=T.relu))
VGG19.add(Dropout(0.5))
VGG19.add(Logistic(10))

### Load Data ###
trainset, validset, testset = tools.loaddatas.Load_mnist_image("./datasets/mnist.pkl.gz")
data = DataFrame(trainset, validset, testset)

# debug(data,Mlp)
### Fit Model ###
train(data=data, model=VGG19, optimizer=gradientdescent.adam, extensions=[monitor])
