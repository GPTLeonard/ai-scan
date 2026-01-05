import json
import logging

import azure.functions as func
import requests

import pdf_generator

# Webhook URL for n8n AI Analysis
# Using the production URL provided by the user
N8N_WEBHOOK_URL = "https://n8n.stratuss.cloud/webhook/ai-scanv2"


def parse_n8n_response(response_data):
    """
    Robustly parses n8n response:
    1. Arrays -> take first item
    2. Objects with 'output' string -> parse inner JSON
    3. Handles potential double nesting
    """
    if isinstance(response_data, list):
        if len(response_data) == 0:
            return {}
        response_data = response_data[0]  # Take first item

    # Check if this item is a dict and has 'output' key
    if isinstance(response_data, dict):
        if "output" in response_data:
            try:
                # The 'output' field contains the actual JSON string we need
                inner_data = json.loads(response_data["output"])
                return inner_data
            except json.JSONDecodeError as exc:
                logging.error(f"Failed to parse inner JSON string from n8n: {exc}")
                raise ValueError("Inner JSON string in 'output' is invalid")

        # If no 'output' key, assuming the dict itself IS the data
        return response_data

    return response_data


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing generate-report request.")

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON body", status_code=400)

    url = req_body.get("url")
    company_name = req_body.get("company_name")

    if not url:
        return func.HttpResponse("Please pass a URL", status_code=400)

    # Prepare data for n8n Webhook
    payload = {
        "url": url,
        "company_name": company_name,
        "industry": req_body.get("industry", "Onbekend"),
        "employees": req_body.get("employees", "Onbekend"),
        "ai_experience": req_body.get("ai_experience", "Onbekend"),
        "chatgpt_policy": req_body.get("chatgpt_policy", "Onbekend"),
        "use_case_text": req_body.get("use_case_text", ""),
    }

    logging.info(f"Sending data to n8n Webhook: {N8N_WEBHOOK_URL}")

    try:
        # Long timeout because the user said it might take a few minutes
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=300)
        response.raise_for_status()

        raw_data = response.json()
        analysis_data = parse_n8n_response(raw_data)

        logging.info("Received and parsed analysis data from n8n.")
    except requests.exceptions.RequestException as exc:
        logging.error(f"Error calling n8n webhook: {exc}")
        return func.HttpResponse(f"Error processing AI analysis: {exc}", status_code=502)
    except (json.JSONDecodeError, ValueError) as exc:
        logging.error(f"Invalid JSON response from n8n: {exc}. Content: {response.text}")
        return func.HttpResponse("Invalid JSON response from AI service", status_code=502)

    # Generate PDF
    try:
        pdf_bytes = pdf_generator.generate_pdf(
            analysis_data, company_name or "Organisatie"
        )
    except Exception as exc:
        logging.error("Error generating PDF.", exc_info=exc)
        return func.HttpResponse(f"Error generating PDF: {exc}", status_code=500)

    # Return PDF
    return func.HttpResponse(
        pdf_bytes,
        status_code=200,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="Symbis_Scan_{company_name}.pdf"'
        },
    )
