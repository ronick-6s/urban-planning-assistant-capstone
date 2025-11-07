"""
Chennai Smart Agent Package
External agent for live demographics and spatial data for Chennai city
"""

from .chennai_agent import create_chennai_agent
from .chennai_tools import CHENNAI_TOOLS
from .chennai_data_apis import ChennaiDataAPI, ChennaiSpatialAnalyzer
from .chennai_config import (
    CHENNAI_ZONES,
    CHENNAI_DISTRICTS,
    CHENNAI_TRANSPORT,
    CHENNAI_DEMOGRAPHICS,
    CHENNAI_ECONOMY
)

__version__ = "1.0.0"
__author__ = "Urban Planning Assistant Team"

__all__ = [
    'create_chennai_agent',
    'CHENNAI_TOOLS',
    'ChennaiDataAPI',
    'ChennaiSpatialAnalyzer',
    'CHENNAI_ZONES',
    'CHENNAI_DISTRICTS',
    'CHENNAI_TRANSPORT',
    'CHENNAI_DEMOGRAPHICS',
    'CHENNAI_ECONOMY'
]
