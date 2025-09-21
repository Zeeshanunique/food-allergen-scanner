"""
Barcode Scanner Service for Food Allergen Scanner
"""
import cv2
import numpy as np
from pyzbar import pyzbar
from PIL import Image
import requests
import json
from typing import Dict, Optional, List
import os

class BarcodeScanner:
    """Service for scanning barcodes and retrieving product information"""
    
    def __init__(self):
        # OpenFoodFacts API configuration
        self.openfoodfacts_api = "https://world.openfoodfacts.org/api/v0/product"
        self.barcode_lookup_api = "https://api.upcitemdb.com/prod/trial/lookup"
        
        # Local product database path
        self.local_db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'data', 
            'food_products_db.json'
        )
        
        # Load local database
        self.local_products = self._load_local_database()
    
    def scan_barcode(self, image: Image.Image) -> Optional[str]:
        """
        Scan barcode from PIL Image
        Returns barcode string or None if no barcode found
        """
        try:
            # Convert PIL image to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Scan for barcodes
            barcodes = pyzbar.decode(opencv_image)
            
            if barcodes:
                # Return the first barcode found
                barcode_data = barcodes[0].data.decode('utf-8')
                return barcode_data
            
            # If no barcode found, try preprocessing the image
            return self._scan_with_preprocessing(opencv_image)
            
        except Exception as e:
            print(f"Error scanning barcode: {str(e)}")
            return None
    
    def _scan_with_preprocessing(self, opencv_image) -> Optional[str]:
        """Apply image preprocessing and try scanning again"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply threshold
            _, threshold = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Try scanning the preprocessed image
            barcodes = pyzbar.decode(threshold)
            
            if barcodes:
                return barcodes[0].data.decode('utf-8')
            
            # Try with different threshold
            _, threshold2 = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            barcodes2 = pyzbar.decode(threshold2)
            
            if barcodes2:
                return barcodes2[0].data.decode('utf-8')
                
            return None
            
        except Exception as e:
            print(f"Error in preprocessing: {str(e)}")
            return None
    
    def get_product_info(self, barcode: str) -> Dict:
        """
        Get product information from barcode
        First checks local database, then external APIs
        """
        # Check local database first
        local_info = self._get_local_product_info(barcode)
        if local_info:
            return local_info
        
        # Try OpenFoodFacts API
        openfood_info = self._get_openfoodfacts_info(barcode)
        if openfood_info:
            # Cache the result locally
            self._cache_product_info(barcode, openfood_info)
            return openfood_info
        
        # Try UPC Item DB as fallback
        upc_info = self._get_upc_info(barcode)
        if upc_info:
            self._cache_product_info(barcode, upc_info)
            return upc_info
        
        # Return minimal info if nothing found
        return {
            'barcode': barcode,
            'name': 'Unknown Product',
            'brand': 'Unknown',
            'ingredients': [],
            'allergens': [],
            'source': 'not_found'
        }
    
    def _get_local_product_info(self, barcode: str) -> Optional[Dict]:
        """Get product info from local database"""
        return self.local_products.get(barcode)
    
    def _get_openfoodfacts_info(self, barcode: str) -> Optional[Dict]:
        """Get product info from OpenFoodFacts API"""
        try:
            url = f"{self.openfoodfacts_api}/{barcode}.json"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 1:  # Product found
                    product = data.get('product', {})
                    
                    # Extract ingredients
                    ingredients_text = product.get('ingredients_text', '')
                    ingredients = self._parse_ingredients(ingredients_text)
                    
                    # Extract allergens
                    allergens = product.get('allergens_tags', [])
                    allergens = [a.replace('en:', '').replace('-', ' ') for a in allergens]
                    
                    return {
                        'barcode': barcode,
                        'name': product.get('product_name', 'Unknown Product'),
                        'brand': product.get('brands', 'Unknown'),
                        'ingredients': ingredients,
                        'allergens': allergens,
                        'categories': product.get('categories', ''),
                        'nutrition_score': product.get('nutrition_grades', ''),
                        'image_url': product.get('image_url', ''),
                        'source': 'openfoodfacts'
                    }
            
            return None
            
        except Exception as e:
            print(f"Error fetching from OpenFoodFacts: {str(e)}")
            return None
    
    def _get_upc_info(self, barcode: str) -> Optional[Dict]:
        """Get product info from UPC Item DB API"""
        try:
            params = {'upc': barcode}
            response = requests.get(self.barcode_lookup_api, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('code') == 'OK' and data.get('items'):
                    item = data['items'][0]
                    
                    return {
                        'barcode': barcode,
                        'name': item.get('title', 'Unknown Product'),
                        'brand': item.get('brand', 'Unknown'),
                        'ingredients': [],  # UPC DB doesn't provide ingredients
                        'allergens': [],
                        'category': item.get('category', ''),
                        'description': item.get('description', ''),
                        'source': 'upcitemdb'
                    }
            
            return None
            
        except Exception as e:
            print(f"Error fetching from UPC Item DB: {str(e)}")
            return None
    
    def _parse_ingredients(self, ingredients_text: str) -> List[str]:
        """Parse ingredients text into list"""
        if not ingredients_text:
            return []
        
        # Simple parsing - split by comma and clean
        ingredients = [
            ingredient.strip().lower() 
            for ingredient in ingredients_text.split(',')
            if ingredient.strip()
        ]
        
        # Remove percentages and other annotations
        cleaned_ingredients = []
        for ingredient in ingredients:
            # Remove content in parentheses
            if '(' in ingredient:
                ingredient = ingredient.split('(')[0].strip()
            
            # Remove percentages
            if '%' in ingredient:
                ingredient = ingredient.split('%')[0].strip()
            
            if ingredient:
                cleaned_ingredients.append(ingredient)
        
        return cleaned_ingredients
    
    def _load_local_database(self) -> Dict:
        """Load local product database"""
        try:
            if os.path.exists(self.local_db_path):
                with open(self.local_db_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading local database: {str(e)}")
        
        return {}
    
    def _cache_product_info(self, barcode: str, product_info: Dict):
        """Cache product info to local database"""
        try:
            self.local_products[barcode] = product_info
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.local_db_path), exist_ok=True)
            
            # Save to file
            with open(self.local_db_path, 'w') as f:
                json.dump(self.local_products, f, indent=2)
                
        except Exception as e:
            print(f"Error caching product info: {str(e)}")
    
    def add_custom_product(self, barcode: str, product_info: Dict):
        """Add custom product to local database"""
        self._cache_product_info(barcode, product_info)
    
    def search_products_by_name(self, product_name: str) -> List[Dict]:
        """Search products by name in local database"""
        results = []
        
        search_term = product_name.lower()
        
        for barcode, product in self.local_products.items():
            product_name_lower = product.get('name', '').lower()
            brand_lower = product.get('brand', '').lower()
            
            if (search_term in product_name_lower or 
                search_term in brand_lower):
                results.append(product)
        
        return results
    
    def get_barcode_format(self, barcode: str) -> str:
        """Determine barcode format"""
        if len(barcode) == 12:
            return "UPC-A"
        elif len(barcode) == 13:
            return "EAN-13"
        elif len(barcode) == 8:
            return "EAN-8"
        else:
            return "Unknown"