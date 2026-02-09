from objects.utilisateur import Utilisateur
from objects.bloc import Bloc
from objects.transaction import Transaction
import random
import hashlib


class Mineur(Utilisateur):
    def __init__(self, nom, difficulte=5):
        super().__init__(nom)
        self.difficulte = difficulte


    def creer_bloc_genesis(self, utilisateurs):
        """Crée le premier bloc de la blockchain (bloc genesis) sans le miner"""
        print("\n" + "="*60)
        print("🌟 Création du bloc Genesis")
        print("="*60)
        
        # Transactions Genesis permettent d'initialiser les soldes des utilisateurs
        transactions_genesis = [Transaction(
            expediteur=Utilisateur("GENESIS"),
            destinataire=user,
            montant=random.uniform(10, 100),
            cle_publique_expediteur="SYSTEM"
        ) for user in utilisateurs]
         
        bloc_genesis = Bloc(
            index=0,
            transactions=transactions_genesis,
            hash_precedent="0" * 64,
            difficulte=2
        )

        return self.miner_bloc(bloc_genesis.transactions)

    
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
            expediteur=Utilisateur("RECOMPENSE"),
            destinataire=self,
            montant=recompense,
            cle_publique_expediteur="SYSTEM"
        )
        
        # Calcul des frais de transaction
        frais_totaux = sum(0.0001 for _ in transactions_en_attente)  # 0.0001 BTC par transaction
        transaction_recompense.montant += frais_totaux
        toutes_transactions = transactions_en_attente + [transaction_recompense]

        # Création du bloc
        bloc = Bloc(
            index=index_bloc,
            transactions=toutes_transactions,
            hash_precedent=hash_dernier_bloc,
            difficulte=difficulte
        )
        
        # Minage du bloc (Proof of Work)
        cible = '0' * difficulte
        tentatives = 0
        nonce = 0

        while True:
            # Le minage doit être arrêté si un autre mineur a trouvé le hash
            if is_mining_active is not None and not is_mining_active():
                print(f"🛑 Mineur {self.nom} a arrêté le minage")
                return None

            hash = self.calculer_hash(bloc, nonce)
            
            # Vérifier si le hash commence par le nombre requis de zéros
            if hash.startswith(cible):
                print(f"\n✅ Bloc miné par {self.nom}! Nonce trouvé: {nonce}")
                bloc.nonce = nonce
                bloc.hash = hash
                return bloc
            else:
                nonce += 1
                tentatives += 1
            
            # Affichage de la progression
            if tentatives % 100000 == 0:
                print(f"   {self.nom:<13}: {tentatives:,} tentatives")


    def calculer_hash(self, bloc, nonce):
        """ Calcule le hash du header d'un bloc avec double SHA256 """
        bits = str(self.difficulte)
        header = f"{bloc.hash_precedent}{bloc.racine_merkle}{bloc.timestamp}{bits}{nonce}".encode()
        hash1 = hashlib.sha256(header).digest()
        hash2 = hashlib.sha256(hash1).hexdigest()
        return hash2

    
    def valider_bloc(self, bloc, bloc_precedent):
        """
        Valide un bloc déjà miné
        Vérifie :
        - Le hash du bloc respecte la cible
        - Le chainage avec le bloc précédent
        - Toutes les transactions sont valides
        """
        print(f"\n🔍 Validation du bloc #{bloc.index}...")
        cible = '0' * self.difficulte
        if not bloc.hash.startswith(cible):
            return False
        
        if bloc.hash_precedent != bloc_precedent.hash:
            return False

        for tx in bloc.transactions:
            if tx.expediteur == "RECOMPENSE":
                continue
            if not self.verifier_signature(tx.cle_publique, tx.contenu, tx.signature):
                return False 
        return True 
    

    def calculer_solde(self, chain, cle_publique):
        """Calcule le solde d'une clé publique en parcourant toute la blockchain"""
        solde = 0.0
        
        for bloc in chain:
            for transaction in bloc.transactions:
                if transaction.destinataire.cle_publique == cle_publique:
                    solde += transaction.montant
                if transaction.expediteur.cle_publique == cle_publique:
                    solde -= transaction.montant
        
        return solde
    