import os
from src.utils.load_yaml import ATTACHMENTS_SAVE_DIR,READ_EMAIL,TENANT,EMAIL_APP,APP_SECRET,SUBJECT
from office365.graph_client import GraphClient
import os
import win32com.client

# async def connect_and_fetch_emails():
#      client = GraphClient.with_client_secret(TENANT, EMAIL_APP, APP_SECRET)
#      user = client.users[READ_EMAIL]
#      # Use search endpoint with filter on subject and isRead
#      messages = user.mail_folders["Inbox"].messages \
#        .filter("contains(subject, 'Medical Insurance') and isRead eq false") \
#        .expand(["attachments"]) \
#        .top(1) \
#        .get() \
#        .execute_query()

#      local_path = ATTACHMENTS_SAVE_DIR

#      folders = user.mail_folders.filter("displayName eq 'Medical'") \
#               .get() \
#               .execute_query()

#      var_mail=False
# #with tempfile.TemporaryDirectory() as local_path:
#      for message in messages:
#                 for attachment in message.attachments:
#                     with open(os.path.join(local_path, attachment.name), "wb") as local_file:
#                         attachment.download(local_file).execute_query()
#                     print("Message attachment downloaded into {0}".format(local_file.name))

        
#                 #message.set_property("isRead", True).update().execute_query()
#                 var_mail=True
#                 message.move(folders[0]).execute_query()
#                 #folders[0].mark_all_items_as_read().execute_query()
#                 print("Draft message is created && moved into {0} folder".format(folders[0]))

#      return var_mail    
               
async def connect_and_fetch_emails():

    # Set folder name and save path
    folder_name = "Inbox"  # Replace with the desired folder name
    save_path = ATTACHMENTS_SAVE_DIR  # Replace with the desired save path
    # Define the subject filter and allowed file extensions
    subject_filter = SUBJECT
    allowed_extensions = [".xlsx", ".xls"]  # Specify allowed file extensions
    
    # Connect to Outlook
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    
    # Access the desired folder (e.g., "Inbox")
    folder = outlook.Folders.Item(1).Folders[folder_name]
    
    # Get messages from the folder
    messages = folder.Items
    messages.Sort("[ReceivedTime]", True)  # Sort emails by received time in descending order
    
    # Ensure save path exists
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    # Variable to track if an email was found
    email_found = False

    # Loop through all messages to find the last unread email with the subject filter
    for message in messages:
        # Process only unread messages
        if message.Unread:
            # Check if the message's subject contains the filter text "Motor Insurance Documents"
            if subject_filter.lower() in message.Subject.lower():
                email_found = True  # Email matching the criteria is found
                # Check if the message has attachments
                if message.Attachments.Count > 0:
                    for attachment in message.Attachments:
                        # Check if the attachment's file extension is in the allowed list
                        if any(attachment.FileName.lower().endswith(ext) for ext in allowed_extensions):

                            print(attachment.FileName)
                            # Save each attachment
                            attachment_path = os.path.join(save_path, attachment.FileName)
                            attachment.SaveAsFile(attachment_path)
                            print(f"Downloaded {attachment.FileName} from '{message.Subject}' to {attachment_path}")
                
                # Mark the message as read after processing
                message.Unread = False
                message.Save()
                break  # Exit after processing the last unread email with matching subject
    
    # If no matching email was found, print a message
    if not email_found:
        print("No unread emails found with the subject containing 'Medical Insurance Documents'.")
        return email_found