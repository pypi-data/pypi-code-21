from fizzgun.application.dependencies import (StdoutWriter, IdGenerator, ModuleImporter, RandomGenerator, HttpClient,
                                              FileSystem)


class ServiceContext(object):
    pass


class FilterContext(ServiceContext):
    def __init__(self, stdout_writer: StdoutWriter):
        self._stdout_writer = stdout_writer

    @property
    def stdout_writer(self) -> StdoutWriter:
        return self._stdout_writer


class TransformerContext(ServiceContext):

    def __init__(self,
                 id_generator: IdGenerator,
                 module_importer: ModuleImporter,
                 stdout_writer: StdoutWriter,
                 random_generator: RandomGenerator):
        self._id_generator = id_generator
        self._module_importer = module_importer
        self._stdout_writer = stdout_writer
        self._random_generator = random_generator

    @property
    def module_importer(self) -> ModuleImporter:
        return self._module_importer

    @property
    def id_generator(self) -> IdGenerator:
        return self._id_generator

    @property
    def stdout_writer(self) -> StdoutWriter:
        return self._stdout_writer

    @property
    def random_generator(self) -> RandomGenerator:
        return self._random_generator


class RequestorContext(ServiceContext):

    def __init__(self, http_client: HttpClient):
        self._http_client = http_client

    @property
    def http_client(self) -> HttpClient:
        return self._http_client


class ReporterContext(ServiceContext):

    def __init__(self, file_system: FileSystem):
        self._file_system = file_system

    @property
    def file_system(self) -> FileSystem:
        return self._file_system


class CmdRunFizzgunContext(ServiceContext):
    def __init__(self,
                 file_system: FileSystem=None,
                 http_client: HttpClient=None,
                 id_generator: IdGenerator=None,
                 module_importer: ModuleImporter=None,
                 stdout_writer: StdoutWriter=None,
                 random_generator: RandomGenerator=None):

        self._file_system = file_system or FileSystem()
        self._http_client = http_client or HttpClient()
        self._id_generator = id_generator or IdGenerator()
        self._module_importer = module_importer or ModuleImporter()
        self._stdout_writer = stdout_writer or StdoutWriter()
        self._random_generator = random_generator or RandomGenerator()

    @property
    def file_system(self) -> FileSystem:
        return self._file_system

    def new_service_context(self) -> ServiceContext:
        return ServiceContext()

    def new_filter_context(self) -> FilterContext:
        return FilterContext(self._stdout_writer)

    def new_transformer_context(self) -> TransformerContext:
        return TransformerContext(self._id_generator, self._module_importer,
                                  self._stdout_writer, self._random_generator)

    def new_requestor_context(self) -> RequestorContext:
        return RequestorContext(self._http_client)

    def new_reporter_context(self) -> ReporterContext:
        return ReporterContext(self._file_system)


class CmdBubblesContext(ServiceContext):
    def __init__(self,
                 file_system: FileSystem=None,
                 id_generator: IdGenerator=None,
                 module_importer: ModuleImporter=None,
                 stdout_writer: StdoutWriter=None,
                 random_generator: RandomGenerator=None):

        self._file_system = file_system or FileSystem()
        self._id_generator = id_generator or IdGenerator()
        self._module_importer = module_importer or ModuleImporter()
        self._stdout_writer = stdout_writer or StdoutWriter()
        self._random_generator = random_generator or RandomGenerator()

    @property
    def module_importer(self) -> ModuleImporter:
        return self._module_importer

    @property
    def id_generator(self) -> IdGenerator:
        return self._id_generator

    @property
    def stdout_writer(self) -> StdoutWriter:
        return self._stdout_writer

    @property
    def random_generator(self) -> RandomGenerator:
        return self._random_generator

    @property
    def file_system(self) -> FileSystem:
        return self._file_system


class CmdGenerateConfigContext(ServiceContext):
    def __init__(self,
                 file_system: FileSystem = None,
                 stdout_writer: StdoutWriter = None):
        self._file_system = file_system or FileSystem()
        self._stdout_writer = stdout_writer or StdoutWriter()

    @property
    def file_system(self) -> FileSystem:
        return self._file_system

    @property
    def stdout_writer(self) -> StdoutWriter:
        return self._stdout_writer
