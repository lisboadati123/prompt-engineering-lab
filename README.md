# 🛠️ PromptOps-Engine: Governança Local de LLMs

Este framework gerencia a segurança e o custo de IAs locais.

## 🎯 Arquitetura
```mermaid
graph TD
    A[Input] --> B[Guardrail: Segurança]
    B -- Risco > 0.5 --> C[🚨 BLOQUEADO]
    B -- Seguro --> D[Módulo RAG: PDF]
    D --> E[🤖 IA Local: Qwen 2.5]
    E --> F[📝 Log de Auditoria]
```

## 🚀 Como Rodar
1. Instale as dependências: `pip install -r requirements.txt`
2. Execute o core: `python core.py`
