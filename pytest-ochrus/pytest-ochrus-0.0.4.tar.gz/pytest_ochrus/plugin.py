
from __future__ import absolute_import

from ochrus import timestamp, logger 
from ochrus import config as ochrus_config
import time
import getpass
import sys
INI_FILE = None


def pytest_addoption(parser):
    group = parser.getgroup("terminal reporting")
    group.addoption('--session_name', action='store', dest='session_name',
                    metavar='str', default="",
                    help='set name for the running session.')


def pytest_sessionstart(session):
    rootdir = str(session.config.rootdir)
    if session.config.inifile is None:
        print "Can't find pytest configuration file at: '{}'".format(rootdir)
        print "You can read more about it at:\n"+\
              "https://docs.pytest.org/en/latest/customize.html\n"+\
              "Try to change test directory or put 'pytest.ini' file "+\
              "at the root directory of your tests.\n"
        sys.exit(1)
    else:
        global INI_FILE
        INI_FILE = str(session.config.inifile)
    global session_time
    session_time = time.time()


def pytest_report_header(config, startdir):
    rootdir=str(config.rootdir)
    ochrus_conf = ochrus_config.OchrusConfig(rootdir)
    test_db.result_server = ochrus_conf.get_result_server()
    
    """ initialize ochrus main modules """
    ochrus_conf.init()
    
    return ["ochrus logs directory: {}".format(ochrus_conf.get_logs_dir())]
    

def pytest_report_collectionfinish(config, startdir, items):
    test_db.items = items
    test_db.init_session(name=config.option.session_name)#session_name came from the command line
    test_db.init_tests()
    
    response = test_db.post()


def pytest_runtest_logstart(nodeid, location):
    test_db.set_test_status(nodeid, "running")
    test_db.post()

   
def pytest_runtest_logreport(report):
    report.ochrus_links = logger.links.get_links()
    logger.links.del_links()#clean the links, so next section will start from zero
    test_db.add_section(report)
    test_db.post()


def pytest_sessionfinish(session):
    global session_time
    session_time = time.time() - session_time
    
    
        
        
#=============================================================================
#                Class: TestsDB
#=============================================================================    
class TestsDB(object):
    """A Json DB that should hold test results
    
    Attributes:
        items (list):    list of tests as supplied by pytest hooks
        tests (json):    hold any information about the tests
    
    """
    def __init__(self, items=None, result_server=None):
        self.items = items
        self._result_server = result_server
        self.tests = []
    
    #==================================================================
    @property
    def result_server(self):
        return self._result_server
    
    @result_server.setter
    def result_server(self, result_server):
        self._result_server = result_server
        
    #==================================================================
    def post(self):
        response = self.result_server.post("results/update_session/" ,json=self.tests)
        return response
    
    #==================================================================
    def init_session(self, name=None):
        if name is None:
            name = ""
            
        data = {"sessionid": "{}".format(timestamp.get_timestamp()),
                "username":"{}".format(getpass.getuser()),
                "name": "{}".format(name)
                }
        response = self.result_server.post("results/add_session/" , json=data)
        return response
                       
    #==================================================================    
    def init_tests(self):
        """ Initialize the Json DB.
        
        1. create the tests list
        2. update each test with 'nodeid' as getting from pytest 
        3. Update each test with its __DOC__ info
        4. Update each test with 'n/a' status 
        5. All tests must have same sessionID (timestamp)
        6. Create an empty sections list for each test
        """        
        
        for item in self.items:
            self.tests.append({"nodeid": item.nodeid,
                               "doc" : item.function.func_doc,
                               "status": "n/a",
                               "sessionid": "{}".format(timestamp.get_timestamp()),
                               "sections": []})
    
    #==================================================================
    def set_test_status(self, nodeid, status):
        """update test status field."""
        for i in range(0, len(self.tests)):
            if self.tests[i]["nodeid"] == nodeid:
                self.tests[i]["status"] = status
                return
    
    #==================================================================
    def add_section(self, report):
        for i in range(0, len(self.tests)):
            if self.tests[i]["nodeid"] == report.nodeid:
                self.tests[i]["sections"].append(self.py_test_report_to_json(report))
        
    #==================================================================                
    def py_test_report_to_json(self, report):
        
        if hasattr(report, "wasxfail"):
            wasxfial = True
            wasxfail_reason = report.wasxfail
        else:
            wasxfial = False
            wasxfail_reason = ""
                        
        data = {
                "when":            report.when, 
                "stderr":          report.capstderr,
                "stdout":          report.capstdout,
                "asserted":        report.longreprtext,
                "duration":        report.duration,
                "failed":          report.failed,
                "outcome":         report.outcome,
                "passed":          report.passed,
                "skipped":         report.skipped,
                "links":           report.ochrus_links,
                "wasxfail":        wasxfial,
                "wasxfail_reason": wasxfail_reason
                }
        return data

    
test_db = TestsDB() 
session_time = None    

    