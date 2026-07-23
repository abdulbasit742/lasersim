FROM python:3.12-slim

WORKDIR /workspace

COPY requirements-kmode.txt .
RUN pip install --no-cache-dir -r requirements-kmode.txt

COPY . .

CMD ["python", "training/kmode/cli.py", "--help"]
