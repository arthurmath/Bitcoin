import hashlib
import time


class Transaction:
    def __init__(self, expediteur, destinataire, montant, cle_publique_expediteur):
        self.expediteur = expediteur
        self.destinataire = destinataire
        self.montant = montant
        self.cle_publique = cle_publique_expediteur
        self.timestamp = time.time()
        self.contenu = f"{self.expediteur.adresse}{self.destinataire.adresse}{self.montant}{self.timestamp}"
        self.hash_transaction = hashlib.sha256(self.contenu.encode()).hexdigest()
        self.signature = None


    def __str__(self):
        return f"Transaction : {self.expediteur.nom} -> {self.destinataire.nom} : {self.montant} BTC"


