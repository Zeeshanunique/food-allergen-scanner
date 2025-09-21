"""
Doctor Consultation Service for Food Allergen Scanner
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user_profile import UserProfile

class DoctorConsultation:
    """Service for managing doctor consultations and appointments"""
    
    def __init__(self):
        self.doctors_db = self._load_doctors_database()
        self.consultation_queue = []
        self.consultation_history = []
        
        # Default doctor information
        self.default_doctors = {
            'general_practitioner': {
                'name': 'Dr. Sarah Johnson',
                'specialty': 'General Medicine',
                'phone': '+1-555-0123',
                'email': 'dr.johnson@healthcenter.com',
                'availability': 'Mon-Fri 9AM-5PM',
                'emergency': False,
                'languages': ['English'],
                'experience_years': 15
            },
            'allergist': {
                'name': 'Dr. Michael Chen',
                'specialty': 'Allergy & Immunology',
                'phone': '+1-555-0124',
                'email': 'dr.chen@allergyspecialist.com',
                'availability': 'Mon-Wed-Fri 8AM-4PM',
                'emergency': False,
                'languages': ['English', 'Mandarin'],
                'experience_years': 12
            },
            'emergency_physician': {
                'name': 'Dr. Emily Rodriguez',
                'specialty': 'Emergency Medicine',
                'phone': '+1-555-0911',
                'email': 'emergency@hospital.com',
                'availability': '24/7',
                'emergency': True,
                'languages': ['English', 'Spanish'],
                'experience_years': 8
            },
            'pharmacist': {
                'name': 'PharmD Lisa Wang',
                'specialty': 'Clinical Pharmacy',
                'phone': '+1-555-0125',
                'email': 'lisa.wang@pharmacy.com',
                'availability': 'Mon-Sat 8AM-8PM',
                'emergency': False,
                'languages': ['English'],
                'experience_years': 10
            }
        }
        
        # Consultation types and their priorities
        self.consultation_types = {
            'emergency': {
                'priority': 1,
                'response_time': 'immediate',
                'description': 'Life-threatening allergic reactions'
            },
            'urgent': {
                'priority': 2,
                'response_time': '15-30 minutes',
                'description': 'Severe symptoms requiring prompt attention'
            },
            'allergy_specialist': {
                'priority': 3,
                'response_time': '1-2 hours',
                'description': 'Specialized allergy consultation'
            },
            'general_consultation': {
                'priority': 4,
                'response_time': '2-4 hours',
                'description': 'General health questions and concerns'
            },
            'medication_review': {
                'priority': 4,
                'response_time': '1-2 hours',
                'description': 'Medication interaction concerns'
            }
        }
    
    def request_consultation(self, consultation_data: Dict) -> Dict:
        """
        Request a doctor consultation
        """
        consultation_type = consultation_data.get('type', 'general_consultation').lower()
        urgency = consultation_data.get('urgency', 'low').lower()
        symptoms = consultation_data.get('symptoms', '')
        user_profile = consultation_data.get('user_profile')
        
        # Determine actual consultation type based on urgency
        if urgency == 'emergency':
            consultation_type = 'emergency'
        elif urgency == 'high':
            consultation_type = 'urgent'
        
        # Create consultation request
        consultation_request = {
            'id': self._generate_consultation_id(),
            'type': consultation_type,
            'urgency': urgency,
            'symptoms': symptoms,
            'user_profile': user_profile.to_dict() if user_profile else None,
            'requested_at': datetime.now(),
            'status': 'pending',
            'estimated_response_time': self._get_response_time(consultation_type),
            'assigned_doctor': self._assign_doctor(consultation_type, urgency),
            'contact_methods': self._get_contact_methods(consultation_type, urgency)
        }
        
        # Handle emergency requests immediately
        if consultation_type == 'emergency':
            return self._handle_emergency_consultation(consultation_request)
        
        # Add to consultation queue
        self.consultation_queue.append(consultation_request)
        
        # Send notifications
        notification_result = self._send_consultation_notification(consultation_request)
        
        return {
            'consultation_id': consultation_request['id'],
            'status': 'requested',
            'estimated_response_time': consultation_request['estimated_response_time'],
            'assigned_doctor': consultation_request['assigned_doctor'],
            'contact_methods': consultation_request['contact_methods'],
            'priority': self.consultation_types.get(consultation_type, {}).get('priority', 4),
            'instructions': self._get_consultation_instructions(consultation_type, urgency),
            'notification_sent': notification_result,
            'next_steps': self._get_next_steps(consultation_type, urgency)
        }
    
    def _handle_emergency_consultation(self, consultation_request: Dict) -> Dict:
        """Handle emergency consultation requests"""
        emergency_response = {
            'consultation_id': consultation_request['id'],
            'status': 'emergency_initiated',
            'immediate_action': 'CALL 911 IMMEDIATELY',
            'emergency_number': '911',
            'assigned_doctor': self.default_doctors['emergency_physician'],
            'hospital_contact': {
                'name': 'City General Hospital Emergency Department',
                'phone': '+1-555-0911',
                'address': '123 Health Street, Your City'
            },
            'instructions': [
                '🚨 Call 911 immediately',
                '💉 Use EpiPen if available and prescribed',
                '🏥 Go to nearest emergency room',
                '📋 Bring all medications and allergy information',
                '👥 Have someone accompany you if possible'
            ],
            'estimated_response_time': 'immediate',
            'priority': 1
        }
        
        # Log emergency consultation
        self.consultation_history.append({
            **consultation_request,
            'resolved_at': datetime.now(),
            'resolution': 'emergency_protocol_initiated'
        })
        
        return emergency_response
    
    def _assign_doctor(self, consultation_type: str, urgency: str) -> Dict:
        """Assign appropriate doctor based on consultation type"""
        
        if consultation_type == 'emergency':
            return self.default_doctors['emergency_physician']
        elif consultation_type in ['allergy_specialist', 'urgent'] and 'allerg' in consultation_type:
            return self.default_doctors['allergist']
        elif consultation_type == 'medication_review':
            return self.default_doctors['pharmacist']
        else:
            return self.default_doctors['general_practitioner']
    
    def _get_response_time(self, consultation_type: str) -> str:
        """Get estimated response time for consultation type"""
        return self.consultation_types.get(consultation_type, {}).get('response_time', '2-4 hours')
    
    def _get_contact_methods(self, consultation_type: str, urgency: str) -> List[Dict]:
        """Get available contact methods"""
        if consultation_type == 'emergency':
            return [
                {'method': 'phone', 'number': '911', 'description': 'Emergency services'},
                {'method': 'hospital', 'address': 'Nearest emergency room', 'description': 'In-person emergency care'}
            ]
        
        return [
            {'method': 'phone', 'description': 'Phone consultation', 'available': True},
            {'method': 'video', 'description': 'Video call consultation', 'available': True},
            {'method': 'chat', 'description': 'Secure text chat', 'available': urgency != 'high'},
            {'method': 'in_person', 'description': 'Office visit', 'available': urgency == 'low'}
        ]
    
    def _get_consultation_instructions(self, consultation_type: str, urgency: str) -> List[str]:
        """Get instructions for different consultation types"""
        
        base_instructions = [
            '📱 Keep your phone nearby for doctor contact',
            '📋 Have your allergy profile and medication list ready',
            '🆔 Have your identification and insurance information available'
        ]
        
        if consultation_type == 'emergency':
            return [
                '🚨 This is a medical emergency',
                '📞 Call 911 immediately',
                '💉 Use emergency medication if prescribed',
                '🏥 Proceed to nearest emergency room'
            ]
        
        elif urgency == 'high':
            return [
                '⚠️ This is urgent - doctor will contact you soon',
                '📱 Answer phone calls from healthcare providers',
                '💊 Do not take any new medications until speaking with doctor',
                '🏥 Be prepared to visit emergency room if symptoms worsen'
            ] + base_instructions
        
        else:
            return [
                '📞 Doctor will contact you within estimated timeframe',
                '❓ Prepare any questions you want to ask',
                '📝 Note any symptom changes while waiting'
            ] + base_instructions
    
    def _get_next_steps(self, consultation_type: str, urgency: str) -> List[str]:
        """Get next steps for patient"""
        
        if consultation_type == 'emergency':
            return [
                'Seek immediate emergency medical care',
                'Follow emergency protocol',
                'Contact emergency services'
            ]
        
        elif urgency == 'high':
            return [
                'Wait for doctor to contact you within 15-30 minutes',
                'Monitor symptoms closely',
                'Seek emergency care if symptoms worsen',
                'Take photos of any visible reactions if safe to do so'
            ]
        
        else:
            return [
                f'Doctor will contact you within {self._get_response_time(consultation_type)}',
                'Prepare questions and relevant information',
                'Continue monitoring any symptoms',
                'Avoid suspected allergens until consultation'
            ]
    
    def _send_consultation_notification(self, consultation_request: Dict) -> bool:
        """Send notification to healthcare provider"""
        try:
            # In a real implementation, this would send actual notifications
            # via email, SMS, or integration with medical systems
            
            doctor = consultation_request['assigned_doctor']
            notification_data = {
                'consultation_id': consultation_request['id'],
                'patient_info': consultation_request.get('user_profile', {}),
                'urgency': consultation_request['urgency'],
                'symptoms': consultation_request['symptoms'],
                'doctor_contact': doctor,
                'timestamp': consultation_request['requested_at']
            }
            
            # Log notification (simulate sending)
            print(f"Notification sent to {doctor['name']} for consultation {consultation_request['id']}")
            return True
            
        except Exception as e:
            print(f"Error sending notification: {str(e)}")
            return False
    
    def get_consultation_status(self, consultation_id: str) -> Optional[Dict]:
        """Get status of a consultation request"""
        
        # Check pending consultations
        for consultation in self.consultation_queue:
            if consultation['id'] == consultation_id:
                return {
                    'id': consultation_id,
                    'status': consultation['status'],
                    'estimated_response_time': consultation['estimated_response_time'],
                    'assigned_doctor': consultation['assigned_doctor'],
                    'requested_at': consultation['requested_at'],
                    'time_elapsed': str(datetime.now() - consultation['requested_at'])
                }
        
        # Check consultation history
        for consultation in self.consultation_history:
            if consultation['id'] == consultation_id:
                return {
                    'id': consultation_id,
                    'status': 'completed',
                    'resolved_at': consultation.get('resolved_at'),
                    'resolution': consultation.get('resolution'),
                    'assigned_doctor': consultation['assigned_doctor']
                }
        
        return None
    
    def get_available_doctors(self, specialty: Optional[str] = None) -> List[Dict]:
        """Get list of available doctors"""
        available_doctors = []
        
        for doctor_type, doctor_info in self.default_doctors.items():
            if specialty is None or specialty.lower() in doctor_info['specialty'].lower():
                available_doctors.append({
                    **doctor_info,
                    'type': doctor_type,
                    'currently_available': self._is_doctor_available(doctor_info)
                })
        
        return available_doctors
    
    def _is_doctor_available(self, doctor_info: Dict) -> bool:
        """Check if doctor is currently available"""
        availability = doctor_info.get('availability', '')
        
        if '24/7' in availability:
            return True
        
        # Simple availability check (in real implementation, would check actual schedules)
        current_time = datetime.now()
        current_hour = current_time.hour
        current_weekday = current_time.weekday()  # 0 = Monday
        
        if 'Mon-Fri' in availability and current_weekday < 5:
            if '9AM-5PM' in availability and 9 <= current_hour < 17:
                return True
            elif '8AM-4PM' in availability and 8 <= current_hour < 16:
                return True
        
        return False
    
    def _generate_consultation_id(self) -> str:
        """Generate unique consultation ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        import random
        random_suffix = random.randint(1000, 9999)
        return f"CONSULT_{timestamp}_{random_suffix}"
    
    def _load_doctors_database(self) -> Dict:
        """Load doctors database from file"""
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'data', 
            'doctor_contacts.json'
        )
        
        try:
            if os.path.exists(db_path):
                with open(db_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading doctors database: {str(e)}")
        
        return {}
    
    def add_custom_doctor(self, doctor_info: Dict):
        """Add custom doctor to the system"""
        doctor_id = doctor_info.get('id', f"custom_{len(self.default_doctors)}")
        self.default_doctors[doctor_id] = doctor_info
    
    def get_consultation_history(self, user_profile: UserProfile = None) -> List[Dict]:
        """Get consultation history for user"""
        if not user_profile:
            return self.consultation_history
        
        # Filter by user profile if provided
        user_consultations = []
        user_name = user_profile.name.lower() if user_profile.name else ""
        
        for consultation in self.consultation_history:
            consultation_profile = consultation.get('user_profile', {})
            consultation_name = consultation_profile.get('name', '').lower()
            
            if consultation_name == user_name:
                user_consultations.append(consultation)
        
        return user_consultations
    
    def cancel_consultation(self, consultation_id: str) -> bool:
        """Cancel a pending consultation"""
        for i, consultation in enumerate(self.consultation_queue):
            if consultation['id'] == consultation_id:
                consultation['status'] = 'cancelled'
                consultation['cancelled_at'] = datetime.now()
                
                # Move to history
                self.consultation_history.append(consultation)
                self.consultation_queue.pop(i)
                
                return True
        
        return False