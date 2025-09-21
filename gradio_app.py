import gradio as gr
import sys
import os
from pathlib import Path
import json
import logging
from PIL import Image
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try importing services with fallback
try:
    from models.user_profile import UserProfileManager
    # Try the regular barcode scanner first, then fallback
    try:
        from services.barcode_scanner import BarcodeScanner
    except ImportError:
        from services.barcode_scanner_fallback import BarcodeScanner
        logger.info("Using fallback barcode scanner")
    
    from services.ingredient_extractor import IngredientExtractor
    from services.allergen_detector import AllergenDetector
    from services.drug_interaction_checker import DrugInteractionChecker
    from services.ai_assistant import AIAssistant
    from services.doctor_consultation import DoctorConsultationService
    from utils.alert_system import AlertSystem
    
    SERVICES_AVAILABLE = True
    logger.info("All services loaded successfully")
    
except ImportError as e:
    logger.error(f"Error importing services: {e}")
    SERVICES_AVAILABLE = False

# Initialize services with fallback
if SERVICES_AVAILABLE:
    try:
        user_manager = UserProfileManager()
        barcode_scanner = BarcodeScanner()
        ingredient_extractor = IngredientExtractor()
        allergen_detector = AllergenDetector()
        drug_checker = DrugInteractionChecker()
        ai_assistant = AIAssistant()
        doctor_service = DoctorConsultationService()
        alert_system = AlertSystem()
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        SERVICES_AVAILABLE = False

# Global user profile storage
current_user_id = None

# Mock file class for compatibility
class MockFile:
    def __init__(self, file_buffer):
        self.file_buffer = file_buffer
        
    def read(self):
        return self.file_buffer.getvalue()

def create_user_profile(name, age, allergies_text, medications_text, dietary_restrictions_text):
    """Create user profile from Gradio inputs"""
    global current_user_id

    if not SERVICES_AVAILABLE:
        current_user_id = "demo_user"
        return "⚠️ Services not available. Using demo mode.\n\n✅ Demo profile created successfully!"

    try:
        # Parse allergies (format: "peanuts:severe, milk:moderate")
        allergies = []
        if allergies_text.strip():
            for allergy in allergies_text.split(','):
                if ':' in allergy:
                    allergen, severity = allergy.strip().split(':')
                    allergies.append({"allergen": allergen.strip(), "severity": severity.strip()})
                else:
                    allergies.append({"allergen": allergy.strip(), "severity": "moderate"})

        # Parse medications (format: "warfarin, metformin")
        medications = []
        if medications_text.strip():
            for med in medications_text.split(','):
                medications.append({"name": med.strip()})

        # Parse dietary restrictions
        dietary_restrictions = []
        if dietary_restrictions_text.strip():
            dietary_restrictions = [item.strip() for item in dietary_restrictions_text.split(',')]

        user_data = {
            "name": name,
            "age": int(age) if age else 0,
            "allergies": allergies,
            "medications": medications,
            "dietary_restrictions": dietary_restrictions
        }

        profile = user_manager.create_profile(user_data)
        current_user_id = profile['id']

        return f"✅ Profile created successfully! User ID: {current_user_id}"

    except Exception as e:
        return f"❌ Error creating profile: {str(e)}"

