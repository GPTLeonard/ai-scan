import sys
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from io import BytesIO
import json
import requests

# Add api folder to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

# Still import pdf_generator because we do that locally
import pdf_generator

app = Flask(__name__)
CORS(app)

# NOTE: For local dev, we now mirror the production logic and call the n8n webhook
N8N_WEBHOOK_URL = "https://n8n.stratuss.cloud/webhook/ai-scanv2"

def parse_n8n_response(response_data):
    """
    Robustly parses n8n response:
    1. Arrays -> take first item
    2. Objects with 'output' string -> parse inner JSON
    """
    if isinstance(response_data, list):
        if len(response_data) == 0:
            return {}
        response_data = response_data[0] # Take first item
    
    # Check if this item is a dict and has 'output' key
    if isinstance(response_data, dict):
        if 'output' in response_data:
            try:
                # The 'output' field contains the actual JSON string we need
                inner_data = json.loads(response_data['output'])
                return inner_data
            except json.JSONDecodeError as e:
                print(f"Failed to parse inner JSON string from n8n: {e}")
                # Try to use it as is if it fails? No, it's a string.
                raise ValueError("Inner JSON string in 'output' is invalid")
        
        # If we are here, it's a dict but has no output key.
        # Maybe it IS the data?
        return response_data
    
    return response_data

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    print("Received request...")
    data = request.json
    
    url = data.get('url')
    company_name = data.get('company_name')

    if not url:
        return jsonify({"error": "Please pass a URL"}), 400

    print(f"Calling n8n Webhook for analysis: {N8N_WEBHOOK_URL}")
    
    # 1. Prepare Payload for n8n
    payload = {
        "url": url,
        "company_name": company_name,
        "industry": data.get('industry', 'Onbekend'),
        "employees": data.get('employees', 'Onbekend'),
        "ai_experience": data.get('ai_experience', 'Onbekend'),
        "chatgpt_policy": data.get('chatgpt_policy', 'Onbekend'),
        "use_case_text": data.get('use_case_text', '') 
    }

    try:
        # 2. Call n8n (long timeout)
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=300)
        response.raise_for_status()
        raw_data = response.json()
        
        # Robust Parsing
        analysis_data = parse_n8n_response(raw_data)
        
        print("Received and parsed analysis from n8n!")
        # Debug: print keys to verify unpacking
        print(f"Data Keys: {list(analysis_data.keys()) if isinstance(analysis_data, dict) else 'Not a dict'}")
        
    except Exception as e:
        print(f"Error calling n8n: {e}")
        return jsonify({"error": str(e)}), 502

    print("Generating PDF...")
    try:
        pdf_bytes = pdf_generator.generate_pdf(analysis_data, company_name or "Organisatie")
    except Exception as e:
        print(f"PDF Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"PDF Gen failed: {e}"}), 500

    return send_file(
        BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'Symbis_Scan_{company_name}.pdf'
    )

if __name__ == '__main__':
    print("Starting local Symbis Server on port 7071...")
    print("MODE: n8n Webhook Integration")
    app.run(port=7071)
