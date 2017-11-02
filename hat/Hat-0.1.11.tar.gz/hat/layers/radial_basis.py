'''
SUMMARY:  radial basis NN
AUTHOR:   Qiuqiang Kong
Created:  2016.11.25
--------------------------------------
'''
import numpy as np
import inspect
from core import Layer
from ..import backend as K
from ..import initializations
from ..import activations
from ..import regularizations 
from ..globals import new_id
from ..supports import to_tuple, to_list, is_one_element, is_elem_equal
from abc import ABCMeta, abstractmethod, abstractproperty


'''
Radial basis NN
Usage: RadialBasis( 100, mu_init=np.random.normal(loc=0, scale=0.1, size=100), beta_init=0.01*np.ones(100), name='rb' )
'''
class RadialBasis( Layer ):
    def __init__( self, n_out, 
                  mu_init=None, beta_init=None, mu_reg=None, beta_reg=None, trainable_params=['mu', 'beta'], name=None ):
                      
        super( RadialBasis, self ).__init__( name )
        self._n_out_ = n_out
        self._mu_init_ = mu_init
        self._beta_init_ = beta_init
        self._mu_reg_ = mu_reg
        self._beta_reg_ = beta_reg
        self._trainable_params_ = trainable_params
        
    def __call__( self, in_layers ):
        # merge
        in_layers = to_list( in_layers )
        input = in_layers[0].output_
        n_in = in_layers[0].out_shape_[-1]
        n_dim = len( in_layers[0].out_shape_ )
        
        # init mu & beta
        self._mu_ = self._init_params( self._mu_init_, None, shape=(n_in, self._n_out_), name=str(self._name_)+'_mu' )        
        self._beta_ = self._init_params( self._beta_init_, None, shape=(self._n_out_, ), name=str(self._name_)+'_beta' )

        # output
        if n_dim==2:
            Diff = input[:,:,None] - self._mu_  # shape: (N1, n_in, n_out)
        if n_dim==3:
            Diff = input[:,:,:,None] - self._mu_  # shape: (N1, N2, n_in, n_out)
        
        output = K.exp( - self._beta_ * K.sum( K.sqr( Diff ), axis=-2 ) )   # shape: (..., n_out)
        
        
        # assign attributes
        self._prevs_ = in_layers
        self._nexts_ = []
        self._out_shape_ = in_layers[0].out_shape_[0:-1] + (self._n_out_,)
        self._output_ = output
        self.set_trainable_params( self._trainable_params_ )
        self._reg_value_ = self._get_reg()
        
        # below are compulsory parts
        [ layer.add_next(self) for layer in in_layers ]     # add this layer to all prev layers' nexts pointer
        self._check_attributes()                             # check if all attributes are implemented
        return self
        
    # ---------- Public attributes ----------
        
    @property
    def mu_( self ):
        return K.get_value( self._mu_ )
        
    @property
    def beta_( self ):
        return K.get_value( self._beta_ )
        
    # layer's info & params
    @property
    def info_( self ):
        dict = { 'class_name': self.__class__.__name__, 
                 'id': self._id_, 
                 'name': self._name_, 
                 'n_out': self._n_out_, 
                 'mu': self.mu_, 
                 'beta': self.beta_, 
                 'mu_reg_info': regularizations.get_info( self._mu_reg_ ),
                 'beta_reg_info': regularizations.get_info( self._beta_reg_ ), 
                 'trainable_params': self._trainable_params_ }
        return dict
        
    # ---------- Public methods ----------
            
    # set trainable params
    def set_trainable_params( self, trainable_params ):
        legal_params = [ 'mu', 'beta' ]
        self._params_ = []
        for ch in trainable_params:
            assert ch in legal_params, "'ch' is not a param of " + self.__class__.__name__ + "! "
            self._params_.append( self.__dict__[ '_'+ch+'_' ] )
    
    # load layer from info
    @classmethod
    def load_from_info( cls, info ):
        mu_reg = regularizations.get_obj( info['mu_reg_info'] )
        beta_reg = regularizations.get_obj( info['beta_reg_info'] )

        layer = cls( n_out=info['n_out'], 
                     mu_init=info['mu'], beta_init=info['beta'], mu_reg=mu_reg, beta_reg=beta_reg, 
                     trainable_params=info['trainable_params'], name=info['name'] )
                     
        return layer
    
    # ---------- Private methods ----------
        
    # get regularization
    def _get_reg( self ):
        reg_value = 0. 

        if self._mu_reg_ is not None:
            reg_value += self._mu_reg_.get_reg( [self._mu_] )

        if self._beta_reg_ is not None:
            reg_value += self._beta_reg_.get_reg( [self._beta_] )
            
        return reg_value
        
    # ------------------------------------