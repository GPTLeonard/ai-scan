import azure.functions as func
import logging
import json

app = func.FunctionApp()

import azure.functions as func
import logging
import json
import scraper
import ai_analyzer
import pdf_generator

app = func.FunctionApp()

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

    # 1. Scrape Website
    site_text = scraper.scrape_website(url)

    # 2. AI Analysis
    company_info = {
        "company_name": company_name,
        "industry": req_body.get('industry', 'Onbekend'),
        "employees": req_body.get('employees', 'Onbekend'),
        "ai_experience": req_body.get('ai_experience', 'Onbekend'),
        "chatgpt_policy": req_body.get('chatgpt_policy', 'Onbekend')
    }
    
    analysis_data = ai_analyzer.get_ai_analysis(company_info, site_text)

    # 3. Generate PDF
    pdf_bytes = pdf_generator.generate_pdf(analysis_data, company_name or "Organisatie")

    # 4. Return PDF
    return func.HttpResponse(
        pdf_bytes,
        status_code=200,
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="Symbis_Scan_{company_name}.pdf"'
        }
    )
