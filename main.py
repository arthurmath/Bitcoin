from objects.utilisateur import Utilisateur
from objects.transaction import Transaction
from objects.blockchain import Blockchain
from objects.mineur import Mineur
from typing import List
import random
import threading
import time



class Simulation:
    def __init__(self):
        # Configuration
        self.difficulte = 5
        self.recompense_bloc = 3.125
        self.max_transactions_par_bloc = 10
        
        # Créer 10 utilisateurs
        self.noms = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Satoshi", "Henry", "Iris", "Jack"]
        self.utilisateurs = [Utilisateur(nom) for nom in self.noms]
        
        # Créer 4 mineurs
        self.mineurs = [
            Mineur("Mineur_Alpha"),
            Mineur("Mineur_Beta"),
            Mineur("Mineur_Gamma"),
            Mineur("Mineur_Delta")
        ]

        # Initialiser la blockchain
        self.blockchain = Blockchain()
        bloc_genesis = self.blockchain.creer_bloc_genesis(self.utilisateurs)
        bloc_genesis = self.mineurs[0].miner_bloc(bloc_genesis.transactions)
        self.blockchain.ajouter_bloc(bloc_genesis)
        self.afficher_soldes()
        
        # Liste des transactions en attente
        self.mempool: List[Transaction] = []
        
        # État du minage
        self.minage_en_cours = False
        self.minage_threads = []
        self.minage_lock = threading.Lock()
        self.bloc_gagnant = None


    def afficher_soldes(self):
        print(f"\n{'-'*60}\n💰 SOLDES :\n{'-'*60}")
        print("\nUtilisateurs:")
        for user in self.utilisateurs:
            print(f"  {user.nom}: {self.blockchain.calculer_solde(user.adresse):.2f} BTC")
        print("\nMineurs:")
        for mineur in self.mineurs:
            print(f"  {mineur.nom}: {self.blockchain.calculer_solde(mineur.adresse):.2f} BTC")
        print()


    
    def creer_transaction(self):
        """Crée une transaction aléatoire entre deux utilisateurs"""
        expediteur = random.choice(self.utilisateurs)
        destinataire = random.choice([u for u in self.utilisateurs if u != expediteur])
        
        # Montant aléatoire entre 0.1 et 5 BTC
        montant = round(random.uniform(0.1, 5.0), 2)
        
        # Vérifier que l'expéditeur a assez de fonds
        if self.blockchain.calculer_solde(expediteur.adresse) < montant:
            return None
        
        # Créer et signer la transaction
        tx = Transaction(expediteur, destinataire, montant, expediteur.cle_publique_hex)
        expediteur.signe(tx)

        self.mempool.append(tx)

        print(tx)
        return tx

    
    def lancer_minage(self):
        """Lance le minage en parallèle pour tous les mineurs"""
        print("\n⛏️ Minage en cours ")
        self.minage_en_cours = True
        self.minage_threads = []
        
        for i, mineur in enumerate(self.mineurs):
            thread = threading.Thread(
                target=self.minage_bloc,
                args=(i, mineur)
            )
            thread.daemon = True
            thread.start()
            self.minage_threads.append(thread)

    
    def minage_bloc(self, id, mineur):
        def check_active():
            """Fonction pour l'arrêt anticipé"""
            return self.minage_en_cours

        # Appel à la méthode du mineur
        bloc = mineur.miner_bloc(
            transactions_en_attente=self.mempool,
            hash_dernier_bloc=self.blockchain.chaine[-1].hash,
            index_bloc=len(self.blockchain.chaine),
            recompense=self.recompense_bloc,
            difficulte=self.difficulte,
            is_mining_active=check_active
        )
        
        # Si un bloc a été miné
        if bloc:
            with self.minage_lock:
                if self.minage_en_cours:
                    self.minage_en_cours = False
                    self.bloc_gagnant = bloc

                
    
    def run(self):
        cycles = 0
        while cycles < 1:
            if len(self.mempool) == 0:
                print(f"\n{'='*60}\n Bloc {cycles+1}\n{'='*60}\n")

            if len(self.mempool) < self.max_transactions_par_bloc:
                self.creer_transaction()
            else:
                self.lancer_minage()
                
                while self.minage_en_cours:
                    time.sleep(0.1)
                
                self.mineurs[0].valider_bloc(self.bloc_gagnant, self.blockchain.chaine[-1])
                self.blockchain.ajouter_bloc(self.bloc_gagnant)
                self.bloc_gagnant = None
                self.mempool = []
                cycles += 1
            time.sleep(0.1)

        self.afficher_soldes()
        self.blockchain.sauvegarder()
        
        # Arrêter tous les threads de minage
        self.minage_en_cours = False
        for thread in self.minage_threads:
            if thread.is_alive():
                thread.join(timeout=1.0)
        

if __name__ == "__main__":
    simulation = Simulation()
    simulation.run()



# TODO : mineur.miner(bloc) et non bloc.transactions
# Utiliser fonction blockchain.calculer_montant pour connaitre les soldes des utilisateurs