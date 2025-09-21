"""
Product Model for Food Allergen Scanner
"""
from datetime import datetime
from typing import List, Dict, Optional
import json

class Product:
    """Product model containing ingredient and nutritional information"""
    
    def __init__(self,
                 barcode: str = "",
                 name: str = "",
                 brand: str = "",
                 ingredients: List[str] = None,
                 allergens: List[str] = None,
                 nutritional_info: Dict = None,
                 category: str = "",
                 serving_size: str = "",
                 expiry_date: Optional[datetime] = None,
                 country_of_origin: str = "",
                 created_at: Optional[datetime] = None):
        
        self.barcode = barcode
        self.name = name
        self.brand = brand
        self.ingredients = ingredients or []
        self.allergens = allergens or []
        self.nutritional_info = nutritional_info or {}
        self.category = category
        self.serving_size = serving_size
        self.expiry_date = expiry_date
        self.country_of_origin = country_of_origin
        self.created_at = created_at or datetime.now()
        self.updated_at = datetime.now()
    
    def add_ingredient(self, ingredient: str):
        """Add an ingredient to the product"""
        if ingredient and ingredient.lower() not in [i.lower() for i in self.ingredients]:
            self.ingredients.append(ingredient)
            self.updated_at = datetime.now()
    
    def remove_ingredient(self, ingredient: str):
        """Remove an ingredient from the product"""
        self.ingredients = [i for i in self.ingredients if i.lower() != ingredient.lower()]
        self.updated_at = datetime.now()
    
    def add_allergen(self, allergen: str):
        """Add an allergen to the product"""
        if allergen and allergen.lower() not in [a.lower() for a in self.allergens]:
            self.allergens.append(allergen)
            self.updated_at = datetime.now()
    
    def contains_ingredient(self, ingredient: str) -> bool:
        """Check if product contains a specific ingredient"""
        return any(ingredient.lower() in ing.lower() or 
                  ing.lower() in ingredient.lower() 
                  for ing in self.ingredients)
    
    def contains_allergen(self, allergen: str) -> bool:
        """Check if product contains a specific allergen"""
        # Check both explicit allergens list and ingredients
        explicit_match = any(allergen.lower() in all.lower() or 
                           all.lower() in allergen.lower() 
                           for all in self.allergens)
        
        ingredient_match = self.contains_ingredient(allergen)
        
        return explicit_match or ingredient_match
    
    def get_risk_level(self, user_allergies: List[str]) -> str:
        """Calculate risk level for a user based on their allergies"""
        high_risk_allergens = []
        moderate_risk_allergens = []
        
        for user_allergy in user_allergies:
            if self.contains_allergen(user_allergy):
                # Check severity (simplified logic)
                if user_allergy.lower() in ['peanuts', 'shellfish', 'tree nuts']:
                    high_risk_allergens.append(user_allergy)
                else:
                    moderate_risk_allergens.append(user_allergy)
        
        if high_risk_allergens:
            return "high"
        elif moderate_risk_allergens:
            return "moderate"
        else:
            return "low"
    
    def get_nutritional_summary(self) -> Dict:
        """Get summarized nutritional information"""
        if not self.nutritional_info:
            return {}
        
        summary = {}
        
        # Common nutritional fields
        fields_of_interest = [
            'calories', 'protein', 'carbohydrates', 'fat', 'sugar', 
            'sodium', 'fiber', 'saturated_fat', 'cholesterol'
        ]
        
        for field in fields_of_interest:
            if field in self.nutritional_info:
                summary[field] = self.nutritional_info[field]
        
        return summary
    
    def is_suitable_for_diet(self, diet_type: str) -> bool:
        """Check if product is suitable for specific diet types"""
        diet_restrictions = {
            'vegetarian': ['meat', 'chicken', 'beef', 'pork', 'fish', 'gelatin'],
            'vegan': ['meat', 'chicken', 'beef', 'pork', 'fish', 'dairy', 'milk', 'eggs', 'honey', 'gelatin'],
            'gluten_free': ['wheat', 'gluten', 'barley', 'rye', 'oats'],
            'dairy_free': ['milk', 'dairy', 'cheese', 'butter', 'cream', 'lactose'],
            'nut_free': ['nuts', 'almonds', 'walnuts', 'peanuts', 'cashews', 'hazelnuts']
        }
        
        restricted_ingredients = diet_restrictions.get(diet_type.lower(), [])
        
        return not any(self.contains_ingredient(restricted) 
                      for restricted in restricted_ingredients)
    
    def to_dict(self) -> Dict:
        """Convert product to dictionary"""
        return {
            'barcode': self.barcode,
            'name': self.name,
            'brand': self.brand,
            'ingredients': self.ingredients,
            'allergens': self.allergens,
            'nutritional_info': self.nutritional_info,
            'category': self.category,
            'serving_size': self.serving_size,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'country_of_origin': self.country_of_origin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_json(self) -> str:
        """Convert product to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Product':
        """Create product from dictionary"""
        product = cls(
            barcode=data.get('barcode', ''),
            name=data.get('name', ''),
            brand=data.get('brand', ''),
            ingredients=data.get('ingredients', []),
            allergens=data.get('allergens', []),
            nutritional_info=data.get('nutritional_info', {}),
            category=data.get('category', ''),
            serving_size=data.get('serving_size', ''),
            country_of_origin=data.get('country_of_origin', '')
        )
        
        # Handle datetime fields
        if data.get('expiry_date'):
            product.expiry_date = datetime.fromisoformat(data['expiry_date'])
        if data.get('created_at'):
            product.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            product.updated_at = datetime.fromisoformat(data['updated_at'])
        
        return product
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Product':
        """Create product from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """String representation of the product"""
        return f"Product(name='{self.name}', brand='{self.brand}', barcode='{self.barcode}')"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"Product(name='{self.name}', brand='{self.brand}', "
                f"ingredients={len(self.ingredients)}, allergens={len(self.allergens)})")