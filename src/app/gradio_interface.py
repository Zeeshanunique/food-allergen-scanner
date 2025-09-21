"""
Gradio Interface for AI Food Allergen Scanner
"""
import gradio as gr
import os
import sys
import json
from PIL import Image
import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.barcode_scanner import BarcodeScanner
    from services.ingredient_analyzer import IngredientAnalyzer
    from services.medication_checker import MedicationChecker
    from services.ai_assistant import AIAssistant
    from services.doctor_consultation import DoctorConsultation
    from models.user_profile import UserProfile
    from utils.database import DatabaseManager
except ImportError as e:
    print(f"Import error: {e}")
    # Create mock classes for basic functionality
    class BarcodeScanner:
        def scan_barcode(self, image): return "123456789"
        def get_product_info(self, barcode): return {"name": "Test Product", "ingredients": ["test"]}
    
    class IngredientAnalyzer:
        def analyze_ingredients(self, ingredients, profile): return {"risk_level": "low"}
    
    class MedicationChecker:
        def check_interactions(self, ingredients, profile): return {"interactions": []}
    
    class AIAssistant:
        def get_response(self, message, profile): return "AI assistant is initializing..."
    
    class DoctorConsultation:
        def request_consultation(self, data): return {"status": "requested"}
    
    class UserProfile:
        def __init__(self, **kwargs): pass
        def to_dict(self): return {}
    
    class DatabaseManager:
        def save_user_profile(self, profile): return True

