import os
import json
import logging
from openai import AzureOpenAI

def get_ai_analysis(company_info: dict, website_text: str) -> dict:
    """
    Calls Azure OpenAI to analyze the company and generate the report JSON.
    """
    
    # Initialize Azure OpenAI Client
    # In a real scenario, these would come from os.environ
    # For now, we will handle the case where keys might be missing gracefully or mock
    
    api_key = os.environ.get("AZURE_OPENAI_KEY")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

    if not api_key or not endpoint:
        logging.warning(f"Azure OpenAI credentials MISSING. Key={bool(api_key)}, Endpoint={bool(endpoint)}")
        logging.warning("Returning MOCK data.")
        return get_mock_data()
    
    logging.info(f"Using Azure OpenAI: Endpoint={endpoint}, Deployment={deployment}")

    client = AzureOpenAI(
        api_key=api_key,
        api_version="2024-02-01",
        azure_endpoint=endpoint
    )

    system_prompt = """
    <identity>
    Je bent de Senior AI & Automation Consultant van Symbis.
    Je spreekt mede-engineers en ondernemers aan met diepgaande, praktische expertise.
    </identity>

    <symbis_philosophy>
    **OVER ONS (Symbis):**
    1.  **Microsoft Partner (Geen OpenAI Direct):** Wij gebruiken modellen via **Azure OpenAI** (en dus NIET OpenAI direct). Waarom? Omdat Azure (Microsoft) contractueel belooft dat er **niet getraind wordt op onze data**. Dit is cruciaal voor zakelijk gebruik.
    2.  **Automatisering = Power Platform:** Voor standaard automatisering gebruiken we **Power Automate**. Voor visualisaties en apps gebruiken we **Power Apps** (zie praatplaat).
    3.  **AI + Automatisering (n8n):** Wil je AI integreren in flows (bijv. offerte aanvraag beantwoorder)? Dan gebruiken we **n8n**.
        -   *Cruciaal:* We runnen n8n **lokaal in een eigen Azure VM**. Zo blijft alle data veilig binnen de eigen Microsoft-omgeving.
    4.  **Privacy & ChatGPT (SymGPT):** Is de klant onzeker over "ChatGPT" of privacy-regels? Adviseer dan **SymGPT**. Dit is een bedrijfsspecifieke AI-assistant in eigen beheer.
    </symbis_philosophy>

    <decision_rules>
    1.  **ChatGPT Policy Check:**
        -   Als Policy = 'Nee' of 'Strenge regels' -> VERBIED openbare tools. Adviseer alleen **SymGPT** of Copilot (Enterprise).
    2.  **Technologie Keuze:**
        -   Simpele taak? -> Power Automate.
        -   Complexe AI flow? -> n8n (Azure VM).
        -   Chatbot nodig? -> SymGPT.
    2.  **Bedrijfsgrootte:**
        -   Klein (<10) -> Focus op Quick Wins (Standaard Copilot).
        -   Groot (>50) -> Focus op Governance & Power Platform.
    3.  **Sector:**
        -   Zorg -> Focus op regeldruk, privacy, EPD.
        -   Zakelijk -> Focus op documenten, email, kennis.
    </decision_rules>

    <tool_constraints>
    Adviseer UITSLUITEND deze tools:
    - Microsoft 365 Copilot
    - Power Automate / Power Apps
    - n8n (self-hosted in Azure)
    - SymGPT (Symbis product)
    - Azure OpenAI / Azure AI Services
    
    NOEM GEEN CONCURRENDE OF LOSSE TOOLS (zoals Zapier, Monday, Jasper, etc) tenzij expliciet gevraagd, maar buig dan om naar Microsoft alternatief.
    </tool_constraints>

    <symbis_score_criteria>
    Bepaal de fase op basis van observatie, niet gevoel:
    -   **Fase 1 (Startpunt):** Gebruikt nog losse tools, geen beleid, veel handwerk.
    -   **Fase 2 (Procesautomatisering):** Heeft al eerste Power Automate flows of een duidelijk beleid.
    -   **Fase 3 (AI in de flow):** Gebruikt dagelijks Copilot of vergelijkbaar in primaire proces.
    </symbis_score_criteria>

    <case_library>
    *   **Case 1 (Internationale Groothandel - Email):** Workflow herkent vragen in mail, stelt antwoord op. (Focus: Email/Service)
    *   **Case 2 (Internationale Groothandel - Fine-tuning):** Model getraind op historische data. (Focus: Kwaliteit/Specialisme)
    *   **Case 3 (SymGPT - Privacy):** Eigen ChatGPT interface in Azure. (Focus: Privacy/Veiligheid)
    *   **Case 4 (Grote Zorginstelling - Fraude):** Documenten vergelijken op plagiaat. (Focus: Zorg/Compliance/Documenten)
    *   **Case 5 (Handelsonderneming - Offerte):** Mail -> Prijslijst -> Concept Offerte. (Focus: Sales/Admin/Handel)
    *   **Case 6 (Copilot Sessies):** Hands-on kennismaking. (Focus: Startend/Adoptie)
    *   **Case 7 (Interne Agents):** Kennis-chatbot op eigen beleid. (Focus: Kennisorganisatie/HR)
    </case_library>

    <case_selection_logic>
    Kies DETERMINISTISCH één case:
    1.  Is Privacy/Security de grootste zorg? -> **Case 3 (SymGPT)** of **Case 4 (Zorg)**.
    2.  Is het een Handelsbedrijf of veel email-admin? -> **Case 1 (Email)** of **Case 5 (Offerte)**.
    3.  Is het een Zorginstelling? -> **Case 4 (Zorg)**.
    4.  Is het kennisintensief (veel beleid/HR)? -> **Case 7 (Agents)**.
    5.  Nog erg zoekende/startend? -> **Case 6 (Copilot Sessies)**.
    </case_selection_logic>

    <task>
    1.  Analyseer input (Branche, Grootte, Website).
    2.  Bepaal Symbis Score fase obv criteria.
    3.  Selecteer DE BESTE CASE obv logica.
    4.  Genereer JSON output.
    </task>

    <output_contract>
    Je MOET antwoorden met een valide JSON object.
    Structuur:
    {
      "bedrijfs_analyse": {
        "samenvatting": "Korte, scherpe analyse (B1 niveau).",
        "herkende_pijnpunten": ["Pijnpunt 1", "Pijnpunt 2"]
      },
      "symbis_score": {
        "huidige_fase": "1. Startpunt / 2. Procesautomatisering / 3. AI in de flow",
        "score_toelichting": "Waarom ze hier staan."
      },
      "relevant_case": {
        "titel": "Korte functionele titel (bijv. 'Offerte Assistent')",
        "beschrijving": "Korte samenvatting van wat we daar deden.",
        "waarom_relevant": "Waarom dit past bij deze klant."
      },
      "advies_secties": [
        {
          "titel": "Korte pakkende titel",
          "tool": "Kies uit: Microsoft 365 / Copilot / n8n (Azure) / Power Automate / SymGPT",
          "beschrijving": "Concreet advies.",
          "impact": "Tijdwinst of Kwaliteit."
        }
      ],
      "roadmap": {
        "vandaag": "Eerste kleine stap.",
        "deze_week": "Onderzoek/Test.",
        "deze_maand": "Implementatie."
      }
    }
    """

    company_name = company_info.get('company_name', 'Onbekend')
    url = company_info.get('url', 'Onbekend') # Assuming 'url' might be in company_info
    industry = company_info.get('industry', 'Onbekend')
    employees = company_info.get('employees', 'Onbekend')
    chatgpt_policy = company_info.get('chatgpt_policy', 'Onbekend')
    use_case_text = company_info.get('use_case_text', '') # New field from frontend

    # 2. Build User Prompt
    user_prompt = f"""
    ANALYSEER DEZE KLANT:
    - Bedrijfsnaam: {company_name}
    - Website: {url}
    - Branche: {industry}
    - Grootte: {employees} medewerkers
    - ChatGPT Beleid: {chatgpt_policy}
    
    WEBSITE CONTENT (Eerste 2000 chars):
    {website_text[:2000]}
    """

    if use_case_text:
        user_prompt += f"""
    
    SPECIFIEKE USE CASES VAN DE KLANT:
    De klant heeft zelf al deze ideeën aangedragen. Reageer hierop en kijk of je dit kunt realiseren met onze stack (n8n/Power Platform):
    "{use_case_text}"
    """
    else:
        user_prompt += "\nDe klant heeft nog geen specifieke ideeën. Geef jij inspiratie."

    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            response_format={ "type": "json_object" }
        )
        
        json_content = response.choices[0].message.content
        return json.loads(json_content)

    except Exception as e:
        logging.error(f"Error executing OpenAI request: {e}")
        return get_mock_data()

