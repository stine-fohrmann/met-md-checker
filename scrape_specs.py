from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import json


url = 'https://adc.met.no/submit-data-as-netcdf-cf'


# Start webdriver headless
options = Options()
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)

driver.get(url)

# Get minimal set of required attrs
minimal_attrs_id = 'MinimalsetofattributesrequiredandparsedbyADC21requiredfields'
minimal_attrs_table = driver.find_element(By.ID, minimal_attrs_id).find_element(By.XPATH, '../..').find_element(By.CSS_SELECTOR, f'table')

# Extract info on minimal required attrs
rows = minimal_attrs_table.find_elements(By.CSS_SELECTOR, 'tr')[1:]
attrs_list = []
for row in rows:
    cells = row.find_elements(By.CSS_SELECTOR, 'td')
    attrs_list.append({
        'name':         cells[0].get_attribute('textContent'),
        'type':         cells[1].get_attribute('textContent'),
        'description':  cells[2].get_attribute('textContent'),
        'comments':     cells[3].get_attribute('textContent'),
        'requirements': cells[4].get_attribute('textContent')
    })

# Save to json
with open("adc-checker/minimal_attrs.json", "w") as f:
    json.dump(attrs_list, f)

driver.quit()