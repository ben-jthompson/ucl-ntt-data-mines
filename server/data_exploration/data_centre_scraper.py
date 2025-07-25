from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup
import pandas as pd
import time

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def dismiss_cookie_banner(driver):
    try:
        wait = WebDriverWait(driver, 5)
        close_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#onetrust-close-btn-container button.onetrust-close-btn-handler")))
        close_btn.click()
        print("Cookie banner closed")
        time.sleep(2)  # give time for banner to disappear
    except TimeoutException:
        print("Cookie banner close button not found or already dismissed.")


def parse_results_page(soup):
    base_url = "https://www.datacenters.com"
    results = []

    for card in soup.select("a.flex.flex-col.rounded.border"):
        try:
            link = base_url + card["href"]

            provider = card.select_one("div.text-xs.text-gray-500")
            name = card.select_one("div.font-medium")
            location = card.select("div.text-xs.text-gray-500")

            results.append({
                "Name": name.text.strip() if name else "N/A",
                "Provider": provider.text.strip() if provider else "N/A",
                "Location": location[-1].text.strip() if len(location) > 1 else "N/A",
                "Link": link
            })
        except Exception as e:
            print(f"Error: {e}")
            continue

    return results

def get_all_paginated_cards(driver):
    all_cards = []
    page_num = 1

    
    for i in range(9):
        print(f"Scraping page {page_num}")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        cards = parse_results_page(soup)
        all_cards.extend(cards)

        # Click next page
        if i <= 9:
            try:
                next_btn = driver.find_element(By.XPATH,
        "//button[contains(@class, 'Pagination__symbol__')][div[not(contains(@style, 'rotate(180deg)'))]]")
                next_btn.click()
            except (NoSuchElementException, ElementClickInterceptedException) as e:
                print('Exception: ', e)
                break

    
            time.sleep(3)  # Allow next page to load
            page_num+=1
                
            

    return all_cards

def main():
    print("Scraping:")
    driver = setup_driver()
    driver.get("https://www.datacenters.com/locations")

    try:
        # Wait for the search input to be ready and enter the query
        wait = WebDriverWait(driver, 10)
        search_input = wait.until(EC.presence_of_element_located((By.ID, "locations-search")))
        search_input.clear()
        search_input.send_keys("United Kingdom")
        time.sleep(4)

        # Begin paginated scraping
        dismiss_cookie_banner(driver)
        all_data = get_all_paginated_cards(driver)

    finally:
        driver.quit()

    df = pd.DataFrame(all_data)
    df.to_csv("uk_data_centres.csv", index=False)
    print("Scraped and saved to 'uk_data_centres.csv'.")

if __name__ == "__main__":
    main()
