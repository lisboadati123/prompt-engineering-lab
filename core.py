import torch
from transformers import pipeline
import psutil

class DellAI:
    """Motor de IA para Diagnóstico de Hardware (Padrão Dell)"""
    def __init__(self):
        # Detecta se há GPU ou usa CPU
        self.device = 0 if torch.cuda.is_available() else -1
        self.model_name = "Qwen/Qwen2.5-0.5B-Instruct"
        print(f"🖥️ Sistema carregado no hardware: {'GPU' if self.device == 0 else 'CPU'}")

    def analisar_problema(self, ticket):
        # Carrega o pipeline de IA local
        pipe = pipeline("text-generation", model=self.model_name, device=self.device)
        
        prompt = f"Instrução: Você é um técnico Dell Nível 3. Resolva o problema: {ticket}"
        
        # Gera a resposta técnica
        resultado = pipe(prompt, max_new_tokens=150, do_sample=True, temperature=0.7)
        return resultado[0]['generated_text']

# Teste automático do sistema
if __name__ == "__main__":
    app = DellAI()
    ticket_exemplo = "Meu notebook Dell está apitando 2 bips"
    print(f"\n🔍 Diagnóstico Sugerido:\n{app.analisar_problema(ticket_exemplo)}")

