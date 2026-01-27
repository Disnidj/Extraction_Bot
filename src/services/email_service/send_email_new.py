from O365 import Account

def send_email(
    client_id, 
    client_secret, 
    tenant_id, 
    sender_email, 
    recipient_email, 
    subject, 
    body, 
    attachment_path=None
):
    """
    Sends an email using Microsoft Office 365 API.
    """
    # Set credentials
    credentials = (client_id, client_secret)

    # Create an account object
    account = Account(credentials, auth_flow_type='credentials', tenant_id=tenant_id)

    # Authenticate the account
    if account.authenticate():
        print('Authenticated successfully!')
        
        # Access the sender's mailbox
        mailbox = account.mailbox(sender_email)
        
        # Create a new email message
        m = mailbox.new_message()
        m.to.add(recipient_email)
        m.subject = subject
        m.body = body

        # Add attachment if provided
        if attachment_path:
            m.attachments.add(attachment_path)

        # Send the email
        m.send()
        print('Email sent successfully!')
    else:
        print('Authentication failed! Check credentials.')
