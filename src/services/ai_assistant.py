"""
AI Assistant Service for Food Allergen Scanner
"""
from typing import List, Dict, Optional
import json
import re
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user_profile import UserProfile

class AIAssistant:
    """AI-powered assistant for food allergy and health guidance"""
    
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.conversation_history = []
        
        # Predefined responses for common queries
        self.predefined_responses = {
            'common_allergens': {
                'keywords': ['common', 'allergens', 'what', 'allergies'],
                'response': """The 9 most common food allergens are:
                
🥜 **Peanuts** - Can cause severe reactions
🌰 **Tree nuts** (almonds, walnuts, cashews, etc.)
🥛 **Milk/Dairy** - Contains proteins like casein and whey
🥚 **Eggs** - Both whites and yolks can cause reactions  
🐟 **Fish** - Including salmon, tuna, cod
🦐 **Shellfish** - Crabs, lobsters, shrimp, mollusks
🌾 **Wheat** - Contains gluten protein
🫘 **Soy** - Found in many processed foods
🌰 **Sesame** - Recently added to major allergen list

These account for about 90% of all food allergic reactions."""
            },
            
            'reading_labels': {
                'keywords': ['read', 'labels', 'ingredients', 'how'],
                'response': """Here's how to read food labels for allergens:

📋 **Required Allergen Labeling:**
- Major allergens must be listed in plain English
- Look for "Contains:" statements
- Check "May contain:" warnings

🔍 **What to Look For:**
- Ingredient names (obvious and hidden)
- Processing statements ("manufactured in facility...")
- Cross-contamination warnings

⚠️ **Hidden Allergens:**
- Casein, whey (dairy)
- Albumin, lecithin (eggs) 
- Modified food starch (wheat)
- Natural flavoring (can contain allergens)

💡 **Pro Tips:**
- When in doubt, contact the manufacturer
- Check every time - formulations change
- Look for certified allergen-free products"""
            },
            
            'emergency_response': {
                'keywords': ['emergency', 'reaction', 'allergic', 'epipen', 'anaphylaxis'],
                'response': """🚨 **Emergency Allergic Reaction Response:**

**Immediate Actions:**
1. 🏥 **Call 911** for severe reactions
2. 💉 **Use EpiPen** if available (inject into thigh)
3. 🛏️ **Lie down** with legs elevated
4. 🫁 **Stay calm** and breathe slowly

**Severe Reaction Signs:**
- Difficulty breathing or swallowing
- Swelling of face, lips, tongue
- Rapid pulse, dizziness
- Severe whole-body reaction
- Loss of consciousness

**After EpiPen:**
- Still call 911 - effects are temporary
- Second dose may be needed after 15 minutes
- Go to emergency room even if feeling better

**Always carry emergency medication if prescribed!**"""
            },
            
            'healthy_alternatives': {
                'keywords': ['alternatives', 'substitute', 'replace', 'healthy'],
                'response': """🌱 **Healthy Allergen Alternatives:**

**Dairy Alternatives:**
- Almond, oat, coconut, or soy milk
- Nutritional yeast for cheesy flavor
- Coconut cream for cooking

**Egg Alternatives:**
- Flax or chia eggs (1 tbsp + 3 tbsp water)
- Applesauce or banana for baking
- Aquafaba (chickpea liquid)

**Wheat/Gluten Alternatives:**
- Rice, quinoa, millet flour
- Almond or coconut flour
- Gluten-free oats

**Nut Alternatives:**
- Sunflower seed butter
- Pumpkin seed butter
- Tahini (sesame seed paste)

**Protein Sources:**
- Quinoa, lentils, beans
- Seeds (hemp, chia, pumpkin)
- Safe meats and fish"""
            }
        }
    
    def get_response(self, user_message: str, user_profile: Optional[UserProfile] = None) -> str:
        """
        Generate AI response based on user message and profile
        """
        # Add to conversation history
        self.conversation_history.append({
            'user': user_message,
            'timestamp': self._get_timestamp()
        })
        
        # Clean and analyze the message
        message_lower = user_message.lower().strip()
        
        # Check for predefined responses
        for response_key, response_data in self.predefined_responses.items():
            keywords = response_data['keywords']
            if any(keyword in message_lower for keyword in keywords):
                response = response_data['response']
                
                # Personalize if user profile available
                if user_profile:
                    response = self._personalize_response(response, user_profile)
                
                self._add_response_to_history(response)
                return response
        
        # Handle specific user profile questions
        if user_profile:
            profile_response = self._handle_profile_specific_questions(message_lower, user_profile)
            if profile_response:
                self._add_response_to_history(profile_response)
                return profile_response
        
        # Handle general questions
        general_response = self._handle_general_questions(message_lower)
        if general_response:
            self._add_response_to_history(general_response)
            return general_response
        
        # Default response
        default_response = self._get_default_response(message_lower, user_profile)
        self._add_response_to_history(default_response)
        return default_response
    
    def _handle_profile_specific_questions(self, message: str, user_profile: UserProfile) -> Optional[str]:
        """Handle questions specific to user's profile"""
        
        # Questions about user's allergies
        if any(word in message for word in ['my', 'allergies', 'allergy', 'allergic']):
            if user_profile.allergies:
                response = f"Based on your profile, you have allergies to: **{', '.join(user_profile.allergies)}**\n\n"
                response += "Here are some key things to watch for:\n\n"
                
                for allergy in user_profile.allergies[:3]:  # Limit to first 3
                    hidden_sources = self._get_hidden_allergen_sources(allergy)
                    if hidden_sources:
                        response += f"🔍 **{allergy.title()}** can hide in: {', '.join(hidden_sources[:3])}\n"
                
                response += "\n💡 Always read ingredient labels carefully and ask about preparation methods when dining out."
                return response
            else:
                return "You haven't listed any allergies in your profile yet. Would you like help setting up your allergy profile?"
        
        # Questions about medications
        if any(word in message for word in ['medication', 'medicine', 'drug', 'interaction']):
            if user_profile.medications:
                response = f"You're currently taking: **{', '.join(user_profile.medications)}**\n\n"
                response += "⚠️ **Important Food Interactions to Avoid:**\n\n"
                
                interactions = self._get_medication_food_interactions(user_profile.medications)
                for med, foods in interactions.items():
                    if foods:
                        response += f"• **{med}**: Avoid {', '.join(foods[:3])}\n"
                
                response += "\n📞 Always consult your healthcare provider before making dietary changes."
                return response
            else:
                return "You haven't listed any medications in your profile. If you take any medications, consider adding them to get food interaction warnings."
        
        # Safe food suggestions
        if any(word in message for word in ['safe', 'eat', 'food', 'recommend']):
            if user_profile.allergies:
                response = "🍎 **Foods Generally Safe for Your Allergies:**\n\n"
                safe_foods = self._get_safe_foods_for_allergies(user_profile.allergies)
                
                for category, foods in safe_foods.items():
                    if foods:
                        response += f"**{category.title()}**: {', '.join(foods[:4])}\n"
                
                response += "\n⚠️ Always verify ingredients and check for cross-contamination warnings."
                return response
        
        return None
    
    def _handle_general_questions(self, message: str) -> Optional[str]:
        """Handle general health and allergy questions"""
        
        # Cross-contamination questions
        if any(word in message for word in ['cross', 'contamination', 'shared', 'facility']):
            return """🏭 **Cross-Contamination Information:**

**What is Cross-Contamination?**
When allergens are transferred from one food to another through shared equipment, surfaces, or air.

**Common Sources:**
- Shared manufacturing equipment
- Shared cooking surfaces
- Airborne particles (flour dust)
- Utensils and cutting boards
- Fryer oil used for multiple foods

**Prevention Tips:**
- Look for "may contain" warnings
- Choose certified allergen-free facilities
- Ask about preparation methods
- Use separate cooking equipment at home
- Clean surfaces thoroughly

**Risk Levels:**
- Manufacturing: Highest risk
- Restaurant kitchens: High risk  
- Home cooking: Manageable risk"""

        # Dining out questions
        if any(word in message for word in ['restaurant', 'dining', 'eat out', 'menu']):
            return """🍽️ **Safe Dining Out Tips:**

**Before You Go:**
- Call ahead about allergen policies
- Check online menus and allergen info
- Research allergen-friendly restaurants

**At the Restaurant:**
- Inform server about allergies immediately
- Ask to speak with the chef if needed
- Ask about ingredients and preparation
- Request clean cooking surfaces/utensils

**Questions to Ask:**
- "How is this dish prepared?"
- "What oil do you use for frying?"
- "Can you guarantee no cross-contamination?"
- "Do you have allergen protocols?"

**Red Flags:**
- Server seems unsure or dismissive
- "Probably fine" or "I think so" responses
- Busy kitchen with no allergen protocols
- Shared fryers or preparation areas

**Always carry emergency medication when dining out!**"""

        # Symptoms questions
        if any(word in message for word in ['symptoms', 'reaction', 'signs']):
            return """⚠️ **Allergic Reaction Symptoms:**

**Mild Reactions:**
- Skin: Hives, itching, redness
- Digestive: Nausea, stomach cramps, diarrhea
- Respiratory: Sneezing, runny nose

**Moderate Reactions:**
- Skin: Widespread hives, swelling
- Digestive: Vomiting, severe cramps
- Respiratory: Coughing, wheezing

**Severe Reactions (Anaphylaxis):**
🚨 **CALL 911 IMMEDIATELY**
- Breathing: Difficulty breathing, throat swelling
- Circulation: Rapid pulse, dizziness, fainting
- Skin: Severe swelling, pale/blue lips
- Digestive: Severe vomiting, loss of bladder control

**Timeline:**
- Symptoms usually appear within 2 hours
- Can be immediate or delayed
- Second wave possible 4-12 hours later

**When in Doubt:**
- Treat as serious emergency
- Use EpiPen if available
- Seek immediate medical attention"""

        return None
    
    def _get_default_response(self, message: str, user_profile: Optional[UserProfile]) -> str:
        """Generate default response for unrecognized queries"""
        
        # Acknowledge the question
        greeting = "Thanks for your question! "
        
        # Provide general guidance
        if user_profile and (user_profile.allergies or user_profile.medications):
            response = greeting + """I'm here to help you navigate food safety with your allergies and medications. 

🤔 **I can help you with:**
- Understanding your specific allergies
- Food-medication interactions  
- Safe food alternatives
- Reading ingredient labels
- Emergency response guidance
- Dining out safely

💬 **Try asking me:**
- "What are my allergy risks?"
- "What foods should I avoid with my medications?"
- "How do I read food labels?"
- "What should I do in an emergency?"

Would you like information on any of these topics?"""
        else:
            response = greeting + """I'm your AI assistant for food allergen and health guidance!

📚 **I can help you with:**
- Common food allergens
- Reading ingredient labels
- Emergency response procedures
- Healthy food alternatives
- Dining out safety tips
- Cross-contamination prevention

💡 **Popular questions:**
- "What are the most common allergens?"
- "How do I read food labels?"
- "What should I do in an allergic emergency?"
- "What are healthy alternatives to common allergens?"

Set up your health profile to get personalized advice!"""
        
        return response
    
    def _personalize_response(self, response: str, user_profile: UserProfile) -> str:
        """Add personalization to predefined responses"""
        if not user_profile:
            return response
        
        personalization = "\n\n"
        
        if user_profile.allergies:
            relevant_allergies = []
            response_lower = response.lower()
            
            for allergy in user_profile.allergies:
                if allergy.lower() in response_lower:
                    relevant_allergies.append(allergy)
            
            if relevant_allergies:
                personalization += f"⚠️ **Important for you:** You have allergies to {', '.join(relevant_allergies)}. Pay special attention to the information about these allergens above."
        
        if user_profile.medications:
            personalization += f"\n💊 **Medication Note:** You're taking {len(user_profile.medications)} medication(s). Consider food-drug interactions when making dietary choices."
        
        return response + personalization
    
    def _get_hidden_allergen_sources(self, allergy: str) -> List[str]:
        """Get common hidden sources for specific allergens"""
        hidden_sources = {
            'milk': ['casein', 'whey', 'lactose', 'ghee'],
            'dairy': ['casein', 'whey', 'lactose', 'ghee'],
            'egg': ['albumin', 'lecithin', 'lysozyme'],
            'eggs': ['albumin', 'lecithin', 'lysozyme'],
            'wheat': ['modified starch', 'malt', 'dextrin'],
            'soy': ['lecithin', 'natural flavor', 'vegetable protein'],
            'peanut': ['arachis oil', 'groundnut'],
            'peanuts': ['arachis oil', 'groundnut']
        }
        
        allergy_lower = allergy.lower()
        for allergen, sources in hidden_sources.items():
            if allergen in allergy_lower or allergy_lower in allergen:
                return sources
        
        return []
    
    def _get_medication_food_interactions(self, medications: List[str]) -> Dict[str, List[str]]:
        """Get food interactions for user's medications"""
        interactions = {}
        
        interaction_db = {
            'warfarin': ['vitamin K foods', 'grapefruit', 'alcohol'],
            'aspirin': ['alcohol', 'omega-3 supplements'],
            'metformin': ['alcohol', 'high sugar foods'],
            'lisinopril': ['potassium-rich foods', 'salt substitutes']
        }
        
        for medication in medications:
            med_lower = medication.lower()
            for db_med, foods in interaction_db.items():
                if db_med in med_lower or any(word in med_lower for word in db_med.split()):
                    interactions[medication] = foods
                    break
        
        return interactions
    
    def _get_safe_foods_for_allergies(self, allergies: List[str]) -> Dict[str, List[str]]:
        """Get generally safe foods for user's allergies"""
        safe_foods = {
            'proteins': ['chicken', 'turkey', 'beef', 'pork'],
            'grains': ['rice', 'quinoa', 'oats', 'corn'],
            'vegetables': ['carrots', 'broccoli', 'spinach', 'peppers'],
            'fruits': ['apples', 'bananas', 'berries', 'oranges']
        }
        
        # Remove potentially unsafe foods based on allergies
        allergies_lower = [a.lower() for a in allergies]
        
        if any('egg' in a for a in allergies_lower):
            # Eggs are less commonly found in basic foods
            pass
        
        if any('dairy' in a or 'milk' in a for a in allergies_lower):
            # Remove dairy-containing items
            pass
            
        if any('wheat' in a or 'gluten' in a for a in allergies_lower):
            safe_foods['grains'] = ['rice', 'quinoa', 'corn']
        
        if any('soy' in a for a in allergies_lower):
            # Most basic foods don't contain soy
            pass
        
        return safe_foods
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _add_response_to_history(self, response: str):
        """Add AI response to conversation history"""
        if self.conversation_history:
            self.conversation_history[-1]['ai_response'] = response
    
    def _load_knowledge_base(self) -> Dict:
        """Load AI knowledge base from file"""
        kb_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'data', 
            'ai_knowledge_base.json'
        )
        
        try:
            if os.path.exists(kb_path):
                with open(kb_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading knowledge base: {str(e)}")
        
        return {}
    
    def get_conversation_summary(self) -> Dict:
        """Get summary of conversation history"""
        return {
            'total_interactions': len(self.conversation_history),
            'recent_topics': [entry.get('user', '')[:50] + '...' 
                            for entry in self.conversation_history[-5:]],
            'most_recent': self.conversation_history[-1] if self.conversation_history else None
        }