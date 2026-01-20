# Keike Stay Web

## Como rodar

### 1) Baixar o projeto

Se você **não tem o Git instalado** (mensagem: "git não é reconhecido"), escolha uma das opções:

- **Opção A — baixar ZIP pelo GitHub**
  1. Abra: https://github.com/OZeDoPicadinho/Keike-Automacao
  2. Clique em **Code** → **Download ZIP**
  3. Extraia o ZIP em uma pasta (ex: `C:\Keike-Automacao`)

- **Opção B — instalar Git e clonar**
  1. Instale o Git: https://git-scm.com/downloads
  2. Depois, rode:
     ```bash
     git clone https://github.com/OZeDoPicadinho/Keike-Automacao
     cd Keike-Automacao
     ```

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload
```

> **Windows (PowerShell)**
> ```powershell
> python -m venv .venv
> .venv\Scripts\activate
> pip install -r requirements.txt
> python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
> ```

Acesse: `http://127.0.0.1:8000`

## Observações

- Execute o comando na raiz do repositório para garantir que os templates/estáticos sejam encontrados.
- Banco padrão: SQLite (`keike_stay.db`).
- Integrações Tuya/SmartThings ficam salvas na tabela `integration_accounts`.
