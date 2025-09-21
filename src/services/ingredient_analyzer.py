"""
Ingredient Analyzer Service for Food Allergen Scanner
"""
from typing import List, Dict, Optional
import re
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.allergy_checker import AllergyChecker
from models.user_profile import UserProfile

class IngredientAnalyzer:
    """Service for analyzing ingredients against user allergies"""
    
    def __init__(self):
        self.allergy_checker = AllergyChecker()
        
        # Ingredient processing patterns
        self.processing_patterns = {
            'percentage': r'\b\d+\.?\d*%',
            'parentheses': r'\([^)]*\)',
            'brackets': r'\[[^\]]*\]',
            'additives': r'E\d{3,4}',
            'preservatives': r'(preservative|antioxidant|emulsifier|stabilizer):\s*',
            'allergen_warnings': r'(may contain|contains|produced in facility)',
        }
        
        # Common ingredient aliases and variations
        self.ingredient_aliases = {
            'sugar': ['glucose', 'fructose', 'sucrose', 'dextrose', 'corn syrup', 'high fructose corn syrup'],
            'salt': ['sodium chloride', 'sea salt', 'rock salt'],
            'oil': ['vegetable oil', 'sunflower oil', 'palm oil', 'rapeseed oil', 'canola oil'],
            'flour': ['wheat flour', 'white flour', 'enriched flour', 'all-purpose flour'],
            'milk': ['whole milk', 'skim milk', 'milk powder', 'dairy'],
            'egg': ['whole egg', 'egg white', 'egg yolk', 'dried egg']
        }
        
        # Ingredient severity scoring
        self.ingredient_scores = {
            'artificial': -10,
            'natural': 5,
            'organic': 10,
            'preservative': -5,
            'additive': -3,
            'whole grain': 8,
            'refined': -2
        }
    
    def analyze_ingredients(self, ingredients_text: str, user_profile: UserProfile) -> Dict:
        """
        Comprehensive analysis of ingredients against user profile
        """
        # Parse and clean ingredients
        ingredients = self._parse_ingredients(ingredients_text)
        
        if not ingredients:
            return {
                'error': 'No ingredients found to analyze',
                'risk_level': 'unknown',
                'recommendations': ['Please provide ingredient information']
            }
        
        # Perform allergy check
        allergy_analysis = self.allergy_checker.check_allergens(ingredients, user_profile)
        
        # Analyze ingredient quality
        quality_analysis = self._analyze_ingredient_quality(ingredients)
        
        # Check for hidden allergens
        hidden_allergens = self._detect_hidden_allergens(ingredients, user_profile)
        
        # Generate nutritional insights
        nutritional_insights = self._analyze_nutritional_content(ingredients)
        
        # Combine all analyses
        comprehensive_analysis = {
            **allergy_analysis,
            'ingredient_quality': quality_analysis,
            'hidden_allergens': hidden_allergens,
            'nutritional_insights': nutritional_insights,
            'processed_ingredients': ingredients,
            'total_ingredients': len(ingredients)
        }
        
        # Enhance recommendations
        comprehensive_analysis['recommendations'] = self._generate_enhanced_recommendations(
            comprehensive_analysis, user_profile
        )
        
        return comprehensive_analysis
    
    def _parse_ingredients(self, ingredients_text: str) -> List[str]:
        """Parse and clean ingredients text"""
        if not ingredients_text or not ingredients_text.strip():
            return []
        
        # Convert to lowercase for processing
        text = ingredients_text.lower().strip()
        
        # Remove common patterns that interfere with parsing
        for pattern_name, pattern in self.processing_patterns.items():
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Split by common separators
        separators = [',', ';', '\\n', '\\r', '|']
        ingredients = [text]
        
        for separator in separators:
            new_ingredients = []
            for ingredient in ingredients:
                new_ingredients.extend([part.strip() for part in ingredient.split(separator)])
            ingredients = new_ingredients
        
        # Clean each ingredient
        cleaned_ingredients = []
        for ingredient in ingredients:
            ingredient = ingredient.strip()
            if ingredient and len(ingredient) > 1:  # Skip empty or single character entries
                # Remove leading numbers, dots, and dashes
                ingredient = re.sub(r'^[\d\.\-\s]*', '', ingredient)
                
                # Remove trailing punctuation
                ingredient = ingredient.rstrip('.,;:')
                
                if ingredient:
                    cleaned_ingredients.append(ingredient)
        
        return cleaned_ingredients
    
    def _analyze_ingredient_quality(self, ingredients: List[str]) -> Dict:
        """Analyze the quality and healthiness of ingredients"""
        quality_score = 0
        quality_factors = {
            'artificial_ingredients': [],
            'natural_ingredients': [],
            'preservatives': [],
            'additives': [],
            'whole_foods': [],
            'processed_foods': []
        }
        
        artificial_indicators = [
            'artificial', 'synthetic', 'modified', 'hydrolyzed', 
            'monosodium glutamate', 'msg', 'high fructose corn syrup'
        ]
        
        natural_indicators = [
            'natural', 'organic', 'whole', 'fresh', 'pure', 'raw'
        ]
        
        preservative_indicators = [
            'preservative', 'sodium benzoate', 'potassium sorbate', 
            'bht', 'bha', 'tbhq', 'sulfite'
        ]
        
        additive_indicators = [
            'color', 'coloring', 'dye', 'flavor', 'flavoring', 
            'emulsifier', 'stabilizer', 'thickener'
        ]
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            
            # Check for artificial ingredients
            if any(indicator in ingredient_lower for indicator in artificial_indicators):
                quality_factors['artificial_ingredients'].append(ingredient)
                quality_score -= 5
            
            # Check for natural ingredients
            elif any(indicator in ingredient_lower for indicator in natural_indicators):
                quality_factors['natural_ingredients'].append(ingredient)
                quality_score += 3
            
            # Check for preservatives
            if any(indicator in ingredient_lower for indicator in preservative_indicators):
                quality_factors['preservatives'].append(ingredient)
                quality_score -= 2
            
            # Check for additives
            if any(indicator in ingredient_lower for indicator in additive_indicators):
                quality_factors['additives'].append(ingredient)
                quality_score -= 1
            
            # Check if it's a whole food
            whole_foods = [
                'water', 'salt', 'sugar', 'flour', 'oil', 'milk', 'egg', 
                'meat', 'chicken', 'beef', 'fish', 'vegetable', 'fruit'
            ]
            if any(food in ingredient_lower for food in whole_foods):
                quality_factors['whole_foods'].append(ingredient)
                quality_score += 1
        
        # Determine quality category
        if quality_score >= 10:
            quality_category = 'excellent'
        elif quality_score >= 5:
            quality_category = 'good'
        elif quality_score >= 0:
            quality_category = 'fair'
        elif quality_score >= -5:
            quality_category = 'poor'
        else:
            quality_category = 'very_poor'
        
        return {
            'quality_score': quality_score,
            'quality_category': quality_category,
            'quality_factors': quality_factors,
            'total_artificial': len(quality_factors['artificial_ingredients']),
            'total_natural': len(quality_factors['natural_ingredients']),
            'total_preservatives': len(quality_factors['preservatives']),
            'total_additives': len(quality_factors['additives'])
        }
    
    def _detect_hidden_allergens(self, ingredients: List[str], user_profile: UserProfile) -> List[str]:
        """Detect allergens that might be hidden under different names"""
        hidden_allergens = []
        
        if not user_profile or not user_profile.allergies:
            return hidden_allergens
        
        # Common hidden allergen sources
        hidden_sources = {
            'dairy': [
                'casein', 'whey', 'lactose', 'lactoglobulin', 'lactalbumin',
                'ghee', 'butter flavor', 'cream flavor', 'milk solids'
            ],
            'egg': [
                'albumin', 'globulin', 'lecithin', 'lysozyme', 'ovalbumin',
                'egg whites', 'egg substitute'
            ],
            'soy': [
                'lecithin', 'tocopherol', 'vegetable protein', 'vegetable oil',
                'natural flavor' # sometimes soy-based
            ],
            'wheat': [
                'modified food starch', 'vegetable protein', 'malt', 
                'dextrin', 'maltodextrin', 'starch'
            ],
            'peanuts': [
                'arachis oil', 'groundnut oil', 'beer nuts', 'monkey nuts'
            ],
            'tree_nuts': [
                'natural flavoring', 'marzipan', 'nougat', 'praline'
            ]
        }
        
        for user_allergy in user_profile.allergies:
            allergy_lower = user_allergy.lower()
            
            # Find matching allergen category
            for allergen_category, hidden_names in hidden_sources.items():
                if allergen_category in allergy_lower or allergy_lower in allergen_category:
                    # Check ingredients for hidden sources
                    for ingredient in ingredients:
                        ingredient_lower = ingredient.lower()
                        for hidden_name in hidden_names:
                            if hidden_name in ingredient_lower:
                                hidden_allergens.append(f"{ingredient} (hidden {allergen_category})")
                                break
        
        return list(set(hidden_allergens))  # Remove duplicates
    
    def _analyze_nutritional_content(self, ingredients: List[str]) -> Dict:
        """Analyze nutritional aspects of ingredients"""
        nutritional_analysis = {
            'high_sodium_ingredients': [],
            'high_sugar_ingredients': [],
            'healthy_ingredients': [],
            'fiber_sources': [],
            'protein_sources': [],
            'vitamin_sources': [],
            'mineral_sources': []
        }
        
        # Categorize ingredients by nutritional value
        high_sodium = ['salt', 'sodium', 'monosodium glutamate', 'msg', 'baking soda']
        high_sugar = ['sugar', 'glucose', 'fructose', 'corn syrup', 'honey', 'molasses']
        healthy_foods = ['whole grain', 'vegetable', 'fruit', 'nuts', 'seeds', 'beans']
        fiber_sources = ['whole grain', 'oats', 'bran', 'fiber', 'cellulose']
        protein_sources = ['protein', 'meat', 'chicken', 'fish', 'egg', 'milk', 'nuts', 'beans']
        vitamin_sources = ['vitamin', 'ascorbic acid', 'tocopherol', 'beta carotene']
        mineral_sources = ['iron', 'calcium', 'zinc', 'magnesium', 'potassium']
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            
            if any(sodium in ingredient_lower for sodium in high_sodium):
                nutritional_analysis['high_sodium_ingredients'].append(ingredient)
            
            if any(sugar in ingredient_lower for sugar in high_sugar):
                nutritional_analysis['high_sugar_ingredients'].append(ingredient)
            
            if any(healthy in ingredient_lower for healthy in healthy_foods):
                nutritional_analysis['healthy_ingredients'].append(ingredient)
            
            if any(fiber in ingredient_lower for fiber in fiber_sources):
                nutritional_analysis['fiber_sources'].append(ingredient)
            
            if any(protein in ingredient_lower for protein in protein_sources):
                nutritional_analysis['protein_sources'].append(ingredient)
            
            if any(vitamin in ingredient_lower for vitamin in vitamin_sources):
                nutritional_analysis['vitamin_sources'].append(ingredient)
            
            if any(mineral in ingredient_lower for mineral in mineral_sources):
                nutritional_analysis['mineral_sources'].append(ingredient)
        
        return nutritional_analysis
    
    def _generate_enhanced_recommendations(self, analysis: Dict, user_profile: UserProfile) -> List[str]:
        """Generate comprehensive recommendations based on analysis"""
        recommendations = analysis.get('recommendations', [])
        
        # Add quality-based recommendations
        quality_category = analysis.get('ingredient_quality', {}).get('quality_category', 'fair')
        
        if quality_category == 'very_poor':
            recommendations.append("🚫 This product contains many artificial and processed ingredients")
            recommendations.append("💡 Consider looking for more natural alternatives")
        elif quality_category == 'poor':
            recommendations.append("⚠️ This product contains several artificial ingredients")
            recommendations.append("💡 Look for products with fewer additives")
        elif quality_category == 'excellent':
            recommendations.append("✅ This product contains mostly natural, wholesome ingredients")
        
        # Add nutritional recommendations
        nutritional = analysis.get('nutritional_insights', {})
        
        if nutritional.get('high_sodium_ingredients'):
            recommendations.append("🧂 High sodium content detected - monitor salt intake")
        
        if nutritional.get('high_sugar_ingredients'):
            recommendations.append("🍭 High sugar content detected - consume in moderation")
        
        if nutritional.get('healthy_ingredients'):
            recommendations.append("🥗 Contains beneficial ingredients: " + 
                                 ', '.join(nutritional['healthy_ingredients'][:3]))
        
        # Add hidden allergen warnings
        hidden_allergens = analysis.get('hidden_allergens', [])
        if hidden_allergens:
            recommendations.append("🔍 Hidden allergens detected:")
            recommendations.extend([f"  • {allergen}" for allergen in hidden_allergens[:3]])
        
        # Add alternative suggestions if high risk
        if analysis.get('risk_level') in ['high', 'moderate']:
            detected_allergens = analysis.get('detected_allergens', [])
            alternatives = self.allergy_checker.get_safe_alternatives(detected_allergens)
            if alternatives:
                recommendations.append("🔄 Consider these alternatives:")
                recommendations.extend([f"  • {alt}" for alt in alternatives[:3]])
        
        return recommendations