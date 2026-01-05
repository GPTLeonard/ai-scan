import sys
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
import json

# Add api folder to path to import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

# Load local settings manually FIRST
try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(base_dir, 'api', 'local.settings.json')
    sys.stderr.write(f"DEBUG: Attempting to load settings from: {settings_path}\n")
    
    if os.path.exists(settings_path):
        with open(settings_path, 'r') as f:
            settings = json.load(f)
            values = settings.get('Values', {})
            sys.stderr.write(f"DEBUG: Found {len(values)} settings keys: {list(values.keys())}\n")
            for key, value in values.items():
                os.environ[key] = value
        sys.stderr.write("DEBUG: Successfully loaded settings into os.environ\n")
    else:
        sys.stderr.write(f"DEBUG: Settings file NOT FOUND at {settings_path}\n")
except Exception as e:
    sys.stderr.write(f"DEBUG: Error loading settings: {e}\n")

import scraper
import ai_analyzer
import pdf_generator

app = Flask(__name__)
CORS(app)  # Enable CORS for local dev

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    print("Received request...")
    data = request.json
    
    url = data.get('url')
    company_name = data.get('company_name')

    if not url:
        return jsonify({"error": "Please pass a URL"}), 400

    print(f"Scraping {url}...")
    site_text = scraper.scrape_website(url)

    print("Analyzing with AI...")
    company_info = {
        "company_name": company_name,
        "industry": data.get('industry', 'Onbekend'),
        "employees": data.get('employees', 'Onbekend'),
        "ai_experience": data.get('ai_experience', 'Onbekend'),
        "chatgpt_policy": data.get('chatgpt_policy', 'Onbekend')
    }
    
    analysis_data = ai_analyzer.get_ai_analysis(company_info, site_text)

    print("Generating PDF...")
    pdf_bytes = pdf_generator.generate_pdf(analysis_data, company_name or "Organisatie")

    return send_file(
        BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'Symbis_Scan_{company_name}.pdf'
    )

if __name__ == '__main__':
    print("Starting local Symbis Server on port 7071...")
    app.run(port=7071)
