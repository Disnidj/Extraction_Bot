from src.services.email_service.send_email_new import send_email

# Azure App Credentials
client_id = '663fc2a3-e388-40bf-9327-ca33a82a4966'
client_secret = 'd1V8Q~ZpVENL~Ms9uDLa.TofrGtP54kBa3aSW'
tenant_id = '08ac45-bab9-4ee3-b714-6c3af55ef9b2'

# Email Details
sender_email = 'rpa-dev@lifecareinternational.com'
recipient_email = 'sadika.w@algospring.com'
subject = 'Testing!'
body = "George Best quote: I've stopped, but only while I'm asleep."
attachment_path = r'C:\sadika\solutions\RPA\Lifecare\Azure Portal.docx'

# Call the function
send_email(
    client_id, 
    client_secret, 
    tenant_id, 
    sender_email, 
    recipient_email, 
    subject, 
    body, 
    attachment_path
)
