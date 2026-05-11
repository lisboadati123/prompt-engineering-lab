import json
import os
import time
import psutil
import logging
from datetime import datetime
from PyPDF2 import PdfReader
from typing import Dict, Any

class PromptOpsEngine:
    def __init__(self, model_name: str = "Qwen/Qwen2.5-0.5B-Instruct"):
        self.model_name = model_name
        self.log_file = "auditoria_seguranca.json"
        self.telemetry_file = "telemetria_hardware.json"
        print(f"🤖 PromptOps-Engine Active: {self.model_name}")

    def monitor_resources(self, start_time: float):
        """Senior Module: Hardware & Performance Monitoring"""
        total_time = (time.time() - start_time) * 1000
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "latency_ms": round(total_time, 2),
            "cpu_percent": psutil.cpu_percent(),
            "ram_percent": psutil.virtual_memory().percent,
            "status": "OPTIMAL" if total_time < 2000 else "DEGRADED"
        }
        with open(self.telemetry_file, "a") as f:
            f.write(json.dumps(metrics) + "\n")
        print(f"📊 Telemetry: {metrics['latency_ms']}ms | RAM: {metrics['ram_percent']}%")

    def extract_pdf(self, path: str) -> str:
        """RAG Module: Extract text from PDFs."""
        text = ""
        try:
            reader = PdfReader(path)
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            return f"Error reading PDF: {e}"

if __name__ == "__main__":
    engine = PromptOpsEngine()
    start = time.time()
    # Simulating work
    engine.monitor_resources(start)
