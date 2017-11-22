"""Management of Python Classes.

This module is responsible of management of the Class Objects. A central Python
Metaclass is responsible of Class (not object) instantiation.

Note that this managers also includes most serialization/deserialization code
related to classes and function call parameters.
"""
from dataclay import runtime, RuntimeType
from dataclay.core.exceptions import ImproperlyConfigured
from dataclay.core.management import (MetaClass, Operation, Type, UserType,
                                      PythonImplementation, Property, PythonClassInfo)
from dataclay.core.management.classmgr import STATIC_ATTRIBUTE_FOR_EXTERNAL_INIT
from dataclay.core.primitives import *
from dataclay.management import load_babel_data
from dataclay.managers.metaclass_containers import load_metaclass
from dataclay.managers.objects.deserialization import deserialize_association
from dataclay.managers.objects.serialization import serialize_association
from decorator import getfullargspec
import inspect
from logging import getLogger, DEBUG
from operator import attrgetter
import re
import uuid

from .extradata import DataClayInstanceExtraData, DataClayClassExtraData
from .methods import dclayMethod, dclayEmptyMethod
from .properties import DynamicProperty, ReplicatedDynamicProperty, PreprocessedProperty, DCLAY_PROPERTY_PREFIX

# Publicly show the dataClay method decorators
__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2016 Barcelona Supercomputing Center (BSC-CNS)'

logger = getLogger(__name__)

# For efficiency purposes compile the folowing regular expressions:
# (they return a tuple of two elements)
re_property = re.compile(r"(?:^\s*@dclayReplication\s*\((before|after)Update='([^']+)'(?:,\s(before|after)Update='([^']+)')?\)\n)?^\s*@ClassField\s+([\w.]+)[ \t]+([\w.\[\]<> ,]+)", re.MULTILINE)
re_import = re.compile(r"^\s*@dclayImport(?P<from_mode>From)?\s+(?P<import>.+)$", re.MULTILINE)


# Populated by ExecutionGateway, can be freely accessed and cleared (see MetaClassFactory)
loaded_classes = set()


