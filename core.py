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
        """Inicializa o motor com monitoramento de hardware e auditoria."""
        self.model_name = model_name
        self.log_file = "auditoria_seguranca.json"
        self.telemetry_file = "telemetria_hardware.json"
        print(f"🤖 PromptOps-Engine Active: {self.model_name}")

    def monitor_resources(self, start_time: float):
        """Módulo de Telemetria: Mede latência, CPU e RAM em tempo real."""
        total_time = (time.time() - start_time) * 1000
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "latency_ms": round(total_time, 2),
            "cpu_percent": psutil.cpu_percent(),
            "ram_percent": psutil.virtual_memory().percent,
            "status": "OPTIMAL" if total_time < 2000 else "DEGRADED"
        }
        
        # Salva métricas para análise de performance (Padrão Dell/Enterprise)
        try:
            with open(self.telemetry_file, "a") as f:
                f.write(json.dumps(metrics) + "\n")
            print(f"📊 Telemetry: {metrics['latency_ms']}ms | RAM: {metrics['ram_percent']}% | CPU: {metrics['cpu_percent']}%")
        except Exception as e:
            print(f"Erro ao salvar telemetria: {e}")

    def extract_pdf(self, path: str) -> str:
        """Módulo RAG: Extração de texto para base de conhecimento local."""
        text = ""
        try:
            if not os.path.exists(path):
                return "Erro: Arquivo não encontrado."
            
            reader = PdfReader(path)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted
            return text
        except Exception as e:
            return f"Error reading PDF: {e}"

    def audit_security(self, prompt: str, risk_score: float):
        """Módulo de Governança: Registra auditoria de segurança."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt_preview": prompt[:50],
            "risk": risk_score,
            "decision": "BLOCKED" if risk_score > 0.5 else "ALLOWED"
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

if __name__ == "__main__":
    # Exemplo de execução profissional
    engine = PromptOpsEngine()
    start = time.time()
    
    # Simulação de tarefa de IA
    print("Executing local governance check...")
    engine.audit_security("Exemplo de prompt confidencial", 0.1)
    
    # Finaliza com telemetria
    engine.monitor_resources(start)
