# -*- coding: utf-8 -*-
import commands
import logging
import os
import subprocess
import time
import threading
import shutit

import agent.util.file as file_tool
from agent.consts import TestRunStatus
from agent.exc import WorkerException
from agent.qualityplatform import server_api
from base import BaseWorker

logger = logging.getLogger(__name__)

duration_time = 30 * 60  # 测试 30
# duration_time = 100  # 测试 10s
ios_monkey_dir = file_tool.make_worker_dir(os.getcwd() + '/agent/iosMonkey/')
# 是否需要卸载重装
needuninstall = True


class iosmonkey(BaseWorker):
    def __init__(self, data):
        super(iosmonkey, self).__init__(data)
        self.notice_account = self.data.get('notice_account')
        self.udid = self.data.get('device_id')
        self.grand_id = self.data.get('grand_id')
        self.platform = self.data.get('platform')
        self.packtype = self.data.get('packtype')
        self.app_version = self.data.get('app_version')
        self.run_id = self.data.get('run_id')
        self.case_id = self.data.get('case_id')
        self.throttle = self.data.get('throttle')
        self.pct_touch = self.data.get('pct_touch')
        self.pct_motion = self.data.get('pct_motion')
        self.pct_syskeys = self.data.get('pct_syskeys')
        self.app = server_api.get_latest_app(self.grand_id, self.platform, self.packtype, self.app_version)
        self.port = self.data.get('port')
        self.wkdir = ios_monkey_dir + str(self.task_id)
        self.install_dir = self.wkdir + '/install_dir/'
        self.crash_dir = self.wkdir + "/crashReoprt/"
        self.search_key = 'ele'
        # XCTestWD 所在位置
        self.wdadir = ios_monkey_dir + "/Fastmonkey/XCTestWD-master/XCTestWD/XCTestWD.xcodeproj"
        self.bundleId = 'me.ele.ios.eleme'
        self.duration_time = duration_time

    def start_worker(self):
        file_tool.make_worker_dir(self.crash_dir)
        file_tool.make_worker_dir(self.install_dir)

        print "beigin monkey"

        self.get_deviceName()

        # self.pull_git()
        # # 卸载重装
        # if needuninstall:
        #     # 下载
        #     self.down_app()
        #     self.uninstall_app()
        #     self.install_app()
        self.start_WDATest()
        self.start_runmonkey()
        self.deal_report()
        self.complete()

    def stop_monkey(self):
        self.session.send(echo=True, check_exit=False)

    def pull_git(self):
        print "git pull"
        print self.wdadir
        if not os.path.exists(self.wdadir):
            raise WorkerException(self.wdadir + ' not exist')
            return
        git_cmd = "cd %s && git pull" % (ios_monkey_dir + "/Fastmonkey")
        commands.getstatusoutput(git_cmd)

    def down_app(self):
        print "downing...."
        file_tool.save_file(self.app['downloadURL'], self.install_dir, 'eleme_ios.ipa')
        if not os.path.exists(self.install_dir + 'eleme_ios.ipa'):
            raise WorkerException('down app fail')

    def install_app(self):
        output = subprocess.check_output(
            ["ideviceinstaller", "-u", self.udid, "-i", self.install_dir + '/eleme_ios.ipa'])
        logging.warning(output)
        # time.sleep(3)
        # if output.find("Complete") != -1:
        #     print (self.bundleId + " install success")
        #     return True
        # logging.warning(self.bundleId + " install not success")
        # raise WorkerException('install app fail')

    def uninstall_app(self):
        print "uninstall_app"
        uninstall_cmd = "ideviceinstaller -u %s -U %s" % (self.udid, self.bundleId)
        status, output = commands.getstatusoutput(uninstall_cmd)
        logging.warning(output)
        if output.find("Complete", 0, len(output)):
            print(self.bundleId + " uninstall success")
            return True
        logging.warning(self.bundleId + " uninstall not success")
        raise WorkerException('uninstall app fail')

    def get_deviceName(self):
        cmd = "ideviceinfo -u %s -k DeviceName" % (self.udid)
        status, output = commands.getstatusoutput(cmd)
        self.device_name = output
        print "get_deviceName: " + output


    def start_WDATest(self):
        def start_build():
            print "startWDA"
            cmd_WDA = "xcodebuild -project %s -scheme XCTestWDUITests -destination 'platform=iOS,name=%s' XCTESTWD_PORT=%s  clean test -allowProvisioningUpdates " % (
                self.wdadir, self.device_name, "8100")
            print cmd_WDA
            # commands.getstatusoutput(cmd_WDA)
            self.p_WDA = subprocess.call(cmd_WDA, shell=True)

            #
            # p_WDA = subprocess.Popen(cmd_WDA, stdout=subprocess.PIPE, shell=True,
            #                          preexec_fn=os.setsid)
            # while True:
            #         str = p_WDA.stdout.readline().strip()
            #         # print str
            #         if str.find('TEST FAILED') != -1:
            #             print "TEST FAILED"
            #             raise WorkerException('TEST FAILD')
            #         elif str.find('Provisioning Profile') != -1:
            #             print "building start success"


        def getDeviceIP():
            print "getDeviceIP"
            cmd_deviceip = "idevicesyslog -u " + self.udid
            self.p_devicelog = subprocess.Popen(cmd_deviceip, stdout=subprocess.PIPE, shell=True,
                                           preexec_fn=os.setsid)
            print cmd_deviceip
            while True:
                    str2 = self.p_devicelog.stdout.readline().strip()
                    # print str2
                    if str2.find('XCTestWDSetup->') != -1:
                        i = str2.find("http")
                        self.device_ip = "" * i + str2[i:]
                        self.p_devicelog.kill()
                        self.p_WDA.kill()
                        logging.warn('device_ip:' + self.device_ip)
                        break


        print "start FastMonkey"
        t1 = threading.Thread(target=start_build,name="start_build")
        t1.start()

        t2 = threading.Thread(target=getDeviceIP,name="getDeviceIP")
        t2.start()
        t2.join()


    def start_runmonkey(self):
        print "start_runmonkey"
        os.system('security unlock -p "qweqwe" ~/Library/Keychains/login.keychain')
        os.system('security set-keychain-settings -t 3600 -l ~/Library/Keychains/login.keychain')
        os.system('security import login.keychain -P "pwd" -T /usr/bin/codesign')

        cmd_monkey = "curl -X POST -H 'Content-Type:application/json' -d '{\"desiredCapabilities\":{\"deviceName\":\"%s\",\"platformName\":\"iOS\", \"bundleId\":\"%s\",\"autoAcceptAlerts\":\"true\",\"throttle\":\"%s\",\"pct_touch\":\"%s\",\"pct_syskeys\":\"%s\",\"pct_motion\":\"%s\"}}'  %s/wd/hub/monkey" % (
            self.device_name, self.bundleId, self.throttle, self.pct_touch, self.pct_syskeys, self.pct_motion,
            self.device_ip)
        print cmd_monkey
        self.p_monkey = subprocess.call(cmd_monkey, shell=True)
        time.sleep(self.duration_time)
        logging.info("monkey 结束")

    def deal_report(self):
        # 删除所有的信息
        list = os.listdir(self.crash_dir)
        for x in list:
            os.remove(self.crash_dir + x)

        # 从设备中提取所有的crash日志

        dealreport_cmd = "idevicecrashreport -u %s -e %s" % (self.udid, self.crash_dir)
        print dealreport_cmd
        status, output = commands.getstatusoutput(dealreport_cmd)

        if output.find("Done") != -1:
            logging.info(self.udid + " deal_report success")
            list = os.listdir(self.crash_dir)
            print list
            crashlist = []
            for i in list:
                ips_name = str(i)
                print ips_name
                if ips_name.find(self.search_key) != -1 and ips_name.find('ips') != -1:
                    crashlist.append(ips_name)

            if len(crashlist) > 0:
                self.send_mail("1")
            else:
                print "no crash"
                self.send_mail("0")

    def send_mail(self, ips):
        if ips != '0':
            self.upload(self.crash_dir, str(self.task_id))
            mail_content = "http://10.12.38.246:8000/report/" + self.task_id
            test_run_status = TestRunStatus.failed.value
        else:
            test_run_status = TestRunStatus.passed.value
            mail_content = 'No crash happened'
        server_api.upload_task_reports(self.task_id, mail_content)
        if self.run_id:
            server_api.add_results_for_cases(self.run_id, self.case_id, mail_content, test_run_status, self.app)