class ExecutionGateway(type):
    """Python' Metaclass dataClay "magic"

    This type-derived Metaclass is used by DataClayObject to control the class
    instantiation and also object instances.
    """
    def __new__(mcs, classname, bases, dct):
        if classname == 'DataClayObject':
            # Trivial implementation, do nothing
            return super(ExecutionGateway, mcs).__new__(mcs, classname, bases, dct)
        # at this point, a real dataClay class is on-the-go

        module_name = dct['__module__']
        full_name = "%s.%s" % (module_name, classname)
        logger.verbose('Proceeding to prepare the class `%s` from the ExecutionGateway',
                       full_name)
        logger.debug("The RuntimeType is: %s",
                     "client" if runtime.current_type == RuntimeType.client else "not client")

        dc_ced = DataClayClassExtraData(
            full_name=full_name,
            classname=classname,
            namespace=module_name.split('.', 1)[0],
            properties=dict(),
            imports=list(),
        )

        if runtime.current_type == RuntimeType.client:
            class_stubinfo = None

            try:
                all_classes = load_babel_data()

                for c in all_classes:
                    if "%s.%s" % (c.namespace, c.className) == full_name:
                        class_stubinfo = c
                        break
            except ImproperlyConfigured:
                pass

            if class_stubinfo is None:
                # Either ImproperlyConfigured (not initialized) or class not found:
                # assuming non-registered class

                # Prepare properties from the docstring
                doc = dct.get('__doc__', "")  # If no documentation, consider an empty string
                property_pos = 0

                for m in re_property.finditer(doc):
                    # declaration in the form [ 'before|after', 'method', 'before|after', 'method', 'name', 'type' ]
                    declaration = m.groups()
                    prop_name = declaration[-2]
                    prop_type = declaration[-1]

                    beforeUpdate = declaration [1] if declaration [0] == 'before' else declaration [3] if declaration [2] == 'before' else None

                    afterUpdate = declaration [1] if declaration [0] == 'after' else declaration [3] if declaration [2] == 'after' else None

                    current_type = Type.build_from_docstring(prop_type)

                    logger.trace("Property `%s` (with type signature `%s`) ready to go",
                                 prop_name, current_type.signature)

                    dc_ced.properties[prop_name] = PreprocessedProperty(name=prop_name, position=property_pos, type=current_type, beforeUpdate=beforeUpdate, afterUpdate=afterUpdate)

                    # Keep the position tracking (required for other languages compatibility)
                    property_pos += 1

                    # Prepare the `property` magic --this one without getter and setter ids
                    dct[prop_name] = DynamicProperty(prop_name)

                for m in re_import.finditer(doc):
                    gd = m.groupdict()

                    if gd["from_mode"]:
                        import_str = "from %s\n" % gd["import"]
                    else:
                        import_str = "import %s\n" % gd["import"]

                    dc_ced.imports.append(import_str)

            else:
                logger.debug("Loading a class with babel_data information")

                dc_ced.class_id = class_stubinfo.classID
                dc_ced.stub_info = class_stubinfo

                # WIP WORK IN PROGRESS (because all that is for the ancient StubInfo, not the new one)

                # Prepare the `property` magic --in addition to prepare the properties dictionary too
                for i, prop_name in enumerate(dc_ced.stub_info.propertyListWithNulls):

                    if prop_name is None:
                        continue

                    prop_info = class_stubinfo.properties[prop_name]

                    if prop_info.beforeUpdate is not None or prop_info.afterUpdate is not None:
                        dct[prop_name] = ReplicatedDynamicProperty(prop_name, prop_info.beforeUpdate, prop_info.afterUpdate)
                    else:
                        dct[prop_name] = DynamicProperty(prop_name)
                    dc_ced.properties[prop_name] = PreprocessedProperty(name=prop_name, position=i, type=prop_info.propertyType, beforeUpdate=prop_info.beforeUpdate, afterUpdate=prop_info.afterUpdate)

        elif runtime.current_type == RuntimeType.exe_env:
            logger.verbose("Seems that we are a DataService, proceeding to load class %s",
                           dc_ced.full_name)
            namespace_in_classname, dclay_classname = dc_ced.full_name.split(".", 1)
            assert namespace_in_classname == dc_ced.namespace
            mc = load_metaclass(dc_ced.namespace, dclay_classname)
            dc_ced.metaclass_container = mc
            dc_ced.class_id = mc.dataClayID

            # Prepare the `property` magic --in addition to prepare the properties dictionary too
            for p in dc_ced.metaclass_container.properties:
                
                dct[p.name] = DynamicProperty(p.name)
                dc_ced.properties[p.name] = PreprocessedProperty(
                    name=p.name, position=p.position, type=p.type, beforeUpdate=p.beforeUpdate, afterUpdate=p.afterUpdate)
        else:
            raise RuntimeError("Could not recognize RuntimeType %s", runtime.current_type)

        dct["_dclay_class_extradata"] = dc_ced

        klass = super(ExecutionGateway, mcs).__new__(mcs, classname, bases, dct)
        loaded_classes.add(klass)

        return klass

    def __init__(cls, name, bases, dct):
        logger.verbose("Initialization of class %s in module %s",
                    name, cls.__module__)

        super(ExecutionGateway, cls).__init__(name, bases, dct)

    def __call__(cls, *args, **kwargs):
        if getattr(cls, STATIC_ATTRIBUTE_FOR_EXTERNAL_INIT, False):
            logger.debug("New Persistent Instance (remote init) of class `%s`", cls.__name__)
            return runtime.new_persistent_instance_aux(cls, args, kwargs)
        else:
            ret = object.__new__(cls)  # this differs the __call__ method
            logger.debug("New regular dataClay instance of class `%s`", cls.__name__)
            cls._populate_internal_fields(ret)
            cls.__init__(ret, *args, **kwargs)

            # FIXME this should read "make_volatile" because the object is not "persistent"
            if runtime.current_type == RuntimeType.exe_env:
                logger.verbose("Making the recently created object persistent (in fact, it should be volatile for now)")
                runtime.make_persistent(ret, None, None, True)
            return ret

    def new_dataclay_instance(cls, **kwargs):
        """Return a new instance, without calling to the class methods."""
        logger.debug("New dataClay instance (without __call__) of class `%s`", cls.__name__)
        ret = object.__new__(cls)  # this differs the __call__ method
        cls._populate_internal_fields(ret, **kwargs)
        return ret

    @staticmethod
    def _populate_internal_fields(instance, **kwargs):
        assert isinstance(instance, DataClayObject), \
            "Population of fields is assumed to be done onto a DataClayObject"

        logger.debug("Populating internal fields for the class. Provided kwargs: %s", kwargs)

        # Mix default values with the provided ones through kwargs
        fields = {
            "persistent_flag": False,
            "proxy_flag": False,
            "object_id": uuid.uuid4(),
            "dataset_id": None,
            "loaded_flag": True,
        }
        fields.update(kwargs)

        # Store some extradata in the class
        instance_dict = object.__getattribute__(instance, "__dict__")
        instance_dict["_dclay_instance_extradata"] = DataClayInstanceExtraData(**fields)
        return instance

    def _prepare_metaclass(cls, namespace, responsible_account):
        """Build a dataClay "MetaClass" for this class.

        :param str namespace: The namespace for this class' MetaClass.
        :param str responsible_account: Responsible account's username.
        :return: A MetaClass Container.
        """
        try:
            class_extradata = cls._dclay_class_extradata
        except AttributeError:
            raise ValueError("MetaClass can only be prepared for correctly initialized DataClay Classes")

        logger.verbose("Preparing MetaClass container for class %s (%s)",
                    class_extradata.classname, class_extradata.full_name)

        # The thing we are being asked (this method will keep populating it)
        current_python_info = PythonClassInfo(
            imports=list()
        )
        current_class = MetaClass(
            namespace=namespace,
            name=class_extradata.full_name,
            parentType=None,
            operations=list(),
            properties=list(),
            isAbstract=False,
            languageDepInfos={'LANG_PYTHON': current_python_info}
        )

        ####################################################################
        # OPERATIONS
        ####################################################################
        for name, dataclay_func in inspect.getmembers(cls, inspect.ismethod):
            # Consider only functions with _dclay_method
            if not getattr(dataclay_func, "_dclay_method", False):
                logger.verbose("Method `%s` doesn't have attribute `_dclay_method`",
                             dataclay_func)
                continue

            original_func = dataclay_func._dclay_entrypoint
            logger.debug("MetaClass container will contain method `%s`, preparing", name)

            # Skeleton for the operation
            current_operation = Operation(
                namespace=namespace,
                className=class_extradata.full_name,
                descriptor=name,  # FIXME this is *not* correct at all!
                signature=name,  # FIXME this is *not* correct at all!
                name=name,
                nameAndDescriptor=name,  # FIXME this is *not* correct at all!
                params=dict(),
                paramOrder=list(),
                returnType=Type.build_from_type(dataclay_func._dclay_ret),
                implementations=list(),
                isAbstract=False,
                isStaticConstructor=False)

            # Start with parameters
            #########################

            # The actual order should be retrieved from the signature
            signature = getfullargspec(original_func)
            if signature.varargs or signature.varkw:
                raise NotImplementedError("No support for varargs or varkw yet")

            current_operation.paramOrder[:] = signature.args[1:]  # hop over 'self'
            current_operation.params.update({k: Type.build_from_type(v)
                                             for k, v in dataclay_func._dclay_args.iteritems()})

            assert len(current_operation.paramOrder) == len(current_operation.params), \
                "All the arguments are expected to be annotated, " \
                "there is some error in %s::%s|%s" \
                % (namespace, class_extradata.full_name, name)

            # Follow by implementation
            ############################

            current_implementation = PythonImplementation(
                responsibleAccountName=responsible_account,
                namespace=namespace,
                className=class_extradata.full_name,
                opNameAndDescriptor=name,  # FIXME
                position=0,
                includes=list(),
                accessedProperties=list(),
                accessedImplementations=list(),
                requiredQuantitativeFeatures=dict(),
                requiredQualitativeFeatures=dict(),
                code=inspect.getsource(dataclay_func._dclay_entrypoint))

            current_operation.implementations.append(current_implementation)

            # Finally, add the built operation container into the class
            #############################################################
            current_class.operations.append(current_operation)

        ####################################################################
        # PROPERTIES
        ####################################################################
        for n, p in class_extradata.properties.iteritems():
            current_property = Property(
                namespace=namespace,
                className=class_extradata.full_name,
                name=n,
                position=p.position,
                type=p.type,
                beforeUpdate=p.beforeUpdate,
                afterUpdate=p.afterUpdate)

            current_class.properties.append(current_property)

        ####################################################################
        # IMPORTS
        ####################################################################
        current_python_info.imports.extend(class_extradata.imports)

        return current_class


