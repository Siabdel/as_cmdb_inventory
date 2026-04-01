from typing import Type, Optional
from .printer_base import AbstractThermalPrinter
from .bixolon_srp350 import BixolonSRP350

class PrinterFactory:
    """Factory pour instancier le bon driver selon le modèle"""
    
    _registry = {
        'bixolon_srp350': BixolonSRP350,
        # Future: 'epson_tm_t88': EpsonTMT88, 'star_tsp143': StarTSP143
    }
    
    @classmethod
    def create(cls, model: str, device_id: Optional[str] = None) -> AbstractThermalPrinter:
        if model not in cls._registry:
            raise ValueError(f"Modèle non supporté: {model}")
        return cls._registry[model](device_id=device_id)
    
    @classmethod
    def register(cls, model: str, driver_class: Type[AbstractThermalPrinter]):
        """Enregistrer un nouveau driver"""
        cls._registry[model] = driver_class