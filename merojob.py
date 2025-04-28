import requests
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import schedule
import time

# Email details (use your email and password directly)
SENDER_EMAIL = 'sachinsinghey987@gmail.com'  # Your Gmail address
SENDER_PASSWORD = 'dcmf ailt dhuk zeio'  # Your app password
RECIPIENT_EMAIL = 'sachinsinghey987@gmail.com'  # You can send the email to yourself or another recipient
SMTP_SERVER = 'smtp.gmail.com'  # Gmail's SMTP server
SMTP_PORT = 587  # The port to use for sending emails

# Function to send email
def send_email(subject, body, attachment=None):
    try:
        print(f"Attempting to send email with subject: {subject}")

        # Set up the MIME
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject

        # Attach the body of the email
        msg.attach(MIMEText(body, 'plain'))

        # Attach file if it exists
        if attachment:
            print(f"Attaching file: {attachment}")
            with open(attachment, 'rb') as f:
                attach_file = MIMEApplication(f.read(), _subtype="xlsx")
                attach_file.add_header('Content-Disposition', 'attachment', filename=attachment)
                msg.attach(attach_file)

        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        # Send email
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print(f"Email sent to {RECIPIENT_EMAIL} successfully!")

    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to scrape the vacancies from MeroJobs IT & Telecommunication category
def scrape_mero_jobs_vacancies(url):
    print("Starting the script...")

    try:
        print("Attempting to scrape data...")

        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Failed to fetch page, Status code: {response.status_code}")
            return
        
        print(f"Successfully fetched the page! Response code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # Locate job listings based on MeroJobs HTML structure (inspect the page and adjust accordingly)
        vacancies = soup.find_all('div', class_='job-listing')  # Adjust based on actual class used for job listings

        if not vacancies:
            print("No job vacancies found. Check the HTML structure.")
            return

        jobs = []

        for vacancy in vacancies:
            try:
                title = vacancy.find('h3', class_='job-title').text.strip()  # Adjust the tag and class

                # Extract additional job details
                location = vacancy.find('span', class_='location').text.strip() if vacancy.find('span', class_='location') else ''
                posted_date = vacancy.find('span', class_='date-posted').text.strip() if vacancy.find('span', class_='date-posted') else ''
                apply_link = vacancy.find('a', class_='btn-apply')['href'] if vacancy.find('a', class_='btn-apply') else 'No Apply Link Found'

                job_data = {
                    'Title': title,
                    'Location': location,
                    'Posted Date': posted_date,
                    'Apply Link': apply_link
                }

                jobs.append(job_data)
            except Exception as e:
                print(f"Error extracting vacancy details: {e}")
        
        # Save the scraped data to Excel
        df = pd.DataFrame(jobs)
        file_name = 'mero_jobs_telecom.xlsx'
        df.to_excel(file_name, index=False)

        print(f"✅ Scraped {len(jobs)} jobs and saved to 'mero_jobs_telecom.xlsx'")

        # Email body content
        body = "Please find the attached file with the latest job vacancies scraped from MeroJobs (IT & Telecommunication category)."

        # Send the email with the file attached
        send_email('MeroJobs IT & Telecommunication Job Vacancies', body, file_name)

        print("Scraping and email sending completed!")

    except Exception as e:
        print(f"Error occurred: {e}")

# Schedule the task to run once at 11:00 AM
#schedule.every().day.at("11:00").do(scrape_mero_jobs_vacancies, url='https://merojob.com/category/it-telecommunication/')
scrape_mero_jobs_vacancies(url='https://merojob.com/category/it-telecommunication/')

# Run the task once
scrape_mero_jobs_vacancies(url='https://merojob.com/category/it-telecommunication/')

