import re
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


sys.stdout.reconfigure(encoding="utf-8")

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=chrome_options)


try:
    driver.get("https://www.amazon.in")

    search_box = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.ID, "twotabsearchtextbox"))
    )
    search_box.send_keys("mobile phones")
    search_box.send_keys(Keys.ENTER)

    product_card_locator = (
        By.CSS_SELECTOR,
        "div[data-component-type='s-search-result']",
    )
    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located(product_card_locator)
    )
    product_cards = driver.find_elements(*product_card_locator)

    matching_products = []
    seen_names = set()

    for product_card in product_cards:
        price_elements = product_card.find_elements(
            By.CSS_SELECTOR, "span.a-price span.a-offscreen"
        )
        if not price_elements:
            continue

        displayed_price = (
            price_elements[0].get_attribute("textContent")
            or price_elements[0].text
            or ""
        ).strip()
        numeric_price_text = re.sub(r"\D", "", displayed_price)
        if not numeric_price_text:
            continue

        numeric_price = int(numeric_price_text)
        if numeric_price >= 100000:
            continue

        title_elements = product_card.find_elements(
            By.CSS_SELECTOR, "h2 span"
        )
        product_name = (
            title_elements[0].text.strip()
            if title_elements and title_elements[0].text.strip()
            else "Not available"
        )
        if product_name in seen_names:
            continue
        seen_names.add(product_name)

        rating_elements = product_card.find_elements(
            By.CSS_SELECTOR, "span.a-icon-alt"
        )
        rating = "Not available"
        if rating_elements:
            rating = (
                rating_elements[0].get_attribute("aria-label")
                or rating_elements[0].text
                or "Not available"
            ).strip()

        matching_products.append(
            {
                "name": product_name,
                "rating": rating,
                "price": numeric_price,
                "displayed_price": displayed_price,
            }
        )

    print("\nMatching products under Rs.100,000")
    print("=" * 80)
    for product_number, product in enumerate(matching_products, start=1):
        print(f"\nProduct {product_number}")
        print(f"Name: {product['name']}")
        print(f"Rating: {product['rating']}")
        print(
            f"Price: {product['displayed_price'].replace('₹', 'Rs.')}"
        )

    print(f"\nTotal matching products: {len(matching_products)}")
except TimeoutException:
    print(
        "Timed out while loading Amazon or its search results. "
        "The page may show a CAPTCHA or have changed its layout."
    )
except WebDriverException as error:
    print(f"Browser automation failed: {error}")
finally:
    driver.quit()
