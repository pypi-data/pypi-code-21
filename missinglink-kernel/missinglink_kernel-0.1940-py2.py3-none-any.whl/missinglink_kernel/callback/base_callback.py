# coding=utf-8
import base64
import copy
import datetime
import hashlib
import logging
import os
import platform
import random
import uuid
import warnings
import weakref

import six

from .exceptions import ExperimentStopped
from .settings import EventTypes, HyperParamTypes

#

DISPATCH_INTERVAL = 5
MAX_BATCHES_PER_EPOCH = 1000
SAMPLING_SIZE = 1000
SEND_EPOCH_CANDIDATES = False
FIRST_ITERATION = 1

WEIGHTS_HASH_PREFIX = 'v1_'


class RootLoggerSniffer(object):
    class Handler(logging.Handler):
        def __init__(self, parent):
            super(RootLoggerSniffer.Handler, self).__init__()
            self._parent = parent

        def emit(self, record):
            try:
                self._parent.on_root_log(record)
            except ReferenceError:
                pass

    def __init__(self, log_level):
        self.root_logger = logging.getLogger()
        self.log_level = log_level
        self.handler = None

    def __del__(self):
        self.close()

    def close(self):
        self._deactivate()

    def emit(self, record):
        self.on_root_log(record)

    def on_root_log(self, record):
        pass

    def _activate(self):
        self.handler = self.Handler(weakref.proxy(self))

        self.root_logger.addHandler(self.handler)

    def _deactivate(self):
        self.root_logger.removeHandler(self.handler)


class LoggerWrapper(object):
    class RootLogsMemoryCache(RootLoggerSniffer):
        def __init__(self, log_level):
            from missinglink_kernel.callback import get_global_root_logger_sniffer

            super(LoggerWrapper.RootLogsMemoryCache, self).__init__(log_level)

            if get_global_root_logger_sniffer():
                log_records = get_global_root_logger_sniffer().log_records
                get_global_root_logger_sniffer().stop_capture_global()
            else:
                log_records = []

            self.log_records = log_records[:]

            self._activate()

        def on_root_log(self, record):
            self.log_records.append(record)

        def close(self):
            self.log_records = []
            super(LoggerWrapper.RootLogsMemoryCache, self).close()

    def __init__(self, log_level=logging.DEBUG):
        self.remote_logger = None
        self.logger = self._create_null_logger(log_level)
        self.log_cache = self._create_logs_cache(log_level)

    def activate_if_needed(self):
        if self.remote_logger is not None:
            self.remote_logger.activate_if_needed()

    def close(self):
        if self.remote_logger is not None:
            self.remote_logger.close()

    @classmethod
    def _create_logs_cache(cls, log_level):
        return LoggerWrapper.RootLogsMemoryCache(log_level)

    @classmethod
    def _create_null_logger(cls, log_level):
        logger = logging.getLogger('missinglink')

        return logger

    def exception(self, *args, **kwargs):
        self.logger.error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        self.logger.critical(*args, **kwargs)

    def error(self, *args, **kwargs):
        self.logger.error(*args, **kwargs)

    def warning(self, *args, **kwargs):
        self.logger.warning(*args, **kwargs)

    def info(self, *args, **kwargs):
        self.logger.info(*args, **kwargs)

    def debug(self, *args, **kwargs):
        self.logger.debug(*args, **kwargs)

    def _create_remote_logger(self, session_id, endpoint, remote_log_level, remote_log_filter, terminate_endpoint):
        self.info('remote_logger global level: %s filter: %s', remote_log_level, remote_log_filter)
        self.debug('__create_remote_logger %s %s %s %s %s', session_id, endpoint, remote_log_level, remote_log_filter, terminate_endpoint)

        from .remote_logger import RemoteLoggerHandler

        disable_process_monkey_patch = os.environ.get('ML_DISABLE_PROCESS_MONKEY_PATCH')

        remote_logger = RemoteLoggerHandler(
            session_id, endpoint, remote_log_level, self.log_cache.log_records, remote_log_filter, terminate_endpoint)

        remote_logger.start_remote_script(disable_process_monkey_patch)
        return remote_logger

    def activate_remote_logging(self, session_id, endpoint, remote_log_level, remote_log_filter, terminate_endpoint):
        self.remote_logger = self._create_remote_logger(
            session_id, endpoint, remote_log_level, remote_log_filter, terminate_endpoint)

        self.log_cache.close()


