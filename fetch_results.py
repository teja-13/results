import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def is_website_live(url):
    """
    Check if the website is live by sending a HEAD request.
    """
    try:
        response = requests.head(url, timeout=10)  # Send a HEAD request to check if the page exists
        if response.status_code == 200:
            print(f"Website is live! Status Code: {response.status_code}")
            return True
        else:
            print(f"Website returned status code: {response.status_code}. Retrying in 1 minute...")
            return False
    except requests.RequestException as e:
        print(f"Website is not accessible: {e}. Retrying in 1 minute...")
        return False

def fetch_results(url, roll_numbers, output_file):
    """
    Fetch results for a list of roll numbers from a results website.
    """
    while True:
        # Check if the website is live every 1 minute
        if is_website_live(url):
            print("Website is live. Launching browser to fetch results...")
            
            # Initialize Selenium WebDriver
            driver = webdriver.Chrome()

            try:
                # Open the results page
                driver.get(url)
                time.sleep(2)  # Wait for the page to load

                # Open the output file to save results
                with open(output_file, "w", encoding="utf-8") as file:
                    for roll_no in roll_numbers:
                        try:
                            # Enter roll number
                            roll_input = driver.find_element(By.ID, "rno")  # Update with actual ID
                            roll_input.clear()
                            roll_input.send_keys(roll_no)
                            time.sleep(2)

                            # Wait for the result to load
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.ID, "resdata"))
                            )

                            # Fetch and save the result
                            result_div = driver.find_element(By.ID, "resdata")  # Update with actual ID
                            result_text = result_div.text
                            file.write(f"Roll Number: {roll_no}\nResult: {result_text}\n\n")
                            print(f"Fetched result for Roll Number: {roll_no}")

                        except Exception as e:
                            print(f"Failed to fetch result for Roll Number: {roll_no}: {e}")

                print("Results successfully fetched and stored in the file.")
                break  # Exit the loop after fetching results
            finally:
                # Close the browser
                driver.quit()
        else:
            # Wait 1 minute before retrying
            time.sleep(60)

# Example Usage
url = "https://www.vvitguntur.com/results/R23/Y23_2-1_REGULAR_JAN25/results.html"
roll_numbers = ["23bq1a0524", "23bq1a4218", "23bq1a0566", "23bq1a0579", "23bq1a05b6", "23bq1a05f5"]  # Replace with actual roll numbers
output_file = "results.txt"

fetch_results(url, roll_numbers, output_file)
