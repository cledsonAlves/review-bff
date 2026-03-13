from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.review import MonitoredApp, MonitoredAppCreate
from app.services.database_service import get_monitored_apps, add_monitored_app, remove_monitored_app
from app.services.scheduler_service import scrape_all_monitored_apps

router = APIRouter(prefix="/api/schedule", tags=["Schedule"])

@router.get("/apps", response_model=List[MonitoredApp])
async def list_monitored_apps():
    """Lista todos os apps atualmente configurados para scraping de hora em hora."""
    return get_monitored_apps()

@router.post("/apps", response_model=dict)
async def add_app_to_schedule(app_data: MonitoredAppCreate):
    """Adiciona um novo app ao monitoramento agendado."""
    success = add_monitored_app(
        package=app_data.package,
        store=app_data.store,
        lang=app_data.lang,
        country=app_data.country
    )
    if not success:
        raise HTTPException(status_code=500, detail="Erro ao salvar configuração do app.")
    return {"status": "success", "message": f"App {app_data.package} adicionado ao schedule."}

@router.delete("/apps/{package}", response_model=dict)
async def remove_app_from_schedule(package: str):
    """Remove um app do monitoramento agendado."""
    success = remove_monitored_app(package)
    if not success:
        raise HTTPException(status_code=500, detail="Erro ao remover app.")
    return {"status": "success", "message": f"App {package} removido do schedule."}

@router.post("/run-now", response_model=dict)
async def run_schedule_manually():
    """Dispara o processo de scraping imediatamente para todos os apps monitorados."""
    # Como o scraping pode demorar, o ideal seria usar background tasks do fastapi
    # Mas para simplificar vamos chamar direto aqui ou via thread
    import threading
    thread = threading.Thread(target=scrape_all_monitored_apps)
    thread.start()
    return {"status": "success", "message": "Scraping disparado em background."}