class BaseCallback(object):
    def __init__(self, owner_id, project_token, stopped_callback=None, host=None, framework='none'):
        from missinglink_kernel import get_version
        self.logger = LoggerWrapper()

        stoppable = True

        self.experiment_args = {
            'owner_id': owner_id,
            'project_token': project_token,
            'host': host,
            'stoppable': stoppable
        }

        self.stopped_callback = stopped_callback

        if stopped_callback and not callable(stopped_callback):
            self.logger.warning('stopped_callback is not callable, will be ignored')

        self.properties = {
            'env': {
                'framework': framework,
                'missinglink_version': get_version(),
                'node': platform.node(),
                'platform': platform.platform(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
            },
            'source_tracking': {
                'error': 'disabled'
            },
            'callback_tag': self.generate_tag(),
            'stoppable': stoppable,
        }

        self.post_requests = None

        self.batches_queue = []
        self.points_candidate_indices = {}
        self.iteration = 0
        self._test_iteration = 0
        self.ts_start = 0
        self.epoch_addition = 0
        self.has_ended = False
        self.tests_counter = 0
        self.stopped = False
        self.dispatch_interval = DISPATCH_INTERVAL
        self._has_test_context = False
        self._test_iter = -1
        self._test_iteration_count = 0
        self._test_token = None
        self._class_mapping = None
        self._found_classes = None
        self._latest_metrics = {}

        if SEND_EPOCH_CANDIDATES:
            self.epoch_candidate_indices = {}

    @classmethod
    def _source_tracking_data(cls):
        from .utilities import source_tracking

        try:
            if source_tracking.git_version() is None:
                return {'error': 'git not found'}

            if source_tracking.git_status() is None:
                return {'error': 'no git status'}

            src_data = {
                'branch': source_tracking.git_branch_name(),
                'remote': source_tracking.git_remote_url(),
                'sha_local': source_tracking.git_local_tip(),
                'sha_local_url': source_tracking.git_local_tip_url(),
                'clean': source_tracking.git_is_clean(),
            }

            commit_data = source_tracking.git_get_commit_by_sha(source_tracking.git_local_tip())
            if commit_data is not None:
                src_data.update(commit_data)

        # noinspection PyBroadException
        except Exception as ex:
            logging.exception('git init failed')

            src_data = {'error': str(ex)}

        return src_data

    @property
    def _is_first_iteration(self):
        return self.iteration == 1

    def _update_test_token(self):
        self._test_token = uuid.uuid4().hex

    def close(self):
        if self.post_requests is not None:
            self.post_requests.close()

        if self.logger is not None:
            self.logger.close()

    def set_properties(self, display_name=None, description=None, class_mapping=None, **kwargs):
        if display_name is not None:
            self.properties['display'] = display_name

        if description is not None:
            self.properties['description'] = description

        if class_mapping:
            if isinstance(class_mapping, list):
                class_mapping = {k: v for k, v in enumerate(class_mapping)}

            self._class_mapping = class_mapping

        if len(kwargs) > 0:
            self.set_hyperparams(**kwargs)
            self.logger.warning(
                'passing hyper parameters using the set_properties method is deprecated.'
                'please use the set_hyperparams method instead')

    def set_hyperparams(self, total_epochs=None, batch_size=None, epoch_size=None, max_iterations=None,
                        optimizer_algorithm=None, learning_rate=None, total_batches=None, learning_rate_decay=None,
                        samples_count=None, **kwargs):
        self._set_hyperparams(HyperParamTypes.RUN, total_epochs=total_epochs, batch_size=batch_size,
                              epoch_size=epoch_size, total_batches=total_batches, max_iterations=max_iterations,
                              samples_count=samples_count)

        self._set_hyperparams(HyperParamTypes.OPTIMIZER, algorithm=optimizer_algorithm,
                              learning_rate=learning_rate, learning_rate_decay=learning_rate_decay)

        self._set_hyperparams(HyperParamTypes.CUSTOM, **kwargs)

    def _set_hyperparams(self, hp_type, **kwargs):
        hyperparams = self.get_hyperparams()

        for key, val in kwargs.items():
            if val is None:
                continue

            hyperparams.setdefault(hp_type, {})[key] = val

        self.properties['hyperparams'] = hyperparams

    def get_hyperparams(self):
        return self.properties.get('hyperparams', {})

    def _create_remote_logger_if_needed(self, create_experiment_result):
        if os.environ.get('MISSINGLINKAI_DISABLE_REMOTE_LOGGER') is not None:
            return

        remote_logger = create_experiment_result.get('remote_logger')

        if remote_logger is not None:
            session_id = remote_logger['session_id']
            endpoint = remote_logger['endpoint']
            log_level = remote_logger.get('log_level', logging.INFO)
            log_filter = remote_logger.get('log_filter')
            terminate_endpoint = remote_logger.get('terminate_endpoint')

            self.logger.activate_remote_logging(session_id, endpoint, log_level, log_filter, terminate_endpoint)

    def _call_new_experiment(self, throw_exceptions=None):
        one_hour_seconds = int(datetime.timedelta(hours=1).total_seconds())

        keep_alive_interval = int(os.environ.get('ML_KEEP_ALIVE_INTERVAL', one_hour_seconds))
        res = self.post_requests.create_new_experiment(keep_alive_interval, throw_exceptions=throw_exceptions)

        self._create_remote_logger_if_needed(res)
        if self.post_requests.allow_source_tracking:
            self.properties['source_tracking'] = self._source_tracking_data()

    @property
    def has_experiment(self):
        return self.post_requests is not None

    def new_experiment(self, throw_exceptions=None):
        from .dispatchers.missinglink import post_requests_for_experiment

        self.post_requests = post_requests_for_experiment(**self.experiment_args)

        self._call_new_experiment(throw_exceptions=throw_exceptions)

        self.batches_queue = []
        self.points_candidate_indices = {}
        self.iteration = 0
        self._test_iteration = 0
        self.ts_start = 0
        self.epoch_addition = 0
        self.has_ended = False
        self.stopped = False

        if SEND_EPOCH_CANDIDATES:
            self.epoch_candidate_indices = {}

    @classmethod
    def _image_to_json(cls, img):
        # need to check for string types because we have keep_origin option
        if isinstance(img, six.string_types):
            if six.PY2:
                encoded = base64.b64encode(img)
            else:
                encoded = base64.b64encode(img.encode()).decode()
        else:
            encoded = base64.b64encode(img).decode()
        return encoded

    @classmethod
    def _get_toplevel_metadata(cls, test_token, algo, uri):
        meta = {
            "algo": algo,
            "test_token": test_token,
            "path": uri,
            "prediction_id": uuid.uuid4().hex,
        }
        return meta

    @classmethod
    def _prepare_images_payload(cls, image_objects, keep_origin, uri):
        first_entry = image_objects[0]
        if keep_origin:
            original_image = str(uri)
        else:
            original_image = first_entry["original_image"]
        heatmaps = []
        for i, img_obj in enumerate(image_objects):
            entry = {
                "number": i + 1,  # this should start from 1
                "heatmap_image": cls._image_to_json(img_obj["heatmap_image"]),
                "heatmap_image_key": img_obj["heatmap_image_key"],
                "meta": img_obj["meta"]
            }
            heatmaps.append(entry)

        images = {
            "original_image_key": first_entry["original_image_key"],
            "heatmaps": heatmaps,
            "original_image": cls._image_to_json(original_image)
        }

        return images

    def upload_images(self, model_hash, images, meta, description=None):
        from .dispatchers.missinglink import get_post_requests

        post_requests = get_post_requests(
            self.experiment_args['owner_id'], self.experiment_args['project_token'], host=self.experiment_args['host'])

        data = {
            'model_hash': model_hash,
            'images': images,
            'meta': meta,
            'description': description
        }

        post_requests.send_images(data)

    def send_chart(self, name, x_values, y_values, x_legend=None, y_legends=None, scope='test', type='line', experiment_id=None, model_weights_hash=None):
        """
        Send experiment external chart to an experiment. The experiment can be identified by its ID (experiment_id) or by model_weights_hash in the experiment. Exactly one of experiment_id or model_weights_hash must be provided
        :param name: The name of the chart. The name is used in order to identify the chart against different experiments and through the same experiment.
        :param x_values: Array of `m` Strings / Ints / Floats  -  X axis points.
        :param y_values: Array/Matrix of `m` Y axis points. Can be either array `m` of Integers/Floats or a matrix (having `n` Ints/Floats each), a full matrix describing the values of every y chart in every data point.
        :param x_legend: String, Legend for the X axis
        :param y_legends: String/Array of `n` Strings legend of the Y axis chart(s)
        :param scope: Scope type. Can be 'test', 'validation' or 'train', defaults to 'test'
        :param type: Chart type, currently only 'line' is supported.
        :param experiment_id: The id of the target experiment.
        :param model_weights_hash: a hexadecimal sha1 hash of the model's weights.
        :return:
        """
        from .dispatchers.missinglink import post_requests_for_experiment
        self.logger.activate_if_needed()

        post_r = post_requests_for_experiment(**self.experiment_args)
        post_r.send_chart(name, x_values, y_values, x_legend, y_legends, scope, type, experiment_id, model_weights_hash, throw_exceptions=True)

    @property
    def experiment_id(self):
        if self.has_experiment:
            return self.post_requests.experiment_id
        self.logger.warning('experiment_id is only available after train_begin is called.')
        return None

    def batch_command(self, event, data, flush=False):
        self.logger.activate_if_needed()

        if self.post_requests is None:
            self.logger.warning(
                'missinglink callback cannot send data before train_begin is called.\n'
                'please access the instruction page for proper use')
            return

        if self.stopped:
            self.logger.debug('experiment stopped, discarding data')
            return

        command = (event, data, datetime.datetime.utcnow().isoformat())

        if event == EventTypes.BATCH_END:
            if SEND_EPOCH_CANDIDATES and data.get('epoch_candidate') in self.epoch_candidate_indices:
                i = self.epoch_candidate_indices[data['epoch_candidate']]
            elif data.get('points_candidate') in self.points_candidate_indices:
                i = self.points_candidate_indices[data['points_candidate']]
            else:
                i = len(self.batches_queue)
                self.batches_queue.append(None)

            self.batches_queue[i] = command

            if SEND_EPOCH_CANDIDATES and 'epoch_candidate' in data:
                self.epoch_candidate_indices[data['epoch_candidate']] = i

            if 'points_candidate' in data:
                self.points_candidate_indices[data['points_candidate']] = i
        else:
            self.batches_queue.append(command)

        if SEND_EPOCH_CANDIDATES and event == EventTypes.EPOCH_END:
            self.epoch_candidate_indices = {}

        if len(self.batches_queue) == 1:
            self.ts_start = datetime.datetime.utcnow()

        ts_end = datetime.datetime.utcnow()
        queue_duration = ts_end - self.ts_start

        if queue_duration.total_seconds() > self.dispatch_interval or flush:
            response = self.post_requests.send_commands(self.batches_queue)
            self.batches_queue = []
            self.epoch_candidate_indices = {}
            self.points_candidate_indices = {}

            if response.get('stopped'):
                if self.stopped_callback and callable(self.stopped_callback):
                    self.stopped_callback()
                    self.stopped = True
                else:
                    raise ExperimentStopped('Experiment was stopped from web interface.')

    def train_begin(self, params=None, throw_exceptions=None, **kwargs):
        self.logger.info('train begin params: %s, %s', params, kwargs)

        params = params or {}
        self.new_experiment(throw_exceptions=throw_exceptions)
        data = copy.copy(self.properties)
        data['params'] = params
        data.update(kwargs)
        self.batch_command(EventTypes.TRAIN_BEGIN, data, flush=True)

    def _train_end(self, **kwargs):
        if not self.has_ended:
            self.logger.info('train end %s', kwargs)

            # Use `iterations` if it is passed. As we move forward, we want to reduce the
            # responsibility of this class. The experiment's state should be managed by another class
            # e.g. Experiment in TensorFlowProject.
            iterations = int(kwargs.get('iterations', self.iteration))

            data = {'iterations': iterations}
            data.update(kwargs)
            self.batch_command(EventTypes.TRAIN_END, data, flush=True)
            self.has_ended = True
            self._latest_metrics = {}

    def train_end(self, **kwargs):
        warnings.warn("This method is deprecated", DeprecationWarning)
        self._train_end(**kwargs)

    # noinspection PyUnusedLocal
    def epoch_begin(self, epoch, **kwargs):
        epoch = int(epoch)

        if epoch == 0:
            self.epoch_addition = 1

    def epoch_end(self, epoch, metric_data=None, **kwargs):
        self.logger.info('epoch %s ended %s', epoch, metric_data)

        epoch = int(epoch)

        if not metric_data:
            return

        data = {
            'epoch': epoch + self.epoch_addition,
            'results': metric_data,
        }

        data.update(kwargs)
        self.batch_command(EventTypes.EPOCH_END, data, flush=data['epoch'] == 1)

    def batch_begin(self, batch, epoch, **kwargs):
        self.iteration += 1

    def batch_end(self, batch, epoch, metric_data, **kwargs):
        batch = int(batch)
        epoch = int(epoch)
        is_test = kwargs.get('is_test', False)

        # Use `iteration` if it is passed into `batch_end`. As we move forward, we want to reduce the
        # responsibility of this class. The experiment's state should be managed by another class
        # e.g. Experiment in TensorFlowProject.
        iteration = int(kwargs.get('iteration', self.iteration))

        data = {
            'batch': batch,
            'epoch': epoch,
            'iteration': iteration,
            'metricData': metric_data,
        }
        self._latest_metrics = metric_data

        if is_test:
            self._test_iteration += 1

        starting_offset = SAMPLING_SIZE if is_test else 0
        iteration = self._test_iteration if is_test else iteration

        # Filter batch
        if iteration <= SAMPLING_SIZE:
            if SEND_EPOCH_CANDIDATES:
                data['epoch_candidate'] = batch

            data['points_candidate'] = starting_offset + iteration
        else:
            # Conserve initial location
            points_candidate = random.randint(FIRST_ITERATION + 1, iteration)
            if points_candidate <= SAMPLING_SIZE:
                data['points_candidate'] = starting_offset + points_candidate

            if SEND_EPOCH_CANDIDATES:
                if batch < MAX_BATCHES_PER_EPOCH:
                    data['epoch_candidate'] = batch
                else:
                    epoch_candidate = random.randint(0, batch - 1)
                    if epoch_candidate < MAX_BATCHES_PER_EPOCH:
                        data['epoch_candidate'] = epoch_candidate

        send = 'points_candidate' in data or 'epoch_candidate' in data

        if send:
            data.update(kwargs)
            self.batch_command(EventTypes.BATCH_END, data, flush=iteration == 1)

    def _test_begin(self, test_iter, weights_hash):
        if self._has_test_context:
            self.logger.warning('test begin called twice without calling end')
            return

        self._test_iteration_count = 0
        self._test_samples_count = 0
        self._has_test_context = True
        self._test_iter = test_iter
        self._update_test_token()
        self._found_classes = set()

        data = {
            'test_token': self._test_token,
            'test_data_size': self._test_iter,
        }

        if weights_hash is not None:
            data['weights_hash'] = weights_hash

        self.batch_command(EventTypes.TEST_BEGIN, data, flush=True)

    def _send_test_iteration_end(self, expected, predictions, probabilities, partial_class_mapping, is_finished, **kwargs):
        data = {
            'test_token': self._test_token,
            'predicted': predictions,
            'expected': expected,
            'probabilities': probabilities,
            'iteration': self._test_iteration_count,
            'partial_class_mapping': partial_class_mapping,
            'partial_total_classes': len(self._found_classes)
        }

        data.update(kwargs)
        event = EventTypes.TEST_END if is_finished else EventTypes.TEST_ITERATION_END
        flush = is_finished
        self.batch_command(event, data, flush=flush)

    def _test_iteration_end(self, expected, predictions, probabilities, **kwargs):
        self._test_iteration_count += 1

        is_finished = self._test_iteration_count >= self._test_iter

        partial_class_mapping = {}

        unique_ids = list(set(expected) | set(predictions))
        for class_id in unique_ids:
            if class_id not in self._found_classes:
                self._found_classes.add(class_id)
                if self._class_mapping:
                    if class_id in self._class_mapping:
                        partial_class_mapping[class_id] = self._class_mapping[class_id]
                    else:
                        self.logger.warning('no class mapping for class id %d', class_id)

        self._send_test_iteration_end(expected, predictions, probabilities, partial_class_mapping, is_finished=is_finished, **kwargs)

        if is_finished:
            self._test_end()

    def _test_end(self):
        self._has_test_context = False
        self._test_iteration_count = 0
        self._test_token = None

    @staticmethod
    def generate_tag(length=4):
        chars = '1234567890_-abcdefghijklmnopqrstuvwxyz'
        tag = ''
        for _ in range(length):
            tag += random.choice(chars)

        return tag

    def _extract_hyperparams(self, hp_type, obj, object_type_to_attrs, attr_to_hyperparam, object_type=None):
        if isinstance(obj, dict):
            def has_attr(name):
                return name in obj

            def get_attr(name):
                return obj.get(name)
        else:
            def has_attr(name):
                return hasattr(obj, name)

            def get_attr(name):
                return getattr(obj, name)

        object_type = object_type or obj.__class__.__name__
        hyperparams = {}
        attrs = object_type_to_attrs.get(object_type, [])

        for param_name in attrs:
            if has_attr(param_name):
                value = self.variable_to_value(get_attr(param_name))
                param_name = attr_to_hyperparam.get(param_name, param_name)
                hyperparams[param_name] = value
        self._set_hyperparams(hp_type, **hyperparams)

    @classmethod
    def variable_to_value(cls, variable):
        return variable

    @classmethod
    def _hash(cls, value):
        str_repr = str(value).encode("utf-8")
        h = hashlib.sha1(str_repr).hexdigest()
        return h
