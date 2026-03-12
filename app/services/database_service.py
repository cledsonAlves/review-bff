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

# Inicializa o banco ao importar o módulo
init_db()
