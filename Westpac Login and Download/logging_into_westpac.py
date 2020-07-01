"""Westpac bank login and download. Imports email_module from one of my other projects."""

import os
import time
from datetime import datetime
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from email_module import send_email_365


def main():
    """
    Logs into westpac, downloads bank statement for previous year, and then emails it off
    """
    opts = Options()
    # Adding this so that file downloads are enabled for headless browsing
    opts.add_experimental_option("prefs", {
        "download.default_directory": "/Users/chad/Downloads/",
        "download.prompt_for_download": False,
    })

    # Enabling headless browsing
    opts.add_argument("--headless")
    browser = Chrome(options=opts)

    # This is also to enable file downloads in headless browsing
    browser.command_executor._commands["send_command"] = \
        ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior',
              'params': {'behavior': 'allow', 'downloadPath': "/Users/chad/Downloads/"}}
    browser.execute("send_command", params)

    # Getting the westpac login page
    browser.get('https://banking.westpac.com.au/wbc/banking/handler'
                '?TAM_OP=login&segment=personal&logout=false')

    # Logging in
    browser.find_element_by_xpath('//input[@id="fakeusername"]').send_keys(input('Username:'))
    browser.find_element_by_xpath('//input[@id="password"]').send_keys(input('Password:'))
    browser.find_element_by_xpath('//button[@type="submit" and @id="signin"]').click()

    WebDriverWait(browser, 10).until(EC.presence_of_element_located(
        (By.XPATH, '//h2[contains(text(), "Westpac eSaver")]')))

    browser.get('https://banking.westpac.com.au/secure/banking/reportsandexports/home')

    WebDriverWait(browser, 10).until(EC.presence_of_element_located(
        (By.XPATH, '//a[contains(text(), "Export") and contains(@class, "Transactions")]')))\
        .click()

    # Entering the start and end date for bank statements
    start_date = WebDriverWait(browser, 10).until(EC.presence_of_element_located(
        (By.XPATH, '//input[@id="DateRange_StartDate"]')))

    start_date.clear()
    todays_date = datetime.now().strftime('%d/%m/%Y')
    last_years_date = '{}{}'.format(todays_date[:-4], int(todays_date[-4:])-1)
    start_date.send_keys(last_years_date)

    end_date = browser.find_element_by_xpath('//input[@id="DateRange_EndDate"]')
    end_date.clear()
    end_date.send_keys(todays_date)

    # Clicking the download button
    browser.find_element_by_xpath('//button[@type="submit" and contains(text(), "Export")]')\
        .click()

    # Checking the file has downloaded
    file_path = '/Users/chad/Downloads/Data.csv'
    while not os.path.isfile(file_path):
        time.sleep(1)
        print('stuck')

    browser.quit()

    # Sending email
    print(send_email_365('recipent@email', 'Westpac Test', 'Yeh',
                         'sender@email', 'password', (file_path,)))

    # Removing the downloaded file from downloads folder
    os.remove(file_path)


if __name__ == '__main__':
    main()
