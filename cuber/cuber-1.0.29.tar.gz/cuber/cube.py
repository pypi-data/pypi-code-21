import abc
import cPickle as pickle
import os.path
import logging

import cache
import utils

logger = logging.getLogger(__name__)

class Cube(object):
    __metaclass__  = abc.ABCMeta

    checkpoints_dir = 'checkpoints/'

    '''
    In derived cube may be set to false. 
    If it is set to false, cube will be evalued every time. 
    May be helpful, if cube generates window with plot, etc.
    '''
    restorable = True

    '''
    Set it to true, if you garuantee that cube.eval (and constructor) does not change the argumetns (that are passed by reference) 
    It speed up in-memory cache getting (due to not to coping).
    '''
    immutable_args = False

    def name(self):
        '''
            Unique name for cube and params. This name is key for cache.
            It could be overrited
        '''
        version = self.__class__.version if 'version' in self.__class__.__dict__ else '0'
        logger.info('Auto generated name. Keys: {}, version: {}'.format(self.__dict__.keys(), version))
        return '{}_v{}_{}'.format(
            self.__class__.__name__,
            version,
            utils.universal_hash(self.__dict__)
        )

    def get_unique_file(self, filename):
        '''
            Generate filepath that is unique for pair (cube name (hash), filename).
            Second call of the function from cube with same params returns the same path.
        '''
        work_dir = os.path.join(self.checkpoints_dir, self.name())
        if not os.path.isdir(work_dir):
            os.makedirs(work_dir)
        return os.path.join(work_dir, filename)

    def get(self, disable_file_cache = False, disable_inmemory_cache = False, cleanup = False, perfomance_logging = False):
        '''
            Checks if there is a cached verison and loads it.
            If there is no cached version, runs calcualtions via eval function.
            If you want to get cube's result, use only this function.
        '''
        if not self.restorable:
            logger.info('Cube is not resotrable. Evaluating...')
            data = self.eval()
            logger.info('Evaluated')
            return data

        if perfomance_logging:
            logger.info('Getting data for {}'.format(self.__class__.__name__))
        key = self.name() # hashing make take some time
        if perfomance_logging:
            logger.info('Key (hash) is done: {}'.format(key))
        logger.debug('Key: {}'.format(key))

        data = None
        data_done = False # flag the data is already got from cache
        
        # resources the data is already uploaded to
        data_inmemory_cache = False
        data_file_cache = False

        # try load form memory
        if not disable_inmemory_cache and not data_done:
            cached, cached_data = cache.Cache().get(key, do_not_copy = self.immutable_args)
            if perfomance_logging:
                logger.info('In-memory cache has answered: {}'.format('contains' if cached else 'does not contain'))
            if cached: # true, if object is found 
                logger.debug('Loaded from in-memory cache')
                data = cached_data
                data_inmemory_cache = True
                data_done = True

        # try load from file
        pickle_name = os.path.join(self.checkpoints_dir, '{}.pkl'.format(key))
        if not disable_file_cache and not data_done:
            logger.info('Pickle name: {}'.format(pickle_name))
            if os.path.isfile(pickle_name):
                logger.debug('Loading from file cache')
                with open(pickle_name, 'rb') as f:
                    data = pickle.load(f)
                data_file_cache = True
                data_done = True
                if perfomance_logging:
                    logger.info('Loaded from pickle')

        if not data_done:
            logger.info('Caches do not contain the data. Evaluating...')
            data = self.eval()
            logger.info('Evaluated')
            data_done = True

        # save to file cache
        if not disable_file_cache and not data_file_cache:
            logger.debug('Save to file cache')
            if not os.path.isdir(Cube.checkpoints_dir):
                os.makedirs(Cube.checkpoints_dir)
            with open(pickle_name, 'wb') as f:
                pickle.dump(data, f)
            if perfomance_logging:
                logger.info('Saved to pickle')

        if cleanup:
            if os.path.isfile(pickle_name):
                os.remove(pickle_name)

        # save to inmemory cache
        if not disable_inmemory_cache and not data_inmemory_cache:
            logger.debug('Save to inmemory cache')
            cache.Cache().add(key, data, do_not_copy = self.immutable_args) # Are we able to set do_not_copy here true in any case?
            if perfomance_logging:
                logger.info('Added to in-memory cache')

        return data

    @abc.abstractmethod
    def eval(self):
        '''
            This method should contain meaningful calculations. It have to return dict with result.
        '''
        return