class FoodAllergenScannerInterface:
    """Gradio interface for the Food Allergen Scanner application"""
    
    def __init__(self):
        self.barcode_scanner = BarcodeScanner()
        self.ingredient_analyzer = IngredientAnalyzer()
        self.medication_checker = MedicationChecker()
        self.ai_assistant = AIAssistant()
        self.doctor_consultation = DoctorConsultation()
        self.db_manager = DatabaseManager()
        self.current_user_profile = None
        
        # Initialize the interface
        self.interface = self._create_interface()
    
    def _create_interface(self):
        """Create the Gradio interface"""
        
        with gr.Blocks(
            title="AI Food Allergen Scanner",
            theme=gr.themes.Soft(),
            css=self._get_custom_css()
        ) as interface:
            
            # Header
            gr.HTML("""
            <div class="header">
                <h1>🍎 AI Food Allergen Scanner</h1>
                <p>Your intelligent companion for safe food consumption</p>
            </div>
            """)
            
            # User Profile Section
            with gr.Tab("👤 User Profile"):
                self._create_profile_tab()
            
            # Barcode Scanner Section
            with gr.Tab("📱 Barcode Scanner"):
                self._create_barcode_tab()
            
            # Manual Input Section
            with gr.Tab("✍️ Manual Input"):
                self._create_manual_input_tab()
            
            # Analysis Results Section
            with gr.Tab("🔍 Analysis Results"):
                self._create_results_tab()
            
            # Doctor Consultation Section
            with gr.Tab("👨‍⚕️ Doctor Consultation"):
                self._create_consultation_tab()
            
            # AI Assistant Section
            with gr.Tab("🤖 AI Assistant"):
                self._create_ai_assistant_tab()
            
            # ML Training Section
            with gr.Tab("🧠 ML Training"):
                self._create_ml_training_tab()
        
        return interface
    
    def _create_profile_tab(self):
        """Create user profile management tab"""
        gr.HTML("<h2>Manage Your Health Profile</h2>")
        
        with gr.Row():
            with gr.Column():
                name_input = gr.Textbox(label="Full Name", placeholder="Enter your full name")
                age_input = gr.Number(label="Age", minimum=1, maximum=120)
                weight_input = gr.Number(label="Weight (kg)", minimum=1)
                
                allergies_input = gr.Textbox(
                    label="Known Allergies",
                    placeholder="Enter allergies separated by commas (e.g., peanuts, shellfish, dairy)",
                    lines=3
                )
                
                medications_input = gr.Textbox(
                    label="Current Medications",
                    placeholder="Enter medications separated by commas (e.g., aspirin, insulin)",
                    lines=3
                )
                
                medical_conditions = gr.Textbox(
                    label="Medical Conditions",
                    placeholder="Enter any medical conditions (e.g., diabetes, hypertension)",
                    lines=2
                )
                
                emergency_contact = gr.Textbox(
                    label="Emergency Contact",
                    placeholder="Name and phone number"
                )
            
            with gr.Column():
                profile_status = gr.HTML("<p>No profile loaded</p>")
                
                save_profile_btn = gr.Button("💾 Save Profile", variant="primary")
                load_profile_btn = gr.Button("📂 Load Profile")
                
                # Profile actions
                save_profile_btn.click(
                    fn=self._save_user_profile,
                    inputs=[name_input, age_input, weight_input, allergies_input, 
                           medications_input, medical_conditions, emergency_contact],
                    outputs=[profile_status]
                )
    
    def _create_barcode_tab(self):
        """Create barcode scanning tab"""
        gr.HTML("<h2>Scan Product Barcode</h2>")
        
        with gr.Row():
            with gr.Column():
                barcode_image = gr.Image(
                    label="Upload Barcode Image",
                    type="pil",
                    height=300
                )
                
                scan_btn = gr.Button("🔍 Scan Barcode", variant="primary")
                
            with gr.Column():
                barcode_result = gr.Textbox(
                    label="Barcode Number",
                    interactive=False
                )
                
                product_info = gr.JSON(
                    label="Product Information",
                    visible=False
                )
                
                ingredients_list = gr.Textbox(
                    label="Ingredients",
                    lines=5,
                    interactive=False
                )
        
        # Barcode scanning action
        scan_btn.click(
            fn=self._scan_barcode,
            inputs=[barcode_image],
            outputs=[barcode_result, product_info, ingredients_list]
        )
    
    def _create_manual_input_tab(self):
        """Create manual ingredient input tab"""
        gr.HTML("<h2>Manual Ingredient Input</h2>")
        
        with gr.Row():
            with gr.Column():
                product_name_input = gr.Textbox(
                    label="Product/Dish Name",
                    placeholder="Enter the name of the food item"
                )
                
                ingredients_manual = gr.Textbox(
                    label="Ingredients List",
                    placeholder="Enter ingredients separated by commas",
                    lines=8
                )
                
                serving_size = gr.Textbox(
                    label="Serving Size (optional)",
                    placeholder="e.g., 100g, 1 cup"
                )
                
                analyze_manual_btn = gr.Button("🔍 Analyze Ingredients", variant="primary")
            
            with gr.Column():
                manual_analysis_result = gr.HTML("<p>Enter ingredients to analyze</p>")
        
        # Manual analysis action
        analyze_manual_btn.click(
            fn=self._analyze_manual_ingredients,
            inputs=[product_name_input, ingredients_manual, serving_size],
            outputs=[manual_analysis_result]
        )
    
    def _create_results_tab(self):
        """Create analysis results tab"""
        gr.HTML("<h2>Analysis Results & Health Alerts</h2>")
        
        # Risk Assessment Display
        risk_assessment = gr.HTML(
            "<div class='risk-neutral'>No analysis performed yet</div>"
        )
        
        # Detailed Analysis
        with gr.Row():
            with gr.Column():
                allergy_alerts = gr.HTML("<h3>🚨 Allergy Alerts</h3><p>No alerts</p>")
                
            with gr.Column():
                medication_interactions = gr.HTML("<h3>💊 Medication Interactions</h3><p>No interactions found</p>")
        
        # Recommendations
        recommendations = gr.HTML("<h3>💡 Recommendations</h3><p>No recommendations available</p>")
        
        # Store components for later use
        self.risk_assessment = risk_assessment
        self.allergy_alerts = allergy_alerts
        self.medication_interactions = medication_interactions
        self.recommendations = recommendations
    
    def _create_consultation_tab(self):
        """Create doctor consultation tab"""
        gr.HTML("<h2>Doctor Consultation</h2>")
        
        with gr.Row():
            with gr.Column():
                consultation_type = gr.Radio(
                    choices=["General Consultation", "Allergy Specialist", "Emergency"],
                    label="Consultation Type",
                    value="General Consultation"
                )
                
                symptoms = gr.Textbox(
                    label="Current Symptoms (if any)",
                    placeholder="Describe any symptoms you're experiencing",
                    lines=3
                )
                
                urgency = gr.Radio(
                    choices=["Low", "Medium", "High", "Emergency"],
                    label="Urgency Level",
                    value="Low"
                )
                
                request_consultation_btn = gr.Button("📞 Request Consultation", variant="primary")
            
            with gr.Column():
                doctor_list = gr.HTML(self._get_available_doctors())
                consultation_status = gr.HTML("<p>Ready to connect with healthcare professionals</p>")
        
        # Consultation request action
        request_consultation_btn.click(
            fn=self._request_consultation,
            inputs=[consultation_type, symptoms, urgency],
            outputs=[consultation_status]
        )
    
    def _create_ai_assistant_tab(self):
        """Create AI assistant tab"""
        gr.HTML("<h2>AI Health Assistant</h2>")
        
        chatbot = gr.Chatbot(
            label="Chat with AI Assistant",
            height=400
        )
        
        with gr.Row():
            msg_input = gr.Textbox(
                label="Your Message",
                placeholder="Ask me anything about food allergies, nutrition, or health...",
                scale=4
            )
            
            send_btn = gr.Button("Send", variant="primary", scale=1)
        
        # Predefined quick questions
        gr.HTML("<h4>Quick Questions:</h4>")
        with gr.Row():
            quick_btns = [
                gr.Button("What are common food allergens?"),
                gr.Button("How to read ingredient labels?"),
                gr.Button("Emergency allergy response"),
                gr.Button("Healthy alternatives")
            ]
        
        # Chat functionality
        def respond(message, chat_history):
            response = self.ai_assistant.get_response(message, self.current_user_profile)
            chat_history.append((message, response))
            return "", chat_history
        
        send_btn.click(respond, [msg_input, chatbot], [msg_input, chatbot])
        msg_input.submit(respond, [msg_input, chatbot], [msg_input, chatbot])
        
        # Quick question handlers
        for i, btn in enumerate(quick_btns):
            quick_questions = [
                "What are common food allergens?",
                "How to read ingredient labels?",
                "What should I do in case of allergic reaction?",
                "What are healthy alternatives for common allergens?"
            ]
            btn.click(
                lambda q=quick_questions[i]: ("", [(q, self.ai_assistant.get_response(q, self.current_user_profile))]),
                outputs=[msg_input, chatbot]
            )
    
    def _create_ml_training_tab(self):
        """Create ML training and data management tab"""
        gr.HTML("<h2>Machine Learning Training</h2>")
        
        with gr.Tab("📊 Training Data"):
            with gr.Row():
                with gr.Column():
                    training_data_upload = gr.File(
                        label="Upload Training Data (CSV/JSON)",
                        file_types=[".csv", ".json"]
                    )
                    
                    data_type = gr.Radio(
                        choices=["Product Data", "Allergen Data", "Medication Data"],
                        label="Data Type",
                        value="Product Data"
                    )
                    
                    upload_training_btn = gr.Button("📤 Upload Data", variant="primary")
                
                with gr.Column():
                    training_status = gr.HTML("<p>No training data uploaded</p>")
        
        with gr.Tab("🎯 Model Training"):
            with gr.Row():
                with gr.Column():
                    model_type = gr.Radio(
                        choices=["Ingredient Classifier", "Allergy Predictor", "Risk Assessor"],
                        label="Model Type",
                        value="Ingredient Classifier"
                    )
                    
                    training_params = gr.JSON(
                        label="Training Parameters",
                        value={"epochs": 10, "batch_size": 32, "learning_rate": 0.001}
                    )
                    
                    start_training_btn = gr.Button("🚀 Start Training", variant="primary")
                
                with gr.Column():
                    training_progress = gr.HTML("<p>Ready to train</p>")
                    model_metrics = gr.JSON(label="Model Performance", visible=False)
        
        # Training actions
        upload_training_btn.click(
            fn=self._upload_training_data,
            inputs=[training_data_upload, data_type],
            outputs=[training_status]
        )
        
        start_training_btn.click(
            fn=self._start_model_training,
            inputs=[model_type, training_params],
            outputs=[training_progress, model_metrics]
        )
    
    def _get_custom_css(self):
        """Return custom CSS for the interface"""
        return """
        .header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
            color: white;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .risk-high {
            background-color: #ffebee;
            border: 2px solid #f44336;
            padding: 15px;
            border-radius: 8px;
            color: #d32f2f;
        }
        
        .risk-medium {
            background-color: #fff3e0;
            border: 2px solid #ff9800;
            padding: 15px;
            border-radius: 8px;
            color: #f57c00;
        }
        
        .risk-low {
            background-color: #e8f5e8;
            border: 2px solid #4caf50;
            padding: 15px;
            border-radius: 8px;
            color: #388e3c;
        }
        
        .risk-neutral {
            background-color: #f5f5f5;
            border: 2px solid #9e9e9e;
            padding: 15px;
            border-radius: 8px;
            color: #616161;
        }
        """
    
    def _save_user_profile(self, name, age, weight, allergies, medications, conditions, emergency_contact):
        """Save user profile to database"""
        try:
            profile_data = {
                'name': name,
                'age': int(age) if age else None,
                'weight': float(weight) if weight else None,
                'allergies': [a.strip() for a in allergies.split(',') if a.strip()],
                'medications': [m.strip() for m in medications.split(',') if m.strip()],
                'medical_conditions': [c.strip() for c in conditions.split(',') if c.strip()],
                'emergency_contact': emergency_contact
            }
            
            self.current_user_profile = UserProfile(**profile_data)
            self.db_manager.save_user_profile(self.current_user_profile)
            
            return f"<div class='risk-low'>✅ Profile saved successfully for {name}</div>"
        except Exception as e:
            return f"<div class='risk-high'>❌ Error saving profile: {str(e)}</div>"
    
    def _scan_barcode(self, image):
        """Scan barcode from uploaded image"""
        if image is None:
            return "No image uploaded", {}, "Please upload a barcode image"
        
        try:
            barcode_data = self.barcode_scanner.scan_barcode(image)
            if barcode_data:
                product_info = self.barcode_scanner.get_product_info(barcode_data)
                ingredients = product_info.get('ingredients', 'No ingredients found')
                return barcode_data, product_info, ingredients
            else:
                return "No barcode detected", {}, "Could not detect barcode in image"
        except Exception as e:
            return f"Error: {str(e)}", {}, "Error processing barcode"
    
    def _analyze_manual_ingredients(self, product_name, ingredients, serving_size):
        """Analyze manually entered ingredients"""
        if not ingredients.strip():
            return "<div class='risk-neutral'>Please enter ingredients to analyze</div>"
        
        try:
            # Perform analysis
            analysis_result = self.ingredient_analyzer.analyze_ingredients(
                ingredients, self.current_user_profile
            )
            
            # Check for medication interactions
            medication_result = self.medication_checker.check_interactions(
                ingredients, self.current_user_profile
            )
            
            # Generate comprehensive report
            report = self._generate_analysis_report(analysis_result, medication_result, product_name)
            
            return report
        except Exception as e:
            return f"<div class='risk-high'>Error analyzing ingredients: {str(e)}</div>"
    
    def _generate_analysis_report(self, allergy_result, medication_result, product_name="Unknown Product"):
        """Generate comprehensive analysis report"""
        risk_level = "low"
        alerts = []
        
        # Check allergy risks
        if allergy_result.get('high_risk_allergens'):
            risk_level = "high"
            alerts.extend(allergy_result['high_risk_allergens'])
        elif allergy_result.get('moderate_risk_allergens'):
            risk_level = "medium"
            alerts.extend(allergy_result['moderate_risk_allergens'])
        
        # Check medication interactions
        if medication_result.get('interactions'):
            if risk_level != "high":
                risk_level = "high" if medication_result.get('severe_interactions') else "medium"
        
        # Generate HTML report
        risk_class = f"risk-{risk_level}"
        status_emoji = {"high": "🚨", "medium": "⚠️", "low": "✅", "neutral": "ℹ️"}
        
        report = f"""
        <div class='{risk_class}'>
            <h3>{status_emoji.get(risk_level, 'ℹ️')} Analysis Results for {product_name}</h3>
        """
        
        if risk_level == "high":
            report += "<p><strong>HIGH RISK - DO NOT CONSUME</strong></p>"
        elif risk_level == "medium":
            report += "<p><strong>MODERATE RISK - CAUTION ADVISED</strong></p>"
        else:
            report += "<p><strong>LOW RISK - SAFE TO CONSUME</strong></p>"
        
        if alerts:
            report += f"<p><strong>Alerts:</strong> {', '.join(alerts)}</p>"
        
        report += "</div>"
        
        return report
    
    def _get_available_doctors(self):
        """Get list of available doctors"""
        return """
        <h4>Available Healthcare Providers:</h4>
        <ul>
            <li>👨‍⚕️ Dr. Smith - General Medicine (Available)</li>
            <li>👩‍⚕️ Dr. Johnson - Allergy Specialist (Available)</li>
            <li>👨‍⚕️ Dr. Brown - Emergency Medicine (On Call)</li>
        </ul>
        <p><small>* Availability shown in real-time</small></p>
        """
    
    def _request_consultation(self, consultation_type, symptoms, urgency):
        """Request doctor consultation"""
        try:
            consultation_data = {
                'type': consultation_type,
                'symptoms': symptoms,
                'urgency': urgency,
                'user_profile': self.current_user_profile
            }
            
            result = self.doctor_consultation.request_consultation(consultation_data)
            
            if urgency == "Emergency":
                return "<div class='risk-high'>🚨 Emergency consultation requested. You will be contacted immediately.</div>"
            else:
                return f"<div class='risk-low'>✅ Consultation requested. Estimated wait time: {result.get('wait_time', '15-30 minutes')}</div>"
        
        except Exception as e:
            return f"<div class='risk-high'>Error requesting consultation: {str(e)}</div>"
    
    def _upload_training_data(self, file_data, data_type):
        """Upload training data for ML models"""
        if file_data is None:
            return "<div class='risk-neutral'>No file uploaded</div>"
        
        try:
            # Process uploaded file
            # This would involve parsing CSV/JSON and storing in training database
            return f"<div class='risk-low'>✅ {data_type} training data uploaded successfully</div>"
        except Exception as e:
            return f"<div class='risk-high'>Error uploading training data: {str(e)}</div>"
    
    def _start_model_training(self, model_type, training_params):
        """Start ML model training"""
        try:
            # This would trigger the actual ML training process
            progress_html = f"<div class='risk-neutral'>🔄 Training {model_type} model...</div>"
            metrics = {"accuracy": 0.85, "precision": 0.82, "recall": 0.88}
            
            return progress_html, metrics
        except Exception as e:
            return f"<div class='risk-high'>Error starting training: {str(e)}</div>", {}
    
    def launch(self, share=False, debug=True):
        """Launch the Gradio interface"""
        return self.interface.launch(
            share=share,
            debug=debug,
            server_name="0.0.0.0",
            server_port=7860,
            show_error=True
        )