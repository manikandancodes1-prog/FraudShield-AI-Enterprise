from sklearn.ensemble import IsolationForest
import numpy as np

class FraudDetector:
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        # Dummy training data
        X_train = np.random.rand(100, 2)
        self.model.fit(X_train)

    def predict_anomaly_score(self, amount, user_risk_history):
        data = np.array([[amount, user_risk_history]])
        score = self.model.decision_function(data)
        # Score normalization
        normalized_score = score[0] + 0.5
        return float(1 - normalized_score)

def calculate_final_risk(amount, location, merchant_type, ml_score=0.4):
    rule_score = 0
    reasons = []

    # 1. Amount Logic
    if amount > 5000:
        rule_score += 0.7
        reasons.append("High Amount (>5000)")
    
    # 2. Location Logic
    if location == "Foreign" or location == "Unknown City":
        rule_score += 0.3
        reasons.append("Unusual Location")
    
    # 3. Merchant Logic
    if merchant_type == "Crypto" or merchant_type == "Gambling":
        rule_score += 0.5
        reasons.append("High-Risk Merchant")

    if ml_score > 0.7:
        reasons.append("AI Pattern Anomaly")

    if not reasons:
        reasons.append("Safe Pattern")

    # Final calculation
    final_score = (ml_score * 0.4) + (min(rule_score, 1.0) * 0.6)
    
    status = "Approved"
    if final_score > 0.8: 
        status = "Blocked"
    elif final_score > 0.5: 
        status = "Flagged"

    return round(final_score * 100, 2), status, " | ".join(reasons)