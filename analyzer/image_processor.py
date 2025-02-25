from google.cloud import vision
from google.oauth2 import service_account
import io
from django.conf import settings

class ImageProcessor:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient(
            credentials=service_account.Credentials.from_service_account_info({
                "type": "service_account",
                "project_id": "your-project-id",  # You'll need to configure this
                "private_key_id": "",
                "private_key": "",
                "client_email": "",
                "client_id": "",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": ""
            })
        )
    
    def extract_text_from_image(self, image_file):
        """Extract text from an ingredient list image"""
        content = image_file.read()
        image = vision.Image(content=content)
        response = self.client.text_detection(image=image)
        texts = response.text_annotations
        
        if texts:
            extracted_text = texts[0].description
            return extracted_text
        
        return ""