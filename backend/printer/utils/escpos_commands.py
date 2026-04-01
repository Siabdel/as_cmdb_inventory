"""
printer/utils/escpos_commands.py
Constantes ESC/POS pour Bixolon SRP-350
"""

class ESCPOS:
    """Commandes ESC/POS courantes pour imprimantes thermiques"""
    
    # === Contrôle de base ===
    INIT = b'\x1b\x40'           # Reset imprimante
    CUT = b'\x1d\x56\x42\x00'    # Coupe papier (mode B)
    
    # === Alignement ===
    @staticmethod
    def align_left() -> bytes:
        """Alignement gauche"""
        return b'\x1b\x61\x00'
    
    @staticmethod
    def align_center() -> bytes:
        """Alignement centre"""
        return b'\x1b\x61\x01'
    
    @staticmethod
    def align_right() -> bytes:
        """Alignement droite"""
        return b'\x1b\x61\x02'
    
    # === Style de texte ===
    @staticmethod
    def bold_on() -> bytes:
        """Gras activé"""
        return b'\x1b\x45\x01'
    
    @staticmethod
    def bold_off() -> bytes:
        """Gras désactivé"""
        return b'\x1b\x45\x00'
    
    @staticmethod
    def double_on() -> bytes:
        """Double hauteur + largeur activé"""
        return b'\x1b\x21\x30'
    
    @staticmethod
    def double_off() -> bytes:
        """Double hauteur + largeur désactivé"""
        return b'\x1b\x21\x00'
    
    @staticmethod
    def underline_on() -> bytes:
        """Souligné activé"""
        return b'\x1b\x2d\x01'
    
    @staticmethod
    def underline_off() -> bytes:
        """Souligné désactivé"""
        return b'\x1b\x2d\x00'
    
    # === Espacement ===
    @staticmethod
    def line_feed(n: int = 1) -> bytes:
        """Saut de ligne (n lignes)"""
        return b'\x1b\x64' + bytes([min(n, 255)])
    
    @staticmethod
    def text(text: str) -> bytes:
        """Convertir texte en bytes UTF-8"""
        return text.encode('utf-8')