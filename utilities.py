from sendgrid.helpers.mail import Mail, Email, To, Content
import sendgrid
import os
import sys
import pandas as pd

def send_test_email():
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("jim@masinyusane.org")
    to_email = To("jim@masinyusane.org")
    content = Content("text/plain", "This is an important test email")
    mail = Mail(from_email, to_email, "Test email", content).get()
    response = sg.client.mail.send.post(request_body=mail)
    print(response.status_code)

# We need to set root directory so we can find the zz_data_process_23.py file. I should obviously move this into a better named directory, will do so in the future.
root_dir = os.path.abspath(os.path.join(os.getcwd(), '..', '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# IMPORT DATA FOR THE TOOLS

#2023 Data

def import_2023_results():
    # Import dataframes
    df = pd.read_csv("data/2023 Results - Simple (Anonymized).csv")
    return df

def import_2024_results():
    df = pd.read_csv("data/2024 Results - Simple (Anonymized).csv")
    return df


def import_2025_results():
    # Load data
    df = pd.read_csv("data/2025 Results - Simple (Anonymized).csv")

    # Create initial and midline datasets for comparison charts
    initial_df = df[df['submission_date'] < pd.Timestamp('2025-04-15')]
    midline_df = df[df['submission_date'] >= pd.Timestamp('2025-04-15')]
    
    return initial_df, midline_df