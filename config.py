import os
import logging.handlers
from selenium.webdriver.chrome.options import Options

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Accept-Language': 'ko-KR',
}

os_info = "mac"
if "os" in os.environ:
    os_info = os.environ.get("os")

########################################################################
# Setting
########################################################################
# logger
logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s [%(threadName)-10s] - %(filename)s [%(lineno)d] - %(funcName)s : %(message)s')

streamHandler = logging.StreamHandler()
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Chrome Driver Option Setting
options = Options()
options.add_argument("--window-size=100,100")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--blink-settings=imagesEnabled=false')

if os_info == "linux":
    options.add_argument('--headless')
    # options.add_argument("--disable-gpu")
elif os_info == "windows":
    # options.add_argument('--headless')
    # options.add_argument("--disable-gpu")
    pass
else:
    options.add_argument('--headless')
    # options.add_argument("--disable-gpu")
    pass

