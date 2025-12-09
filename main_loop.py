import random
import threading
import time
from objects.utilisateur import Utilisateur
from objects.transaction import Transaction
from objects.blockchain import Blockchain
from objects.mineur import Mineur
from objects.bloc import Bloc



class Simulation:
    def __init__(self):
        # Configuration
        self.difficulte = 5
        self.recompense_bloc = 3.125
        
        # Créer 10 utilisateurs
        self.noms = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Satoshi", "Henry", "Iris", "Jack"]
        self.utilisateurs = [Utilisateur(nom) for nom in self.noms]
        
        # Créer 4 mineurs
        self.mineurs = [
            Mineur("Mineur_Alpha", self.utilisateurs[0].adresse, self.difficulte),
            Mineur("Mineur_Beta", self.utilisateurs[1].adresse, self.difficulte),
            Mineur("Mineur_Gamma", self.utilisateurs[2].adresse, self.difficulte),
            Mineur("Mineur_Delta", self.utilisateurs[3].adresse, self.difficulte)
        ]
        
        # Créer la blockchain
        self.blockchain = Blockchain(difficulte=2)
        bloc_genesis = self.blockchain.creer_bloc_genesis(self.utilisateurs)
        bloc_genesis = self.mineurs[0].miner_bloc_genesis(bloc_genesis)
        self.blockchain.ajouter_bloc(bloc_genesis)
        
        # Bloc temporaire
        self.transactions_bloc_actuel = []
        self.max_transactions_par_bloc = 10
        
        # État du minage
        self.minage_en_cours = False
        self.minage_threads = []
        self.minage_resultats = {}
        self.minage_lock = threading.Lock()
        self.bloc_gagnant = None


    
    def creer_transaction(self):
        """Crée une transaction aléatoire entre deux utilisateurs"""
        expediteur = random.choice(self.utilisateurs)
        destinataire = random.choice([u for u in self.utilisateurs if u != expediteur])
        
        # Montant aléatoire entre 0.1 et 5 BTC
        montant = round(random.uniform(0.1, 5.0), 2)
        
        # Vérifier que l'expéditeur a assez de fonds
        if expediteur.solde_btc < montant:
            return None
        
        # Créer et signer la transaction
        tx = Transaction(expediteur.adresse, destinataire.adresse, montant, expediteur.cle_publique_hex)
        expediteur.signe(tx)

        if self.blockchain.bloc_temporaire.ajouter_transaction(tx):
            self.blockchain.transactions_en_attente.append(tx)
        
        # Mettre à jour les soldes
        expediteur.solde_btc -= montant
        destinataire.solde_btc += montant
        
        return tx
    
    def lancer_minage_parallele(self):
        """Lance le minage en parallèle pour tous les mineurs"""
        self.minage_en_cours = True
        self.minage_resultats = {}
        self.minage_threads = []
        
        for i, mineur in enumerate(self.mineurs):
            thread = threading.Thread(
                target=self._miner_bloc_thread,
                args=(i, mineur)
            )
            thread.daemon = True
            thread.start()
            self.minage_threads.append(thread)
    
    def _miner_bloc_thread(self, mineur_id, mineur):
        # Créer la transaction de récompense
        transaction_recompense = Transaction(
            expediteur_adresse="RECOMPENSE",
            destinataire_adresse=mineur.adresse,
            montant=self.recompense_bloc,
            cle_publique_expediteur="SYSTEM"
        )
        
        # Calculer les frais
        frais_totaux = sum(0.0001 for _ in self.transactions_bloc_actuel)
        transaction_recompense.montant += frais_totaux
        
        # Créer le bloc
        toutes_transactions = [transaction_recompense] + self.transactions_bloc_actuel
        
        bloc = Bloc(
            index=len(self.blockchain.chaine),
            transactions=toutes_transactions,
            hash_precedent=self.blockchain.chaine[-1].hash,
            difficulte=self.difficulte
        )
        
        # Miner (Proof of Work)
        cible = '0' * self.difficulte
        tentatives = 0
        nonce = 0
        
        while self.minage_en_cours:
            header = bloc.header(nonce)
            hash = mineur.calculer_hash(header)
            
            if hash.startswith(cible):
                # Succès !
                bloc.hash = hash
                with self.minage_lock:
                    if self.minage_en_cours:
                        self.minage_en_cours = False
                        self.bloc_gagnant = bloc
                        self.minage_resultats['gagnant'] = mineur_id
                        self.minage_resultats['bloc'] = bloc
                        self.minage_resultats['tentatives'] = tentatives
                        mineur.solde_btc += transaction_recompense.montant
            else:
                tentatives += 1
                nonce += 1

                
    
    def run(self):
        cycles = 0
        while cycles < 1:
            if not self.minage_en_cours:
                if len(self.transactions_bloc_actuel) < self.max_transactions_par_bloc:
                    tx = self.creer_transaction()
                    if tx:
                        self.transactions_bloc_actuel.append(tx)
                else:
                    self.lancer_minage_parallele()
                    
                    while self.minage_en_cours:
                        time.sleep(0.1)

                    self.blockchain.ajouter_bloc(self.bloc_gagnant)
                    self.transactions_bloc_actuel = []
                    self.minage_resultats = {}
                    self.bloc_gagnant = None
                    cycles += 1
            time.sleep(1)

        # Sauvegarde de la blockchain
        self.blockchain.sauvegarder('blockchain.txt')
        
        # Arrêter tous les threads de minage
        self.minage_en_cours = False
        for thread in self.minage_threads:
            if thread.is_alive():
                thread.join(timeout=1.0)
        

if __name__ == "__main__":
    simulation = Simulation()
    simulation.run()

