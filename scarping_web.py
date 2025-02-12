from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import getpass

# Set up Chrome options
options = webdriver.ChromeOptions()

# You can add any additional options here, like headless mode:
# options.add_argument('--headless')  # Uncomment to run in headless mode

# Set up ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open a webpage
driver.get('https://notebooklm.google.com/notebook/0de77a7f-3141-46a9-9680-a8c947a4ca74')

# Wait for the page to load
time.sleep(2)

# Enter the email
email_field = driver.find_element(By.ID, "identifierId")
email_field.send_keys("haviethung300409@gmail.com")
email_field.send_keys(Keys.RETURN)

# Wait for the password field to appear
time.sleep(2)

password = getpass.getpass("Enter your password: ")

# Enter the password
password_field = driver.find_element(By.NAME, "Passwd")
password_field.send_keys(password)
password_field.send_keys(Keys.RETURN)

# Wait for login to complete
time.sleep(5)

# Check if login was successful
if "myaccount.google.com" in driver.current_url:
    print("Login successful!")
else:
    print("Login failed.")

# Close the browser
# driver.quit()