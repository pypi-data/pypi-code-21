import numpy as np
import janus.gmm
import janus.features
import janus.encoding
import janus.template
import bobo.util
import ctypes
import janus.cache
import sklearn.decomposition
import janus.classifier

class FisherNetwork(object):
    def __init__(self,
                 layer1_params,
                 output_params,
                 seed=None,
                 svmIterations=1e6,
                 numBatches=1e2,
                 numTrainingFeatures=1e6,
                 gmmIterations=20):
        self.mSeed = seed
        self.mSvmIterations = svmIterations
        self.mNumBatches = numBatches
        self.mNumTrainingFeatures = numTrainingFeatures
        self.mGmmIterations = gmmIterations
        self.mLayer1 = {'d':layer1_params['d'],
                        'k':layer1_params['n_modes'],
                        'dl':layer1_params['dl'],
                        'ql':layer1_params['ql'],
                        'gmm':None,
                        'pca':None,
                        'OVR':None}
        self.mLayer2 = {'k':output_params['n_modes'],
                        'd':output_params['d'],
                        'do_media_pooling':output_params['do_media_pooling'],
                        'pca':None,
                        'gmm':None,
                        'OVR':None}

    def train(self,trainset):
        # - trainset is an RDD containing janus.template.GalleryTemplates

        self.trainLayer1(trainset)
        self.trainOutputLayer(trainset)
        return self

    def trainLayer1(self, trainset):
        if self.mLayer1['gmm'] == None:
            imageset = trainset.flatMap(lambda tmpl: tmpl.explode()) # templates to images
            gmmModes = self.mLayer1['k']
            pcaComponents = self.mLayer1['d']
            gmmIterations = self.mGmmIterations
            numTrainingFeatures = self.mNumTrainingFeatures
            svmIterations = self.mSvmIterations
            numBatches = self.mNumBatches
            seed = self.mSeed

            import janus.recognition
            d01 = janus.recognition.CompactAndDiscriminativeFaceTrackDescriptor().train(
                trainset=imageset,
                gmmModes=gmmModes,
                pcaComponents=pcaComponents,
                gmmIterations=gmmIterations,
                do_ddr=False,
                do_jointmetric=False,
                do_parallel_sgd=True,
                seed=seed,
                trainingFeatures=numTrainingFeatures,
                svmIterations=svmIterations,
                numBatches=numBatches,
                do_metric=False
            )

            gmm = d01.gmm
            self.mLayer1['gmm'] = gmm

            pca = d01.pca
            self.mLayer1['pca'] = pca

            print 'saving network with layer 1 GMM and PCA models'
            bobo.util.save(self,'network.pkl')

        if self.mLayer1['OVR'] == None:
            # train the W matrix using OVR classifiers
            categories = imageset.map(lambda tmpl: tmpl.category()).collect()
            label_dict = dict()
            for c in categories:
                if c not in label_dict:
                    label_dict[c] = len(label_dict)
        
            Ltrain = np.zeros((len(categories),),dtype=np.int32)
            for i in xrange(0,len(Ltrain)):
                Ltrain[i] = label_dict[categories[i]]

            pca = self.mLayer1['pca']
            f_densesift = (
                lambda im: janus.features.denseMultiscaleSIFT(
                    im,
                    scales=[1.0, 1.0/np.sqrt(2), 0.5, 1.0/(2*np.sqrt(2)), 0.25],
                    dx=1,
                    dy=1,
                    weakGeometry=True,
                    rootsift=True,
                    binSizeX=6,
                    binSizeY=6,
                    floatDescriptor=False,
                    do_fast=False,
                    do_weak_scale=False,
                    weakAspectRatio=False
                )
            )
            f_densePCAsift = (
                lambda im: reduce(
                    lambda x,y: np.concatenate( (pca.transform(x),y), axis=1),
                    np.split(f_densesift(im), [-2], axis=1))
            )

            gmm = self.mLayer1['gmm']
            dl = self.mLayer1['dl']
            ql = self.mLayer1['ql']
            f_avg_semilocalfv = (
                lambda im: janus.encoding.average_semilocalfishervector(
                    im,
                    features = f_densePCAsift,
                    gmmMean = gmm.mean,
                    gmmCovar = gmm.covariance,
                    gmmPrior = gmm.prior,
                    dl = dl,
                    ql = ql)
            )
            average_semilocalfvs = imageset.map(
                lambda tmpl: f_avg_semilocalfv(tmpl[0]).squeeze()
            ).collect()
            Xtrain = np.concatenate([np.reshape(fv,(1,len(fv))) for fv in average_semilocalfvs],axis=0)

            import janus.crossval_optimization
            if False: # perform an optimization search over training parameters
                co = janus.crossval_optimization.CrossvalOptimization(Xtrain = Xtrain,
                                                                      Ltrain = Ltrain,
                                                                      topk = 5,
                                                                      n_folds = 10,
                                                                      verbose = 1)
                (_,model) = co.optimize()
            else: # or, just use these parameters that worked well for CS2 split 1
                (model,_,_) = janus.crossval_optimization.train_one_vs_rest(
                    labels = Ltrain, # an N-length array of feature labels
                    features = Xtrain,
                    eval_freq = 5,
                    n_epoch = 100,
                    verbose = 1,
                    n_thread = 48,
                    _lambda = 1e-3,
                    beta = 200,
                    eta0 = 1e-2,
                    bias_term = 100,
                    stop_valid_threshold = -0.02,
                    temperature = 10.0,
                    topk = 5,
                    n_folds = 10
                )

            # choose 128 dimensions at random, because I have no idea what is a better way to do it
            # TODO figure out a better way to choose the 128 dimensions
            model.selected_dims = np.random.permutation(np.arange(model.W.shape[0]))[:128]
            self.mLayer1['OVR'] = model

            print 'saving network with layer 1 One-vs-Rest model'
            bobo.util.save(self,'network.pkl')

        return self

    def trainOutputLayer(self, trainset):
        layer1_pca = self.mLayer1['pca']
        f_densesift = (
            lambda im: janus.features.denseMultiscaleSIFT(
                im,
                scales=[1.0, 1.0/np.sqrt(2), 0.5, 1.0/(2*np.sqrt(2)), 0.25],
                dx=1,
                dy=1,
                weakGeometry=True,
                rootsift=True,
                binSizeX=6,
                binSizeY=6,
                floatDescriptor=False,
                do_fast=False,
                do_weak_scale=False,
                weakAspectRatio=False
            )
        )
        f_densePCAsift = (
            lambda im: reduce(
                lambda x,y: np.concatenate( (layer1_pca.transform(x),y), axis=1),
                np.split(f_densesift(im), [-2], axis=1))
        )
        gmm = self.mLayer1['gmm']
        dl = self.mLayer1['dl']
        ql = self.mLayer1['ql']
        ovr_model = self.mLayer1['OVR']
        W = ovr_model.W[ovr_model.selected_dims,:]
        K = self.mLayer1['k']
        D = self.mLayer1['d']+2
        reordered_W = np.zeros(W.shape,dtype=np.float32)
        for k in xrange(0,K):
            reordered_W[:,2*k*D:(2*k+1)*D] = W[:,k*D:(k+1)*D]
            reordered_W[:,(2*k+1)*D:2*D*(k+1)] = W[:,(k+K)*D:(k+K+1)*D]

        f_semilocalfv = (
            lambda im: janus.encoding.semilocalfishervector_reduce_and_stack2x2(
                im,
                features = f_densePCAsift,
                gmmMean = gmm.mean,
                gmmCovar = gmm.covariance,
                gmmPrior = gmm.prior,
                dl = dl,
                ql = ql,
                W = reordered_W,
                do_signsqrt = True,
                do_normalized = True, # normalized *after* reduction by W and 2x2 stacking
                scale_factor = 3.0 # scale factor, applied to the descriptor before augmentation with weak geometry components
            )
        )

        featset = trainset.flatMap(lambda tmpl: bobo.util.tolist(tmpl.images())+bobo.util.tolist(tmpl.frames())) # templates to images
        featset = featset.flatMap(f_semilocalfv) # explode descriptors into RDD of features

        # PCA dimensionality reduction on dense sift only, then augment with weak geometry
        trainingFeatures = self.mNumTrainingFeatures
        if self.mLayer2['pca'] is None:
            seed = self.mSeed
            f_semilocalfv_only = (lambda d: d[0:-2])  # remove weak geometry from descriptor (final two columns)
            pcaset = featset.context.parallelize(
                featset.map(f_semilocalfv_only).takeSample(withReplacement=False, num=int(trainingFeatures), seed=seed)
            )
            pcaComponents = self.mLayer2['d']
            self.mLayer2['pca'] = janus.reduction.pca(pcaset, n_components=pcaComponents)
            print 'saving network with output layer PCA'
            bobo.util.save(self,'network.pkl')

        # GMM learning
        if self.mLayer2['gmm'] is None:
            layer2_pca = self.mLayer2['pca']
            f_pca_semilocalfv = (
                lambda d: reduce(
                    lambda x,y: np.concatenate((layer2_pca.transform(x).flatten(),y) ),
                    np.split(d, [len(d)-2])
                )
            )
            seed = self.mSeed
            gmmset = featset.context.parallelize(
                featset.map(f_pca_semilocalfv).takeSample(withReplacement=False, num=int(trainingFeatures), seed=seed)
            )
            n_modes = self.mLayer2['k']
            gmmIterations = self.mGmmIterations
            self.mLayer2['gmm'] = janus.gmm.train(
                gmmset,
                n_modes=n_modes,
                do_verbose=True,
                n_iterations=gmmIterations,
                seed=seed
            )
            print 'saving network with output layer GMM'
            bobo.util.save(self,'network.pkl')

        return self

    def encodeLayer1(self, dataset):
        # - dataset is an RDD containing janus.template.GalleryTemplates
        layer1_pca = self.mLayer1['pca']
        f_densesift = (
            lambda im: janus.features.denseMultiscaleSIFT(
                im,
                scales=[1.0, 1.0/np.sqrt(2), 0.5, 1.0/(2*np.sqrt(2)), 0.25],
                dx=1,
                dy=1,
                weakGeometry=True,
                rootsift=True,
                binSizeX=6,
                binSizeY=6,
                floatDescriptor=False,
                do_fast=False,
                do_weak_scale=False,
                weakAspectRatio=False
            )
        )
        f_densePCAsift = (
            lambda im: reduce(
                lambda x,y: np.concatenate( (layer1_pca.transform(x),y), axis=1),
                np.split(f_densesift(im), [-2], axis=1))
        )
        gmm = self.mLayer1['gmm']
        ovr_model = self.mLayer1['OVR']
        W = ovr_model.W[ovr_model.selected_dims,:]
        D = gmm.mean.shape[1]
        K = gmm.mean.shape[0]
        reordered_W = np.zeros(W.shape,dtype=np.float32)
        for k in xrange(0,K):
            reordered_W[:,2*k*D:(2*k+1)*D] = W[:,k*D:(k+1)*D]
            reordered_W[:,(2*k+1)*D:2*D*(k+1)] = W[:,(k+K)*D:(k+K+1)*D]

        dl = self.mLayer1['dl']
        ql = self.mLayer1['ql']
        f_semilocalfv = (
            lambda im: janus.encoding.semilocalfishervector_reduce_and_stack2x2(
                im,
                features = f_densePCAsift,
                gmmMean = gmm.mean,
                gmmCovar = gmm.covariance,
                gmmPrior = gmm.prior,
                dl = dl,
                ql = ql,
                W = reordered_W,
                do_signsqrt = True,
                do_normalized = True, # normalized *after* reduction by W and 2x2 stacking
                scale_factor = 3.0 # scale factor, applied to the descriptor before augmentation with weak geometry components
            )
        )
        # encode features from single images
        return dataset.flatMap(lambda tmpl: tmpl.explode()).map(lambda tmpl: (tmpl.templateid(), tmpl.category(), f_semilocalfv(tmpl[0]).squeeze()))

    def encode(self, dataset):
        # - dataset is an RDD containing janus.template.GalleryTemplates
        layer1_pca = self.mLayer1['pca']
        f_densesift = (
            lambda im: janus.features.denseMultiscaleSIFT(
                im,
                scales=[1.0, 1.0/np.sqrt(2), 0.5, 1.0/(2*np.sqrt(2)), 0.25],
                dx=1,
                dy=1,
                weakGeometry=True,
                rootsift=True,
                binSizeX=6,
                binSizeY=6,
                floatDescriptor=False,
                do_fast=False,
                do_weak_scale=False,
                weakAspectRatio=False
            )
        )
        f_densePCAsift = (
            lambda im: reduce(
                lambda x,y: np.concatenate( (layer1_pca.transform(x),y), axis=1),
                np.split(f_densesift(im), [-2], axis=1))
        )
        ovr_model = self.mLayer1['OVR']
        W = ovr_model.W[ovr_model.selected_dims,:]
        layer1_gmm = self.mLayer1['gmm']
        D = layer1_gmm.mean.shape[1]
        K = layer1_gmm.mean.shape[0]
        reordered_W = np.zeros(W.shape,dtype=np.float32)
        for k in xrange(0,K):
            reordered_W[:,2*k*D:(2*k+1)*D] = W[:,k*D:(k+1)*D]
            reordered_W[:,(2*k+1)*D:2*D*(k+1)] = W[:,(k+K)*D:(k+K+1)*D]

        dl = self.mLayer1['dl']
        ql = self.mLayer1['ql']
        f_semilocalfv = (
            lambda im: janus.encoding.semilocalfishervector_reduce_and_stack2x2(
                im,
                features = f_densePCAsift,
                gmmMean = layer1_gmm.mean,
                gmmCovar = layer1_gmm.covariance,
                gmmPrior = layer1_gmm.prior,
                dl = dl,
                ql = ql,
                W = reordered_W,
                do_signsqrt = True,
                do_normalized = True, # normalized *after* reduction by W and 2x2 stacking
                scale_factor = 3.0 # scale factor, applied to the descriptor before augmentation with weak geometry components
            )
        )
        layer2_pca = self.mLayer2['pca']
        f_densePCAsemilocalfv = (
            lambda im: reduce(
                lambda x,y: np.concatenate((layer2_pca.transform(x),y), axis=1),
                np.split(f_semilocalfv(im), [-2], axis=1)
            )
        )
        layer2_gmm = self.mLayer2['gmm']

        f_fishervector = (
            lambda im: janus.encoding.fishervector(
                im,
                features=f_densePCAsemilocalfv,
                gmm=layer2_gmm,
                do_improvedfisher=False,
                do_fastfisher=False
            )
        )

        f_encoding = (
            lambda tmpl: janus.encoding.fishervector_pooling(
                tmpl.images() + tmpl.videos(), # fishervector_pooling has a bug when fed media templates
                f_encoding=f_fishervector,
                do_jitter=True,
                do_signsqrt=True,
                do_normalized=True,
                do_verbose=True,
                do_random_jitter=False
            )
        )
        return dataset.map(lambda tmpl: (tmpl.templateid(), tmpl.category(), f_encoding(tmpl).squeeze()))