class DataClayObject(object):
    __metaclass__ = ExecutionGateway

    _dclay_instance_extradata = None

    def get_location(self):
        """Return a single (random) location of this object."""
        return runtime.get_execution_environment_by_oid(self._dclay_instance_extradata.object_id)

    def get_all_locations(self):
        """Return all the locations of this object."""
        return runtime.get_all_execution_environments_by_oid(self._dclay_instance_extradata.object_id)

    def make_persistent(self, alias=None, backend_id=None, recursive=True):
        runtime.make_persistent(self, alias=alias, backend_id=backend_id, recursive=recursive)

    def getID(self):
        """Return the string representation of the persistent object.

        dataClay specific implementation: The objects are internally represented
        through ObjectID, which are UUID. This method returns the UUID as a
        string.
        """
        return str(self._dclay_instance_extradata.object_id)

    def get_object_by_id(self, object_id):
        return runtime.get_object_by_id(self, object_id)

    @classmethod
    def get_by_alias(cls, alias):
        return runtime.get_by_alias(cls, alias)

    @classmethod
    def delete_alias(cls, alias):
        return runtime.delete_alias(cls, alias)

    def is_persistent(self):
        return self._dclay_instance_extradata.persistent_flag

    def is_proxy(self):
        return self._dclay_instance_extradata.proxy_flag

    def serialize(self, io_file, ignore_user_types, iface_bitmaps,
                  cur_serialized_objs, pending_objs,
                  cur_serialized_python_objs):

        # Put slow debugging info inside here:
        if logger.isEnabledFor(DEBUG):
            import inspect
            klass = self.__class__
            logger.debug("Serializing instance %r from class %s",
                         self, klass.__name__)
            logger.debug("The previous class is from module %s, in file %s",
                         klass.__module__, inspect.getfile(klass))
            logger.debug("The class extradata is:\n%s", klass._dclay_class_extradata)
            assert klass._dclay_class_extradata == self._dclay_class_extradata

        if hasattr(self, "__dclay_serialize__"):
            # The object has a user-defined serialization method.
            dco_extradata = self._dclay_instance_extradata
            last_flag = dco_extradata.loaded_flag
            dco_extradata.loaded_flag = True

            # Use pickle to the result of the serialization
            import cPickle as pickle
            state = pickle.dumps(self.__dclay_serialize__())

            # Leave the previous value, probably False
            dco_extradata.loaded_flag = last_flag

            Str(mode="binary").write(io_file, state)

        else:
            # Regular dataClay provided serialization
            # Get the list of properties, making sure it is sorted
            properties = sorted(
                self._dclay_class_extradata.properties.values(),
                key=attrgetter('position'))

            logger.verbose("Serializing list of properties: %s", properties)

            for p in properties:
                try:
                    value = object.__getattribute__(self, "%s%s" % (DCLAY_PROPERTY_PREFIX, p.name))
                except AttributeError:
                    value = None

                if value is None:
                    Bool().write(io_file, False)
                else:
                    Bool().write(io_file, True)
                    if isinstance(p.type, UserType):
                        serialize_association(io_file, value, cur_serialized_objs, pending_objs)
                        PyTypeWildcard('unicode', True).write(io_file, value._dclay_instance_extradata.object_id)
                    else:
                        PyTypeWildcard(p.type.signature).write(io_file, value)

    def deserialize(self, io_file, iface_bitmaps,
                    obj_map, metadata,
                    cur_deserialized_python_objs):
        # It is reciprocal to serialize

        # Put slow debugging info inside here:
        if logger.isEnabledFor(DEBUG):
            klass = self.__class__
            logger.debug("Deserializing instance %r from class %s",
                         self, klass.__name__)
            logger.debug("The previous class is from module %s, in file %s",
                         klass.__module__, inspect.getfile(klass))
            logger.debug("The class extradata is:\n%s", klass._dclay_class_extradata)
            assert klass._dclay_class_extradata == self._dclay_class_extradata

        # This may be due to race conditions. It may need to do some extra locking
        if self._dclay_instance_extradata.loaded_flag:
            return
        else:
            self._dclay_instance_extradata.loaded_flag = True

        if hasattr(self, "__dclay_deserialize__"):
            # The object has a user-defined deserialization method.

            # Use pickle, and use that method instead
            import cPickle as pickle
            state = pickle.loads(Str(mode="binary").read(io_file))
            self.__dclay_deserialize__(state)

        else:
            # Regular dataClay provided deserialization

            # Start by getting the properties
            properties = sorted(
                self._dclay_class_extradata.properties.values(),
                key=attrgetter('position'))

            logger.verbose("Deserializing list of properties: %s", properties)

            for p in properties:
                not_null = Bool().read(io_file)

                if not_null:
                    if isinstance(p.type, UserType):
                        try:
                            deserialize_association(io_file, iface_bitmaps, obj_map, metadata, cur_deserialized_python_objs)
                        except KeyError as e:
                            print e

                        obj_id = PyTypeWildcard('unicode', True).read(io_file)
                        if obj_id is not None:
                            value = runtime.get_object_by_id(obj_id)
                        else:
                            value = None
                    else:
                        value = PyTypeWildcard(p.type.signature).read(io_file)
                else:
                    value = None

                object.__setattr__(self, "%s%s" % (DCLAY_PROPERTY_PREFIX, p.name), value)

    def __getstate__(self):
        """Support for pickle protocol"""
        logger.debug("Proceeding to getstate on DataClayObject")
        dco_extradata = self._dclay_instance_extradata

        if not dco_extradata.persistent_flag:
            # FIXME: Support for volatile means that this is not acceptable.
            # FIXME: But right now, this is a sensible default (specially for Tiramisu)
            logger.warning("Trying to pickle a non-persistent object. Unsupported. Making it persistent")
            self.make_persistent()

        state = (dco_extradata.dataset_id.bytes if dco_extradata.dataset_id else None,
                 dco_extradata.object_id.bytes if dco_extradata.object_id else None,
                 dco_extradata.execenv_id.bytes if dco_extradata.execenv_id else None)
        logger.debug("State pickled: %s", state)
        return state

    def __setstate__(self, state):
        """Support for pickle protocol"""
        logger.debug("Proceeding to setstate on DataClayObject with state: %s", state)
        dataset_id, object_id, execenv_id = map(
            lambda x: uuid.UUID(bytes=x) if x else None, state)
        self._dclay_instance_extradata = DataClayInstanceExtraData(
            persistent_flag=True,
            loaded_flag=False,
            proxy_flag=True,
            dataset_id=dataset_id,
            execenv_id=execenv_id,
            object_id=object_id,
        )

    def __del__(self):
        """Before being garbage collected, ensure sync with database."""
        dco_extradata = self._dclay_instance_extradata
        if not dco_extradata.persistent_flag or \
                not dco_extradata.loaded_flag:
            logger.debug("Doing nothing on __del__ for object %r: persistent_flag: %s, loaded_flag: %s" % 
                         (self, dco_extradata.persistent_flag, dco_extradata.loaded_flag))
            return

        logger.debug("__del__ called on persistent and loaded object: %s",
                     dco_extradata.object_id)
        if runtime.current_type != RuntimeType.exe_env:
            raise RuntimeError("Persistent Objects which are loaded should only "
                               "be found in ExecutionEnvironment, not here")

        # Persistent object with local data... proceed to store it
        logger.info("Storing object before memory cleanup")
        runtime.store_object(self)

    def __repr__(self):
        dco_extradata = self._dclay_instance_extradata
        dcc_extradata = self._dclay_class_extradata

        if dco_extradata.persistent_flag:
            return "<%s (ClassID=%s) instance with ObjectID=%s>" % \
                   (dcc_extradata.classname, dcc_extradata.class_id, dco_extradata.object_id)
        else:
            return "<%s (ClassID=%s) volatile instance>" % \
                   (dcc_extradata.classname, dcc_extradata.class_id)

    def __eq__(self, other):
        if not isinstance(other, DataClayObject):
            return False

        self_extradata = self._dclay_instance_extradata
        other_extradata = other._dclay_instance_extradata

        if not self_extradata.persistent_flag or not other_extradata.persistent_flag:
            return False

        return self_extradata.object_id and other_extradata.object_id \
            and self_extradata.object_id == other_extradata.object_id
