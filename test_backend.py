import requests
import json
import base64

# MOCK payload
payload = {
    "url": "https://www.symbis.nl",  # Example validation
    "company_name": "Symbis Test",
    "industry": "Zakelijke dienstverlening",
    "employees": "11-50",
    "ai_experience": "4",
    "chatgpt_policy": "Nee"
}

def test_local_function():
    # Note: This requires the function to be running physically via 'func start'
    # Since we can't easily start the background process and keep it running for this script in one go without 'func' tool support in this environment,
    # We will simulate the function call by importing the app object and calling the function directly if possible,
    # OR we just rely on unit-test style call.
    
    print("Testing internal logic (Unit Test style)...")
    try:
        import api.function_app as app
        import azure.functions as func
        
        # Mock Request
        req = func.HttpRequest(
            method='POST',
            body=json.dumps(payload).encode('utf-8'),
            url='/api/generate-report',
            params={}
        )
        
        # Invoke function
        print("Invoking generate_report...")
        resp = app.generate_report(req)
        
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            print("Success! PDF generated.")
            # Verify body is PDF
            if resp.get_body()[:4] == b'%PDF':
                print("Header is %PDF. Output valid.")
                # Save to file
                with open("test_output.pdf", "wb") as f:
                    f.write(resp.get_body())
                print("Saved to test_output.pdf")
            else:
                print(f"Output does not look like PDF: {resp.get_body()[:20]}")
        else:
            print(f"Error: {resp.get_body()}")

    except Exception as e:
        print(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_local_function()
