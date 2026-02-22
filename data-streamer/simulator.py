import time
import random
import requests
from faker import Faker

fake = Faker()


API_URL = "http://localhost:8000/process-transaction" 

# 🛡️ SECURITY TOKEN (JWT)
TOKEN = "test_token_123" 
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def generate_transaction():
    
    is_anomaly = random.random() < 0.1 
    
    
    amount = round(random.uniform(10.0, 500.0), 2)
    location = fake.city()
    
    if is_anomaly:
        
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
            
            response = requests.post(
                API_URL, 
                json=data, 
                headers=HEADERS, 
                timeout=5
            ) 
            
            if response.status_code == 200:
                server_response = response.json()
                
                action = server_response.get('action', 'Processed')
                
                
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
        
        
        time.sleep(random.uniform(0.5, 2.0)) 

if __name__ == "__main__":
    try:
        start_streaming()
    except KeyboardInterrupt:
        print("\n🛑 Simulator நிறுத்தப்பட்டது.")