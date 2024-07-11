import os, sys, platform
import shutil, tempfile
import random
import time
import json
from datetime import datetime, timezone
import requests
import soundfile as sf
import re
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
    else: options.add_argument(f"--load-extension={extension},{nopecha_extension},{vpn}")

    prefs = {"credentials_enable_service": False,
        "profile.password_manager_enabled": False}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(
        options=options,
        enable_cdp_events=True
    )
    driver.get('https://nopecha.com/setup#sub_1NnGb4CRwBwvt6ptDqqrDlul|keys=|enabled=true|disabled_hosts=|hcaptcha_auto_open=true|hcaptcha_auto_solve=true|hcaptcha_solve_delay=true|hcaptcha_solve_delay_time=3000|recaptcha_auto_open=true|recaptcha_auto_solve=true|recaptcha_solve_delay=true|recaptcha_solve_delay_time=1000|funcaptcha_auto_open=true|funcaptcha_auto_solve=true|funcaptcha_solve_delay=true|funcaptcha_solve_delay_time=0|awscaptcha_auto_open=true|awscaptcha_auto_solve=true|awscaptcha_solve_delay=true|awscaptcha_solve_delay_time=0|turnstile_auto_solve=true|turnstile_solve_delay=true|turnstile_solve_delay_time=1000|perimeterx_auto_solve=false|perimeterx_solve_delay=true|perimeterx_solve_delay_time=1000|textcaptcha_auto_solve=true|textcaptcha_solve_delay=true|textcaptcha_solve_delay_time=0|textcaptcha_image_selector=#img_captcha|textcaptcha_input_selector=#secret|recaptcha_solve_method=Image')
    # set_random_16_9_resolution(driver)
    return driver


def check_for_element(driver_element, selector, click=False, xpath=False, debugMode=False, js_click=False):
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
        if js_click:
            driver.execute_script("arguments[0].scrollIntoView();", element)
            driver.execute_script("arguments[0].click();", element)
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
    

def wait_for_element(driver, selector, click=False, timeout=10, xpath=False, debugMode=False, scrollToBottom=False, js_click=False):
    try:
        if xpath:
            element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, selector)))
        else:
            element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        
        if click:
            driver.execute_script("arguments[0].scrollIntoView();", element)
            if scrollToBottom: driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", check_for_element(driver, '#main-content'))
            element.click()
        if js_click:
            driver.execute_script("arguments[0].scrollIntoView();", element)
            if scrollToBottom: driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", check_for_element(driver, '#main-content'))
            driver.execute_script("arguments[0].click();", element)
        return element
    except Exception as e:
        if debugMode: print("selector: ", selector, "\n", e)
        return False
    

def wait_for_elements(driver, selector, click=False, timeout=10, xpath=False, debugMode=False, scrollToBottom=False):
    try:
        if xpath:
            element = WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((By.XPATH, selector)))
        else:
            element = WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
        
        if click:
            driver.execute_script("arguments[0].scrollIntoView();", element)
            if scrollToBottom: driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", check_for_element(driver, '#main-content'))
            element.click()
        return element
    except Exception as e:
        if debugMode: print("selector: ", selector, "\n", e)
        return False
    

def collect_data(driver):

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
    category = ''
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
        category = row_category
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


