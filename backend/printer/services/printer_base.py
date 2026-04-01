from abc import ABC, abstractmethod
from typing import Optional

class AbstractThermalPrinter(ABC):
    """Interface commune pour tous les drivers d'imprimantes thermiques"""
    
    @abstractmethod
    def connect(self, max_retries: int = 3) -> bool:
        """Établir la connexion physique"""
        pass
    
    @abstractmethod
    def print_cmdb_label(self, asset_id: str, 
                         qr_data: Optional[str] = None,
                        barcode_ : Optional[str] = None,
                        custom_text: Optional[str] = None
                        ) -> bool   :   
    
        """Impression d'une étiquette CMDB"""
        pass
    
    @abstractmethod
    def close(self):
        """Libérer les ressources"""
        pass
    
    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """État de la connexion"""
        pass