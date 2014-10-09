#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
Скрипт собирает номера задач со страницы обновления, их описание в отдельный файл.
Для подготовки информашки о релизе. 
"""
import os
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#delete old screenshot artifacts.
os.system('find -iname \*.png -delete')

#delete old text artifacts.
os.system('find -iname \*.txt -delete')

BASE_URL='http://project.terminal.ru/'
ARTSOURCE = '%sartifact/' % os.getenv('BUILD_URL')
RELEASE_TASK = 'issues/' + os.getenv('TASK_NUM')
RELEASE_FILE = os.getenv('FILE_NAME')
USER_NAME = os.getenv('USER_NAME')
USER_PASSWORD = os.getenv('USER_PASSWORD')

def element(driver, how, what, timeout = 10, screen = True):
    """ Поиск элемента по локатору

            По умолчанию таймаут 10 секунд, не влияет на скорость выполнения теста
            если элемент найден, если нет - ждет его появления 10 сек
            
            Параметры:
               how - метод поиска
               what - локатор
            Методы - атрибуты класса By:
             |  CLASS_NAME = 'class name'
             |  
             |  CSS_SELECTOR = 'css selector'
             |  
             |  ID = 'id'
             |  
             |  LINK_TEXT = 'link text'
             |  
             |  NAME = 'name'
             |  
             |  PARTIAL_LINK_TEXT = 'partial link text'
             |  
             |  TAG_NAME = 'tag name'
             |  
             |  XPATH = 'xpath'
                                             """
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((how, what)))
    except:
        print u'Элемент не найден'
        print 'URL: ', driver.current_url
        print u'Метод поиска: ', how
        print u'Локатор: ', what
        if screen:
            screen_name = '%d.png' % int(time.time())
            driver.get_screenshot_as_file(screen_name)
            print u'Скриншот страницы: ', ARTSOURCE + screen_name
        raise Exception('ElementNotPresent')

driver = webdriver.Firefox()
driver.implicitly_wait(10)


#login
driver.get(BASE_URL + RELEASE_TASK)
element(driver, By.ID, 'username').send_keys(USER_NAME)
element(driver, By.ID, 'password').send_keys(USER_PASSWORD)
element(driver, By.NAME, 'login').click()

buf=''
idx=1
print 'ISSUES URL:', BASE_URL + RELEASE_TASK, ' RELEASE FILE:', RELEASE_FILE

# Собираем ссылки на задачи в релиз из страницы описания
task_link_list = element(driver, By.ID, 'relations').find_elements_by_tag_name('tr')

issues_urls = []

#collect urls
for task_link in task_link_list:
    issues_urls.append(task_link.find_element_by_class_name('subject').find_element_by_tag_name('a').get_attribute('href'))

#перебор элементов для получения информации
for task_url in issues_urls:

    driver.get(task_url)
    
    task_number = task_url[task_url.find('issues')+7:]
    task_name = element(driver, By.CLASS_NAME, 'subject').find_element_by_tag_name('h3').text
    description = element(driver, By.CLASS_NAME, 'description').find_element_by_class_name('wiki').text

    owner = driver.find_elements_by_class_name('cf_11')
    if owner[1].text == '':
        author = element(driver, By.CLASS_NAME, 'author').text.split(' ')  #parse info string because of different locators used
        owner_string = '%s %s %s.\n\n' % (owner[0].text, author[1], author[2])
    else:
        owner_string = '%s %s.\n\n' % (owner[0].text, owner[1].text)
    
    
    buf+= '*%d.* ' % idx  #index
    buf+= '#%s - ' % task_number
    buf+= task_name
    buf+= '\n\n%s\n\n' % description
    buf+= owner_string
    print ('%d. Link:%s')%(idx, driver.current_url)
    idx+=1

fp = open(RELEASE_FILE, 'w+')
fp.write(buf.decode('utf-8', 'ignore'))
fp.close()

driver.close()
