from objects.utilisateur import Utilisateur
from objects.transaction import Transaction
from objects.blockchain import Blockchain
from objects.mineur import Mineur
import random
import threading
import time



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
            Mineur("Mineur_Alpha"),
            Mineur("Mineur_Beta"),
            Mineur("Mineur_Gamma"),
            Mineur("Mineur_Delta")
        ]

        self.afficher_soldes()
        
        # Créer la blockchain
        self.blockchain = Blockchain(difficulte=2)
        bloc_genesis = self.blockchain.creer_bloc_genesis(self.utilisateurs)
        bloc_genesis = self.mineurs[0].miner_bloc(bloc_genesis.transactions)
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


    def afficher_soldes(self):
        print("\n", "-"*60)
        print("💰 SOLDES :")
        print("-"*60)
        print("\nUtilisateurs:")
        for user in self.utilisateurs:
            print(f"  {user.nom}: {user.solde_btc:.2f} BTC")
        print("\nMineurs:")
        for mineur in self.mineurs:
            print(f"  {mineur.nom}: {mineur.solde_btc:.2f} BTC")
        print()


    
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
        tx = Transaction(expediteur, destinataire, montant, expediteur.cle_publique_hex)
        expediteur.signe(tx)

        if self.blockchain.bloc_temporaire.ajouter_transaction(tx):
            self.blockchain.transactions_en_attente.append(tx)
        
        # Mettre à jour les soldes
        expediteur.solde_btc -= montant
        destinataire.solde_btc += montant

        print(tx)
        return tx
    
    def lancer_minage(self):
        """Lance le minage en parallèle pour tous les mineurs"""
        print("\n⛏️ Minage en cours ")
        self.minage_en_cours = True
        self.minage_resultats = {}
        self.minage_threads = []
        
        for i, mineur in enumerate(self.mineurs):
            thread = threading.Thread(
                target=self.miner_bloc,
                args=(i, mineur)
            )
            thread.daemon = True
            thread.start()
            self.minage_threads.append(thread)
    
    def miner_bloc(self, mineur_id, mineur):
        def check_active():
            """Fonction de vérification pour l'arrêt anticipé"""
            return self.minage_en_cours

        # Appel à la méthode du mineur
        bloc = mineur.miner_bloc(
            transactions_en_attente=list(self.transactions_bloc_actuel),
            hash_dernier_bloc=self.blockchain.chaine[-1].hash,
            index_bloc=len(self.blockchain.chaine),
            recompense=self.recompense_bloc,
            difficulte=self.difficulte,
            is_mining_active=check_active
        )
        
        # Si un bloc a été trouvé
        if bloc:
            with self.minage_lock:
                # On vérifie encore si le minage est toujours en cours 
                if self.minage_en_cours:
                    self.minage_en_cours = False
                    self.bloc_gagnant = bloc
                    self.minage_resultats['gagnant'] = mineur_id
                    self.minage_resultats['bloc'] = bloc
                    self.minage_resultats['tentatives'] = bloc.nonce
                    
                    # # Mise à jour du solde du gagnant
                    # mineur.solde_btc += bloc.transactions[0].montant

                
    
    def run(self):
        cycles = 0
        while cycles < 1:
            # print("\n","="*60,"\n","Bloc",cycles,"\n","="*60,"\n")
            if not self.minage_en_cours:
                if len(self.transactions_bloc_actuel) < self.max_transactions_par_bloc:
                    tx = self.creer_transaction()
                    if tx:
                        self.transactions_bloc_actuel.append(tx)
                else:
                    self.lancer_minage()
                    
                    while self.minage_en_cours:
                        time.sleep(0.1)
                    
                    self.mineurs[0].valider_bloc(self.bloc_gagnant, self.blockchain.chaine[-1])
                    self.blockchain.ajouter_bloc(self.bloc_gagnant)
                    self.transactions_bloc_actuel = []
                    self.minage_resultats = {}
                    self.bloc_gagnant = None
                    cycles += 1
            time.sleep(0.1)


        self.blockchain.sauvegarder()
        self.afficher_soldes()
        
        # Arrêter tous les threads de minage
        self.minage_en_cours = False
        for thread in self.minage_threads:
            if thread.is_alive():
                thread.join(timeout=1.0)
        

if __name__ == "__main__":
    simulation = Simulation()
    simulation.run()



# TODO : miner.miner(bloc) et non bloc.transactions
# reprendre main_determined