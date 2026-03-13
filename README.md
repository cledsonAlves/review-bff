# Review Sentiment Analysis — API

API para scraping de reviews da Google Play Store e Apple App Store, com armazenamento local em SQLite e pipeline futuro de análise de sentimentos.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| API | FastAPI + Uvicorn |
| Scraping (Play Store) | google-play-scraper |
| Scraping (App Store) | iTunes Lookup & RSS API |
| Banco de Dados | SQLite |
| Validação | Pydantic v2 |
| Análise (futuro) | Sentence Transformers, BERTopic, Scikit-learn |

## Estrutura

```
review-apps/
├── app/
│   ├── main.py              # Entry point FastAPI & Configuração do Scheduler
│   ├── routes/
│   │   ├── scraper.py       # Endpoints de scraping manual
│   │   ├── reviews.py       # Consulta de reviews salvos no banco
│   │   └── schedule.py      # Configuração do monitoramento automático
│   ├── services/
│   │   ├── play_store.py    # Lógica Play Store
│   │   ├── apple_store.py   # Lógica App Store
│   │   ├── database_service.py # Persistência e CRUD SQLite
│   │   └── scheduler_service.py # Lógica de busca de hora em hora (APScheduler)
│   └── schemas/
│       └── review.py        # Modelos Pydantic
├── reviews.db               # Banco de dados local (gerado automaticamente)
├── requirements.txt
├── .env.example
└── README.md
```

## Instalação

```bash
# 1. Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate     # Linux/macOS
# venv\Scripts\activate      # Windows

# 2. Instalar dependências
pip install -r requirements.txt
```

## 🚀 Como rodar a API

Certifique-se de que o ambiente virtual está ativado. O servidor iniciará automaticamente o **Scheduler** para buscas de hora em hora.

**Rodar localmente:**
```bash
python -m app.main
```

**Rodar no servidor (Produção):**
Para manter o processo rodando após fechar o terminal:
```bash
nohup ./venv/bin/python -m app.main > out.log 2>&1 &
```

---

## 🛠 Endpoints da API

### 1. Reviews (Banco de Dados)

#### `GET /api/reviews/`
Retorna os reviews salvos no banco. Aceita parâmetros opcionais para filtrar por plataforma:
*   **package**: ID do pacote (ex: `com.itau.investimentos`)
*   **store**: Loja (`google_play` ou `apple_store`)

**Exemplo:** `/api/reviews/?package=com.itau.investimentos&store=apple_store`

#### `GET /api/reviews/{package}`
Retorna os reviews de um app específico filtrados pelo ID do pacote (ex: `com.itau.investimentos`).

---

### 2. Agendamento (Schedule)

O sistema possui um agendador que busca reviews de hora em hora para os apps configurados.

#### `GET /api/schedule/apps`
Lista todos os apps atualmente monitorados pelo scheduler.

#### `POST /api/schedule/apps`
Adiciona um novo app ao monitoramento automático.
**Body:**
```json
{
  "package": "com.itau.investimentos",
  "store": "google_play",
  "lang": "pt",
  "country": "br"
}
```

#### `DELETE /api/schedule/apps/{package}`
Remove um app do monitoramento automático.

#### `POST /api/schedule/run-now`
Dispara o processo de scraping imediatamente para todos os apps monitorados.

---

### 3. Scraping Manual

#### `POST /api/scrape`
Busca reviews e informações do app na loja especificada e salva no SQLite imediatamente.

**Body:**
```json
{
  "package": "com.itau.investimentos",
  "store": "apple_store",
  "lang": "pt",
  "country": "br",
  "count": 100
}
```

#### `GET /api/app-info/{package}`
Retorna somente os metadados do app.

---

### 4. Status

#### `GET /health`
Health check do sistema.

## Banco de Dados (SQLite)

Os dados são salvos no arquivo `reviews.db` em duas tabelas principais:
- `review_store`: Armazena os reviews capturados.
- `monitored_apps`: Armazena a configuração do scheduler.

Para consultar via terminal:
```bash
sqlite3 reviews.db "SELECT * FROM review_store ORDER BY date DESC LIMIT 5;"
```

## Roadmap

- [x] MVP: Scraping API (Google Play & App Store)
- [x] Persistência Local (SQLite)
- [x] Agendamento (Schedule) de busca automática de hora em hora
- [ ] Dashboard de resultados simples no Frontend
- [ ] Exportação de dados (CSV/JSON)
