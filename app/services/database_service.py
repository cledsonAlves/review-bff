import sqlite3
import logging
import os
from datetime import datetime
from typing import List
from app.schemas.review import ReviewItem

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reviews.db")

def init_db():
    """Inicializa o banco de dados SQLite e cria a tabela review_store se não existir."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS review_store (
                id TEXT PRIMARY KEY,
                review_id TEXT,
                store TEXT,
                package TEXT,
                user_name TEXT,
                user_image TEXT,
                rating INTEGER,
                content TEXT,
                thumbs_up INTEGER,
                app_version TEXT,
                date TEXT,
                reply_content TEXT,
                reply_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitored_apps (
                package TEXT PRIMARY KEY,
                store TEXT NOT NULL,
                lang TEXT DEFAULT 'pt',
                country TEXT DEFAULT 'br',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Banco de dados SQLite inicializado em: {DB_PATH}")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")

def save_reviews_to_sqlite(reviews: List[ReviewItem], store: str, package: str):
    """Salva uma lista de reviews no SQLite."""
    if not reviews:
        return
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Preparar os dados para inserção
        data_to_insert = []
        for r in reviews:
            # ID único para evitar duplicatas (loja + ID do review)
            unique_id = f"{store}_{r.review_id}"
            
            data_to_insert.append((
                unique_id,
                r.review_id,
                store,
                package,
                r.user_name,
                r.user_image,
                r.rating,
                r.content,
                r.thumbs_up,
                r.app_version,
                r.date,
                r.reply_content,
                r.reply_date
            ))
            
        # Usar INSERT OR IGNORE para não dar erro em duplicatas (ou INSERT OR REPLACE se preferir atualizar)
        cursor.executemany('''
            INSERT OR REPLACE INTO review_store (
                id, review_id, store, package, user_name, user_image, 
                rating, content, thumbs_up, app_version, date, 
                reply_content, reply_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data_to_insert)
        
        conn.commit()
        conn.close()
        logger.info(f"Salvo {len(reviews)} reviews no SQLite para o app {package} ({store}).")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar reviews no SQLite: {e}")
        return False

def get_all_reviews():
    """Retorna todos os reviews armazenados no banco de dados."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM review_store ORDER BY date DESC")
        rows = cursor.fetchall()
        
        reviews = []
        for row in rows:
            reviews.append(dict(row))
            
        conn.close()
        return reviews
    except Exception as e:
        logger.error(f"Erro ao buscar todos os reviews: {e}")
        return []

def get_reviews_by_package(package: str):
    """Retorna os reviews filtrados por um pacote específico."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM review_store WHERE package = ? ORDER BY date DESC", (package,))
        rows = cursor.fetchall()
        
        reviews = [dict(row) for row in rows]
        conn.close()
        return reviews
    except Exception as e:
        logger.error(f"Erro ao buscar reviews para o pacote {package}: {e}")
        return []

def get_monitored_apps():
    """Retorna a lista de apps configurados para o schedule."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM monitored_apps WHERE is_active = 1")
        rows = cursor.fetchall()
        
        apps = [dict(row) for row in rows]
        conn.close()
        return apps
    except Exception as e:
        logger.error(f"Erro ao buscar apps monitorados: {e}")
        return []

def add_monitored_app(package: str, store: str, lang: str = "pt", country: str = "br"):
    """Adiciona um app para ser monitorado de hora em hora."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO monitored_apps (package, store, lang, country, is_active)
            VALUES (?, ?, ?, ?, 1)
        ''', (package, store, lang, country))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erro ao adicionar app monitorado: {e}")
        return False

def remove_monitored_app(package: str):
    """Remove um app do monitoramento."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM monitored_apps WHERE package = ?", (package,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erro ao remover app monitorado: {e}")
        return False

# Inicializa o banco ao importar o módulo
init_db()
