import json
import logging

import azure.functions as func
import requests

# Webhook URL for n8n AI Analysis
# Using the production URL provided by the user
N8N_WEBHOOK_URL = "https://n8n.stratuss.cloud/webhook/ai-scanv2"


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing generate-report request.")

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON body", status_code=400)

    required_fields = ["company_name", "url", "email", "name"]
    missing_fields = [field for field in required_fields if not req_body.get(field)]
    if missing_fields:
        return func.HttpResponse(
            f"Missing required fields: {', '.join(missing_fields)}",
            status_code=400,
        )

    # Forward the full form payload to n8n without filtering.
    payload = dict(req_body)

    logging.info(f"Sending data to n8n Webhook: {N8N_WEBHOOK_URL}")

    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        logging.info("n8n webhook accepted the request.")
    except requests.exceptions.ReadTimeout:
        logging.warning("n8n webhook timed out after 10 seconds; returning accepted.")
    except requests.exceptions.RequestException as exc:
        logging.error(f"Error calling n8n webhook: {exc}")
        return func.HttpResponse(
            f"Error processing request: {exc}", status_code=502
        )

    response_body = {
        "message": "Bedankt! Je rapport wordt binnen enkele minuten naar je mail gestuurd.",
        "company_name": req_body.get("company_name"),
        "email": req_body.get("email"),
    }
    return func.HttpResponse(
        json.dumps(response_body),
        status_code=202,
        mimetype="application/json",
    )
