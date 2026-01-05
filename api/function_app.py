import azure.functions as func
import logging
import json
import requests
import pdf_generator
import os

app = func.FunctionApp()

# Webhook URL for n8n AI Analysis
# Using the production URL provided by the user
N8N_WEBHOOK_URL = "https://n8n.stratuss.cloud/webhook/ai-scanv2"

def parse_n8n_response(response_data):
    """
    Robustly parses n8n response which might be:
    1. A direct JSON object (dict).
    2. A list containing an object with an 'output' key (which is a JSON string).
    """
    if isinstance(response_data, list) and len(response_data) > 0:
        # Check if it's the specific n8n array format
        item = response_data[0]
        if isinstance(item, dict) and 'output' in item:
            try:
                # The 'output' field contains the actual JSON string we need
                return json.loads(item['output'])
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse inner JSON string from n8n: {e}")
                raise ValueError("Inner JSON string in n8n response is invalid")
        else:
            # Maybe it's just a list of results? Return as is if it looks like data
            return item
    
    # If it's already a dict, assume it's the direct data
    return response_data

@app.route(route="generate-report", auth_level=func.AuthLevel.ANONYMOUS)
def generate_report(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing generate-report request.')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON body", status_code=400)

    url = req_body.get('url')
    company_name = req_body.get('company_name')

    if not url:
        return func.HttpResponse("Please pass a URL", status_code=400)

    # Prepare data for n8n Webhook
    payload = {
        "url": url,
        "company_name": company_name,
        "industry": req_body.get('industry', 'Onbekend'),
        "employees": req_body.get('employees', 'Onbekend'),
        "ai_experience": req_body.get('ai_experience', 'Onbekend'),
        "chatgpt_policy": req_body.get('chatgpt_policy', 'Onbekend'),
        "use_case_text": req_body.get('use_case_text', '') # Pass the custom use case
    }
    
    logging.info(f"Sending data to n8n Webhook: {N8N_WEBHOOK_URL}")

    try:
        # Long timeout because the user said it might take a few minutes
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=300) 
        response.raise_for_status() # Raise error for bad status codes
        
        raw_data = response.json()
        
        # Robust Parsing Logic
        analysis_data = parse_n8n_response(raw_data)
        
        logging.info("Received and parsed analysis data from n8n.")
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling n8n webhook: {e}")
        return func.HttpResponse(f"Error processing AI analysis: {str(e)}", status_code=502)
    except (json.JSONDecodeError, ValueError) as e:
        logging.error(f"Invalid JSON response from n8n: {e}. Content: {response.text}")
        return func.HttpResponse("Invalid JSON response from AI service", status_code=502)

    # 3. Generate PDF
    try:
        pdf_bytes = pdf_generator.generate_pdf(analysis_data, company_name or "Organisatie")
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        return func.HttpResponse(f"Error generating PDF: {str(e)}", status_code=500)

    # 4. Return PDF
    return func.HttpResponse(
        pdf_bytes,
        status_code=200,
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="Symbis_Scan_{company_name}.pdf"'
        }
    )
