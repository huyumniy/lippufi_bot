import os, sys, platform
import shutil, tempfile
import random
import time
import json
from datetime import datetime, timezone
import requests
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
        except Exception as e:
            print(f"Error creating new connection: {e}")
            if driver:
                driver.quit()
            time.sleep(10)  # Adding a delay before retrying

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
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-site-isolation-trials")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--lang=EN')
    cwd = os.getcwd()
    extension = ''
    nopecha_extension = ''
    vpn = ''
    if os.name == 'posix' and platform.system() == 'Darwin':
        extension = cwd + "/uBlock-Origin"
        nopecha_extension = cwd + "/NopeCHA"
        vpn = cwd + "/vpn"
    elif os.name == 'nt':
        extension = cwd + "\\uBlock-Origin"
        nopecha_extension = cwd + "\\NopeCHA"
        vpn = cwd + "\\vpn"

    if proxy and proxy != 'vpn':
        proxy = proxy.split(":", 3)
        proxy[1] = int(proxy[1])
        print(proxy)
        proxy_extension = ProxyExtension(*proxy)
        options.add_argument(f"--load-extension={proxy_extension.directory},{extension},{nopecha_extension}")
    else:
        options.add_argument(f"--load-extension={extension},{nopecha_extension},{vpn}")

    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        options=options,
        enable_cdp_events=True
    )
    driver.get('https://nopecha.com/setup#sub_1NnGb4CRwBwvt6ptDqqrDlul|keys=|enabled=true|disabled_hosts=|hcaptcha_auto_open=true|hcaptcha_auto_solve=true|hcaptcha_solve_delay=true|hcaptcha_solve_delay_time=3000|recaptcha_auto_open=true|recaptcha_auto_solve=true|recaptcha_solve_delay=true|recaptcha_solve_delay_time=1000|funcaptcha_auto_open=true|funcaptcha_auto_solve=true|funcaptcha_solve_delay=true|funcaptcha_solve_delay_time=0|awscaptcha_auto_open=true|awscaptcha_auto_solve=true|awscaptcha_solve_delay=true|awscaptcha_solve_delay_time=0|turnstile_auto_solve=true|turnstile_solve_delay=true|turnstile_solve_delay_time=1000|perimeterx_auto_solve=false|perimeterx_solve_delay=true|perimeterx_solve_delay_time=1000|textcaptcha_auto_solve=true|textcaptcha_solve_delay=true|textcaptcha_solve_delay_time=0|textcaptcha_image_selector=#img_captcha|textcaptcha_input_selector=#secret|recaptcha_solve_method=Image')
    # set_random_16_9_resolution(driver)
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
    

def wait_for_element(driver, selector, click=False, timeout=10, xpath=False, debugMode=False, scrollToBottom=False):
    try:
        if xpath:
            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, selector)))
        else:
            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        
        if click:
            driver.execute_script("arguments[0].scrollIntoView();", element)
            if scrollToBottom: driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", check_for_element(driver, '#main-content'))
            element.click()
        return element
    except Exception as e:
        if debugMode: print("selector: ", selector, "\n", e)
        return False
    

def collect_data(driver, category):

    try:
        amount_price_raw = driver.find_element(By.CSS_SELECTOR, '.main-ticket-card-headline-text span').text
    except Exception as e:
        print(f"Error finding amount and price: {e}")
        amount_price_raw = "0, 0 USD"

    try:
        event_name = driver.find_element(By.CSS_SELECTOR, '.event-name').text
    except Exception as e:
        print(f"Error finding event name: {e}")
        event_name = "Unknown Event"

    try:
        info_rows = driver.find_elements(By.CSS_SELECTOR, 'ev-price-information[class="main-ticket-card-priceinfo main-ticket-card-grid ng-star-inserted"]')
    except Exception as e:
        print(f"Error finding info rows: {e}")
        info_rows = []

    try:
        city = driver.find_element(By.CSS_SELECTOR, '[class="venue-info normalspace ng-star-inserted"]').text
    except Exception as e:
        print(f"Error finding city: {e}")
        city = "Unknown City"

    try:
        city_date = driver.find_element(By.CSS_SELECTOR, '[class="time normalspace ng-star-inserted"]').text
    except Exception as e:
        print(f"Error finding city date: {e}")
        city_date = "Unknown Date"

    description = city + ' ' + city_date + '\nurl: ' + driver.current_url + '\n\n'
    cookies = driver.get_cookies()
    ua = driver.execute_script('return navigator.userAgent')
    for info_row in info_rows:
        try:
            row_category = info_row.find_element(By.CSS_SELECTOR, 'div[class="price-category-info middlespace ng-star-inserted"]').text
        except Exception as e:
            print(f"Error finding row category: {e}")
            row_category = "Unknown Category"

        try:
            row_price = info_row.find_element(By.CSS_SELECTOR, '[class="price-category-price endspace ng-star-inserted"]').text
        except Exception as e:
            print(f"Error finding row price: {e}")
            row_price = "Unknown Price"

        try:
            row_place = info_row.find_element(By.CSS_SELECTOR, '[class="u-color-highlight normalspace ng-star-inserted"]').text
        except Exception as e:
            print(f"Error finding row place: {e}")
            row_place = "Unknown Place"

        description += row_category + ' ' + row_price + "\n" + row_place + '\n\n'
    try:
        amount, price = amount_price_raw.split(', ')
        amount = int(amount.split(' ')[0].strip())
        price, currency = price.strip().split(' ')
        price = float(price.replace(',', '.'))
    except Exception as e:
        print(f"Error parsing amount and price: {e}")
        amount = 0
        price = 0.0
        currency = "USD"

    bot_name = 'lippufy bot'
    data = {
        "name": event_name,
        "description": description,
        "date": datetime.now(timezone.utc).isoformat(),
        "amount": amount,
        "price": price,
        "currency": currency,
        "category": category, 
        "bot_name": bot_name,
        "cookies": cookies,
        "user_agent": ua
    }

    print(amount, price, currency, event_name, description)
    return data

    


