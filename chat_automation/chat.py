from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import time
contact = "Hajabarala"
text = "Hey, this message was sent using Selenium"
driver = webdriver.Chrome()
# driver.get("https://web.whatsapp.com")
# print("Scan QR Code, And then Enter")
# input()
# print("Logged In")
# inp_xpath_search = "//input[@title='Search or start new chat']"
# input_box_search = WebDriverWait(driver,50).until(lambda driver: driver.find_element_by_xpath(inp_xpath_search))
# input_box_search.click()
# time.sleep(2)
# input_box_search.send_keys(contact)
# time.sleep(2)
# selected_contact = driver.find_element_by_xpath("//span[@title='"+contact+"']")
# selected_contact.click()
# inp_xpath = '//div[@class="_2S1VP copyable-text selectable-text"][@contenteditable="true"][@data-tab="1"]'
# input_box = driver.find_element_by_xpath(inp_xpath)
# time.sleep(2)
# input_box.send_keys(text + Keys.ENTER)
# time.sleep(2)
# driver.quit()

# driver = webdriver.Chrome('/home/saket/Downloads/chromedriver')
  
driver.get("https://web.whatsapp.com/")
wait = WebDriverWait(driver, 600)
  
# Replace 'Friend's Name' with the name of your friend 
# or the name of a group 
target = '"Neermegha"'
  
# Replace the below string with your own message
text = "Greetings Hooman"
  
x_arg = '//span[contains(@title,' + target + ')]'
group_title = wait.until(EC.presence_of_element_located((
    By.XPATH, x_arg)))
group_title.click()
inp_xpath = '//div[@class="input"][@dir="auto"][@data-tab="1"]'
print('locating input box')
## <div class="_2_1wd copyable-text selectable-text" contenteditable="true" data-tab="6" dir="ltr" spellcheck="true">hello world</div>
inp_xpath = '//div[@class="_2A8P4"]'
input_box = driver.find_element_by_xpath(inp_xpath)
time.sleep(2)
input_box.send_keys(text + Keys.ENTER)

# input_box = wait.until(EC.presence_of_element_located((
#     By.XPATH, inp_xpath)))
# print(f'input box located.')
# for i in range(100):
#     print(f"send attempt {i}")
#     input_box.send_keys(string + Keys.ENTER)
#     time.sleep(1)

