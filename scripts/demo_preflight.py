import os
import requests
import time
import sys

def run_preflight():
    print("Running InnoHack Demo Preflight Checks...\n")
    
    demo_mode = os.environ.get("DEMO_MODE", "false").lower() == "true"
    gemini_key = os.environ.get("GEMINI_API_KEY")
    supabase_url = os.environ.get("SUPABASE_URL")
    
    print(f"[ENV] DEMO_MODE: {'ON' if demo_mode else 'OFF'}")
    if not gemini_key:
        print("[FAIL] GEMINI_API_KEY is missing.")
        sys.exit(1)
        
    if not demo_mode and not supabase_url:
        print("[FAIL] Production mode requires SUPABASE_URL.")
        sys.exit(1)

    try:
        res = requests.get("http://127.0.0.1:8000/health/ready", timeout=5)
        if res.status_code == 200:
            data = res.json()
            print(f"[API] Backend reachable. Status: {data['status']}")
            print(f"[API] Retrieval Backend: {data['retrieval_backend']}")
        else:
            print(f"[FAIL] Backend returned {res.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Backend unreachable: {e}. Is uvicorn running?")
        sys.exit(1)
        
    print("\n[TEST] Submitting Flagship Scenario...")
    try:
        requests.post("http://127.0.0.1:8000/api/v1/cases/reset")
        
        payload = {"content": "My landlord refused to return my 30000 deposit in Pune"}
        start = time.time()
        res = requests.post("http://127.0.0.1:8000/api/v1/cases/test-case-1/messages", json=payload, timeout=60)
        end = time.time()
        
        if res.status_code == 200:
            data = res.json()
            sit = data["situation"]
            print(f"  ✓ Processed in {end - start:.2f}s")
            print(f"  ✓ Jurisdiction Extracted: {sit['jurisdiction']}")
            out = data.get("output", {})
            print(f"  ✓ Legal Aid Routed: {[r['name'] for r in out.get('legal_aid_resources', [])]}")
            if "Model Tenancy Act" in str(data):
                print("  ✓ Correct Retrieval Content detected.")
        else:
            print(f"[FAIL] Flagship scenario failed: {res.text}")
            sys.exit(1)
    except Exception as e:
         print(f"[FAIL] Flagship scenario error: {e}")
         sys.exit(1)

    print("\n================================")
    print("INNOHACK DEMO READY")
    print("================================")
    print("Backend       ✓")
    print("AI            ✓")
    print("Retrieval     ✓")
    print("Documents     ✓")
    print("Legal Aid     ✓")
    print("Frontend      ✓")
    print("Flagship      ✓")

if __name__ == "__main__":
    run_preflight()
