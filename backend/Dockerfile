FROM python:3.9-slim

WORKDIR /app

# Dependencies இன்ஸ்டால் செய்தல்
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# கோப்புகளை காப்பி செய்தல்
COPY . .

# FastAPI ரன் செய்தல்
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]