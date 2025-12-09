import pygame
import math
import random
import time
import threading
from objects.utilisateur import Utilisateur
from objects.transaction import Transaction
from objects.blockchain import Blockchain
from objects.mineur import Mineur
from objects.bloc import Bloc


# Configuration de la fenêtre
LARGEUR = 1600
HAUTEUR = 900
FPS = 60

# Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
BLEU = (70, 130, 255)
VERT = (50, 205, 50)
ROUGE = (255, 69, 69)
JAUNE = (255, 215, 0)
GRIS = (128, 128, 128)
GRIS_CLAIR = (236, 240, 241)
ORANGE = (255, 165, 0)
VIOLET = (138, 43, 226)


class Animation:
    def __init__(self, start_pos, end_pos, montant, expediteur, destinataire):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.current_pos = list(start_pos)
        self.montant = montant
        self.expediteur = expediteur
        self.destinataire = destinataire
        self.progress = 0.0
        self.vitesse = 0.02
        self.terminee = False
    
    def update(self):
        if self.progress < 1.0:
            self.progress += self.vitesse
            self.current_pos[0] = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * self.progress
            self.current_pos[1] = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * self.progress
        else:
            self.terminee = True


class BlocAnimation:
    def __init__(self, start_pos, end_pos, bloc):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.current_pos = list(start_pos)
        self.bloc = bloc
        self.progress = 0.0
        self.vitesse = 0.015
        self.terminee = False
    
    def update(self):
        if self.progress < 1.0:
            self.progress += self.vitesse
            self.current_pos[0] = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * self.progress
            self.current_pos[1] = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * self.progress
        else:
            self.terminee = True


