import hashlib
import time
import json


class Transaction:
    def __init__(self, expediteur_adresse, destinataire_adresse, montant, cle_publique_expediteur):
        self.expediteur = expediteur_adresse
        self.destinataire = destinataire_adresse
        self.montant = montant
        self.cle_publique = cle_publique_expediteur
        self.timestamp = time.time()
        self.signature = None
        self.hash_transaction = None
    
    def calculer_hash(self):
        """Calcule le hash de la transaction"""
        contenu = f"{self.expediteur}{self.destinataire}{self.montant}{self.timestamp}"
        return hashlib.sha256(contenu.encode()).hexdigest()
    
    def signer(self, utilisateur):
        """
        L'expéditeur signe la transaction avec sa clé privée
        Cela prouve qu'il autorise le transfert
        """
        message = f"{self.expediteur}{self.destinataire}{self.montant}{self.timestamp}"
        self.signature = utilisateur.signer_transaction(message)
        self.hash_transaction = self.calculer_hash()
    
    def est_valide(self):
        """Vérifie que la transaction est valide"""
        # Transaction de récompense (coinbase) n'a pas d'expéditeur
        if self.expediteur == "COINBASE":
            return True
        
        # Vérifier que la transaction est signée
        if not self.signature:
            return False
        
        # Vérifier la signature avec la clé publique
        from utilisateur import Utilisateur
        message = f"{self.expediteur}{self.destinataire}{self.montant}{self.timestamp}"
        return Utilisateur.verifier_signature(self.cle_publique, message, self.signature)
    
    def to_dict(self):
        """Convertit la transaction en dictionnaire"""
        return {
            'expediteur': self.expediteur,
            'destinataire': self.destinataire,
            'montant': self.montant,
            'cle_publique': self.cle_publique,
            'timestamp': self.timestamp,
            'signature': self.signature,
            'hash': self.hash_transaction
        }
    
    def __str__(self):
        return f"{self.expediteur[:10]}... -> {self.destinataire[:10]}... : {self.montant} BTC"

