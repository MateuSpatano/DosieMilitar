from app.db import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.services.stats_service import StatsService

def get_dashboard_data(db: Session = Depends(get_db)):
    """Dependência para obter todos os dados do dashboard."""
    stats_service = StatsService(db)
    stats = stats_service.get_dashboard_stats()
    military_stats = stats_service.get_military_stats()
    
    # Preparar dados para o gráfico
    chart_data = {
        "labels": list(stats["dtype_distribution"].keys()),
        "data": list(stats["dtype_distribution"].values())
    }
    
    return {
        "stats": stats,
        "military_stats": military_stats,
        "chart_data": chart_data
    }