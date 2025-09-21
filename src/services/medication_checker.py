"""
Medication Checker Service for Food Allergen Scanner
"""
from typing import List, Dict, Optional, Tuple
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user_profile import UserProfile

class MedicationChecker:
    """Service for checking food-medication interactions"""
    
    def __init__(self):
        # Load medication interaction database
        self.interactions_db = self._load_interaction_database()
        
        # Common food-medication interactions
        self.known_interactions = {
            'warfarin': {
                'avoid': ['vitamin k', 'green leafy vegetables', 'broccoli', 'spinach', 'kale'],
                'caution': ['alcohol', 'cranberry juice', 'grapefruit'],
                'severity': 'high'
            },
            'aspirin': {
                'avoid': ['alcohol'],
                'caution': ['vitamin e', 'omega-3', 'fish oil', 'garlic supplements'],
                'severity': 'moderate'
            },
            'metformin': {
                'avoid': ['excessive alcohol'],
                'caution': ['high carbohydrate foods', 'sugary drinks'],
                'severity': 'moderate'
            },
            'lisinopril': {
                'avoid': ['potassium supplements', 'salt substitutes'],
                'caution': ['bananas', 'oranges', 'potatoes', 'high potassium foods'],
                'severity': 'moderate'
            },
            'simvastatin': {
                'avoid': ['grapefruit', 'grapefruit juice'],
                'caution': ['red yeast rice', 'niacin', 'alcohol'],
                'severity': 'high'
            },
            'digoxin': {
                'avoid': ['licorice', 'st johns wort'],
                'caution': ['high fiber foods', 'bran'],
                'severity': 'high'
            },
            'levothyroxine': {
                'avoid': ['soy products', 'coffee', 'calcium supplements'],
                'caution': ['iron supplements', 'high fiber foods'],
                'timing': 'take 30-60 minutes before eating',
                'severity': 'moderate'
            },
            'monoamine oxidase inhibitor': {
                'avoid': ['aged cheeses', 'wine', 'beer', 'soy sauce', 'pickled foods', 'smoked meats'],
                'caution': ['chocolate', 'caffeine', 'fava beans'],
                'severity': 'high'
            },
            'tetracycline': {
                'avoid': ['dairy products', 'calcium', 'iron supplements'],
                'caution': ['antacids', 'aluminum', 'magnesium'],
                'timing': 'take 1 hour before or 2 hours after meals',
                'severity': 'moderate'
            },
            'phenytoin': {
                'avoid': ['alcohol'],
                'caution': ['folic acid supplements', 'tube feeding'],
                'severity': 'moderate'
            }
        }
        
        # Medication categories and their interactions
        self.medication_categories = {
            'blood_thinners': {
                'medications': ['warfarin', 'heparin', 'coumadin', 'eliquis', 'xarelto'],
                'food_interactions': ['vitamin k rich foods', 'alcohol', 'cranberry', 'grapefruit'],
                'severity': 'high'
            },
            'antibiotics': {
                'medications': ['tetracycline', 'ciprofloxacin', 'amoxicillin', 'penicillin'],
                'food_interactions': ['dairy products', 'calcium', 'iron'],
                'severity': 'moderate'
            },
            'antidepressants': {
                'medications': ['ssri', 'maoi', 'tricyclic', 'sertraline', 'fluoxetine'],
                'food_interactions': ['alcohol', 'aged foods', 'tyramine rich foods'],
                'severity': 'high'
            },
            'heart_medications': {
                'medications': ['digoxin', 'beta blockers', 'ace inhibitors'],
                'food_interactions': ['potassium', 'sodium', 'alcohol'],
                'severity': 'moderate'
            },
            'diabetes_medications': {
                'medications': ['metformin', 'insulin', 'sulfonylureas'],
                'food_interactions': ['alcohol', 'high sugar foods', 'carbohydrates'],
                'severity': 'moderate'
            }
        }
    
    def check_interactions(self, ingredients: List[str], user_profile: UserProfile) -> Dict:
        """
        Check for food-medication interactions
        Returns detailed interaction analysis
        """
        if not user_profile or not user_profile.medications:
            return {
                'interactions_found': False,
                'total_interactions': 0,
                'high_risk_interactions': [],
                'moderate_risk_interactions': [],
                'low_risk_interactions': [],
                'recommendations': ['No medications listed in profile'],
                'timing_recommendations': []
            }
        
        all_interactions = []
        high_risk_interactions = []
        moderate_risk_interactions = []
        low_risk_interactions = []
        timing_recommendations = []
        
        # Check each medication against ingredients
        for medication in user_profile.medications:
            med_interactions = self._check_single_medication(medication, ingredients)
            
            if med_interactions:
                all_interactions.extend(med_interactions)
                
                # Categorize by severity
                for interaction in med_interactions:
                    severity = interaction.get('severity', 'low')
                    if severity == 'high':
                        high_risk_interactions.append(interaction)
                    elif severity == 'moderate':
                        moderate_risk_interactions.append(interaction)
                    else:
                        low_risk_interactions.append(interaction)
                    
                    # Add timing recommendations
                    if interaction.get('timing'):
                        timing_recommendations.append({
                            'medication': medication,
                            'timing': interaction['timing']
                        })
        
        # Generate recommendations
        recommendations = self._generate_medication_recommendations(
            high_risk_interactions, moderate_risk_interactions, low_risk_interactions
        )
        
        return {
            'interactions_found': len(all_interactions) > 0,
            'total_interactions': len(all_interactions),
            'high_risk_interactions': high_risk_interactions,
            'moderate_risk_interactions': moderate_risk_interactions,
            'low_risk_interactions': low_risk_interactions,
            'recommendations': recommendations,
            'timing_recommendations': timing_recommendations,
            'detailed_interactions': all_interactions
        }
    
    def _check_single_medication(self, medication: str, ingredients: List[str]) -> List[Dict]:
        """Check interactions for a single medication"""
        interactions = []
        medication_lower = medication.lower().strip()
        
        # Check direct medication interactions
        for med_name, interaction_data in self.known_interactions.items():
            if (med_name in medication_lower or 
                any(alias in medication_lower for alias in self._get_medication_aliases(med_name))):
                
                # Check avoid list
                for avoid_item in interaction_data.get('avoid', []):
                    if self._ingredient_contains(ingredients, avoid_item):
                        interactions.append({
                            'medication': medication,
                            'ingredient': avoid_item,
                            'interaction_type': 'avoid',
                            'severity': interaction_data.get('severity', 'moderate'),
                            'description': f"Should avoid {avoid_item} when taking {medication}",
                            'timing': interaction_data.get('timing', '')
                        })
                
                # Check caution list
                for caution_item in interaction_data.get('caution', []):
                    if self._ingredient_contains(ingredients, caution_item):
                        interactions.append({
                            'medication': medication,
                            'ingredient': caution_item,
                            'interaction_type': 'caution',
                            'severity': 'moderate' if interaction_data.get('severity') == 'high' else 'low',
                            'description': f"Use caution with {caution_item} when taking {medication}",
                            'timing': interaction_data.get('timing', '')
                        })
        
        # Check medication category interactions
        interactions.extend(self._check_category_interactions(medication, ingredients))
        
        return interactions
    
    def _check_category_interactions(self, medication: str, ingredients: List[str]) -> List[Dict]:
        """Check interactions based on medication categories"""
        interactions = []
        medication_lower = medication.lower().strip()
        
        for category, category_data in self.medication_categories.items():
            # Check if medication belongs to this category
            if any(med in medication_lower for med in category_data['medications']):
                # Check for food interactions
                for food_interaction in category_data['food_interactions']:
                    if self._ingredient_contains(ingredients, food_interaction):
                        interactions.append({
                            'medication': medication,
                            'ingredient': food_interaction,
                            'interaction_type': 'category_interaction',
                            'category': category,
                            'severity': category_data.get('severity', 'moderate'),
                            'description': f"{food_interaction} may interact with {category.replace('_', ' ')} medications"
                        })
        
        return interactions
    
    def _ingredient_contains(self, ingredients: List[str], target: str) -> bool:
        """Check if any ingredient contains the target substance"""
        target_lower = target.lower()
        target_words = target_lower.split()
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            
            # Direct match
            if target_lower in ingredient_lower:
                return True
            
            # Word-by-word match for compound terms
            if all(word in ingredient_lower for word in target_words):
                return True
            
            # Check for common aliases
            if self._check_ingredient_aliases(ingredient_lower, target_lower):
                return True
        
        return False
    
    def _check_ingredient_aliases(self, ingredient: str, target: str) -> bool:
        """Check for ingredient aliases and variations"""
        aliases = {
            'vitamin k': ['phylloquinone', 'menaquinone', 'green leafy'],
            'grapefruit': ['citrus paradisi', 'grapefruit juice'],
            'dairy': ['milk', 'cheese', 'yogurt', 'cream', 'butter'],
            'alcohol': ['ethanol', 'wine', 'beer', 'spirits', 'ethyl alcohol'],
            'caffeine': ['coffee', 'tea', 'cola', 'energy drink'],
            'tyramine': ['aged cheese', 'wine', 'soy sauce', 'pickled'],
            'potassium': ['banana', 'orange', 'potato', 'salt substitute']
        }
        
        for alias_group, alias_list in aliases.items():
            if alias_group in target:
                return any(alias in ingredient for alias in alias_list)
            if target in alias_group:
                return any(alias in ingredient for alias in alias_list)
        
        return False
    
    def _get_medication_aliases(self, medication: str) -> List[str]:
        """Get common aliases for medications"""
        aliases = {
            'warfarin': ['coumadin', 'jantoven'],
            'aspirin': ['acetylsalicylic acid', 'asa'],
            'metformin': ['glucophage', 'fortamet'],
            'lisinopril': ['prinivil', 'zestril'],
            'simvastatin': ['zocor'],
            'levothyroxine': ['synthroid', 'levoxyl', 'thyroid hormone'],
            'digoxin': ['lanoxin', 'digitalis']
        }
        
        return aliases.get(medication, [])
    
    def _generate_medication_recommendations(self, high_risk: List[Dict], 
                                           moderate_risk: List[Dict], 
                                           low_risk: List[Dict]) -> List[str]:
        """Generate recommendations based on interaction severity"""
        recommendations = []
        
        if high_risk:
            recommendations.extend([
                "🚨 CRITICAL: High-risk medication interactions detected",
                "❌ DO NOT consume this product with your current medications",
                "📞 Contact your doctor or pharmacist immediately",
                "🏥 Seek medical attention if you've already consumed this product"
            ])
            
            # Add specific high-risk warnings
            for interaction in high_risk[:3]:  # Limit to first 3
                recommendations.append(
                    f"⚠️ {interaction['medication']} + {interaction['ingredient']}: {interaction['description']}"
                )
        
        elif moderate_risk:
            recommendations.extend([
                "⚠️ CAUTION: Moderate medication interactions detected",
                "🤔 Consider avoiding this product or consult your healthcare provider",
                "⏰ If consuming, follow proper timing guidelines",
                "📱 Monitor for any unusual symptoms"
            ])
            
            # Add specific moderate-risk warnings
            for interaction in moderate_risk[:2]:
                recommendations.append(
                    f"⚠️ {interaction['medication']}: {interaction['description']}"
                )
        
        elif low_risk:
            recommendations.extend([
                "ℹ️ Minor interactions detected - use with caution",
                "👀 Monitor for any changes in medication effectiveness",
                "📋 Consider spacing consumption from medication times"
            ])
        
        else:
            recommendations.extend([
                "✅ No known food-medication interactions detected",
                "👍 This product appears safe with your medications",
                "📝 Always inform healthcare providers about your diet"
            ])
        
        return recommendations
    
    def _load_interaction_database(self) -> Dict:
        """Load medication interaction database from file"""
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'data', 
            'medications_db.json'
        )
        
        try:
            if os.path.exists(db_path):
                with open(db_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading medication database: {str(e)}")
        
        return {}
    
    def add_custom_interaction(self, medication: str, ingredient: str, 
                             severity: str, description: str):
        """Add custom medication-food interaction"""
        if medication not in self.known_interactions:
            self.known_interactions[medication] = {
                'avoid': [],
                'caution': [],
                'severity': severity
            }
        
        interaction_list = 'avoid' if severity == 'high' else 'caution'
        if ingredient not in self.known_interactions[medication][interaction_list]:
            self.known_interactions[medication][interaction_list].append(ingredient)
    
    def get_medication_info(self, medication: str) -> Dict:
        """Get detailed information about a medication"""
        medication_lower = medication.lower().strip()
        
        for med_name, interaction_data in self.known_interactions.items():
            if med_name in medication_lower:
                return {
                    'name': med_name,
                    'avoid_foods': interaction_data.get('avoid', []),
                    'caution_foods': interaction_data.get('caution', []),
                    'severity': interaction_data.get('severity', 'moderate'),
                    'timing_instructions': interaction_data.get('timing', ''),
                    'aliases': self._get_medication_aliases(med_name)
                }
        
        return {
            'name': medication,
            'avoid_foods': [],
            'caution_foods': [],
            'severity': 'unknown',
            'timing_instructions': '',
            'aliases': []
        }