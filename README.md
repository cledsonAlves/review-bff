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
│   ├── main.py              # Entry point FastAPI
│   ├── routes/
│   │   └── scraper.py       # Endpoints de scraping
│   ├── services/
│   │   ├── play_store.py    # Lógica Play Store
│   │   ├── apple_store.py   # Lógica App Store
│   │   └── database_service.py # Persistência SQLite
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
pip install requests # Necessário para App Store e SQLite se não estiver no requirements
```

## 🚀 Como rodar a API

Certifique-se de que o ambiente virtual está ativado e as dependências instaladas. Você tem duas opções para iniciar o servidor local:

**Opção 1: Usando o Uvicorn diretamente**
```bash
uvicorn app.main:app --reload --port 8000
```

**Opção 2: Executando o módulo principal (via Python)**
```bash
python -m app.main
```

Após iniciar o servidor, você poderá acessar:

- **API Base**: [http://localhost:8000](http://localhost:8000)
- **Swagger UI (Documentação Interativa)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc (Documentação Alternativa)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Endpoints

### `POST /api/scrape`

Busca reviews e informações do app na loja especificada e salva no SQLite.

**Body:**
```json
{
  "package": "com.itau.investimentos",
  "store": "apple_store",  // "google_play" (default) ou "apple_store"
  "lang": "pt",
  "country": "br",
  "count": 100
}
```

**Response:**
```json
{
  "app_info": {
    "package": "com.itau.investimentos",
    "title": "íon Itaú: investir com taxa 0",
    "version": "3.109.0",
    "score": 4.73,
    "ratings": 26451,
    "developer": "Itaú Unibanco S.A.",
    "url": "https..."
  },
  "reviews": [
    {
      "review_id": "13828441150",
      "user_name": "claudiomfs",
      "rating": 1,
      "content": "Ao tentar acessar o app...",
      "app_version": "3.107.0",
      "date": "2026-03-08T16:39:04-07:00"
    }
  ],
  "total": 1,
  "lang": "pt",
  "country": "br",
  "store": "apple_store"
}
```

---

### `GET /api/app-info/{package}`

Retorna somente os metadados do app.

```bash
curl "http://localhost:8000/api/app-info/com.itau.investimentos?store=apple_store&lang=pt&country=br"
```

---

### `GET /health`

Health check.

```bash
curl http://localhost:8000/health
# {"status": "ok", "version": "1.0.0"}
```

## Banco de Dados (SQLite)

Os reviews são salvos automaticamente na tabela `review_store` do arquivo `reviews.db`.
Para consultar via terminal:

```bash
sqlite3 reviews.db "SELECT * FROM review_store ORDER BY created_at DESC LIMIT 5;"
```

## Roadmap

- [x] MVP: Scraping API (Google Play & App Store)
- [x] Persistência Local (SQLite)
- [ ] Embeddings com Sentence Transformers
- [ ] Análise de sentimentos (positivo/neutro/negativo)
- [ ] Modelagem de tópicos com BERTopic
- [ ] Dashboard de resultados
