#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.worker.compability
    ~~~~~~~~~~~~

    This module provide the compability test.

    :copyright: (c) 2017 by Ma Fei.
"""
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import agent.util.file as file_tool
from agent.consts import CompatibilityUserStatus
from agent.exc import WorkerException
from agent.qualityplatform import server_api
from agent.worker.base import BaseWorker

android_compatibility_dir = file_tool.make_worker_dir(os.getcwd() + '/agent/Compatibility/')


class Compatibility(BaseWorker):
    def __init__(self, data):
        super(Compatibility, self).__init__(data)
        self.username = self.data.get('user_name')
        self.password = self.data.get('password')
        self.notice_account = self.data.get('notice_account')
        self.grand_id = self.data.get('grand_id')
        self.platform = self.data.get('platform')
        self.packtype = self.data.get('packtype')
        self.app_version = self.data.get('app_version')
        self.run_id = self.data.get('run_id')
        self.case_id = self.data.get('case_id')

        self.wkdir = android_compatibility_dir + str(self.task_id)

    def start_worker(self):
        app = server_api.get_latest_app(self.grand_id, self.platform, self.packtype, self.app_version)

        file_tool.save_file(app['downloadURL'], self.wkdir, 'eleme_android.apk')
        self.__run_testin(self.username, self.password)
        server_api.update_compatibility_user_status(self.username, CompatibilityUserStatus.unavailable.value)
        self.__send_test_report(self.username, self.password, app)
        self.complete()

    def __run_testin(self, username, password):
        browser = webdriver.Firefox()
        try:
            browser.set_page_load_timeout(300)

            browser.set_window_size(1920, 1080)

            browser.get("https://www.testin.cn/account/login.htm")
            wait = WebDriverWait(browser, 600)
            usernameelement = wait.until(EC.visibility_of_element_located((By.ID, "email")))
            usernameelement.send_keys(username)
            passwordelement = wait.until(EC.visibility_of_element_located((By.ID, "pwd")))
            passwordelement.send_keys(password)
            login = wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[2]/div/form/button")))
            login.click()
            waimai_project = wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div/div/div[1]/span")))
            waimai_project.click()
            create_job = wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/button")))
            create_job.click()
            browser.execute_script("document.getElementsByClassName('hide_block')[1].style.display='block';")
            auto_compatibility = wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div/ul/li[2]/div[3]/a")))
            auto_compatibility.click()
            time.sleep(5)
            start_test = wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[4]/ul/li[1]/a")))
            start_test.click()
            uploadapp = wait.until(EC.element_to_be_clickable((By.ID, "uploadApp")))
            uploadapp.click()
            uploadfile = wait.until(EC.visibility_of_element_located((By.NAME, "file")))
            uploadfile.send_keys(self.wkdir + '/eleme_android.apk')
            app_type = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     "/html/body/div[1]/div[4]/div/div/div[2]/div/div[2]/form/div[3]/div/div[1]/select/option[13]")))
            app_type.click()
            submit_app = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[1]/div[4]/div/div/div[2]/div/div[2]/form/div[7]/button")))
            submit_app.click()
            choose_app = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[1]/div[2]/div[1]/table/tbody/tr[2]/td[1]")))
            choose_app.click()
            nextStep = wait.until(EC.element_to_be_clickable((By.ID, "nextStep")))
            nextStep.click()
            nextButton = wait.until(EC.element_to_be_clickable((By.ID, "nextButton")))
            nextButton.click()
            job_desc = wait.until(EC.visibility_of_element_located((By.ID, "descr")))
            job_desc.send_keys(u'饿了么Android兼容性测试')
            subTest = wait.until(EC.element_to_be_clickable((By.ID, "subTest")))
            subTest.click()
            browser.quit()
        except Exception as e:
            browser.quit()
            raise WorkerException(e)

    def __send_test_report(self, username, password, app):
        browser = webdriver.Firefox()
        try:
            browser.set_page_load_timeout(300)
            browser.set_window_size(1920, 1080)

            browser.get("https://www.testin.cn/account/login.htm")
            wait = WebDriverWait(browser, 30000)
            email = wait.until(EC.visibility_of_element_located((By.ID, "email")))
            email.send_keys(username)
            pwd = wait.until(EC.visibility_of_element_located((By.ID, "pwd")))
            pwd.send_keys(password)
            login = wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[2]/div/form/button")))
            login.click()
            waimai_project = wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div/div/div[1]/span")))
            waimai_project.click()
            auto_compatibility = wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div/nav/div/ul/li[1]/ul/li[2]/a")))
            auto_compatibility.click()

            main_window_handle = None
            while not main_window_handle:
                main_window_handle = browser.current_window_handle
            report_visible = wait.until(
                EC.text_to_be_present_in_element(
                    (By.XPATH, "/html/body/div[1]/div[2]/div[4]/table/tbody/tr[2]/td[9]/a"),
                    u"查看报告"))
            if report_visible:
                report = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/div[4]/table/tbody/tr[2]/td[9]/a")))
                report.click()
            signin_window_handle = None
            while not signin_window_handle:
                for handle in browser.window_handles:
                    if handle != main_window_handle:
                        signin_window_handle = handle
                        break
            time.sleep(10)
            browser.switch_to.window(signin_window_handle)
            share_report = wait.until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div/div[2]/button")))
            share_report.click()
            report_url = browser.find_element_by_id("link_text").get_attribute('value')
            server_api.send_mail(self.notice_account, 'testin云测报告', '饿了么android_兼容性测试云测_testin', app, report_url,
                                 'test_report.html')
            if self.run_id:
                server_api.add_results_for_cases(self.run_id, self.case_id, report_url, app)
            report_content = {
                'task_id': self.task_id,
                'content': report_url
            }
            server_api.add_report(report_content)
            browser.quit()
        except Exception as e:
            browser.quit()
            raise WorkerException(e)
