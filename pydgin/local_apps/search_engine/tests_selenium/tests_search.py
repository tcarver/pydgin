''' Test JS in search engine app. '''
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome import service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time

BROWSERS = []
HOST = "http://localhost:8000"
HEADLESS_MODE = getattr(settings, 'HEADLESS_MODE', False)


def setUpModule():
    ''' Open browsers for testing. '''
    global BROWSER

    if HEADLESS_MODE:
        display = Display(visible=0, size=(1000, 800))
        display.start()
    BROWSERS.append(webdriver.Firefox())
    BROWSERS.append(webdriver.Chrome())
    BROWSERS.append(_get_opera_driver())


def tearDownModule():
    ''' Close web browsers. '''
    for br in BROWSERS:
        br.quit()


def _get_opera_driver():
    ''' Use OperaChromiumDriver for Opera testing.
    L{https://github.com/operasoftware/operachromiumdriver}
    L{https://github.com/operasoftware/operachromiumdriver/blob/master/docs/python-setup-step-by-step.md}
    L{https://github.com/operasoftware/operachromiumdriver/blob/master/docs/desktop.md}
    '''
    webdriver_service = service.Service('/gdxbase/www/tim-dev/operadriver64')
    webdriver_service.start()
    desired_caps = DesiredCapabilities.OPERA
    desired_caps['operaOptions'] = {'binary': "/usr/bin/opera"}
    return webdriver.Remote(webdriver_service.service_url, desired_caps)


class Search(TestCase):

    def test_search_box_autosuggest(self):
        ''' Test auto-suggest '''
        for br in BROWSERS:
            br.get(HOST+reverse('search_page'))
            time.sleep(0.2)

            search_box = br.find_element_by_name("query")
            if not search_box.is_displayed():
                navbar = br.find_element_by_class_name("navbar-toggle")
                navbar.click()
                time.sleep(0.2)

            auto_complete = br.find_element_by_class_name("ui-autocomplete")
            search_box.send_keys("PT")
            time.sleep(1)
            self.assertTrue(auto_complete.is_displayed())

    def test_search_box(self):
        ''' Test searching. '''
        for br in BROWSERS:
            br.get(HOST+reverse('search_page'))
            search_box = br.find_element_by_name("query")
            if not search_box.is_displayed():
                navbar = br.find_element_by_class_name("navbar-toggle")
                navbar.click()
                time.sleep(1)
            search_box.send_keys("PTPN22")
            search_box.send_keys(Keys.RETURN)