def scan_barcode_image(image):
    """Scan barcode from uploaded image"""
    global current_user_id

    if not current_user_id:
        return "❌ Please create a user profile first"

    if not SERVICES_AVAILABLE:
        return """📱 **Demo Barcode Scan Result**
        
🏷️ **Product:** Sample Chocolate Cookies
🏢 **Brand:** Demo Brand
📋 **Ingredients:** wheat flour, sugar, chocolate chips, eggs, milk, butter

⚠️ **HEALTH ALERTS:**
- **Milk Allergy Warning**: This product contains milk which may trigger your allergy
- **Egg Allergy Warning**: Contains eggs - avoid if allergic
- **Gluten Warning**: Contains wheat - not suitable for gluten-free diet

📋 **Recommendations:**
- Check with your doctor before consuming
- Look for dairy-free alternatives
- Keep antihistamines handy"""

    try:
        # Convert PIL image to file-like object
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        mock_file = MockFile(img_buffer)

        # Extract barcode
        barcode_data = barcode_scanner.scan_image(mock_file)

        if not barcode_data:
            return "❌ No barcode found in the image. Try:\n- Better lighting\n- Steady camera\n- Clear barcode image"

        # Get product info
        product_info = ingredient_extractor.get_product_info(barcode_data)
        if not product_info:
            return f"❌ No product information found for barcode: {barcode_data}"

        # Extract ingredients
        ingredients = ingredient_extractor.extract_ingredients(product_info)

        # Check for health risks
        user_profile = user_manager.get_profile(current_user_id)
        allergen_warnings = allergen_detector.check_allergens(ingredients, user_profile['allergies'])
        drug_warnings = drug_checker.check_interactions(ingredients, user_profile['medications'])

        # Generate alerts
        alerts = alert_system.generate_alerts(allergen_warnings, drug_warnings)

        # Format response
        result = f"🏷️ **Product:** {product_info.get('product_name', 'Unknown')}\n"
        result += f"🏢 **Brand:** {product_info.get('brand', 'Unknown')}\n\n"

        result += f"📋 **Ingredients:** {', '.join([ing['name'] for ing in ingredients])}\n\n"

        if alerts:
            result += "⚠️ **HEALTH ALERTS:**\n"
            for alert in alerts:
                result += f"- {alert['title']}\n"
                result += f"  {alert['message']}\n\n"
        else:
            result += "✅ **Safe to consume** based on your profile\n"

        return result

    except Exception as e:
        logger.error(f"Error scanning barcode: {e}")
        return f"❌ Error scanning barcode: {str(e)}"

def analyze_manual_ingredients(ingredients_text):
    """Analyze manually entered ingredients"""
    global current_user_id

    if not current_user_id:
        return "❌ Please create a user profile first"

    if not SERVICES_AVAILABLE:
        ingredients_list = [ing.strip() for ing in ingredients_text.split(',') if ing.strip()]
        if not ingredients_list:
            return "❌ Please enter some ingredients"
            
        return f"""📋 **Demo Analysis Result**
        
**Analyzed Ingredients:** {', '.join(ingredients_list)}

⚠️ **HEALTH ALERTS:**
- **Potential Allergen**: Some ingredients may contain common allergens
- **Drug Interaction**: Check with pharmacist if on medications

✅ **Recommendations:**
- Read labels carefully
- Consult healthcare provider if unsure
- Keep emergency medications accessible"""

    try:
        # Parse ingredients
        ingredients_list = [ing.strip() for ing in ingredients_text.split(',') if ing.strip()]

        if not ingredients_list:
            return "❌ Please enter some ingredients"

        # Create ingredient objects
        ingredients = [{"name": ing} for ing in ingredients_list]

        # Check for health risks
        user_profile = user_manager.get_profile(current_user_id)
        allergen_warnings = allergen_detector.check_allergens(ingredients, user_profile['allergies'])
        drug_warnings = drug_checker.check_interactions(ingredients, user_profile['medications'])

        # Generate alerts
        alerts = alert_system.generate_alerts(allergen_warnings, drug_warnings)

        # Format response
        result = f"📋 **Analyzed Ingredients:** {', '.join(ingredients_list)}\n\n"

        if alerts:
            result += "⚠️ **HEALTH ALERTS:**\n"
            for alert in alerts:
                result += f"- {alert['title']}\n"
                result += f"  {alert['message']}\n"
                if alert.get('recommendations'):
                    result += f"  **Recommendations:** {', '.join(alert['recommendations'][:2])}\n\n"
        else:
            result += "✅ **Safe to consume** based on your profile\n"

        return result

    except Exception as e:
        logger.error(f"Error analyzing ingredients: {e}")
        return f"❌ Error analyzing ingredients: {str(e)}"

