# In order to make the IRFlowApi Class available globally we need the below input statement
# TODO Determine if we should call irflow_api.py irflow_client.py

try:
    from irflow_client.irflow_client import IRFlowClient
except ImportError:
    from irflow_client import IRFlowClient

