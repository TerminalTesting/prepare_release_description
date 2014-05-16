#! /usr/bin/python
# -*- coding: utf8 -*-
"""
Скрипт собирает номера задач со страницы обновления, их описание в отдельный файл.
Для подготовки информашки о релизе. 
"""
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import Webform 

BROWSER='FIREFOX'

BASE_URL='http://project.terminal.ru/issues/'
FORM_FILE_NAME = 'wiki_form_file.xml'

RELEASE_TASK=os.getenv('TASK_NUM')
RELEASE_FILE = os.getenv('FILE_NAME')
USER_NAME=os.getenv('USER_NAME')
USER_PASSWORD=os.getenv('USER_PASSWORD')

WAIT_TIME=10.0
SLEEP_TIME=1.0

driver = webdriver.Firefox()

driver.implicitly_wait(WAIT_TIME)
test_web_app=Webform.WebApp(driver, FORM_FILE_NAME, BASE_URL)
test_web_app.app_start('')
login=Webform.WebForm(FORM_FILE_NAME, "LOGIN_FORM", driver)
login.USER_NAME.value=USER_NAME
login.USER_PASSWORD.value=USER_PASSWORD
login.LOGIN_BUTTON.click()

test_web_app.app_start( RELEASE_TASK )
login_form=Webform.WebForm(FORM_FILE_NAME, "DESCRIPTION", driver)

buf=''
idx=1
print 'BASE URL:',BASE_URL,' RELEASE TASK:',RELEASE_TASK, ' RELEASE FILE:', RELEASE_FILE

# Собираем ссылки на задачи в релиз из страницы описания
task_link_list=[ task_link_el.TASK_NUM.get_attribute('href') for task_link_el in login_form.SUBJ ]

# напрямую перебор объектов в массиве делать не получится, т.к. идет переход на новую страницу,
#после чего эти объекты теряются.
for task_link in task_link_list:
    test_web_app.driver.get(task_link)
    task_descr=Webform.WebForm(FORM_FILE_NAME, "TASK_DESCRIPTION_1", driver)
    buf+=('%d.%s: %s.\n%s\n\n%s.\n\n')% (idx, task_descr.NUM.value, task_descr.SUBJ.value,task_descr.WIKI.value, task_descr.OWNER.value)
    print ('%d. Link:%s')%(idx, task_link)
    test_web_app.driver.back()
    idx+=1

fp=file(RELEASE_FILE, 'w+')
fp.write(buf.encode('utf-8', 'ignore'))
fp.close()
test_web_app.app_stop()
