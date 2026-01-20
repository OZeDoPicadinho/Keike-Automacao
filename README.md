# Keike Stay Web

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload
```

Acesse: `http://127.0.0.1:8000`

## Observações

- Banco padrão: SQLite (`keike_stay.db`).
- Integrações Tuya/SmartThings ficam salvas na tabela `integration_accounts`.
