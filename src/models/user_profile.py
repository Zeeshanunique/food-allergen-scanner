"""
User Profile Model for Food Allergen Scanner
"""
from datetime import datetime
from typing import List, Dict, Optional
import json

class UserProfile:
    """User profile containing allergy and medication information"""
    
    def __init__(self, 
                 name: str = "",
                 age: Optional[int] = None,
                 weight: Optional[float] = None,
                 allergies: List[str] = None,
                 medications: List[str] = None,
                 medical_conditions: List[str] = None,
                 emergency_contact: str = "",
                 created_at: Optional[datetime] = None):
        
        self.name = name
        self.age = age
        self.weight = weight
        self.allergies = allergies or []
        self.medications = medications or []
        self.medical_conditions = medical_conditions or []
        self.emergency_contact = emergency_contact
        self.created_at = created_at or datetime.now()
        self.updated_at = datetime.now()
    
    def add_allergy(self, allergy: str):
        """Add an allergy to the profile"""
        if allergy and allergy.lower() not in [a.lower() for a in self.allergies]:
            self.allergies.append(allergy)
            self.updated_at = datetime.now()
    
    def remove_allergy(self, allergy: str):
        """Remove an allergy from the profile"""
        self.allergies = [a for a in self.allergies if a.lower() != allergy.lower()]
        self.updated_at = datetime.now()
    
    def add_medication(self, medication: str):
        """Add a medication to the profile"""
        if medication and medication.lower() not in [m.lower() for m in self.medications]:
            self.medications.append(medication)
            self.updated_at = datetime.now()
    
    def remove_medication(self, medication: str):
        """Remove a medication from the profile"""
        self.medications = [m for m in self.medications if m.lower() != medication.lower()]
        self.updated_at = datetime.now()
    
    def has_allergy(self, ingredient: str) -> bool:
        """Check if user has a specific allergy"""
        return any(allergy.lower() in ingredient.lower() or 
                  ingredient.lower() in allergy.lower() 
                  for allergy in self.allergies)
    
    def has_medication(self, medication: str) -> bool:
        """Check if user is taking a specific medication"""
        return any(med.lower() in medication.lower() or 
                  medication.lower() in med.lower() 
                  for med in self.medications)
    
    def get_risk_factors(self) -> Dict[str, List[str]]:
        """Get risk factors for analysis"""
        return {
            'allergies': self.allergies,
            'medications': self.medications,
            'medical_conditions': self.medical_conditions,
            'age_group': self._get_age_group(),
            'weight_category': self._get_weight_category()
        }
    
    def _get_age_group(self) -> str:
        """Categorize user by age group"""
        if not self.age:
            return "unknown"
        
        if self.age < 2:
            return "infant"
        elif self.age < 13:
            return "child"
        elif self.age < 18:
            return "adolescent"
        elif self.age < 65:
            return "adult"
        else:
            return "senior"
    
    def _get_weight_category(self) -> str:
        """Categorize user by weight (requires height for BMI, simplified here)"""
        if not self.weight:
            return "unknown"
        
        # Simplified weight categories
        if self.weight < 50:
            return "underweight"
        elif self.weight < 80:
            return "normal"
        elif self.weight < 100:
            return "overweight"
        else:
            return "obese"
    
    def to_dict(self) -> Dict:
        """Convert profile to dictionary"""
        return {
            'name': self.name,
            'age': self.age,
            'weight': self.weight,
            'allergies': self.allergies,
            'medications': self.medications,
            'medical_conditions': self.medical_conditions,
            'emergency_contact': self.emergency_contact,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_json(self) -> str:
        """Convert profile to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserProfile':
        """Create profile from dictionary"""
        profile = cls(
            name=data.get('name', ''),
            age=data.get('age'),
            weight=data.get('weight'),
            allergies=data.get('allergies', []),
            medications=data.get('medications', []),
            medical_conditions=data.get('medical_conditions', []),
            emergency_contact=data.get('emergency_contact', '')
        )
        
        # Handle datetime fields
        if data.get('created_at'):
            profile.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            profile.updated_at = datetime.fromisoformat(data['updated_at'])
        
        return profile
    
    @classmethod
    def from_json(cls, json_str: str) -> 'UserProfile':
        """Create profile from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """String representation of the profile"""
        return f"UserProfile(name='{self.name}', allergies={len(self.allergies)}, medications={len(self.medications)})"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"UserProfile(name='{self.name}', age={self.age}, "
                f"allergies={self.allergies}, medications={self.medications})")