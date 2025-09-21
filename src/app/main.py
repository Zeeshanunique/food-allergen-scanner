"""
AI Food Allergen Scanner - Main Application Module
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .gradio_interface import FoodAllergenScannerInterface

class FoodAllergenScannerApp:
    """Main application class for the Food Allergen Scanner"""
    
    def __init__(self):
        self.interface = FoodAllergenScannerInterface()
    
    def launch(self, share=False, debug=True):
        """Launch the Gradio interface"""
        return self.interface.launch(share=share, debug=debug)
    
    def close(self):
        """Close the application"""
        if hasattr(self.interface, 'close'):
            self.interface.close()

def main():
    """Main entry point"""
    app = FoodAllergenScannerApp()
    return app.launch()

if __name__ == "__main__":
    main()