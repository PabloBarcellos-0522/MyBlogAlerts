# 📣 MyBlogAlerts

Automatize o monitoramento de avisos acadêmicos do blog da faculdade, salvando novas postagens num banco PostgreSQL e recebendo alertas via WhatsApp.
Este projeto funciona em Blogs acadêmicos que utilizam o formado de tecnologia Phidelis 

---

## 🚀 O que é

**MyBlogAlerts** é um projeto em Python com scraping automatizado que:

- Detecta novas postagens acadêmicas de disciplinas
- Armazena os dados com segurança em um banco PostgreSQL
- Notifica via WhatsApp sempre que algo novo for publicado

> Documentação completa disponível em [`docs/index.adoc`](docs/index.adoc)

---

## 📦 Requisitos

- Python 3.12+
- PostgreSQL 13+
- Conta e chave da Green API (WhatsApp) ou api compatível
- Id de um grupo WhatsApp que receberá menságens (é possível gerar/viualizar seu ID pelo site da Green API)
- Variáveis configuradas em [`.env`](.env)

---

## ⚙️ Como usar

### 1. Clone o repositório

```bash
git clone https://github.com/PabloBarcellos-0522/MyBlogAlerts.git
cd MyBlogAlerts
```

### 2. Configure o ambiente (Linux)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Crie um arquivo .env na raiz com:

```env
DATABASE_URL = postgresql://usuario:senha@host:port/db
API_URL = suachave_greenAPI
GROUP_ID = idgrupo_whatsapp
BLOG_URL = Url principal do portal do aluno, EX: (https://aluno.uvv.br/)
WEB_SCRAPER_SECRET_KEY = Chave para criptografia dos dados (de preferencia gerada pela lib cryptography)
```

### 3. Execute o projeto

```bash
python -m src.interface.Cli
```

---

Pronto, Agora você irá receber seus avisos diretamente em seu grupo no WhatsApp
