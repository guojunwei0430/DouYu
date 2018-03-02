# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import unittest


class douyu(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.PhantomJS(executable_path=r"C:\KuGou\phantomjs-2.1.1-windows\bin\phantomjs.exe")

    def testDouyu(self):
        self.driver.get('http://www.douyu.com/directory/all')
        while True:
            content = bs(self.driver.page_source, 'xml')
            names = content.find_all('h3', {'class': 'ellipsis'})
            numbers = content.find_all('span', {'class': 'dy-num fr'})
            for name,number in zip(names, numbers):
                print u'房间标题:' + name.get_text().strip(),u'\t观众人数:' + number.get_text().strip()
            if self.driver.page_source.find('shark-pager-disable-next')!= -1:
                break

            self.driver.find_element_by_class_name('shark-pager-next').click()

    def tearDown(self):
        self.driver.quit()


if __name__ == '__main__':
    unittest.main()
