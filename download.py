import config
import os
import time
import requests
import re
from flask import send_file

from selenium import webdriver
from selenium.webdriver.common.by import By

from ext import chrome_cmd


class Download:

    __slots__ = ["b_id", "id", "driver", "logger"]

    def __init__(self, b_id, id):
        self.b_id = b_id
        self.id = id
        self.logger = config.logger
        self.driver = webdriver.Chrome("{}/chromedriver/chromedriver_{}".format(os.getcwd(), config.os_info),
                                       chrome_options=config.options)

    def __del__(self):
        # for handle in self.driver.window_handles:
        #     self.driver.switch_to.window(handle)
        #     self.driver.close()

        self.driver.quit()

    def start(self):
        try:
            view_url = "https://www.tfreeca22.com/board.php?mode=view&b_id={}&id={}".format(self.b_id, self.id)
            self.logger.debug("VIEW_URL : {}".format(view_url))

            self.driver.get(view_url)

            chrome_cmd.wait(driver=self.driver,
                            element_type=By.XPATH,
                            element_name='/html/body/table/tbody/tr/td[2]/table[1]/tbody/tr[4]/td/a',
                            timeout=5,
                            throw_error=True)

            self.logger.debug("Download Page Link Click")

            down_href = self.driver.find_element_by_xpath("/html/body/table/tbody/tr/td[2]/table[1]/tbody/tr[4]/td/a")
            down_href.click()

            self.logger.debug("Download Click")

            self.driver.switch_to.window(self.driver.window_handles[-1])

            time.sleep(1)

            chrome_cmd.wait(driver=self.driver,
                            element_type=By.XPATH,
                            element_name='//*[@id="Down"]/input[1]',
                            timeout=5,
                            throw_error=True)

            time.sleep(1)

            header_referer = config.headers.copy()
            header_referer['Referer'] = self.driver.current_url

            html = self.driver.page_source

            form_down = self.driver.find_element_by_xpath('//*[@id="Down"]')

            param_key = form_down.find_elements_by_name("key")[0].get_attribute("value")
            param_ticket = form_down.find_elements_by_name("Ticket")[0].get_attribute("value")
            param_randstr = form_down.find_elements_by_name("Randstr")[0].get_attribute("value")
            param_userip = form_down.find_elements_by_name("UserIP")[0].get_attribute("value")

            last_url = "?key={}&Ticket={}&Randstr={}&UserIP={}".format(param_key, param_ticket, param_randstr, param_userip)

            regex2 = r"var newUrl = '(.*?)';"
            matches2 = re.finditer(regex2, html, re.DOTALL | re.MULTILINE)
            for matchNum2, match2 in enumerate(matches2, start=1):
                last_url = match2.group(1) + last_url

                r = requests.get(last_url, headers=header_referer, stream=True)

                return send_file(r.raw,
                                 mimetype="application/x-bittorrent",
                                 attachment_filename=self.id + ".torrent",
                                 as_attachment=True
                                 )

        except Exception as e:
            self.logger.error(e)

        return "Download Error", 500

