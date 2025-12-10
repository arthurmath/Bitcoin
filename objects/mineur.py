from objects.bloc import Bloc
from objects.transaction import Transaction
from objects.utilisateur import Utilisateur
import hashlib


class Mineur:
    def __init__(self, nom, difficulte=2):
        self.nom = nom
        self.solde_btc = 0.0
        self.difficulte = difficulte
        self.adresse = nom

    def calculer_hash(self, header):
        """
        Calcule le hash du bloc avec double SHA256
        SHA256(SHA256(header))
        """
        hash1 = hashlib.sha256(header).digest()
        hash2 = hashlib.sha256(hash1).hexdigest()
        return hash2

    
    def miner_bloc(self, transactions_en_attente=[], hash_dernier_bloc="0", index_bloc=0, recompense=3.125, difficulte=2, is_mining_active=None):
        """
        Mine un nouveau bloc :
        1. Regroupe les transactions en attente
        2. Ajoute la transaction de récompense 
        3. Résout le problème de Proof of Work
        4. Retourne le bloc validé
        """
        
        # Créer la transaction de récompense
        transaction_recompense = Transaction(
            expediteur_adresse="RECOMPENSE",
            destinataire_adresse=self.adresse,
            montant=recompense,
            cle_publique_expediteur="SYSTEM"
        )
        
        # Calculer les frais de transaction
        frais_totaux = sum(0.0001 for _ in transactions_en_attente)  # 0.0001 BTC par transaction
        transaction_recompense.montant += frais_totaux
        
        # Combiner la récompense avec les transactions en attente
        toutes_transactions = [transaction_recompense] + transactions_en_attente

        # Créer le bloc
        bloc = Bloc(
            index=index_bloc,
            transactions=toutes_transactions,
            hash_precedent=hash_dernier_bloc,
            difficulte=difficulte
        )
        
        # Miner le bloc (Proof of Work)
        cible = '0' * difficulte
        tentatives = 0
        nonce = 0

        while True:
            # Vérifier si le minage doit être arrêté (par exemple si un autre mineur a trouvé le bloc)
            if is_mining_active is not None and not is_mining_active():
                print(f"🛑 Mineur {self.nom} a arrêté le minage")
                return None

            header = bloc.header(nonce)
            hash = self.calculer_hash(header)
            tentatives += 1
            
            # Vérifier si le hash commence par le nombre requis de zéros
            if hash.startswith(cible):
                bloc.hash = hash
                bloc.nonce = nonce
                print(f"\n✅ Bloc miné par {self.nom}! Hash: {bloc.hash[:20]}..., Nonce: {bloc.nonce}")
                return bloc
            else:
                nonce += 1
            
            # Affichage de progression
            if tentatives % 100000 == 0:
                print(f"   {self.nom:<13}: {tentatives:,} tentatives")

    
    def valider_bloc(self, bloc, bloc_precedent):
        """
        Valide un bloc déjà miné
        Vérifie :
        - Le hash du bloc est correct
        - Toutes les transactions sont valides
        - Le Proof of Work est satisfait
        """
        print(f"\n🔍 Validation du bloc #{bloc.index}...")
        cible = '0' * self.difficulte
        if not bloc.hash.startswith(cible):
            return False
        
        if bloc.hash_precedent != bloc_precedent.hash:
            return False

        for tx in bloc.transactions:
            if tx.expediteur in ["GENESIS", "RECOMPENSE"]:
                continue
            if not Utilisateur.verifier_signature(tx.cle_publique, tx.contenu, tx.signature):
                return False 
        return True 
    
    def afficher_info(self):
        """Affiche les informations du mineur"""
        print(f"\n--- Mineur: {self.nom} ---")
        print(f"Adresse: {self.adresse}")
        print(f"Solde: {self.solde_btc} BTC")
    
    def __str__(self):
        return f"Mineur {self.nom} (Solde: {self.solde_btc} BTC)"

