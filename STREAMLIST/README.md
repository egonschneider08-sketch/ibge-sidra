# Painel Web — SIDRA

Execute no **terminal, na raiz do projeto**:

```powershell
.\.venv\Scripts\python.exe -m pip install -r STREAMLIST/requirements.txt
.\.venv\Scripts\python.exe -m streamlit run STREAMLIST/app.py
```

O navegador abrirá um painel local (normalmente em `http://localhost:8501`). A pasta `STREAMLIST` foi nomeada conforme solicitado, mas o framework se chama **Streamlit**.

O aplicativo reutiliza `SRC.api.consultar_sidra`, que mantém compatibilidade com `python -m SRC.main` e com o notebook existente. Dados são consultados do IBGE; sem conexão, a interface informa o erro e não fabrica dados. Cache de uma hora, com botão de atualização.

**Nota:** os números-índice não são taxas de crescimento mensal. Compare os meses usando a variável correta (11601). Cada indicador e categoria podem ter cobertura diferente.
