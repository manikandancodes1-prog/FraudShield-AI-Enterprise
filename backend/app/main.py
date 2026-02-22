from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm 
from sqlalchemy.orm import Session
from typing import List
import json
import asyncio

# --- 1. Security & Auth Imports ---
from .core.security import create_access_token, verify_token 
from passlib.context import CryptContext 

# --- 2. Database & Models Imports ---
from .core.database import engine, get_db, SessionLocal
from .models import transaction as transaction_models
from .models.user import User # 👈 திருத்தம் 1: User-ஐ நேரடியாக இம்போர்ட் செய்துள்ளேன்
from .models import user as user_models

from .services.fraud_detector import FraudDetector, calculate_final_risk
from .schemas.transaction_schema import TransactionCreate

# பாஸ்வேர்டு சரிபார்க்கும் மெக்கானிசம்
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# 🔒 பாதுகாப்பு டோக்கனைப் பெறுவதற்கான வழிமுறை
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Database tables உருவாக்கம்
transaction_models.Base.metadata.create_all(bind=engine)
user_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FraudShield AI Engine")

# --- 3. CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 👈 திருத்தம் 2: டெஸ்டிங்கிற்காக அனைத்து ஆர்ஜின்களையும் அனுமதிப்போம்
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = FraudDetector()

# --- 4. Connection Manager (WebSocket) ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# --- 5. Auth Endpoint (Login) ---
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # 👈 திருத்தம் 3: இண்டென்டேஷன் மற்றும் பிளைன் டெக்ஸ்ட் செக்
    if not user or form_data.password != user.hashed_password:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # 3. செக்யூரிட்டி டோக்கன் உருவாக்குதல்
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role,
        "full_name": user.full_name
    }

# --- 6. Helper Function ---
def format_transaction(transaction):
    if not transaction:
        return None
    return {
        "transaction_id": transaction.transaction_id,
        "amount": transaction.amount,
        "risk_score": float(transaction.risk_score),
        "status": transaction.status,
        "location": transaction.location,
        "reasons": transaction.reasons 
    }

# --- 7. WebSocket Endpoint ---
@app.websocket("/ws/transactions")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    db = SessionLocal()
    try:
        latest = db.query(transaction_models.Transaction).order_by(transaction_models.Transaction.id.desc()).first()
        if latest:
            await websocket.send_json(format_transaction(latest))
    finally:
        db.close()

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- 8. Process Transaction API (🔒 PROTECTED) ---
@app.post("/process-transaction")
async def process_transaction(
    data: TransactionCreate, 
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme) # 👈 இங்கிருந்து பாதுகாப்பு ஆரம்பமாகிறது
):
    # ML Score கணித்தல்
    ml_score = float(detector.predict_anomaly_score(data.amount, 0.5))

    # Risk & Status கணக்கிடுதல்
    final_risk, status, reasons = calculate_final_risk(
        data.amount, 
        data.location, 
        data.merchant_type,
        ml_score=ml_score  
    )

    new_transaction = transaction_models.Transaction(
        transaction_id=data.transaction_id,
        user_id=data.user_id,
        amount=data.amount,
        location=data.location,
        device_id=data.device_id,
        merchant_type=data.merchant_type,
        risk_score=float(final_risk),
        fraud_probability=ml_score,
        status=status,
        reasons=reasons 
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    # Instant Broadcast
    broadcast_data = format_transaction(new_transaction)
    await manager.broadcast(broadcast_data)

    return new_transaction