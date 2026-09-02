FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Regenerate synthetic datasets (deterministic, seeded) and train ML models at build time.
RUN python data/scripts/generate_synthetic_datasets.py && python app/ml/train_models.py

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
