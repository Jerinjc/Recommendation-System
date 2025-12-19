"""
SHL Assessment Scraper.

This module provides functionality to scrape, enrich, and format assessment
data from the SHL product catalog for a recommendation engine API.
"""

import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Official Mapping for Test Types
TEST_TYPE_MAP = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgement",
    "C": "Competencies",
    "D": "Development & 360",
    "E": "Assessment Exercises",
    "K": "Knowledge & Skills",
    "P": "Personality & Behavior",
    "S": "Simulations"
}


def setup_driver():
    """
    Initialize and return a Chrome WebDriver with standard automation options.

    Returns:
        webdriver.Chrome: A configured Selenium WebDriver instance.
    """
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def has_green_dot(cell):
    """
    Check if a table cell contains the green dot status indicator.

    Args:
        cell (WebElement): The Selenium WebElement representing a table cell.

    Returns:
        str: "Yes" if the indicator is found, "No" otherwise.
    """
    indicators = cell.find_elements(By.CSS_SELECTOR, "span[class*='-yes']")
    return "Yes" if len(indicators) > 0 else "No"


def map_test_types_to_list(raw_text):
    """
    Convert shorthand codes into a list of full descriptive strings.

    Args:
        raw_text (str): Shorthand codes from the catalog (e.g., 'C, P').

    Returns:
        list: Full descriptive names based on TEST_TYPE_MAP.
    """
    codes = [c.strip().upper() for c in raw_text.replace(',', ' ').split()
             if c.strip()]
    return [TEST_TYPE_MAP.get(code, code) for code in codes]


def get_clean_duration(text):
    """
    Extract the numeric duration from a descriptive sentence.

    Args:
        text (str): Sentence containing the duration.

    Returns:
        int: Extracted duration in minutes, or 0 if not found.
    """
    if not text:
        return 0
    match = re.search(r'(\d+)', str(text))
    return int(match.group(1)) if match else 0


def fix_encoding(text):
    if not isinstance(text, str):
        return text
    try:
        return text.encode("latin1").decode("utf-8")
    except:
        return text

def main():
    """Execute the data collection, enrichment, and saving process."""
    driver = setup_driver()
    all_assessments = []
    start_offset = 0
    output_path = r"C:\Jerin\SHL\scraper\shl_assessments.csv"

    # Define the required column order
    column_order = [
        "url", "name", "adaptive_support", "description",
        "duration", "remote_support", "test_type"
    ]

    try:
        print("--- PHASE 1: COLLECTING CATALOG LIST ---")
        while len(all_assessments) < 400:
            url = (f"https://www.shl.com/solutions/products/product-catalog/"
                   f"?start={start_offset}&type=1")
            driver.get(url)
            try:
                rows = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, "//tr[@data-entity-id]")
                    )
                )
            except Exception:
                break

            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) < 4:
                    continue
                name_cell = cols[0]
                all_assessments.append({
                    "name": name_cell.text.strip(),
                    "url": name_cell.find_element(
                        By.TAG_NAME, "a"
                    ).get_attribute("href"),
                    "remote_support": has_green_dot(cols[1]),
                    "adaptive_support": has_green_dot(cols[2]),
                    "test_type": map_test_types_to_list(cols[3].text)
                })
            start_offset += 12

        print("\n--- PHASE 2: ENRICHING DATA ---")
        for i, item in enumerate(all_assessments):
            try:
                driver.get(item['url'])
                time.sleep(1.2)

                # 1. Scrape Description
                try:
                    xpath = "//h4[text()='Description']/following-sibling::p"
                    desc = driver.find_element(
                        By.XPATH, xpath
                    ).text.strip()
                    item['description'] = fix_encoding(desc)
                except Exception:
                    item['description'] = "No description found."

                # 2. Scrape Duration
                try:
                    xpath = "//p[contains(text(), 'Time') or contains(text(), 'length')]"
                    sentence = driver.find_element(By.XPATH, xpath).text
                    item['duration'] = get_clean_duration(sentence)
                except Exception:
                    item['duration'] = 0

                # REAL-TIME CONSOLE PRINT (Clean output only)
                print(f"[{i+1}/{len(all_assessments)}] {item['name']}")
                print(f"   Duration: {item['duration']} mins")
                print(f"   Categories: {item['test_type']}")
                print("-" * 50)

            except Exception as error:
                print(f"   Error on {item['name']}: {error}")

    finally:
        driver.quit()

        # Final Formatting and Save
        if all_assessments:
            df = pd.DataFrame(all_assessments)
            # Ensure only required columns exist in specified order
            df = df[column_order]
            """ The scrapper was saving in UTF-8 without BOM previously,
            which caused issues when reading in Excel. So I changed to UTF-8 with BOM so that
            it could be read properly in Excel.
            """
            df.to_csv(output_path, index=False, encoding="utf-8-sig")
            print(f"\nSuccessfully saved {len(df)} records to {output_path}")


if __name__ == "__main__":
    main()