import time
from src.utils.logger import logger
import win32com.client as win32

USER_EMAIL = "wathsala.d@algospring.com"
DEVELOPER_EMAIL = "wathsala.d@algospring.com"

def send_error_email(screenshot_path ,insurance_name, saved_msg):
    try:
        # Clean up insurance_name and saved_msg to remove extra spaces or dashes
        insurance_name = insurance_name.strip()
        saved_msg = " - ".join(part.strip() for part in saved_msg.split("-") if part.strip())
        
        # Initialize Outlook application
        outlook = win32.Dispatch("Outlook.Application")
        mail = outlook.CreateItem(0)  # 0 means MailItem

        # Set up email details
        mail.Subject = f"{insurance_name} INSURANCE - {saved_msg}"
        mail.To = USER_EMAIL
        mail.CC = DEVELOPER_EMAIL
        mail.Body = f"{saved_msg}\n\n Invalid Login Occured in {insurance_name}  process. Please Update the password."
        
        # Attach screenshot
        mail.Attachments.Add(screenshot_path)
        
        # Send the email
        mail.Send()
        logger.info("Error email sent successfully")
        
        time.sleep(1)
        
        # Exit the program after email is sent
        raise Exception("Error email sent successfully")
        
    except Exception as e:
        logger.error("Failed to send error email", exc_info=True)