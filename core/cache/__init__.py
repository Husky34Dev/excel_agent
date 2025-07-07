"""
Módulo de cache para el sistema Excel Agent.

Proporciona funcionalidades de cache persistente para DataFrames de pandas
y metadatos asociados, optimizando el rendimiento al evitar recargas
innecesarias de archivos Excel.
"""

from .persistent_cache import persistent_cache

__all__ = ["persistent_cache"]
