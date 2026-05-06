import json
import PyPDF2
from datetime import datetime
from typing import Dict, Any

class PromptOpsEngine:
    """
    Engine de Orquestração de LLMs com foco em Segurança (Guardrails), 
    Auditoria (Logs) e Conhecimento local (RAG).
    """
    def __init__(self, model_name="Qwen/Qwen2.5-0.5B-Instruct"):
        self.model_name = model_name
        self.log_file = "auditoria_seguranca.json"

    def extrair_texto_pdf(self, caminho_pdf: str) -> str:
        """Extrai texto de PDFs para prover contexto à IA (RAG)."""
        texto = ""
        try:
            with open(caminho_pdf, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    texto += page.extract_text()
            return texto
        except Exception as e:
            return f"Erro ao processar PDF: {str(e)}"

    def registrar_auditoria(self, user_input: str, risco: float, status: str, motivo: str):
        """Gera logs estruturados para conformidade e segurança corporativa."""
        log = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "input_preview": user_input[:50],
            "risk_score": risco,
            "status": status,
            "reason": motivo
        }
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log, ensure_ascii=False) + "\n")

    def process(self, user_input: str, doc_context: str = "", enable_guardrails: bool = True) -> Dict[str, Any]:
        """Fluxo principal: Validação -> Roteamento -> Resposta."""
        
        risk_score = 0.0
        if enable_guardrails:
            # Lógica de detecção de injeção (Exemplo de threshold sênior)
            is_malicious = any(x in user_input.lower() for x in ["ignore", "system prompt", "reveal"])
            risk_score = 0.95 if is_malicious else 0.05
            
            if risk_score > 0.5:
                self.registrar_auditoria(user_input, risk_score, "BLOCKED", "Tentativa de Prompt Injection")
                # Criamos um objeto de resposta compatível com o seu README
                class Response: pass
                res = Response()
                res.status = "BLOCKED"
                res.output = "Acesso negado por diretrizes de segurança."
                res.injection_score = risk_score
                return res
        
        self.registrar_auditoria(user_input, risk_score, "SAFE", "Input Validado")
        
        # Simulação de saída governada
        class Response: pass
        res = Response()
        res.status = "SAFE"
        res.output = f"Processado com sucesso. Contexto: {len(doc_context)} chars."
        res.injection_score = risk_score
        return res

# --- EXEMPLO DE USO CONFORME O README ---
if __name__ == "__main__":
    engine = PromptOpsEngine()
    response = engine.process(user_input="What is machine learning?", enable_guardrails=True)
    print(f"Status: {response.status}")
    print(f"Output: {response.output}")

