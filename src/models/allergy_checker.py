"""
Allergy Checker Model for Food Allergen Scanner
"""
from typing import List, Dict, Tuple, Optional
from .user_profile import UserProfile
from .product import Product

class AllergyChecker:
    """Core allergy checking logic and risk assessment"""
    
    def __init__(self):
        # Common allergen categories and their variations
        self.allergen_database = {
            'dairy': [
                'milk', 'cheese', 'butter', 'cream', 'yogurt', 'lactose', 
                'casein', 'whey', 'lactoglobulin', 'lactalbumin'
            ],
            'eggs': [
                'egg', 'eggs', 'albumin', 'globulin', 'lecithin', 
                'lysozyme', 'mayonnaise', 'meringue', 'ovalbumin'
            ],
            'peanuts': [
                'peanut', 'peanuts', 'groundnut', 'ground nut', 
                'arachis oil', 'peanut oil', 'peanut butter'
            ],
            'tree_nuts': [
                'almond', 'brazil nut', 'cashew', 'hazelnut', 'pecan', 
                'pistachio', 'walnut', 'macadamia', 'pine nut', 'chestnut'
            ],
            'soy': [
                'soy', 'soya', 'soybean', 'tofu', 'miso', 'tempeh', 
                'soy sauce', 'lecithin', 'edamame'
            ],
            'wheat': [
                'wheat', 'flour', 'gluten', 'semolina', 'spelt', 
                'kamut', 'bulgur', 'couscous', 'seitan'
            ],
            'fish': [
                'fish', 'salmon', 'tuna', 'cod', 'sardine', 'anchovy', 
                'mackerel', 'bass', 'trout', 'fish sauce'
            ],
            'shellfish': [
                'crab', 'lobster', 'shrimp', 'prawn', 'scallop', 
                'oyster', 'mussel', 'clam', 'crayfish', 'langoustine'
            ],
            'sesame': [
                'sesame', 'tahini', 'sesame oil', 'sesame seed', 'gomasio'
            ]
        }
        
        # Severity levels for different allergens
        self.severity_levels = {
            'peanuts': 'high',
            'tree_nuts': 'high',
            'shellfish': 'high',
            'fish': 'moderate',
            'eggs': 'moderate',
            'dairy': 'moderate',
            'soy': 'low',
            'wheat': 'moderate',
            'sesame': 'moderate'
        }
        
        # Cross-contamination risks
        self.cross_contamination_risks = {
            'peanuts': ['tree_nuts', 'soy'],
            'tree_nuts': ['peanuts'],
            'dairy': ['eggs'],
            'wheat': ['oats', 'barley', 'rye']
        }
    
    def check_allergens(self, ingredients: List[str], user_profile: UserProfile) -> Dict:
        """
        Check ingredients against user's allergies
        Returns detailed analysis with risk levels
        """
        if not user_profile or not user_profile.allergies:
            return {
                'risk_level': 'unknown',
                'detected_allergens': [],
                'high_risk_allergens': [],
                'moderate_risk_allergens': [],
                'low_risk_allergens': [],
                'cross_contamination_risks': [],
                'recommendations': ['No allergy profile available']
            }
        
        detected_allergens = []
        high_risk_allergens = []
        moderate_risk_allergens = []
        low_risk_allergens = []
        cross_contamination_risks = []
        
        # Normalize ingredients for comparison
        normalized_ingredients = [ing.lower().strip() for ing in ingredients]
        
        # Check each user allergy against ingredients
        for user_allergy in user_profile.allergies:
            allergen_matches = self._find_allergen_matches(
                user_allergy, normalized_ingredients
            )
            
            if allergen_matches:
                detected_allergens.append(user_allergy)
                
                # Categorize by severity
                severity = self._get_allergen_severity(user_allergy)
                if severity == 'high':
                    high_risk_allergens.append(user_allergy)
                elif severity == 'moderate':
                    moderate_risk_allergens.append(user_allergy)
                else:
                    low_risk_allergens.append(user_allergy)
                
                # Check for cross-contamination risks
                cross_risks = self._check_cross_contamination(user_allergy, normalized_ingredients)
                cross_contamination_risks.extend(cross_risks)
        
        # Determine overall risk level
        overall_risk = self._calculate_overall_risk(
            high_risk_allergens, moderate_risk_allergens, low_risk_allergens
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            overall_risk, detected_allergens, cross_contamination_risks
        )
        
        return {
            'risk_level': overall_risk,
            'detected_allergens': detected_allergens,
            'high_risk_allergens': high_risk_allergens,
            'moderate_risk_allergens': moderate_risk_allergens,
            'low_risk_allergens': low_risk_allergens,
            'cross_contamination_risks': list(set(cross_contamination_risks)),
            'recommendations': recommendations,
            'ingredient_matches': allergen_matches if 'allergen_matches' in locals() else []
        }
    
    def _find_allergen_matches(self, user_allergy: str, ingredients: List[str]) -> List[str]:
        """Find specific ingredient matches for a user's allergy"""
        matches = []
        user_allergy_lower = user_allergy.lower().strip()
        
        # Direct matching
        for ingredient in ingredients:
            if user_allergy_lower in ingredient or ingredient in user_allergy_lower:
                matches.append(ingredient)
        
        # Database matching - find allergen category
        allergen_category = None
        for category, allergens in self.allergen_database.items():
            if any(user_allergy_lower in allergen or allergen in user_allergy_lower 
                   for allergen in allergens):
                allergen_category = category
                break
        
        # Check ingredients against allergen category
        if allergen_category:
            category_allergens = self.allergen_database[allergen_category]
            for ingredient in ingredients:
                for allergen in category_allergens:
                    if allergen in ingredient or ingredient in allergen:
                        if ingredient not in matches:
                            matches.append(ingredient)
        
        return matches
    
    def _get_allergen_severity(self, allergen: str) -> str:
        """Determine severity level of an allergen"""
        allergen_lower = allergen.lower().strip()
        
        # Check direct matches first
        for severity_allergen, severity in self.severity_levels.items():
            if (allergen_lower in severity_allergen or 
                severity_allergen in allergen_lower or
                any(allergen_lower in db_allergen or db_allergen in allergen_lower
                    for db_allergen in self.allergen_database.get(severity_allergen, []))):
                return severity
        
        # Default to moderate if not found
        return 'moderate'
    
    def _check_cross_contamination(self, user_allergy: str, ingredients: List[str]) -> List[str]:
        """Check for cross-contamination risks"""
        risks = []
        allergen_lower = user_allergy.lower().strip()
        
        # Find allergen category
        user_allergen_category = None
        for category, allergens in self.allergen_database.items():
            if any(allergen_lower in allergen or allergen in allergen_lower 
                   for allergen in allergens):
                user_allergen_category = category
                break
        
        if not user_allergen_category:
            return risks
        
        # Check cross-contamination risks
        cross_risk_categories = self.cross_contamination_risks.get(user_allergen_category, [])
        
        for risk_category in cross_risk_categories:
            risk_allergens = self.allergen_database.get(risk_category, [])
            for ingredient in ingredients:
                if any(risk_allergen in ingredient for risk_allergen in risk_allergens):
                    risks.append(f"Cross-contamination risk with {risk_category}")
                    break
        
        return risks
    
    def _calculate_overall_risk(self, high_risk: List[str], 
                              moderate_risk: List[str], 
                              low_risk: List[str]) -> str:
        """Calculate overall risk level"""
        if high_risk:
            return 'high'
        elif moderate_risk:
            return 'moderate'
        elif low_risk:
            return 'low'
        else:
            return 'safe'
    
    def _generate_recommendations(self, risk_level: str, 
                                detected_allergens: List[str],
                                cross_contamination_risks: List[str]) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if risk_level == 'high':
            recommendations.extend([
                "⚠️ DO NOT CONSUME this product",
                "🚨 This product contains high-risk allergens for you",
                "📞 Keep your emergency medication (EpiPen) readily available",
                "👨‍⚕️ Consult with your doctor if you have questions"
            ])
        
        elif risk_level == 'moderate':
            recommendations.extend([
                "⚠️ CAUTION: This product may trigger your allergies",
                "🔍 Read ingredients carefully before consuming",
                "💊 Have your allergy medication available",
                "👨‍⚕️ Consider consulting with your healthcare provider"
            ])
        
        elif risk_level == 'low':
            recommendations.extend([
                "⚠️ Low risk detected - proceed with caution",
                "👀 Monitor for any unusual reactions",
                "💊 Keep allergy medication nearby as precaution"
            ])
        
        else:
            recommendations.extend([
                "✅ No known allergens detected",
                "👍 This product appears safe for your profile",
                "📝 Always verify ingredients as formulations may change"
            ])
        
        # Add cross-contamination warnings
        if cross_contamination_risks:
            recommendations.append("⚠️ Cross-contamination risks detected")
            recommendations.extend([f"• {risk}" for risk in cross_contamination_risks])
        
        # Add specific allergen information
        if detected_allergens:
            recommendations.append(f"🎯 Detected allergens: {', '.join(detected_allergens)}")
        
        return recommendations
    
    def get_safe_alternatives(self, detected_allergens: List[str]) -> List[str]:
        """Suggest safe alternatives for detected allergens"""
        alternatives = {
            'dairy': ['Almond milk', 'Oat milk', 'Coconut milk', 'Soy milk'],
            'eggs': ['Flax eggs', 'Chia eggs', 'Applesauce', 'Aquafaba'],
            'wheat': ['Rice flour', 'Almond flour', 'Coconut flour', 'Quinoa'],
            'nuts': ['Sunflower seed butter', 'Pumpkin seed butter', 'Tahini'],
            'soy': ['Coconut aminos', 'Pea protein', 'Hemp protein']
        }
        
        suggested_alternatives = []
        
        for allergen in detected_allergens:
            allergen_lower = allergen.lower()
            for category, alts in alternatives.items():
                if category in allergen_lower or allergen_lower in category:
                    suggested_alternatives.extend(alts)
        
        return list(set(suggested_alternatives))  # Remove duplicates