from objects.utilisateur import Utilisateur
import hashlib
import time


class Transaction:
    def __init__(self, expediteur, destinataire, montant, cle_publique_expediteur):
        self.expediteur: Utilisateur = expediteur
        self.destinataire: Utilisateur = destinataire
        self.montant: float = montant
        self.cle_publique = cle_publique_expediteur
        self.timestamp = time.time()
        self.contenu = f"{expediteur.cle_publique}{destinataire.cle_publique}{self.montant}{self.timestamp}"
        self.hash_transaction = hashlib.sha256(self.contenu.encode()).hexdigest()
        self.signature = None


    def __str__(self):
        return f"Transaction : {self.expediteur.nom} -> {self.destinataire.nom} : {self.montant} BTC"

