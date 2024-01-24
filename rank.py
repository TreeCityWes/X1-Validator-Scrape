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

# Extract Validator Info
validator_info = {}
info_sections = driver.find_elements(By.XPATH, '//div[@class="f-card"]/div[@class="row no-collapse"]')
for section in info_sections:
    # Extracting label and value
    label_elements = section.find_elements(By.CLASS_NAME, 'f-row-label')
    value_elements = section.find_elements(By.CLASS_NAME, 'col')
    if label_elements and value_elements:
        label = label_elements[0].text.strip()
        value = value_elements[0].text.strip()
        validator_info[label] = value

# Write Validator Info to CSV
validator_csv_filename = 'validator_info.csv'
with open(validator_csv_filename, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Label', 'Value'])
    for label, value in validator_info.items():
        writer.writerow([label, value])

# Scrape Delegation Data
data = {}
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
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
            amount = re.sub(r'[^\d.]+', '', amount)
            try:
                amount_float = float(amount)
            except ValueError:
                continue
            unique_key = f"{address}_{created_on}"
            if unique_key not in data:
                data[unique_key] = (address, created_on, amount_float)

driver.quit()

# Sort and Write Delegation Data to CSV
sorted_data = sorted(data.values(), key=lambda x: x[2], reverse=True)
csv_filename = 'delegation_data.csv'
with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Address', 'Created On', 'Amount'])
    writer.writerows(sorted_data)

print(f"Validator data has been saved to {validator_csv_filename}")
print(f"Delegation data has been saved to {csv_filename}")