def chat_with_ai(message, history):
    """Chat with AI assistant"""
    global current_user_id

    if not current_user_id:
        history.append([message, "❌ Please create a user profile first"])
        return history, ""

    if not SERVICES_AVAILABLE:
        # Simple demo responses
        demo_responses = {
            "allergen": "🤖 I can help with allergen information! Common allergens include milk, eggs, peanuts, tree nuts, fish, shellfish, wheat, and soy. Always read ingredient labels carefully.",
            "milk": "🥛 Milk allergies can cause reactions ranging from mild digestive issues to severe anaphylaxis. Look for alternatives like oat milk, almond milk, or soy milk.",
            "peanut": "🥜 Peanut allergies are serious and can be life-threatening. Always carry an EpiPen if prescribed and avoid cross-contamination.",
            "emergency": "🚨 For severe allergic reactions: 1) Use EpiPen immediately 2) Call 911 3) Get to hospital. This is a medical emergency!",
            "default": "🤖 I'm here to help with food safety questions! Ask me about allergens, ingredients, or emergency procedures."
        }
        
        message_lower = message.lower()
        response = demo_responses.get("default")
        
        for key in demo_responses:
            if key in message_lower:
                response = demo_responses[key]
                break
                
        history.append([message, response])
        return history, ""

    try:
        user_profile = user_manager.get_profile(current_user_id)
        response = ai_assistant.process_query(message, user_profile, current_user_id)

        ai_response = response['response']

        # Add suggestions if available
        if response.get('suggestions'):
            ai_response += f"\n\n💡 **Suggestions:**\n"
            for suggestion in response['suggestions'][:3]:
                ai_response += f"• {suggestion}\n"

        history.append([message, ai_response])
        return history, ""

    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        history.append([message, error_msg])
        return history, ""

def request_doctor_consultation(concern_type, urgency):
    """Request doctor consultation"""
    global current_user_id

    if not current_user_id:
        return "❌ Please create a user profile first"

    if not SERVICES_AVAILABLE:
        return f"""👨‍⚕️ **Demo Consultation Request**
        
**Concern Type:** {concern_type}
**Urgency Level:** {urgency}

📅 **Next Steps:**
1. Contact your primary care physician
2. For allergists: Search online directories
3. Emergency: Call 911 or go to ER

📞 **Sample Contacts:**
- Primary Care: (555) 123-4567
- Allergy Specialist: (555) 987-6543
- Pharmacy: (555) 246-8135

⚠️ This is a demo. Please contact real medical professionals."""

    try:
        consultation_request = {
            "concern_type": concern_type.lower(),
            "urgency": urgency.lower(),
            "user_id": current_user_id,
            "consultation_type": "video"
        }

        result = doctor_service.request_consultation(consultation_request)

        if result.get('status') == 'consultation_scheduled':
            response = f"👨‍⚕️ **Consultation Scheduled**\n\n"
            doctor = result['doctor']
            response += f"**Doctor:** {doctor['name']}\n"
            response += f"**Specialty:** {doctor['specialty']}\n"
            response += f"**Rating:** ⭐ {doctor['rating']}/5.0\n"
            response += f"**Wait Time:** {result['estimated_wait_time']}\n"
            response += f"**Fee:** ${doctor['consultation_fee']}\n\n"
            response += f"**Session ID:** {result['session_id']}\n"
            response += f"**Scheduled Time:** {result['scheduled_time']}\n"

            return response
        else:
            return f"❌ {result.get('message', 'Unable to schedule consultation')}"

    except Exception as e:
        return f"❌ Error requesting consultation: {str(e)}"

