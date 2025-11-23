from objects.bloc import Bloc
from objects.transaction import Transaction


class Mineur:
    def __init__(self, nom, adresse):
        self.nom = nom
        self.adresse = adresse
        self.solde_btc = 0.0
    
    def miner_bloc_genesis(self, bloc_genesis):
        """
        Mine le bloc genesis (sans transaction coinbase)
        """
        print(f"\n{'='*60}")
        print(f"🔨 {self.nom} mine le bloc genesis")
        print(f"{'='*60}")
        
        # Miner le bloc genesis (Proof of Work)
        cible = '0' * bloc_genesis.difficulte
        print(f"\n⛏️  Mining bloc genesis... (difficulté: {bloc_genesis.difficulte} zéros)")
        
        tentatives = 0
        while True:
            bloc_genesis.hash = bloc_genesis.calculer_hash()
            tentatives += 1
            
            if bloc_genesis.hash.startswith(cible):
                print(f"✅ Bloc genesis miné ! Hash: {bloc_genesis.hash}")
                print(f"   Nonce trouvé: {bloc_genesis.nonce} après {tentatives} tentatives")
                break
            
            bloc_genesis.nonce += 1
            
            if tentatives % 100000 == 0:
                print(f"   {tentatives} tentatives...")
        
        return bloc_genesis
    
    def miner_bloc(self, transactions_en_attente, hash_dernier_bloc, index_bloc, recompense=3.125, difficulte=4):
        """
        Mine un nouveau bloc :
        1. Regroupe les transactions en attente
        2. Ajoute la transaction de récompense (coinbase)
        3. Résout le problème de Proof of Work
        4. Retourne le bloc validé
        """
        print(f"\n{'='*60}")
        print(f"🔨 {self.nom} commence le minage du bloc #{index_bloc}")
        print(f"{'='*60}")
        
        # Créer la transaction de récompense (coinbase)
        transaction_recompense = Transaction(
            expediteur_adresse="COINBASE",
            destinataire_adresse=self.adresse,
            montant=recompense,
            cle_publique_expediteur="SYSTEM"
        )
        
        # Calculer les frais de transaction
        frais_totaux = sum(0.0001 for _ in transactions_en_attente)  # 0.0001 BTC par transaction
        transaction_recompense.montant += frais_totaux
        
        # Combiner la récompense avec les transactions en attente
        toutes_transactions = [transaction_recompense] + transactions_en_attente
        
        print(f"📦 Transactions dans le bloc: {len(toutes_transactions)}")
        print(f"   - 1 transaction coinbase: {recompense + frais_totaux} BTC")
        print(f"   - {len(transactions_en_attente)} transactions utilisateurs")
        
        # Créer le bloc
        bloc = Bloc(
            index=index_bloc,
            transactions=toutes_transactions,
            hash_precedent=hash_dernier_bloc,
            difficulte=difficulte
        )
        
        # Miner le bloc (Proof of Work)
        cible = '0' * difficulte
        print(f"\n⛏️  Mining bloc {bloc.index}... (difficulté: {difficulte} zéros)")
        
        tentatives = 0
        while True:
            bloc.hash = bloc.calculer_hash()
            tentatives += 1
            
            # Vérifier si le hash commence par le nombre requis de zéros
            if bloc.hash.startswith(cible):
                print(f"✅ Bloc miné ! Hash: {bloc.hash}")
                print(f"   Nonce trouvé: {bloc.nonce} après {tentatives} tentatives")
                break
            
            bloc.nonce += 1
            
            # Affichage de progression
            if tentatives % 100000 == 0:
                print(f"   {tentatives} tentatives...")
        
        # Ajouter la récompense au solde du mineur
        self.solde_btc += transaction_recompense.montant
        
        print(f"💰 {self.nom} a reçu {transaction_recompense.montant} BTC")
        print(f"   Nouveau solde: {self.solde_btc} BTC")
        
        return bloc
    
    def valider_bloc(self, bloc):
        """
        Valide un bloc miné par un autre mineur
        Vérifie :
        - Le hash du bloc est correct
        - Toutes les transactions sont valides
        - Le Proof of Work est satisfait
        """
        print(f"\n🔍 {self.nom} valide le bloc #{bloc.index}...")
        
        if not bloc.est_valide():
            print(f"❌ Bloc invalide !")
            return False
        
        print(f"✅ Bloc validé par {self.nom}")
        return True
    
    def afficher_info(self):
        """Affiche les informations du mineur"""
        print(f"\n--- Mineur: {self.nom} ---")
        print(f"Adresse: {self.adresse}")
        print(f"Solde: {self.solde_btc} BTC")
    
    def __str__(self):
        return f"Mineur {self.nom} (Solde: {self.solde_btc} BTC)"

