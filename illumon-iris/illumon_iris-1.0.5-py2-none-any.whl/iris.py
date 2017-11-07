import jpy
import wrapt
import dill
import base64
import inspect


class DbWrapper(wrapt.ObjectProxy):
    def executeQuery(self, query):
        pickled = dill.dumps(query)
        newQuery = iris.PythonRemoteQuery(pickled)
        res = self.__wrapped__.executeQuery(newQuery)
        return self.inflateResult(res)

    def pushClass(self, classToDefine):
        if not inspect.isclass(classToDefine):
            raise TypeError(classToDefine + " is not a class!")
        name = classToDefine.__name__
        pickled = dill.dumps(classToDefine)
        pushQuery = iris.PythonPushClassQuery(name, pickled)
        self.__wrapped__.executeQuery(pushQuery)

    def eval(self, string):
        evalQuery = iris.PythonEvalQuery(string)
        self.__wrapped__.executeQuery(evalQuery)

    def fetch(self, name):
        fetchQuery = iris.PythonEvalQuery(name)
        res = self.__wrapped__.executeQuery(fetchQuery)
        return self.inflateResult(res)

    def inflateResult(self, obj):
        if isinstance(obj, iris.Inflatable):
            return obj.inflate(self.__wrapped__.getProcessorConnection())
        elif isinstance(obj, iris.ExportedTableDescriptorMessage):
            return obj.inflate(self.__wrapped__.getProcessorConnection())
        elif isinstance(obj, iris.PythonRemoteQueryPickledResult):
            return dill.loads(base64.b64decode(obj.getPickled()))
        else:
            return obj


class FigureUnsupported():
    def __init__(self):
        raise Exception("Can not create a plot outside of the console.")


class iris:

    def __init__(self):
        config = jpy.get_type(
            "com.fishlib.configuration.Configuration").getInstance()
        iris.RemoteQueryClient = jpy.get_type(
            "com.illumon.iris.db.tables.remotequery.RemoteQueryClient")
        iris.PythonRemoteQuery = jpy.get_type(
            "com.illumon.iris.db.util.PythonRemoteQuery")
        iris.PythonRemoteQueryPickledResult = jpy.get_type(
            "com.illumon.iris.db.util.PythonRemoteQuery$PickledResult")
        iris.PythonPushClassQuery = jpy.get_type(
            "com.illumon.iris.db.util.PythonPushClassQuery")
        iris.PythonEvalQuery = jpy.get_type(
            "com.illumon.iris.db.util.PythonEvalQuery")
        iris.RemoteDatabase = jpy.get_type(
            "com.illumon.iris.db.tables.remote.RemoteDatabase")
        iris.Inflatable = jpy.get_type(
            "com.illumon.iris.db.tables.remote.Inflatable")
        iris.ExportedTableDescriptorMessage = jpy.get_type(
            "com.illumon.iris.db.tables.remote.ExportedTableDescriptorMessage")
        iris.TableTools = jpy.get_type(
            "com.illumon.iris.db.tables.utils.TableTools")
        iris.QueryScope = jpy.get_type(
            "com.illumon.iris.db.tables.select.QueryScope")
        iris.TableManagementTools = jpy.get_type(
            "com.illumon.iris.db.tables.utils.TableManagementTools")
        iris.DBTimeUtils = jpy.get_type(
            "com.illumon.iris.db.tables.utils.DBTimeUtils")
        iris.Calendars = jpy.get_type("com.illumon.util.calendar.Calendars")
        iris.Calendar = jpy.get_type("com.illumon.util.calendar.Calendar")
        iris.DistinctFormatter = jpy.get_type(
            "com.illumon.iris.db.util.DBColorUtilImpl$DistinctFormatter")
        iris.Figure = FigureUnsupported
        iris.PlottingConvenience = FigureUnsupported

        jpy.type_translations['com.illumon.iris.db.tables.remote.RemoteDatabase'] = iris.wrap_db

    @staticmethod
    def wrap_db(type, obj):
        return DbWrapper(obj)
