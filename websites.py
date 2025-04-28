import requests
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import schedule
import time
from dotenv import load_dotenv
import os

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

# Function to scrape the vacancies
def scrape_vianet_vacancies(url):
    print("Starting the script...")

    try:
        print("Attempting to scrape data...")
        
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Failed to fetch page, Status code: {response.status_code}")
            return
        
        print(f"Successfully fetched the page! Response code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')

        vacancies = soup.find_all('div', class_='vacancy-grid-block')

        if not vacancies:
            print("No job vacancies found. Check the HTML structure.")
            return

        jobs = []

        for vacancy in vacancies:
            try:
                title = vacancy.find('h5').text.strip()

                details = vacancy.find('div', class_='vacancy-details')
                all_divs = details.find_all('div') if details else []

                job_data = {
                    'Title': title,
                    'Published Date': '',
                    'Deadline': '',
                    'Job Level': '',
                    'Number of Vacancies': '',
                    'Qualification': '',
                    'Experience': '',
                    'Contract': '',
                    'Location': '',
                    'Apply Link': ''
                }

                for div in all_divs:
                    text = div.get_text(strip=True)
                    if 'Published Date:' in text:
                        job_data['Published Date'] = text.replace('Published Date:', '').strip()
                    elif 'Application Deadline:' in text:
                        job_data['Deadline'] = text.replace('Application Deadline:', '').strip()
                    elif 'Job Level:' in text:
                        job_data['Job Level'] = text.replace('Job Level:', '').strip()
                    elif 'Number of Vacancy(ies):' in text:
                        job_data['Number of Vacancies'] = text.replace('Number of Vacancy(ies):', '').strip()
                    elif 'Qualification:' in text:
                        job_data['Qualification'] = text.replace('Qualification:', '').strip()
                    elif 'Experience:' in text:
                        job_data['Experience'] = text.replace('Experience:', '').strip()
                    elif 'Contract of Employment:' in text:
                        job_data['Contract'] = text.replace('Contract of Employment:', '').strip()
                    elif 'Job Location:' in text:
                        job_data['Location'] = text.replace('Job Location:', '').strip()

                apply_link_tag = vacancy.find('a', class_='btn')
                if apply_link_tag and apply_link_tag.has_attr('href'):
                    job_data['Apply Link'] = apply_link_tag['href']
                else:
                    job_data['Apply Link'] = 'No Apply Link Found'

                jobs.append(job_data)
            except Exception as e:
                print(f"Error extracting vacancy details: {e}")
        
        # Save the scraped data to Excel
        df = pd.DataFrame(jobs)
        file_name = 'vianet_jobs.xlsx'
        df.to_excel(file_name, index=False)

        print(f"✅ Scraped {len(jobs)} jobs and saved to 'vianet_jobs.xlsx'")

        # Email body content
        body = "Please find the attached file with the latest job vacancies scraped from websites."

        # Send the email with the file attached
        send_email('Job Vacancies', body, file_name)

        print("Scraping and email sending completed!")

    except Exception as e:
        print(f"Error occurred: {e}")


# Schedule the task to run daily at 11:00 AM
scrape_vianet_vacancies(url='https://www.vianet.com.np/vacancy/')
#schedule.every().day.at("11:00").do(scrape_vianet_vacancies, url='https://www.vianet.com.np/vacancy/')

# Run the task once
scrape_vianet_vacancies(url='https://www.vianet.com.np/vacancy/')