def post_request(data, endpoint='/book', port='80'):
    try:
        json_data = json.dumps(data)
        
    except Exception as e:
        print(e)
    # Set the headers to specify the content type as JSON
    headers = {
        "Content-Type": "application/json"
    }

    # Send the POST request 
    print(f"http://localhost:{port}{endpoint}")
    try:
        response = requests.post(f"http://localhost:{port}{endpoint}", data=json_data, headers=headers)
        print(response)
    except Exception as e:
        print(e)
        return False
    # Check the response status code
    if response:
        if response.status_code == 200:
            print("POST request successful!")
        else:
            print("POST request failed.")
    else: return False


def reconnect_vpn(driver, vpn_url):
    blacklist = ['Iran', 'Egypt', 'Italy']
    while True:
        try:
            driver.get(vpn_url)
            wait_for_element(driver, 'button[class="button button--pink consent-text-controls__action"]', click=True, timeout=5)
            is_connected = check_for_element(driver, 'div[class="play-button play-button--pause"]')
            if is_connected: 
                driver.find_element(By.CSS_SELECTOR, 'div[class="play-button play-button--pause"]').click()
            select_element = driver.find_element(By.CSS_SELECTOR, 'div[class="select-location"]')
            select_element.click()
            time.sleep(2)
            while True:
                element = random.choice(check_for_elements(driver, '//ul[@class="locations"][2]/li/p', xpath=True))
                element_text = element.text
                if element_text not in blacklist: break
            driver.execute_script("arguments[0].scrollIntoView();", element)
            element.click()
            time.sleep(5)
            break
        except Exception as e: pass


if __name__ == "__main__":
    link = input('link: ')
    proxy = input('proxy: ')
    proxy_url = ''
    if proxy and proxy != 'vpn':
        proxy_url = input('proxy change ip url: ')
    categories = input('Enter required categories (e.g., Category 1 + Category 2...):\n')

    while True:
        try:
            amount = int(input('Enter the number of tickets required: '))
            break
        except ValueError:
            print('Please enter the number of tickets in numerical format')
            continue
    if categories:
        categories = categories.split(' + ')

    driver = create_new_connection(proxy)
    time.sleep(2)
    try:
        tabs = driver.window_handles
        driver.switch_to.window(tabs[1])
        driver.close()
        driver.switch_to.window(tabs[0])
    except Exception as e:
        print(f"Error handling tabs: {e}")

    pn_url = ''
    if proxy == 'vpn':
        driver.get('chrome://extensions/')
        js_code = """
            const callback = arguments[0];
            chrome.management.getAll((extensions) => {
                callback(extensions);
            });
        """
        extensions = driver.execute_async_script(js_code)
        filtered_extensions = [extension for extension in extensions if 'Urban VPN' in extension['description']]

        vpn_id = [extension['id'] for extension in filtered_extensions if 'id' in extension][0]
        vpn_url = f'chrome-extension://{vpn_id}/popup/index.html'
        reconnect_vpn(driver, vpn_url)

    while True:
        driver.get(link)
        time.sleep(2)
        ticket_add_buttons = []
        picked_category = ''
        if categories:
            category = random.choice(categories)
            picked_category = category
            category_element = check_for_element(driver, f'//div[contains(@class, "pc-list-category")]/span[contains(text(), "{category}")]', xpath=True)
            parent_form = check_for_element(category_element, './ancestor::form[1]', xpath=True)
        else:
            parent_form = random.choice(check_for_elements(driver, 'form[class="event-list-content js-focus-item js-form-timestamp   "]'))
        ticket_element = check_for_element(parent_form, './div[2]/div/div/div/div[@data-qa="tickettype"]', xpath=True)
        ticket_add_element = check_for_element(ticket_element, './div[@class="ticket-type-stepper"]', xpath=True)

        if not check_for_element(ticket_element, './div[@class="ticket-type-unavailable-sec"]', xpath=True):
            ticket_add_buttons.append(ticket_add_element)
        if not ticket_add_buttons:
            print('No tickets available')
            time.sleep(30)
            continue
        for ticket_add_button in ticket_add_buttons:
            for i in range(amount):
                check_for_element(ticket_add_button, './div/button[2]', click=True, xpath=True)
        buy_button = check_for_element(parent_form, './div[2]/div[2]/button', click=True, xpath=True, debugMode=True)
        while True:
            if check_for_element(driver, '#spinner[style="display: none;"]'):
                break
            elif not check_for_element(driver, '#spinner'):
                break
            time.sleep(1)
            continue

        if check_for_element(driver, 'div[class="cc-layer-box full-screen-xs theme-text-variant-color js-cc-layer-box"][style="display: block;"]'):
            check_for_element(driver, 'button[data-qa="ccNoTicketsAvailableBackToDetailbBtn"]', click=True)
            print("No Tickets Available")

        if 'checkout' in driver.current_url:
            time.sleep(1)
            data = collect_data(driver, category)

            post_request(data)
            post_request(data=data, endpoint='/api/create-ticket/', port='8000')
            data, fs = sf.read('notify.mp3', dtype='float32')
            sd.play(data, fs)
            status = sd.wait()
            driver.quit()
            time.sleep(1200)

        continue
