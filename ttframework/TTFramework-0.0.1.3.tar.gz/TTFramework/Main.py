# from . import configer
# from . import PostgresSQLConnection
# from . import bindinger
# from . import ServiceManager
# from japronto import Application
# from sys import argv
# from . import logger
#
# def Main():
#     if len(argv) > 1:
#         if 'v' in argv[1].lower():
#             print('V1.0.0')
#         quit(0)
#     app = Application()
#     ServiceManager.init()
#     isUseDB = str(configer.Database['isUseDB']).lower() == 'true'
#     connection = None
#     if isUseDB:
#         connection = PostgresSQLConnection()
#     bindinger.BindingRouter(app.router,configer,logger,connection)
#     app.run(debug = configer.IsDebug,
#             host = configer.Host,
#             port = configer.Port,
#             worker_num=configer.threadCount)
#     ServiceManager.Stop()
#
# if __name__ == '__main__':
#     if len(argv) > 1:
#         if 'v' in argv[1].lower():
#             print('V1.0.0')
#         quit(0)
#     app = Application()
#     ServiceManager.init()
#     connection = PostgresSQLConnection()
#     bindinger.BindingRouter(app.router,configer,logger,connection)
#     app.run(debug = configer.IsDebug,
#             host = configer.Host,
#             port = configer.Port,
#             worker_num=configer.threadCount)
#     ServiceManager.Stop()
#
#
#
