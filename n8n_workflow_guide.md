# n8n Workflow Architectuur: Symbis AI Scan (Deep Research)

Dit document beschrijft de stappen voor je n8n workflow om een diepgaande analyse te maken. We splitsen het proces op in **Verzamelen (Deep Research)** en **Analyseren & Adviseren (Symbis Logic)**.

---

## 🏗️ Workflow Overzicht (De Stappen)

1.  **Webhook Trigger (POST)**
    *   Ontvangt: `url`, `company_name`, `use_case_text`, `industry`, `employees`.
2.  **Web Scraper (Jina AI / Browserless)**
    *   **Actie:** Scrape de hoofdpagina van de klant (`url`).
    *   **Actie:** Scrape optioneel de `/over-ons` en `/diensten` pagina's als die gevonden worden.
    *   **Doel:** Begrijp *wat* ze doen, hun *toon*, en hun *klanten*.
3.  **Google Search (SerpApi / Google Custom Search)**
    *   **Query:** `"{company_name}" concurrenten`, `"{company_name}" nieuws`, `"{branche}" trends & uitdagingen 2025`.
    *   **Doel:** Context buiten hun eigen website. Wat speelt er in de markt? Wie zijn ze?
4.  **AI Stap 1: De Diagnose (Diagnostic Agent)**
    *   **Input:** Website tekst + Zoekresultaten.
    *   **System Prompt:** *Zie hieronder (Prompt A).*
    *   **Doel:** Een scherpe analyse van hun huidige situatie, volwassenheid en pijnpunten.
5.  **AI Stap 2: De Oplossing (Symbis Architect Agent)**
    *   **Input:** De Diagnose uit Stap 1 + Symbis Filosofie.
    *   **System Prompt:** *Zie hieronder (Prompt B).*
    *   **Doel:** Het genereren van de JSON output met recommendations, cases en roadmap.
6.  **Response Webhook**
    *   Stuurt de finale JSON terug naar jouw Azure Function / Local Server.

---

## 🧠 System Prompts

### Prompt A: De Diagnose (Stap 4)
*Deze node analyseert de ruwe data en maakt een profiel.*

```text
# Role
Je bent een Senior Business Analyst gespecialiseerd in Digitale Transformatie. Je bereidt een dossier voor Leonard van Hemert (Symbis) voor.

# Task
Analyseer de bijgevoegde website-data en zoekresultaten van de klant.
Maak een scherpe, eerlijke diagnose van hun huidige situatie.

# Input Data
Bedrijfsnaam: {{ $json.company_name }}
Branche: {{ $json.industry }}
Grootte: {{ $json.employees }}
Website Content: {{ $json.website_text }}
Zoekresultaten: {{ $json.search_results }}

# Analysis Framework
1.  **Business Model:** Wat doen ze precies? Verdienmodel?
2.  **Digitale Volwassenheid:** Oogt de site modern? Gebruiken ze al portals/apps?
3.  **Pijnpunten (Hypothese):** Waar verliezen ze waarschijnlijk tijd? (bv. veel handmatige administratie bij een groothandel, veel compliance bij zorg).
4.  **Concurrentie Context:** Wat doen concurrenten beter?

# Output Format
Schrijf een beknopte analyse van 3 alinea's. Focus op feiten en sterke hypotheses. Geen marketingpraat.
```

---

### Prompt B: De Symbis Architect (Stap 5)
*Deze node vertaalt de diagnose naar Symbis-oplossingen en genereert de JSON.*

```text
# Role
Je bent de digitale AI-consultant van Leonard van Hemert bij Symbis. Je fungeert als zijn expert second brain.

# Context (Diagnose uit vorige stap)
{{ $json.diagnostic_analysis }}

# Specifieke Wens Klant
{{ $json.use_case_text }}

# Symbis Philosophy (CRUCIAAL)
1.  **Microsoft First:** Wij gebruiken Azure OpenAI (geen training op data).
2.  **Automatisering = Power Platform:** Voor standaard flows.
3.  **Complex & Privacy = n8n (Azure VM):** Voor AI-agents en complexe logica, lokaal gehost.
4.  **Chatbot = SymGPT:** Voor veilige, eigen ChatGPT variant.
5.  **Privacy Check:** Bij strenge regels (Zorg/Juridisch) -> Altijd SymGPT of n8n lokaal.

# Decision Rules
-   **Klein bedrijf (<10):** Quick wins met Copilot & Standaard Power Automate.
-   **Groot bedrijf (>50):** Governance, SymGPT, n8n orchestratie.
-   **Zorg:** Focus op Compliance/EPD -> Case 4.
-   **Handel:** Focus op Offertes/Email -> Case 1 of 5.

# Task
Genereer het JSON adviesrapport.

# Output Contract (JSON ONLY)
{
  "bedrijfs_analyse": {
    "samenvatting": "Korte, scherpe samenvatting van de diagnose.",
    "herkende_pijnpunten": ["Punt 1", "Punt 2"]
  },
  "symbis_score": {
    "huidige_fase": "Kies: 1. Startpunt / 2. Procesautomatisering / 3. AI in de flow",
    "score_toelichting": "Onderbouwing op basis van diagnose."
  },
  "relevant_case": {
    "titel": "Kies uit Case Library (zie instructies)",
    "beschrijving": "Wat doen we daar?",
    "waarom_relevant": "Waarom past dit bij DEZE klant?"
  },
  "advies_secties": [
    {
      "titel": "Titel Advies 1",
      "tool": "Kies: Microsoft Copilot / Power Automate / n8n (Azure) / SymGPT",
      "beschrijving": "Concreet advies.",
      "impact": "Verwachte winst."
    },
    {
       "titel": "Titel Advies 2",
       "tool": "...",
       "beschrijving": "...",
       "impact": "..."
    }
  ],
  "roadmap": {
    "vandaag": "Stap 1",
    "deze_week": "Stap 2",
    "deze_maand": "Stap 3"
  }
}
```

---

## 🚀 Implementatie Tips in n8n

1.  **JSON Mode:** Zorg dat je laatste AI-node (De Architect) in n8n ingesteld staat op **"JSON Output"** mode.
2.  **Error Handling:** Zet een `Error Trigger` node in n8n. Als de analyse faalt, stuur dan een "Fallback JSON" (de mock data) terug, zodat de PDF generator niet crasht.
3.  **HTTP Response:** Eindig je flow met een `Respond to Webhook` node die de JSON van de Architect Node teruggeeft.
