from .auth import *
from .workspace import *
from .enrich import *
from .transfer import *
from .store import *
from .serve import *

import unittest


# class EndToEndTestCases(unittest.TestCase):
#     def test_titanic_dataset(self):
#         import os
#         from terrene.auth import EmailPasswordCredentials
#         from terrene.apps import WorkspaceManager
#         from terrene.enrich import PredictiveModelManager
#         from terrene.serve import ModelEndpointManager
#         from terrene.store import StandardWarehouseManager
#         from terrene.transfer import CSVInputManager
#
#         credentials = EmailPasswordCredentials(
#             email=os.environ.get('EMAIL'), password=os.environ.get('PASSWORD'))
#
#         workspace_manager = WorkspaceManager(credentials=credentials)
#         workspace = workspace_manager.create(
#             name="My Workspace", description="A workspace for Terrene's tutorial")
#
#         standard_warehouse_manager = StandardWarehouseManager(
#             workspace=workspace, credentials=credentials)
#         store = standard_warehouse_manager.create(
#             name="default storage", description="default warehouse for my workspace")
#
#         csv_input_manager = CSVInputManager(
#             credentials=credentials, workspace=workspace)
#         with open('tests/dist/train.csv', 'r') as input_file:
#             csv_file_input = csv_input_manager.create(
#                 name="my file", description="training dataset",
#                 file=input_file)
#
#         predictive_model_manager = PredictiveModelManager(
#             credentials=credentials, workspace=workspace)
#
#         model = predictive_model_manager.create(
#             name="my predictive model", description="predictive model",
#             input_variables="Sex, Pclass, Fare, Parch, SibSp, Age, Cabin", output_variables="Survived")
#         model.train(transfer=csv_file_input, epochs=100)
#         # retrain
#         model.train(transfer=csv_file_input, epochs=500)
#
#         model_endpoint_manager = ModelEndpointManager(
#             credentials=credentials, workspace=workspace)
#         endpoint = model_endpoint_manager.create(
#             enrich=model, name="my endpoint", description="used to make predictions",
#             store=store, table="predictions")
#
#         endpoint.predict({
#             "Pclass": 1, "Age": 24, "Sex": "male",
#             "Embarked": "S", "SibSp": 0, "Parch": 0,
#             "Fare": 14.25, "Cabin": "C30"})
#         endpoint.predict({
#             "Pclass": 1, "Age": 24, "Sex": "male",
#             "Embarked": "S", "SibSp": 0, "Parch": 0,
#             "Fare": 14.25, "Cabin": "C30"})
#         endpoint.predict({
#             "Pclass": 1, "Age": 24, "Sex": "male",
#             "Embarked": "S", "SibSp": 0, "Parch": 0,
#             "Fare": 14.25, "Cabin": "C30"})
#
#         print(store.read_rows(table=endpoint.table))
#
#         workspace.delete()
