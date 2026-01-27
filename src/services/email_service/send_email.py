from O365 import Account
from src.utils.load_yaml import SEND_EMAIL, MAIL_ZIP_FILES
import win32com.client
import os

# def send_email_with_attachment(recipient_email_algospring, recipient_email_gargash, subject, body, output_filepath, company_list):
#     # O365 account credentials
#     credentials = ('663fc2a3-e388-40bf-9327-ca33a82a4966', 'd1V8Q~ZpVENL~Ms9uDLa.3ryTofrGtP54kBa3aSW')
#     tenant_id = '08ac4503-bab9-4ee3-b714-6c3af55ef9b2'
    
#     # Authenticate the account
#     account = Account(credentials, auth_flow_type='credentials', tenant_id=tenant_id)
    
#     if account.authenticate():
#         print('Authenticated!')

#         # Create a new email message
#         mailbox = account.mailbox(SEND_EMAIL)
#         message = mailbox.new_message()
#         message.to.add(recipient_email_gargash)
#         message.cc.add(recipient_email_algospring)
#         message.subject = subject
#         message.body = body

#         # Attach the generated comparison report
#         message.attachments.add(output_filepath)
        
#         if 'TAKAFUL EMARAT' in company_list:
#             message.attachments.add(os.path.join(MAIL_ZIP_FILES, "takaful_zip_file.zip"))
            
#         if 'NLGIC COMPANY' in company_list:
#             message.attachments.add(os.path.join(MAIL_ZIP_FILES, "nlgi_zip_file.zip"))
            
#         if 'ORIENT INSURANCE PJSC' in company_list:
#             message.attachments.add(os.path.join(MAIL_ZIP_FILES, "orient_zip_file.zip"))

#         if 'RAK INSURANCE' in company_list:
#             message.attachments.add(os.path.join(MAIL_ZIP_FILES, "rak_zip_file.zip"))
        
#         if 'SUKOON INSURANCE' in company_list:
#             message.attachments.add(os.path.join(MAIL_ZIP_FILES, "sukoon_zip_file.zip"))
            
#         if 'DUBAI NATIONAL INSURANCE' in company_list:
#             message.attachments.add(os.path.join(MAIL_ZIP_FILES, "dni_zip_file.zip"))
        
#         if 'QATAR INSURANCE CO' in company_list:
#             message.attachments.add(os.path.join(MAIL_ZIP_FILES, "qatar_zip_file.zip"))
            
#         # Send the email
#         message.send()
#         print(f"Email sent successfully to {recipient_email_gargash} and {recipient_email_algospring}")
#     else:
#         print("Authentication failed.")


def send_email_with_attachment(to, quo_id, directories):
    # Create an instance of Outlook
    outlook = win32com.client.Dispatch("Outlook.Application")

    # Create a new mail item
    mail = outlook.CreateItem(0)

    # Set email properties
    mail.To = "aruni.j@algospring.com"
    mail.Cc = "wathsala.d@algospring.com"
    mail.Subject = f"Medical Insurance Quotation for Gargash Insurance, Reference No. {quo_id}"

    # Set the body of the email
    mail.Body = (
        "Hello User,\n\n"
        "Please find the attached files for the Gargash Medical Quote Creation for Gargash Insurance, "
        f"under the reference number {quo_id}.\n\n"
        "System version updates are currently in progress to align with the Insurance Portal updates for the year 2025.\n\n"
        "**This is an auto-generated email; please do not reply.**\n\n"
        "Thank you!"
    )

    # Add attachments from the specified directories
    attachments_added = False
    for directory in directories:
        if os.path.isdir(directory):
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):  # Ensure it's a file
                    mail.Attachments.Add(file_path)
                    attachments_added = True
                    print(f"Added attachment: {file_path}")
        else:
            print(f"Directory does not exist: {directory}")
            raise Exception(f"Directory does not exist: {directory}")

    # Check if any attachments were added
    if not attachments_added:
        print("No attachments added. Please check the directories.")

    # Send the email
    try:
        mail.Send()
        print(f"Email sent to wathsala.d@algospring.com with subject: Medical Insurance Quotation for Gargash Insurance, Reference No. '{quo_id}'")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_email_without_attachment(to, quo_id):
    # Create an instance of Outlook
    outlook = win32com.client.Dispatch("Outlook.Application")

    # Create a new mail item
    mail = outlook.CreateItem(0)

    # Set email properties
    mail.To = "sanjana.k@algospring.com"
    mail.Cc = "aruni.j@algospring.com"
    mail.Cc = "wathsala.d@algospring.com"
    mail.Subject = f"Medical Insurance Failed for Gargash Insurance, Reference No. {quo_id}"

    # Set the body of the email with red text
    mail.HTMLBody = (
        "<p style='color:red;'>Hello,</p>"
        f"<p style='color:red;'>Please notice that the request is failed, under the reference number {quo_id}.</p>"
        "<p style='color:red;'>This is an auto-generated email; please do not reply.</p>"
        "<p style='color:red;'>Thank you.</p>"
    )

    # Send the email
    try:
        mail.Send()
        print(f"Email sent to sanjana.k@algospring.com with subject: Medical Insurance Failed for IIB Insurance, Reference No. '{quo_id}'")
    except Exception as e:
        print(f"Failed to send email: {e}")

