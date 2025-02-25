from pyzbar.pyzbar import decode
from PIL import Image
import io
import requests

class BarcodeScanner:
    def scan_barcode(self, image_file):
        """Scan barcode from image and return barcode value"""
        try:
            image = Image.open(image_file)
            decoded = decode(image)
            if decoded:
                return decoded[0].data.decode('utf-8')
            return None
        except Exception as e:
            print(f"Error scanning barcode: {e}")
            return None
    
    def lookup_product(self, barcode):
        """Look up product information from Open Food Facts API"""
        try:
            response = requests.get(f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 1:
                    product_data = data.get('product', {})
                    return {
                        'name': product_data.get('product_name', 'Unknown Product'),
                        'ingredients_text': product_data.get('ingredients_text', ''),
                        'image_url': product_data.get('image_url', '')
                    }
            return None
        except Exception as e:
            print(f"Error looking up barcode: {e}")
            return None