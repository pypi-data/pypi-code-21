
from problog.extern import problog_export

@problog_export('+str', '+str', '-str')
def concat_str(arg1, arg2):
    return arg1 + arg2

@problog_export('+str', '+str', '-str')
def call_service (arg1, arg2):
    return arg1 + arg2