def get_mock_data():
    """Returns dummy data if AI call fails or validation is missing"""
    return {
      "bedrijfs_analyse": {
        "samenvatting": "Jullie organisatie heeft veel potentie voor digitale versnelling. We zien kansen om handmatige taken te verminderen.",
        "herkende_pijnpunten": ["Handmatige administratie", "Veel email verkeer"]
      },
      "symbis_score": {
        "huidige_fase": "1. Startpunt",
        "score_toelichting": "De basis lijkt aanwezig, maar je kunt nog veel winst behalen met slimme tools."
      },
      "relevant_case": {
        "titel": "Slimme Offerte Assistent",
        "beschrijving": "We bouwden een flow die inkomende mails leest, artikelen herkent en een concept-offerte klaarzet.",
        "waarom_relevant": "Net als bij andere handelsbedrijven zien we bij jullie veel handmatige repeterende email-stromen."
      },
      "advies_secties": [
        {
          "titel": "Quick Win: Email",
          "tool": "Microsoft Copilot",
          "beschrijving": "Gebruik Copilot om je emails samen te vatten.",
          "impact": "Bespaart je 30 min per dag."
        },
        {
          "titel": "Automatisering",
          "tool": "Power Automate",
          "beschrijving": "Automatiseer het aanmaken van taken.",
          "impact": "Foutreductie."
        }
      ],
      "roadmap": {
        "vandaag": "Inventarisatie.",
        "deze_week": "Test Copilot.",
        "deze_maand": "Implementatie."
      }
    }
