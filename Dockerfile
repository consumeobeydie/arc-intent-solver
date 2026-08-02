FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY agent/solver.py .
COPY .env .
CMD ["python3", "-u", "solver.py"]
