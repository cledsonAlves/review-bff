import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.play_store import get_reviews as get_play_reviews
from app.services.apple_store import get_reviews as get_apple_reviews
from app.services.database_service import get_monitored_apps, save_reviews_to_sqlite

logger = logging.getLogger(__name__)

# Instância global do scheduler
scheduler = BackgroundScheduler()

def scrape_all_monitored_apps():
    """Tarefa executada pelo scheduler para buscar reviews de todos os apps monitorados."""
    logger.info("Iniciando busca agendada de reviews...")
    apps = get_monitored_apps()
    
    if not apps:
        logger.info("Nenhum app configurado para monitoramento.")
        return

    for app_config in apps:
        package = app_config["package"]
        store = app_config["store"]
        lang = app_config.get("lang", "pt")
        country = app_config.get("country", "br")
        
        logger.info(f"Buscando reviews para {package} ({store})...")
        
        try:
            if store == "apple_store":
                reviews = get_apple_reviews(package, lang=lang, country=country, count=100)
            else:
                reviews = get_play_reviews(package, lang=lang, country=country, count=100)
            
            if reviews:
                save_reviews_to_sqlite(reviews, store, package)
                logger.info(f"Sucesso ao atualizar {package}.")
            else:
                logger.info(f"Nenhum review novo para {package}.")
                
        except Exception as e:
            logger.error(f"Erro ao processar {package} no scheduler: {e}")

def start_scheduler():
    """Inicia o scheduler e agenda a tarefa de hora em hora."""
    if not scheduler.running:
        # Agenda para rodar de hora em hora (no minuto 0)
        # Para testar mais rápido, poderiamos usar interval (minutes=1)
        scheduler.add_job(
            scrape_all_monitored_apps,
            CronTrigger(minute=0),
            id="review_scraping_job",
            replace_existing=True
        )
        # Executa uma vez no início (opcional)
        # scheduler.add_job(scrape_all_monitored_apps, id="immediate_scraping_job")
        
        scheduler.start()
        logger.info("Scheduler de reviews iniciado (Rodando de hora em hora).")

def stop_scheduler():
    """Para o scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler de reviews parado.")
