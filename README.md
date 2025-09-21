# AI Food Allergen Scanner

A comprehensive AI-based food allergen scanner application built with Gradio that helps users identify potential allergens and medication interactions in food products.

## Features

- **User Profile Management**: Store allergy information and current medications
- **Barcode Scanning**: Scan product barcodes to extract ingredient lists
- **Manual Ingredient Input**: Input ingredients for prepared foods
- **Allergy Detection**: Check ingredients against user's allergy profile
- **Medication Interaction Alerts**: Detect potential interactions between food ingredients and medications
- **Health Risk Assessment**: Provide comprehensive health risk alerts
- **Doctor Consultation**: Connect users with healthcare professionals
- **AI Assistant**: Intelligent assistance throughout the application
- **ML-based Training**: Machine learning for product recognition and analysis

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd food-allergen-scanner
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python run_gradio.py
```

2. Open your browser and navigate to the displayed URL (typically http://localhost:7860)

3. Set up your user profile with allergy information and current medications

4. Use the barcode scanner or manual input to analyze food products

## Project Structure

- `src/app/`: Main application files
- `src/models/`: Data models and structures
- `src/services/`: Business logic and external services
- `src/utils/`: Utility functions and helpers
- `src/data/`: Database files and data storage
- `src/ml/`: Machine learning components
- `src/static/`: Static assets (CSS, JS, images)

## Configuration

Update the configuration files in `src/data/` with your specific requirements:
- `allergens_db.json`: Allergen database
- `medications_db.json`: Medication database
- `food_products_db.json`: Food product database
- `doctor_contacts.json`: Healthcare provider contacts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.