import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import tempfile
from selenium.webdriver.chrome.options import Options
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

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

def send_email_with_attachment(sender_email, receiver_email, email_password, subject, body, file_path):
    """
    Send an email with the specified file as an attachment.
    """
    try:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Add body text
        msg.attach(MIMEText(body, 'plain'))

        # Attach the file
        with open(file_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={file_path}')
            msg.attach(part)

        # Connect to the SMTP server and send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, email_password)
            server.send_message(msg)

        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def fetch_results(url, roll_numbers, output_file):
    """
    Fetch results for a list of roll numbers from a results website.
    """
    while True:
        # Check if the website is live every 1 minute
        if is_website_live(url):
            print("Website is live. Launching browser to fetch results...")

            # Create a temporary directory to avoid conflicts with user data
            temp_dir = tempfile.mkdtemp()

            # Initialize Chrome options for headless mode and user data directory
            chrome_options = Options()
            chrome_options.add_argument(f'--user-data-dir={temp_dir}')  # Set a unique user data directory
            chrome_options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
            chrome_options.add_argument('--disable-gpu')  # Disable GPU acceleration (useful for CI/CD)

            # Initialize Selenium WebDriver with options
            driver = webdriver.Chrome(options=chrome_options)

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

                # Send the file via email
                send_email_with_attachment(
                    sender_email="ch.umachandra@gmail.com",  # Replace with your email
                    receiver_email="umachandra4821@gmail.com",  # Replace with recipient's email
                    email_password="qamb xnme qamo ndfd",  # Replace with your email password or app password
                    subject="Results File",
                    body="Please find the attached results file.",
                    file_path=output_file
                )
                break  # Exit the loop after fetching results
            finally:
                # Close the browser
                driver.quit()
        else:
            # Wait 1 minute before retrying
            time.sleep(60)

# Example Usage
url = "https://www.vvitguntur.com/results/R23/Y23_2-1_REGULAR_DEC24/results.html"
roll_numbers = ["23bq1a0524", "23bq1a4218", "23bq1a0539", "23bq1a0566", "23bq1a0579", "23bq1a05b6", "23bq1a05f5","23bq1a0532","23bq1a0510","23bq1a0507","23bq1a0512","23bq1a0520","23bq1a0523","23bq1a0527","23bq1a0531","23bq1a0535","23bq1a0544","23bq1a0546","23bq1a0554","23bq1a0516","23bq1a0519","23bq1a0573"]  # Replace with actual roll numbers
output_file = "results.txt"

fetch_results(url, roll_numbers, output_file)
