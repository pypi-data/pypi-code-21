from .api import BaseModelManager, BaseModel


class BaseApp(BaseModel):
    @property
    def connection_credentials(self):
        return self.act(['credentials', 'read'], {'object_id': self.object_id})


class BaseAppManager(BaseModelManager):
    model = BaseApp
    namespace = ['apps']

    def __init__(self, *args, **kwargs):
        super(BaseAppManager, self).__init__(*args, **kwargs)
        self.workspace = kwargs.pop('workspace', None)

        if self.workspace is None:
            raise AssertionError("Missing workspace parameter on initialization")

    def pre_create(self, **params):
        params['workspace'] = self.workspace.object_id
        return params

    def pre_save(self, **params):
        if not isinstance(self.workspace, str):
            params['workspace'] = params['workspace'].object_id


class Workspace(BaseModel):

    predictive_model_manager = None
    model_endpoint_manager = None
    standard_warehouse_manager = None
    sql_database_manager = None
    csv_input_manager = None
    warehouse_query_input_manager = None

    def __init__(self, *args, **kwargs):
        super(Workspace, self).__init__(*args, **kwargs)

        from .enrich import PredictiveModelManager
        from .serve import ModelEndpointManager
        from .store import StandardWarehouseManager, SQLDatabaseManager
        from .transfer import CSVInputManager, WarehouseQueryInputManager

        self.predictive_model_manager = PredictiveModelManager(
            workspace=self, credentials=self.credentials)
        self.model_endpoint_manager = ModelEndpointManager(
            workspace=self, credentials=self.credentials)
        self.standard_warehouse_manager = StandardWarehouseManager(
            workspace=self, credentials=self.credentials)
        self.sql_database_manager = SQLDatabaseManager(
            workspace=self, credentials=self.credentials)
        self.csv_input_manager = CSVInputManager(
            workspace=self, credentials=self.credentials)
        self.warehouse_query_input_manager = WarehouseQueryInputManager(
            workspace=self, credentials=self.credentials)

    def add_owner(self, email):
        return self.act(['owners', 'create'], {
            'object_id': self.object_id, 'user': email})

    def remove_owner(self, email):
        return self.act(['owners', 'partial_update'], {
            'object_id': self.object_id, 'user': email})

    def add_contributor(self, email):
        return self.act(['contributors', 'create'], {
            'object_id': self.object_id, 'user': email})

    def remove_contributor(self, email):
        return self.act(['contributors', 'partial_update'], {
            'object_id': self.object_id, 'user': email})

    def set_payment_method(self, payment_method_object_id):
        return self.act(['set_payment_method'], {
            'object_id': self.object_id, 'method': payment_method_object_id})

    def notify(self, subject, content):
        return self.act(['notify'], {
            'object_id': self.object_id, 'subject': subject, 'content': content})


class WorkspaceManager(BaseModelManager):
    model = Workspace
    namespace = ['workspaces']
