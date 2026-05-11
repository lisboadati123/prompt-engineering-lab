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
        print(f"🤖 PromptOps-Engine Ativa: {self.model_name}")

    def monitorar_recursos(self, inicio: float):
        """Módulo Sênior: Monitoramento de Performance e Hardware"""
        tempo_total = (time.time() - inicio) * 1000
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "latencia_ms": round(tempo_total, 2),
            "cpu_percent": psutil.cpu_percent(),
            "ram_percent": psutil.virtual_memory().percent,
            "status": "OPTIMAL" if tempo_total < 2000 else "DEGRADED"
        }
        with open(self.telemetry_file, "a") as f:
            f.write(json.dumps(metrics) + "\n")
        print(f"📊 Telemetria: {metrics['latencia_ms']}ms | RAM: {metrics['ram_percent']}%")

    def extrair_pdf(self, path: str) -> str:
        """Módulo RAG: Extrai texto de PDFs para consulta."""
        texto = ""
        try:
            with open(path, "rb") as f:
                pdf = PdfReader(f)
                for page in pdf.pages:
                    texto += page.extract_text()
            return texto
        except Exception as e:
            return f"Erro ao ler PDF: {e}"

# Exemplo de uso para o seu portfólio
if __name__ == "__main__":
    engine = PromptOpsEngine()
    start_time = time.time()
    
    # Simulação de processamento
    print("Processando governança local...")
    time.sleep(1) 
    
    engine.monitorar_recursos(start_time)
