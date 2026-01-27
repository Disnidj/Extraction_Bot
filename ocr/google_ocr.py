import os
from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from PIL import Image


GOOGLE_APPLICATION_CREDENTIALS = r"C:\Users\AkalankaDias\OneDrive - Algospring (PVT) LTD\Documents\Insurance_Playwright_Compare\ocr\gcp\viva-project-467813-65f5e24b2c67.json"
PROJECT_ID = "viva-project-467813"
LOCATION = "us"
PROCESSOR_ID = "5f80269211a37544"


# Set Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS


def process_document(file_path: str):
    """Processes a document using the Document AI Identity Processor."""

    # Check if the file is an image and convert it to PDF if necessary
    if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
        try:
            image = Image.open(file_path)
            pdf_path = os.path.splitext(file_path)[0] + '.pdf'
            image.save(pdf_path, "PDF")
            file_path = pdf_path
        except Exception as e:
            raise RuntimeError(f"Failed to convert image to PDF: {e}")

    opts = {"api_endpoint": f"{LOCATION}-documentai.googleapis.com"}
    client = documentai.DocumentProcessorServiceClient(client_options=opts)
    name = client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)

    with open(file_path, "rb") as file:
        image_content = file.read()

    raw_document = documentai.RawDocument(content=image_content, mime_type='application/pdf')
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)
    result = client.process_document(request=request)

    return result.document.text

pdf_test1 = r'C:\Users\SanjanaKumarasingha\OneDrive - Algospring (PVT) LTD\Desktop\SPC\passport01\passport\test13\02XBSF46.pdf'
text = process_document(pdf_test1)
print(text)



