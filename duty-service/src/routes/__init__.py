from .duty_schedules import router as schedules_router
from .duty_reports import router as reports_router
from .duty_images import router as images_router
from .duty_categories import router as categories_router

__all__ = [
    "schedules_router",
    "reports_router",
    "images_router",
    "categories_router",
]
