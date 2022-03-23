from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import logging

logger = logging.getLogger("main")
wait_timeout = 30


def wait(driver, element_type, element_name, timeout=wait_timeout, throw_error=False):
    try:
        element_present = ec.presence_of_element_located((element_type, element_name))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException as e:
        logger.warning(e)
        if throw_error:
            raise Exception(e)


def page_has_loaded(driver):
    page_state = driver.execute_script('return document.readyState;')
    return page_state == 'complete'