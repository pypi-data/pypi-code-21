#!/usr/bin/env python
# -*- coding: utf-8 -*-

import agent.qualityplatform.api as server_api

if __name__ == '__main__':
    app = server_api.get_latest_app('me.ele', 'Android', 'Release')
    # server_api.send_mail(
    #     'waimai.mobile.platform@ele.me, waimai.qa.platform@ele.me, waimai.qa@ele.me, hongbo.tang@ele.me',
    #     'testin报告', '饿了么android_兼容性测试_testin', app,
    #     'https://www.testin.cn/s/5949a068',
    #     'test_report.html')
    server_api.send_mail(["waimai.qa.platform@ele.me", "waimai.mobile.platform@ele.me", "waimai.qa@ele.me", "hongbo.tang@ele.me"],
                         '阿里云测报告', '饿了么android_兼容性测试_阿里云测', app,
                         'http://mqc.aliyun.com/report.htm?executionId=399170&shareCode=511pEZPcAqQA',
                         'test_report.html')
    # mail_content = 'No crash happened'
    # test_results = {
    #     'results': [
    #         {
    #             "case_id": 1138945,
    #             "comment": mail_content
    #         }
    #     ]
    # }
    # server_api.add_results_for_cases(636070, test_results)
    # mail_content = 'No crash happened'
    # comment = {
    #     "app_name": 'me.ele',
    #     "app_version": '7.24',
    #     "commit_id": 'asdasdas',
    #     "download_url": 'asdasdasd',
    #     "log": mail_content,
    #     "package_type": 'Release',
    #     "platform": 'Android',
    # }
    # test_results = {
    #     'results': [
    #         {
    #             "case_id": 1138945,
    #             "comment": json.dumps(comment)
    #         }
    #     ]
    # }
    # server_api.add_results_for_cases(636489, test_results)
    # oneday = timedelta(days=1)
    # day = datetime.now() - oneday
    # date_from = datetime(day.year, day.month, day.day, 0, 0, 0)
    # query_date = int(time.mktime(time.strptime(str(date_from), '%Y-%m-%d %H:%M:%S')))
    # # print(int(time.time()))
    # print query_date
