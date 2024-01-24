from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import re

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

url = 'https://pwa-explorer.x1-testnet.xen.network/validator/0x5355cd9c2cb1327a10b853d49a82f8f131e70887'
driver.get(url)

data = []
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait for new page segment to load
    time.sleep(5)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

    # Scrape the data
    table_rows = driver.find_elements(By.XPATH, '//div[@class="table-container"]/table/tbody/tr')
    for row in table_rows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        if cells:
            address = cells[0].text.strip()
            created_on = cells[1].text.strip()
            amount = cells[2].text.strip()
        
            # Remove non-numeric characters (except for the decimal point)
            amount = re.sub(r'[^\d.]+', '', amount)

            try:
                amount_float = float(amount)
            except ValueError:
                print(f"Skipping row: Unable to convert '{amount}' to float")
                continue

            data.append((address, created_on, amount_float))

driver.quit()

# Sort the data by amount (descending)
data.sort(key=lambda x: x[2], reverse=True)

# Write data to CSV
csv_filename = 'scraped_data.csv'
with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Address', 'Created On', 'Amount'])
    writer.writerows(data)

print(f"Data has been saved to {csv_filename}")
