
from mhelper.array_helper import Indexer
from mhelper.batch_lists import BatchList
from mhelper.comment_helper import override, abstract, virtual, sealed, overrides, protected, ignore
from mhelper.disposal_helper import ManagedWith
from mhelper.exception_helper import NotSupportedError, SwitchError, LogicError, ImplementationError, NotFoundError
from mhelper.log_helper import Logger
from mhelper.proxy_helper import SimpleProxy, PropertySetInfo
from mhelper.qt_gui_helper import exceptToGui
from mhelper.reflection_helper import AnnotationInspector
from mhelper.generics_helper import MGeneric, MGenericMeta, MAnnotation, GenericString, NonGenericString, GenericStringMeta, MAnnotationFactory, MAnnotation, ByRef, MAnnotationArgs
from mhelper.special_types import Password, Filename, Dirname, EFileMode, MEnum, MFlags, HReadonly, MOptional, MUnion, FileNameAnnotation
from mhelper.string_helper import FindError



from mhelper import array_helper
from mhelper import batch_lists
from mhelper import bio_helper
from mhelper import comment_helper
from mhelper import component_helper
from mhelper import disposal_helper
from mhelper import event_helper
from mhelper import exception_helper
from mhelper import file_helper
from mhelper import generics_helper
from mhelper import io_helper
from mhelper import log_helper
from mhelper import maths_helper
from mhelper import print_helper
from mhelper import proxy_helper
from mhelper import qt_gui_helper
from mhelper import reflection_helper
from mhelper import string_helper
from mhelper import string_parser

# region "Legacy names - do not use"
import sys as sys_

sys_.modules["mhelper.ArrayHelper"] = array_helper 
sys_.modules["mhelper.BatchList"] = batch_lists 
sys_.modules["mhelper.BioHelper"] = bio_helper 
sys_.modules["mhelper.CommentHelper"] = comment_helper 
sys_.modules["mhelper.components"] = component_helper 
sys_.modules["mhelper.DisposalHelper"] = disposal_helper 
sys_.modules["mhelper.event"] = event_helper 
sys_.modules["mhelper.ExceptionHelper"] = exception_helper 
sys_.modules["mhelper.FileHelper"] = file_helper 
sys_.modules["mhelper.GenericsHelper"] = generics_helper 
sys_.modules["mhelper.IoHelper"] = io_helper 
sys_.modules["mhelper.LogHelper"] = log_helper 
sys_.modules["mhelper.MathsHelper"] = maths_helper 
sys_.modules["mhelper.PrintHelper"] = print_helper 
sys_.modules["mhelper.proxy"] = proxy_helper 
sys_.modules["mhelper.QtGuiHelper"] = qt_gui_helper 
sys_.modules["mhelper.ReflectionHelper"] = reflection_helper 
sys_.modules["mhelper.StringHelper"] = string_helper 
sys_.modules["mhelper.StringParser"] = string_parser 
# endregion