class VisualBlockchain:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Bitcoin Network Visualization")
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)
        
        # Configuration
        self.difficulte = 4
        self.recompense_bloc = 3.125
        self.nb_utilisateurs = 10
        self.nb_mineurs = 4
        self.transactions_par_bloc = 10
        
        # Positions
        self.centre_cercle = (400, 400)
        self.rayon_cercle = 250
        self.position_bloc_temp = (900, 200)
        self.position_mineurs_start = (900, 500)
        self.position_blockchain = (1350, 100)
        
        # Données
        self.utilisateurs = []
        self.mineurs = []
        self.blockchain = None
        self.bloc_temporaire_transactions = []
        self.animations_transactions = []
        self.animation_bloc = None
        self.mineur_gagnant = None
        self.temps_illumination = 0
        
        # États
        self.etat = "transactions"  # "transactions", "mining", "validation"
        self.temps_derniere_transaction = time.time()
        self.mining_en_cours = False
        self.mining_thread = None
        self.mining_result = None
        self.mining_lock = threading.Lock()
        
        # Initialisation du réseau
        self._initialiser_reseau()
    
    def _initialiser_reseau(self):
        """Initialise les utilisateurs, mineurs et blockchain"""
        # Créer les utilisateurs
        noms = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry", "Ivy", "Jack"]
        for nom in noms[:self.nb_utilisateurs]:
            user = Utilisateur(nom)
            self.utilisateurs.append(user)
        
        # Créer les mineurs
        for i in range(self.nb_mineurs):
            mineur = Mineur(f"Mineur_{i+1}", self.utilisateurs[i % len(self.utilisateurs)].adresse)
            self.mineurs.append(mineur)
        
        # Créer la blockchain
        self.blockchain = Blockchain(difficulte=self.difficulte)
        bloc_genesis = self.blockchain.creer_bloc_genesis(self.utilisateurs)
        bloc_genesis = self.mineurs[0].miner_bloc_genesis(bloc_genesis)
        self.blockchain.ajouter_bloc(bloc_genesis)
    
    def _calculer_position_utilisateur(self, index):
        """Calcule la position d'un utilisateur sur le cercle"""
        angle = (2 * math.pi * index / self.nb_utilisateurs) - math.pi / 2
        x = self.centre_cercle[0] + self.rayon_cercle * math.cos(angle)
        y = self.centre_cercle[1] + self.rayon_cercle * math.sin(angle)
        return (int(x), int(y))
    
    def _creer_transaction_aleatoire(self):
        """Crée une transaction aléatoire entre deux utilisateurs"""
        expediteur = random.choice(self.utilisateurs)
        destinataire = random.choice([u for u in self.utilisateurs if u != expediteur])
        
        # Montant aléatoire
        montant = round(random.uniform(0.1, 2.0), 2)
        
        # Vérifier que l'expéditeur a assez de BTC
        if expediteur.solde_btc < montant:
            return None
        
        # Créer la transaction
        tx = Transaction(expediteur.adresse, destinataire.adresse, montant, expediteur.cle_publique_hex)
        expediteur.signe(tx)
        
        # Mettre à jour les soldes
        expediteur.solde_btc -= montant
        destinataire.solde_btc += montant
        
        # Ajouter aux transactions temporaires
        self.bloc_temporaire_transactions.append(tx)
        
        # Créer l'animation
        idx_exp = self.utilisateurs.index(expediteur)
        idx_dest = self.utilisateurs.index(destinataire)
        pos_exp = self._calculer_position_utilisateur(idx_exp)
        pos_dest = self._calculer_position_utilisateur(idx_dest)
        
        animation = Animation(pos_exp, pos_dest, montant, expediteur.nom, destinataire.nom)
        self.animations_transactions.append(animation)
        
        return tx
    
    def _miner_bloc_concurrent(self):
        """Mine un bloc avec plusieurs mineurs en parallèle"""
        # Préparer les transactions
        transactions = self.bloc_temporaire_transactions.copy()
        hash_dernier = self.blockchain.chaine[-1].hash
        index_bloc = len(self.blockchain.chaine)
        
        # Thread pour chaque mineur
        threads = []
        resultats = [None] * len(self.mineurs)
        premier_gagnant = [None]  # Liste pour pouvoir modifier dans les threads
        lock = threading.Lock()
        stop_event = threading.Event()
        
        def mine_worker(mineur, idx):
            """Fonction de minage pour un thread"""
            # Créer la transaction coinbase
            transaction_recompense = Transaction(
                expediteur_adresse="RECOMPENSE",
                destinataire_adresse=mineur.adresse,
                montant=self.recompense_bloc,
                cle_publique_expediteur="SYSTEM"
            )
            
            frais_totaux = sum(0.0001 for _ in transactions)
            transaction_recompense.montant += frais_totaux
            toutes_transactions = [transaction_recompense] + transactions
            
            # Créer le bloc
            bloc = Bloc(
                index=index_bloc,
                transactions=toutes_transactions,
                hash_precedent=hash_dernier,
                difficulte=self.difficulte
            )
            
            # Miner avec un nonce aléatoire de départ pour diversifier
            bloc.nonce = random.randint(0, 100000)
            cible = '0' * self.difficulte
            
            while not stop_event.is_set():
                bloc.hash = bloc.calculer_hash()
                
                if bloc.hash.startswith(cible):
                    with lock:
                        if premier_gagnant[0] is None:
                            premier_gagnant[0] = (mineur, bloc)
                            stop_event.set()
                    break
                
                bloc.nonce += 1
            
            resultats[idx] = bloc
        
        # Lancer les threads
        for i, mineur in enumerate(self.mineurs):
            thread = threading.Thread(target=mine_worker, args=(mineur, i))
            thread.start()
            threads.append(thread)
        
        # Attendre que tous les threads se terminent
        for thread in threads:
            thread.join()
        
        # Récupérer le résultat
        if premier_gagnant[0]:
            mineur_gagnant, bloc_gagne = premier_gagnant[0]
            mineur_gagnant.solde_btc += bloc_gagne.transactions[0].montant
            return mineur_gagnant, bloc_gagne
        
        return None, None
    
    def _dessiner_utilisateurs(self):
        """Dessine les utilisateurs en cercle"""
        for i, user in enumerate(self.utilisateurs):
            pos = self._calculer_position_utilisateur(i)
            
            # Cercle de l'utilisateur
            pygame.draw.circle(self.screen, BLEU, pos, 40, 3)
            pygame.draw.circle(self.screen, BLANC, pos, 37)
            
            # Nom
            text = self.font_small.render(user.nom, True, NOIR)
            text_rect = text.get_rect(center=(pos[0], pos[1] - 60))
            self.screen.blit(text, text_rect)
            
            # Solde
            solde_text = f"{user.solde_btc:.2f} BTC"
            text = self.font_small.render(solde_text, True, VERT)
            text_rect = text.get_rect(center=(pos[0], pos[1] + 60))
            self.screen.blit(text, text_rect)
    
    def _dessiner_animations_transactions(self):
        """Dessine les animations de transactions"""
        for anim in self.animations_transactions[:]:
            if not anim.terminee:
                anim.update()
                
                # Dessiner la flèche
                pygame.draw.line(self.screen, ORANGE, anim.start_pos, anim.current_pos, 3)
                
                # Dessiner le montant
                text = self.font_small.render(f"{anim.montant:.2f}", True, ORANGE)
                text_rect = text.get_rect(center=(int(anim.current_pos[0]), int(anim.current_pos[1]) - 10))
                self.screen.blit(text, text_rect)
            else:
                self.animations_transactions.remove(anim)
    
    def _dessiner_bloc_temporaire(self):
        """Dessine le bloc temporaire avec les transactions en attente"""
        x, y = self.position_bloc_temp
        largeur, hauteur = 200, 300
        
        # Rectangle du bloc
        pygame.draw.rect(self.screen, GRIS_CLAIR, (x - largeur//2, y, largeur, hauteur), 0)
        pygame.draw.rect(self.screen, NOIR, (x - largeur//2, y, largeur, hauteur), 3)
        
        # Titre
        text = self.font_medium.render("Bloc Temporaire", True, NOIR)
        text_rect = text.get_rect(center=(x, y - 30))
        self.screen.blit(text, text_rect)
        
        # Nombre de transactions
        nb_tx = len(self.bloc_temporaire_transactions)
        text = self.font_medium.render(f"{nb_tx}/{self.transactions_par_bloc}", True, BLEU)
        text_rect = text.get_rect(center=(x, y + 50))
        self.screen.blit(text, text_rect)
        
        # Barre de progression
        progress_width = int((nb_tx / self.transactions_par_bloc) * (largeur - 40))
        pygame.draw.rect(self.screen, VERT, (x - largeur//2 + 20, y + 100, progress_width, 30))
        pygame.draw.rect(self.screen, NOIR, (x - largeur//2 + 20, y + 100, largeur - 40, 30), 2)
        
        # Liste des transactions
        y_offset = y + 150
        for i in range(min(5, nb_tx)):
            tx = self.bloc_temporaire_transactions[i]
            text = self.font_small.render(f"TX {i+1}: {tx.montant:.2f} BTC", True, NOIR)
            self.screen.blit(text, (x - 80, y_offset))
            y_offset += 25
    
    def _dessiner_mineurs(self):
        """Dessine les mineurs"""
        x_start, y_start = self.position_mineurs_start
        
        for i, mineur in enumerate(self.mineurs):
            x = x_start + (i % 2) * 150
            y = y_start + (i // 2) * 100
            
            # Couleur selon l'état
            if self.mineur_gagnant == mineur and time.time() - self.temps_illumination < 2:
                couleur = JAUNE
                rayon = 50
            elif self.mining_en_cours:
                couleur = ORANGE
                rayon = 45
            else:
                couleur = VIOLET
                rayon = 40
            
            # Cercle du mineur
            pygame.draw.circle(self.screen, couleur, (x, y), rayon, 0)
            pygame.draw.circle(self.screen, NOIR, (x, y), rayon, 3)
            
            # Nom
            text = self.font_small.render(mineur.nom, True, NOIR)
            text_rect = text.get_rect(center=(x, y - 70))
            self.screen.blit(text, text_rect)
            
            # Solde
            solde_text = f"{mineur.solde_btc:.2f} BTC"
            text = self.font_small.render(solde_text, True, VERT)
            text_rect = text.get_rect(center=(x, y + 70))
            self.screen.blit(text, text_rect)
    
    def _dessiner_blockchain(self):
        """Dessine la blockchain sur le côté"""
        x, y_start = self.position_blockchain
        
        # Titre
        text = self.font_medium.render("Blockchain", True, NOIR)
        text_rect = text.get_rect(center=(x, y_start - 40))
        self.screen.blit(text, text_rect)
        
        # Dessiner les derniers blocs (maximum 8)
        nb_blocs_afficher = min(8, len(self.blockchain.chaine))
        debut = max(0, len(self.blockchain.chaine) - nb_blocs_afficher)
        
        for i, bloc in enumerate(self.blockchain.chaine[debut:]):
            y = y_start + i * 90
            
            # Rectangle du bloc
            pygame.draw.rect(self.screen, VERT if i == nb_blocs_afficher - 1 else GRIS_CLAIR, (x - 100, y, 200, 70), 0)
            pygame.draw.rect(self.screen, NOIR, (x - 100, y, 200, 70), 3)
            
            # Numéro du bloc
            text = self.font_small.render(f"Bloc #{bloc.index}", True, NOIR)
            self.screen.blit(text, (x - 90, y + 10))
            
            # Hash (abrégé)
            hash_text = f"{bloc.hash[:10]}..."
            text = self.font_small.render(hash_text, True, BLEU)
            self.screen.blit(text, (x - 90, y + 35))
    
    def _dessiner_animation_bloc(self):
        """Dessine l'animation du bloc vers la blockchain"""
        if self.animation_bloc and not self.animation_bloc.terminee:
            self.animation_bloc.update()
            
            x, y = self.animation_bloc.current_pos
            
            # Rectangle du bloc animé
            pygame.draw.rect(self.screen, VERT, (x - 100, y - 35, 200, 70), 0)
            pygame.draw.rect(self.screen, NOIR, (x - 100, y - 35, 200, 70), 3)
            
            text = self.font_small.render(f"Bloc #{self.animation_bloc.bloc.index}", True, NOIR)
            self.screen.blit(text, (x - 90, y - 25))
    
    def _miner_bloc_thread(self):
        """Thread pour le minage"""
        mineur_gagnant, bloc_gagne = self._miner_bloc_concurrent()
        with self.mining_lock:
            self.mining_result = (mineur_gagnant, bloc_gagne)
    
    def update(self):
        """Met à jour l'état de la simulation"""
        temps_actuel = time.time()
        
        if self.etat == "transactions":
            # Créer une transaction toutes les 2 secondes
            if temps_actuel - self.temps_derniere_transaction > 2.0:
                tx = self._creer_transaction_aleatoire()
                self.temps_derniere_transaction = temps_actuel
                
                # Vérifier si on a assez de transactions pour miner
                if len(self.bloc_temporaire_transactions) >= self.transactions_par_bloc:
                    self.etat = "mining"
                    self.mining_en_cours = True
                    # Lancer le minage dans un thread
                    self.mining_thread = threading.Thread(target=self._miner_bloc_thread)
                    self.mining_thread.start()
        
        elif self.etat == "mining":
            # Attendre la fin du minage
            if self.mining_result is not None:
                mineur_gagnant, bloc_gagne = self.mining_result
                if bloc_gagne:
                    self.mineur_gagnant = mineur_gagnant
                    self.temps_illumination = temps_actuel
                    
                    # Ajouter le bloc à la blockchain
                    self.blockchain.ajouter_bloc(bloc_gagne)
                    
                    # Créer l'animation du bloc vers la blockchain
                    pos_mineurs = (975, 550)
                    pos_blockchain = (self.position_blockchain[0], self.position_blockchain[1] + (len(self.blockchain.chaine) - 1) * 90)
                    self.animation_bloc = BlocAnimation(pos_mineurs, pos_blockchain, bloc_gagne)
                    
                    # Réinitialiser
                    self.bloc_temporaire_transactions = []
                    self.mining_en_cours = False
                    self.mining_result = None
                    self.etat = "validation"
        
        elif self.etat == "validation":
            # Attendre un peu pour voir l'animation
            if temps_actuel - self.temps_illumination > 2.0 and (not self.animation_bloc or self.animation_bloc.terminee):
                self.etat = "transactions"
                self.mineur_gagnant = None
    
    def draw(self):
        """Dessine tous les éléments"""
        self.screen.fill(BLANC)
        
        # Dessiner les éléments
        self._dessiner_utilisateurs()
        self._dessiner_animations_transactions()
        self._dessiner_bloc_temporaire()
        self._dessiner_mineurs()
        self._dessiner_blockchain()
        self._dessiner_animation_bloc()
        
        # Afficher l'état
        etat_text = {
            "transactions": "💸 Transactions en cours...",
            "mining": "⛏️ Minage en cours ",
            "validation": f"✅ Bloc validé par {self.mineur_gagnant.nom if self.mineur_gagnant else ''} !"
        }
        text = self.font_large.render(etat_text[self.etat], True, ROUGE if self.etat == "mining" else VERT)
        text_rect = text.get_rect(center=(LARGEUR // 2, 50))
        self.screen.blit(text, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        """Boucle principale"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()


def main():
    visual = VisualBlockchain()
    visual.run()


if __name__ == "__main__":
    main()

