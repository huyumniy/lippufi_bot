import os, sys, platform
import shutil, tempfile
import random
import time
import json
import soundfile as sf
import sounddevice as sd
import undetected_chromedriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class ProxyExtension:
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {"scripts": ["background.js"]},
        "minimum_chrome_version": "76.0.0"
    }
    """

    background_js = """
    var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: %d
            },
            bypassList: ["localhost"]
        }
    };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        { urls: ["<all_urls>"] },
        ['blocking']
    );
    """

    def __init__(self, host, port, user, password):
        self._dir = os.path.normpath(tempfile.mkdtemp())

        manifest_file = os.path.join(self._dir, "manifest.json")
        with open(manifest_file, mode="w") as f:
            f.write(self.manifest_json)
        background_js = self.background_js % (host, int(port), user, password)
        background_file = os.path.join(self._dir, "background.js")
        with open(background_file, mode="w") as f:
            f.write(background_js)

    @property
    def directory(self):
        return self._dir

    def __del__(self):
        shutil.rmtree(self._dir)


def create_new_connection(proxy):
    while True:
        try:
            driver = selenium_connect(proxy)
            return driver
        except:
            driver.close()
            driver.quit()

def set_random_16_9_resolution(driver):
    # Define the range of resolutions
    min_width, max_width = 1366, 1920
    min_height, max_height = 768, 1080

    # Generate random width and height within the specified range
    width = random.randint(min_width, max_width)
    height = random.randint(min_height, max_height)

    # Set the window size
    driver.set_window_size(width, height)


def selenium_connect(proxy):
    print(proxy)
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    #options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-site-isolation-trials")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--lang=EN')
    cwd= os.getcwd()
    extension = ''
    if os.name == 'posix' and platform.system() == 'Darwin': extension = cwd + "/uBlock-Origin"
    elif os.name == 'nt': extension = cwd + "\\uBlock-Origin"
    print(extension)
    if proxy:
        proxy = proxy.split(":", 3)
        proxy[1] = int(proxy[1])
        print(proxy)
        proxy_extension = ProxyExtension(*proxy)
        options.add_argument(f"--load-extension={proxy_extension.directory},{extension}")
    else: options.add_argument(f"--load-extension={extension}")

    prefs = {"credentials_enable_service": False,
        "profile.password_manager_enabled": False}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        options=options,
        enable_cdp_events=True
    )

    set_random_16_9_resolution(driver)

    return driver


def check_for_element(driver_element, selector, click=False, xpath=False, debugMode=False):
    global driver 
    try:
        if xpath:
            element = driver_element.find_element(By.XPATH, selector)
        else:
            element = driver_element.find_element(By.CSS_SELECTOR, selector)
        if click: 
            driver.execute_script("arguments[0].scrollIntoView();", element)
            # slow_mouse_move_to_element(driver, element)
            element.click()
        return element
    except Exception as e:
        if debugMode: print("selector: ", selector, "\n", e)
        return False


def check_for_elements(driver_element, selector, xpath=False, debugMode=False):
    try:
        if xpath:
            elements = driver_element.find_elements(By.XPATH, selector)
        else:
            elements = driver_element.find_elements(By.CSS_SELECTOR, selector)
        return elements
    except Exception as e:
        if debugMode: print("selector: ", selector, "\n", e)
        return False
    

def wait_for_element(driver, selector, click=False, timeout=10, xpath=False, debugMode=False):
    try:
        if xpath:
            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, selector)))
        else:
            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        
        if click:
            driver.execute_script("arguments[0].scrollIntoView();", element)
            element.click()
        return element
    except Exception as e:
        if debugMode: print("selector: ", selector, "\n", e)
        return False


if __name__ == "__main__":
    link = input('link: ')
    proxy = input('proxy: ')
    categories = input('Введіть потрібні категорії, приклад вводу: Kategoria 1, Kategoria 2...\n')
    
    while True: 
        try: 
            amount = int(input('Ввведіть необхідну кількість квитків: '))
            break
        except: 
            print('Введіть кількість квитків в числовому форматі')
            continue
    if categories: categories = categories.split(', ')
    driver = create_new_connection(proxy)
    while True:
        driver.get(link)
        time.sleep(2)
        ticket_add_buttons = []
        if categories: 
            category = random.choice(categories)
            category_element = check_for_element(driver, f'//div[contains(@class, "pc-list-category")]/span[contains(text(), "{category}")]', xpath=True, debugMode=True)
            parent_form = check_for_element(category_element, './ancestor::form[1]', xpath=True, debugMode=True)
        else: parent_form = random.choice(check_for_elements(driver, 'form[class="event-list-content js-focus-item js-form-timestamp   "]'))
        ticket_element = check_for_element(parent_form, './div[2]/div/div/div/div[@data-qa="tickettype"]', xpath=True, debugMode=True)
        ticket_add_element = check_for_element(ticket_element, './div[@class="ticket-type-stepper"]', xpath=True, debugMode=True)

        if not check_for_element(ticket_element, './div[@class="ticket-type-unavailable-sec"]', xpath=True): ticket_add_buttons.append(ticket_add_element)
        if not ticket_add_buttons: 
            print('No tickets available')
            time.sleep(30)
            continue
        for ticket_add_button in ticket_add_buttons:
            for i in range(0, amount):
                check_for_element(ticket_add_button, './div/button[2]', click=True, xpath=True, debugMode=True)
        buy_button = check_for_element(parent_form, './div[2]/div[2]/button', click=True, xpath=True, debugMode=True)
        while True:
            if check_for_element(driver, '#spinner[style="display: none;"]'): break
            elif not check_for_element(driver, '#spinner'): break
            time.sleep(1)
            continue
        
        if check_for_element(driver, 'div[class="cc-layer-box full-screen-xs theme-text-variant-color js-cc-layer-box"][style="display: block;"]'):
            check_for_element(driver, 'button[data-qa="ccNoTicketsAvailableBackToDetailbBtn"]', click=True)
            print("No Tickets Available")
            
        if 'checkout' in driver.current_url:
            data, fs = sf.read('notify.mp3', dtype='float32')  
            sd.play(data, fs)
            status = sd.wait()
            time.sleep(1200)
        # cookies = driver.get_cookies()
        # json_cookies = json.dumps(cookies)
        # print(json_cookies)
        continue
