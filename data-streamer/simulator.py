import time
import random
import requests
from faker import Faker

fake = Faker()

# நமது Backend இயங்கும் URL
API_URL = "http://localhost:8000/process-transaction" 

# 🛡️ SECURITY TOKEN (JWT)
TOKEN = "test_token_123" 
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def generate_transaction():
    # 10% வாய்ப்பு மோசடிக்கு (Fraud/Anomaly)
    is_anomaly = random.random() < 0.1 
    
    # இயல்பான தொகை ($10 - $500)
    amount = round(random.uniform(10.0, 500.0), 2)
    location = fake.city()
    
    if is_anomaly:
        # 🔥 அனாமலி சிமுலேஷன்: மிக அதிகப்படியான தொகை (Spike உருவாவதற்கு)
        # $15,000 முதல் $25,000 வரை ஒரு பெரிய ஸ்பைக் உருவாக்கும்
        amount = round(random.uniform(15000.0, 25000.0), 2) 
        location = "Suspicious International IP"

    transaction = {
        "transaction_id": fake.uuid4(),
        "user_id": str(random.randint(1001, 1050)), 
        "amount": amount,
        "location": location,
        "device_id": f"DEV-{random.randint(100, 999)}",
        "merchant_type": random.choice(["Retail", "Online", "ATM", "Transfer"]),
        "timestamp": fake.iso8601()
    }
    return transaction

def start_streaming():
    print("🚀 FraudShield Transaction Simulator Started...")
    print(f"📡 API Endpoint: {API_URL}")
    print(f"🔐 Security: JWT Bearer Token Enabled")
    print("-" * 60)

    while True:
        data = generate_transaction()
        try:
            # --- Backend-க்கு டேட்டாவை அனுப்புதல் ---
            response = requests.post(
                API_URL, 
                json=data, 
                headers=HEADERS, 
                timeout=5
            ) 
            
            if response.status_code == 200:
                server_response = response.json()
                # Backend-ல் இருந்து வரும் action (Approve/Flag) ஐப் பெறுகிறோம்
                # குறிப்பு: உங்கள் backend return செய்யும் தரவைப் பொறுத்து இது அமையும்
                action = server_response.get('action', 'Processed')
                
                # அனாமலி என்றால் கொஞ்சம் வித்தியாசமான பிரிண்ட் ஸ்டேட்மெண்ட்
                prefix = "🚨 ALERT:" if data['amount'] > 10000 else "✅ Sent:"
                print(f"{prefix} {data['transaction_id'][:8]}... | Amount: ${data['amount']:>10} | Action: {action}")
            
            elif response.status_code == 401:
                print("❌ Auth Error: Invalid Token!")
            
            else:
                print(f"⚠️ Warning: Server returned {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Backend server (FastAPI) ஓடவில்லை!")
            time.sleep(5)
            continue
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
        
        # எதார்த்தமான இடைவெளி (0.5s to 2s)
        time.sleep(random.uniform(0.5, 2.0)) 

if __name__ == "__main__":
    try:
        start_streaming()
    except KeyboardInterrupt:
        print("\n🛑 Simulator நிறுத்தப்பட்டது.")