def change_ip(url):
    try:
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
           return True
        else:
            print(f"Request failed with status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


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


def validate_price_range(price_input):
    # Define the pattern to match the expected input format
    pattern = re.compile(r'^\d+\s*-\s*\d+(\s*або\s*\d+\s*-\s*\d+)*$')

    if pattern.match(price_input):
        price_ranges = price_input.split('або')
        for price_range in price_ranges:
            # Extract numbers
            numbers = re.findall(r'\d+', price_range)
            price_range_list = [int(num) for num in numbers]
            if len(price_range_list) == 2 and price_range_list[0] < price_range_list[1]:
                continue
            else:
                print(f"Недійсний діапазон: {price_range_list}. Переконайтеся, що нижня межа менша за верхню.")
                return False
        return price_range_list
    else:
        print("Недійсний формат введення. Будь ласка, використовуйте формат 122-450 або 150-220...")
        return False


def validate_ticket_amount(amount_raw):
    try:
        amount_range = [int(a) for a in amount_raw.split('-')]
        if len(amount_range) == 2 and amount_range[0] < amount_range[1]:
            return amount_range
    except ValueError:
        pass
    print("Недійсний діапазон квитків. Будь ласка спробуйте ще раз.")
    return None


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
    while True:
        price_raw = input('Ціновий діапазон (наприклад, 122-450 або 150-220): ')
        price = validate_price_range(price_raw)
        if price: break
    while True:
        amount_raw = input('Діапазон кількості квитків (наприклад, 1-4 або 2-5): ')
        amount = validate_ticket_amount(amount_raw)
        if amount: break
    
    driver = create_new_connection(proxy)
    time.sleep(2)
    try:
        tabs = driver.window_handles
        driver.switch_to.window(tabs[1])
        driver.close()
        driver.switch_to.window(tabs[0])
    except: pass
    vpn_url = ''
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
        if check_for_element(driver, "//h1[contains(text(),'Access Denied')]", xpath=True):
            if proxy == 'vpn': reconnect_vpn(driver, vpn_url)
            elif proxy_url: change_ip(proxy_url)
        time.sleep(2)
        ticket_add_buttons = []
        is_bot = check_for_element(driver, 'div[class="BotProtectionCard-Inner js-BotProtectionModalCardContent"]')
        if is_bot: 
            check_for_element(driver, 'button[class="js-BotProtectionModalButton1 js-BotProtectionModalButtonTrigger BotProtectionCard-Button Button-super Button-small Button"]', click=True)
            wait_for_element(driver, 'button[class="js-BotProtectionModalButton2 js-BotProtectionModalButtonTrigger BotProtectionCard-Button Button-super Button-small Button"]', click=True, timeout=1)
        event_list = wait_for_elements(driver, '#EventDetailsAndListingCard > div:nth-child(4) > div:nth-child(3) > div[data-offer-id]')
        if not event_list: continue
        necessary_tickets = []
        captcha_count = 0
        for event in event_list:
            price_raw = check_for_element(event, '.moneyValueFormat')
            price_el = 0
            if price_raw: 
                try:
                    price_el = float(price_raw.text.replace(',', '.'))
                except: continue
            amount_raw = check_for_element(event, 'span[class="EventEntryRow EventEntryRow-inDetailB NumberOfTicketsInOffer"]')
            amount_raw_2 = check_for_element(event, 'div[class="Dropdown-Container js-Dropdown-Container NumberOfTicketsDropdown"] option:last-child')
            if amount_raw_2: print(amount_raw_2.text)
            #div[class="OfferEntry-Overlay js-OfferEntry-Overlay"]
            event_amount = 0
            if amount_raw: event_amount = amount_raw.text
            if (price[0] <= price_el and price_el <= price[1]) and \
            (amount[0] <= int(event_amount) and amount[1] >= int(event_amount)): necessary_tickets.append(event)
        if not necessary_tickets:
            print('No tickets found')
            continue
        necessary_ticket = random.choice(necessary_tickets)
        if necessary_ticket:
            driver.execute_script("arguments[0].scrollIntoView();", necessary_ticket)
            driver.execute_script("arguments[0].click();", necessary_ticket)
        else: continue
        for _ in range(1, 5):
            buy_button = wait_for_element(driver, 'button[class="js-checkBarcodesForAutomatedReprint js-detailCSubmitButton Button-super Button-superDetailC Button"]', timeout=2, click=True)
            if check_for_element(driver, 'div[style*="visibility: visible;"][style*="position: absolute;"] iframe[title][style*="width"][style*="height"]'): 
                captcha_count += 1
                break
            time.sleep(1)
            
        
        while wait_for_element(driver, 'div[style*="visibility: visible;"][style*="position: absolute;"] iframe[title][style*="width"][style*="height"]', timeout=5): 
            time.sleep(1)
            captcha_count += 1
            if captcha_count >= 90: break
            continue
        
        if wait_for_element(driver, 'div[class="ErrorMessage js-checkBarcodesForAutomatedReprintErrorMessage"]', timeout=5):
            driver.back()
            print('no ticket for match')
            continue
        while check_for_element(driver, 'div[style*="visibility: visible;"][style*="position: absolute;"] iframe[title][style*="width"][style*="height"]'): 
            time.sleep(1)
            captcha_count += 1
            if captcha_count >= 90: break
            continue
        while True:
            if check_for_element(driver, '#spinner[style="display: none;"]'): break
            elif not check_for_element(driver, '#spinner'): break
            time.sleep(1)
            continue

        
        if check_for_element(driver, 'div[class="cc-layer-box full-screen-xs theme-text-variant-color js-cc-layer-box"][style="display: block;"]'):
            check_for_element(driver, 'button[data-qa="ccNoTicketsAvailableBackToDetailbBtn"]', click=True)
            check_for_element(driver, '#offerList-headline', click=True, debugMode=True)
            continue
    
        if 'checkout' in driver.current_url:
            time.sleep(1)
            data = collect_data(driver)
            
            post_request(data)
            post_request(data=data, endpoint='/api/create-ticket/', port='8000')
            data, fs = sf.read('notify.mp3', dtype='float32')  
            sd.play(data, fs)
            status = sd.wait()
            input('continue?')
        print("No Tickets Available")
        continue
