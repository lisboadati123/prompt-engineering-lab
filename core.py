import json
import os
import PyPDF2
from datetime import datetime
from typing import Dict, Any

class PromptOpsEngine:
    def __init__(self, model: str = "Qwen/Qwen2.5-0.5B-Instruct"):
        self.model_name = model
        self.log_file = "auditoria_seguranca.json"
        print(f"🚀 PromptOps-Engine Ativa: {self.model_name}")

    def extrair_pdf(self, path: str) -> str:
        """Módulo RAG: Extrai texto de PDFs para consulta."""
        texto = ""
        try:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    pdf = PyPDF2.PdfReader(f)
                    for page in pdf.pages:
                        texto += page.extract_text()
            return texto
        except:
            return "Erro ao processar documento."

    def registrar_log(self, user_input, risco, status):
        """Módulo de Auditoria: Gera logs JSON corporativos."""
        log = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "input_resumo": user_input[:30],
            "risco": risco,
            "status": status
        }
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log, ensure_ascii=False) + "\n")

    def executar(self, user_input: str, pdf_path: str = None) -> Dict[str, Any]:
        # 🛡️ 1. Segurança (Guardrail)
        risco = 0.95 if any(x in user_input.lower() for x in ["ignore", "admin", "hack"]) else 0.05
        
        if risco > 0.5:
            self.registrar_log(user_input, risco, "BLOQUEADO")
            return {"status": "BLOQUEADO", "output": "🚨 Risco detectado pela camada de segurança."}

        # 📚 2. Conhecimento (RAG)
        contexto = self.extrair_pdf(pdf_path) if pdf_path else ""

        # ✅ 3. Resposta e Auditoria
        self.registrar_log(user_input, risco, "SUCESSO")
        return {"status": "SUCESSO", "output": f"Resposta processada localmente. Contexto: {len(contexto)} chars."}

if __name__ == "__main__":
    engine = PromptOpsEngine()
    print(engine.executar("Como criar uma lista em Python?"))
