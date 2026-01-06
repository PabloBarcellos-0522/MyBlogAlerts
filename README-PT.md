# 📣 MyBlogAlerts

Automatize o monitoramento de avisos acadêmicos do blog da faculdade, salvando novas postagens num banco PostgreSQL e recebendo alertas via WhatsApp.
Este projeto funciona em Blogs acadêmicos que utilizam o formado de tecnologia Phidelis

---

## 🚀 O que é

**MyBlogAlerts** é uma API em Python com scraping automatizado que:

-   Detecta novas postagens acadêmicas de disciplinas
-   Armazena os dados com segurança em um banco PostgreSQL
-   Notifica via WhatsApp sempre que algo novo for publicado
-   Recebe e reponde comandos enviados pelos usuários no whatsapp

> Documentação completa disponível em [`docs/index-pt.adoc`](docs/index-pt.adoc)

---

## 📦 Requisitos

-   Python 3.12+
-   PostgreSQL 13+
-   Api Whatsapp configurada, como o [`HermesCore`](https://github.com/PabloBarcellos-0522/HermesCore)
-   Variáveis configuradas em [`.env`](.env.template)

---

## ⚙️ Como usar

### 1. Clone o repositório

```bash
git clone https://github.com/PabloBarcellos-0522/MyBlogAlerts.git
cd MyBlogAlerts
```

### 2. Configure o ambiente

-   #### Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

-   #### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

-   Crie um arquivo .env na raiz com:

```env
DATABASE_URL = postgresql://usuario:senha@host:port/db
API_URL = url_da_api_whatsapp
API_KEY = chave_api_whatsapp
GROUP_ID = idgrupo_whatsapp (Opcional)
BLOG_URL = Url principal do portal do aluno, EX: (https://aluno.uvv.br/)
WEB_SCRAPER_SECRET_KEY = Chave para criptografia dos dados (de preferencia gerada pela lib cryptography)
ACESS_TOKEN = MyBlogAlerts
REGISTER_PAGE = url_da_página_de_registro (base para ser adicionada a política CORS)
REGISTER_PAGE_URL = url_completa_da_pagina
```

### 3. Execute o projeto

```bash
uvicorn src.interface.api:app --reload
```

---

Pronto, Agora você irá receber seus avisos diretamente em seu grupo no WhatsApp

você pode também usar o Local Tunnel caso queiro hospedar a api localmente:

```bash
lt --port {Porta da api}
```