def get_emergency_contacts():
    """Get emergency contact information"""
    if not SERVICES_AVAILABLE:
        return """🚨 **Emergency Contacts**

**Emergency Services:** 911
**Poison Control:** 1-800-222-1222

🏥 **Nearby Hospitals:**
- General Hospital: (555) 123-4567
- Children's Hospital: (555) 234-5678
- Emergency Center: (555) 345-6789

⚡ **Urgent Care:**
- QuickCare Clinic: (555) 456-7890
- Minute Clinic: (555) 567-8901

🩺 **Specialists:**
- Allergy Center: (555) 678-9012
- Pharmacy 24/7: (555) 789-0123

⚠️ **For severe reactions:**
1. Use EpiPen immediately
2. Call 911
3. Go to nearest ER"""

    try:
        contacts = doctor_service.get_emergency_contacts()

        response = "🚨 **Emergency Contacts**\n\n"
        response += f"**Emergency Services:** {contacts['emergency_services']}\n"
        response += f"**Poison Control:** {contacts['poison_control']}\n\n"

        response += f"**Local Hospital ER:**\n"
        response += f"• {contacts['local_hospital_er']['name']}\n"
        response += f"• {contacts['local_hospital_er']['phone']}\n"
        response += f"• {contacts['local_hospital_er']['address']}\n\n"

        response += f"**24/7 Nurse Hotline:**\n"
        response += f"• {contacts['nurse_hotline']['name']}\n"
        response += f"• {contacts['nurse_hotline']['phone']}\n"

        return response

    except Exception as e:
        return f"❌ Error getting emergency contacts: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="🍎 AI Food Allergen Scanner", theme=gr.themes.Soft()) as app:
    gr.Markdown("""
    # 🍎 AI Food Allergen Scanner

    **Protect your health with AI-powered food analysis**

    This application helps you identify potential allergens and drug interactions in food products.
    """)

    with gr.Tab("👤 User Profile"):
        gr.Markdown("### Create Your Health Profile")

        with gr.Row():
            with gr.Column():
                name_input = gr.Textbox(label="Name", placeholder="Enter your name")
                age_input = gr.Number(label="Age", minimum=0, maximum=120, value=30)

            with gr.Column():
                allergies_input = gr.Textbox(
                    label="Allergies",
                    placeholder="peanuts:severe, milk:moderate, wheat:mild",
                    info="Format: allergen:severity (separated by commas)"
                )
                medications_input = gr.Textbox(
                    label="Medications",
                    placeholder="warfarin, metformin, lisinopril",
                    info="Medication names separated by commas"
                )

        dietary_input = gr.Textbox(
            label="Dietary Restrictions",
            placeholder="vegetarian, gluten-free, kosher",
            info="Dietary restrictions separated by commas"
        )

        create_profile_btn = gr.Button("Create Profile", variant="primary")
        profile_output = gr.Textbox(label="Profile Status", interactive=False)

        create_profile_btn.click(
            create_user_profile,
            inputs=[name_input, age_input, allergies_input, medications_input, dietary_input],
            outputs=profile_output
        )

    with gr.Tab("📷 Barcode Scanner"):
        gr.Markdown("### Scan Product Barcode")

        with gr.Row():
            with gr.Column():
                barcode_image = gr.Image(type="pil", label="Upload Barcode Image")
                scan_btn = gr.Button("Scan Barcode", variant="primary")

            with gr.Column():
                scan_output = gr.Markdown(label="Scan Results")

        scan_btn.click(
            scan_barcode_image,
            inputs=barcode_image,
            outputs=scan_output
        )

    with gr.Tab("📝 Manual Analysis"):
        gr.Markdown("### Analyze Ingredients Manually")

        with gr.Row():
            with gr.Column():
                ingredients_input = gr.Textbox(
                    label="Ingredients List",
                    placeholder="wheat flour, milk, eggs, sugar, chocolate chips",
                    info="Enter ingredients separated by commas",
                    lines=3
                )
                analyze_btn = gr.Button("Analyze Ingredients", variant="primary")

            with gr.Column():
                analysis_output = gr.Markdown(label="Analysis Results")

        analyze_btn.click(
            analyze_manual_ingredients,
            inputs=ingredients_input,
            outputs=analysis_output
        )

    with gr.Tab("🤖 AI Assistant"):
        gr.Markdown("### Chat with Health AI Assistant")

        chatbot = gr.Chatbot(label="AI Health Assistant", height=400, type="messages")
        msg = gr.Textbox(
            label="Ask a question",
            placeholder="Ask about allergens, nutrition, or food safety...",
            lines=2
        )

        msg.submit(chat_with_ai, [msg, chatbot], [chatbot, msg])

    with gr.Tab("👨‍⚕️ Doctor Consultation"):
        gr.Markdown("### Request Medical Consultation")

        with gr.Row():
            with gr.Column():
                concern_type = gr.Dropdown(
                    ["Allergen", "Drug Interaction", "General", "Emergency"],
                    label="Type of Concern",
                    value="Allergen"
                )
                urgency = gr.Dropdown(
                    ["Routine", "Urgent", "Emergency"],
                    label="Urgency Level",
                    value="Routine"
                )
                consult_btn = gr.Button("Request Consultation", variant="primary")

            with gr.Column():
                consultation_output = gr.Markdown(label="Consultation Details")

        consult_btn.click(
            request_doctor_consultation,
            inputs=[concern_type, urgency],
            outputs=consultation_output
        )

    with gr.Tab("🚨 Emergency"):
        gr.Markdown("### Emergency Information")

        emergency_btn = gr.Button("Get Emergency Contacts", variant="stop")
        emergency_output = gr.Markdown(label="Emergency Contacts")

        emergency_btn.click(
            get_emergency_contacts,
            outputs=emergency_output
        )

        gr.Markdown("""
        ### ⚠️ Important Emergency Notice

        **For severe allergic reactions (anaphylaxis):**
        1. Use EpiPen immediately if available
        2. Call 911
        3. Get to nearest hospital

        **This app is for informational purposes only and should not replace professional medical advice.**
        """)

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True
    )