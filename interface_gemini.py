import pygame
import math
import random
import threading
import time
from objects.utilisateur import Utilisateur
from objects.transaction import Transaction
from objects.blockchain import Blockchain
from objects.mineur import Mineur


# Configuration de l'interface
LARGEUR, HAUTEUR = 1400, 800
FPS = 60
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
BLEU = (100, 149, 237)
VERT = (46, 204, 113)
ROUGE = (231, 76, 60)
JAUNE = (241, 196, 15)
ORANGE = (230, 126, 34)
VIOLET = (155, 89, 182)
GRIS = (149, 165, 166)
GRIS_CLAIR = (236, 240, 241)
GRIS_FONCE = (44, 62, 80)
VERT_CLAIR = (144, 238, 144)


class Animation:
    def __init__(self):
        self.transactions_animees = []
        self.bloc_en_cours_anime = None
        self.mineurs_actifs = False
        self.mineur_gagnant = None
        self.mineur_gagnant_timer = 0
        self.bloc_vers_blockchain = None
        self.bloc_vers_blockchain_timer = 0


class InterfaceVisuelle:
    def __init__(self):
        pygame.init()
        self.ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Réseau Bitcoin - Visualisation")
        self.horloge = pygame.time.Clock()
        self.font_petit = pygame.font.Font(None, 20)
        self.font_moyen = pygame.font.Font(None, 28)
        self.font_grand = pygame.font.Font(None, 36)
        self.font_titre = pygame.font.Font(None, 48)
        
        # Configuration
        self.difficulte = 5
        self.recompense_bloc = 3.125
        
        # Créer 10 utilisateurs
        self.noms = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Satoshi", "Henry", "Iris", "Jack"]
        self.utilisateurs = [Utilisateur(nom) for nom in self.noms]
        
        # Créer 4 mineurs
        self.mineurs = [
            Mineur("Mineur_Alpha", self.utilisateurs[0].adresse),
            Mineur("Mineur_Beta", self.utilisateurs[1].adresse),
            Mineur("Mineur_Gamma", self.utilisateurs[2].adresse),
            Mineur("Mineur_Delta", self.utilisateurs[3].adresse)
        ]
        
        # Créer la blockchain
        self.blockchain = Blockchain(difficulte=2)
        bloc_genesis = self.blockchain.creer_bloc_genesis(self.utilisateurs)
        bloc_genesis = self.mineurs[0].miner_bloc_genesis(bloc_genesis)
        self.blockchain.ajouter_bloc(bloc_genesis)
        
        # Positions des utilisateurs (cercle)
        self.positions_utilisateurs = self._calculer_positions_cercle(
            centre_x=340, centre_y=480, rayon=250, nombre=10
        )
        
        # Positions des mineurs
        a = -180
        b = -70
        self.positions_mineurs = [
            (860+a, 600+b), (1030+a, 600+b),
            (860+a, 740+b), (1030+a, 740+b)
        ]
        
        # Animation
        self.animation = Animation()
        
        # Timers
        self.dernier_temps_transaction = time.time()
        self.intervalle_transaction = 2.0
        
        # Bloc temporaire
        self.transactions_bloc_actuel = []
        self.max_transactions_par_bloc = 10
        
        # État du minage
        self.minage_en_cours = False
        self.minage_threads = []
        self.minage_resultats = {}
        self.minage_lock = threading.Lock()
    
    def _calculer_positions_cercle(self, centre_x, centre_y, rayon, nombre):
        """Calcule les positions pour disposer les éléments en cercle"""
        positions = []
        for i in range(nombre):
            angle = (i * 2 * math.pi / nombre) - math.pi / 2
            x = centre_x + rayon * math.cos(angle)
            y = centre_y + rayon * math.sin(angle)
            positions.append((int(x), int(y)))
        return positions
    
    def creer_transaction_aleatoire(self):
        """Crée une transaction aléatoire entre deux utilisateurs"""
        expediteur = random.choice(self.utilisateurs)
        destinataire = random.choice([u for u in self.utilisateurs if u != expediteur])
        
        # Montant aléatoire entre 0.1 et 5 BTC
        montant = round(random.uniform(0.1, 5.0), 2)
        
        # Vérifier que l'expéditeur a assez de fonds
        if expediteur.solde_btc < montant:
            montant = round(expediteur.solde_btc * 0.5, 2)
            if montant < 0.1:
                return None
        
        # Créer et signer la transaction
        tx = Transaction(expediteur.adresse, destinataire.adresse, montant, expediteur.cle_publique_hex)
        expediteur.signe(tx)
        
        # Mettre à jour les soldes
        expediteur.solde_btc -= montant
        destinataire.solde_btc += montant
        
        # Ajouter l'animation
        idx_exp = self.utilisateurs.index(expediteur)
        idx_dest = self.utilisateurs.index(destinataire)
        self.animation.transactions_animees.append({
            'tx': tx,
            'de': self.positions_utilisateurs[idx_exp],
            'vers': self.positions_utilisateurs[idx_dest],
            'progression': 0.0,
            'expediteur_nom': expediteur.nom,
            'destinataire_nom': destinataire.nom
        })
        
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
        """Thread de minage pour un mineur"""
        # Créer la transaction de récompense
        transaction_recompense = Transaction(
            expediteur_adresse="COINBASE",
            destinataire_adresse=mineur.adresse,
            montant=self.recompense_bloc,
            cle_publique_expediteur="SYSTEM"
        )
        
        # Calculer les frais
        frais_totaux = sum(0.0001 for _ in self.transactions_bloc_actuel)
        transaction_recompense.montant += frais_totaux
        
        # Créer le bloc
        from objects.bloc import Bloc
        toutes_transactions = [transaction_recompense] + self.transactions_bloc_actuel
        
        bloc = Bloc(
            index=len(self.blockchain.chaine),
            transactions=toutes_transactions,
            hash_precedent=self.blockchain.chaine[-1].hash,
            difficulte=self.difficulte
        )

        print("DIFFICULTEEEEEEEEEE : ", self.difficulte)
        
        # Miner (Proof of Work)
        cible = '0' * self.difficulte
        tentatives = 0
        
        while self.minage_en_cours:
            bloc.hash = bloc.calculer_hash()
            tentatives += 1
            
            if bloc.hash.startswith(cible):
                # Succès !
                with self.minage_lock:
                    if self.minage_en_cours:
                        self.minage_en_cours = False
                        self.minage_resultats['gagnant'] = mineur_id
                        self.minage_resultats['bloc'] = bloc
                        self.minage_resultats['tentatives'] = tentatives
                        mineur.solde_btc += transaction_recompense.montant
                        
                        # Déclencher l'animation du mineur gagnant
                        self.animation.mineur_gagnant = mineur_id
                        self.animation.mineur_gagnant_timer = time.time()
                break
            
            bloc.nonce += 1
    
    def dessiner_utilisateur(self, position, utilisateur, index):
        """Dessine un utilisateur"""
        x, y = position
        rayon = 40
        
        # Cercle de l'utilisateur
        pygame.draw.circle(self.ecran, BLEU, (x, y), rayon)
        pygame.draw.circle(self.ecran, NOIR, (x, y), rayon, 2)
        
        # Nom
        texte_nom = self.font_moyen.render(utilisateur.nom, True, BLANC)
        rect_nom = texte_nom.get_rect(center=(x, y - 5))
        self.ecran.blit(texte_nom, rect_nom)
        
        # Solde
        texte_solde = self.font_petit.render(f"{utilisateur.solde_btc:.1f} BTC", True, BLANC)
        rect_solde = texte_solde.get_rect(center=(x, y + 15))
        self.ecran.blit(texte_solde, rect_solde)
    
    def dessiner_transaction_animee(self, anim_tx):
        """Dessine une transaction animée (flèche)"""
        x1, y1 = anim_tx['de']
        x2, y2 = anim_tx['vers']
        prog = anim_tx['progression']
        
        # Position actuelle
        x_actuel = x1 + (x2 - x1) * prog
        y_actuel = y1 + (y2 - y1) * prog
        
        # Dessiner la ligne
        pygame.draw.line(self.ecran, VERT, (x1, y1), (x_actuel, y_actuel), 3)
        
        # Dessiner un point animé
        pygame.draw.circle(self.ecran, JAUNE, (int(x_actuel), int(y_actuel)), 8)
        
        # Afficher le montant
        if prog > 0.3 and prog < 0.7:
            montant_texte = f"{anim_tx['tx'].montant:.2f} BTC"
            texte = self.font_petit.render(montant_texte, True, VERT)
            rect = texte.get_rect(center=(int(x_actuel), int(y_actuel) - 20))
            
            # Fond blanc pour lisibilité
            fond = pygame.Surface((rect.width + 10, rect.height + 4))
            fond.fill(BLANC)
            fond.set_alpha(200)
            self.ecran.blit(fond, (rect.x - 5, rect.y - 2))
            self.ecran.blit(texte, rect)
    
    def dessiner_bloc_temporaire(self):
        """Dessine le bloc en cours de construction"""
        x, y = 700, 120 
        largeur, hauteur = 280, 380
        
        # Rectangle du bloc
        pygame.draw.rect(self.ecran, GRIS_CLAIR, (x, y, largeur, hauteur))
        pygame.draw.rect(self.ecran, NOIR, (x, y, largeur, hauteur), 3)
        
        # Titre
        titre = self.font_moyen.render("Bloc en cours", True, NOIR)
        rect_titre = titre.get_rect(center=(x + largeur // 2, y + 25))
        self.ecran.blit(titre, rect_titre)
        
        # Compteur de transactions
        compteur = self.font_moyen.render(
            f"{len(self.transactions_bloc_actuel)}/{self.max_transactions_par_bloc}",
            True, ORANGE
        )
        rect_compteur = compteur.get_rect(center=(x + largeur // 2, y + 55))
        self.ecran.blit(compteur, rect_compteur)
        
        # Barre de progression
        barre_x = x + 20
        barre_y = y + 80
        barre_largeur = largeur - 40
        barre_hauteur = 30
        
        pygame.draw.rect(self.ecran, GRIS, (barre_x, barre_y, barre_largeur, barre_hauteur))
        
        if self.max_transactions_par_bloc > 0:
            progression = len(self.transactions_bloc_actuel) / self.max_transactions_par_bloc
            pygame.draw.rect(
                self.ecran, VERT,
                (barre_x, barre_y, int(barre_largeur * progression), barre_hauteur)
            )
        
        pygame.draw.rect(self.ecran, NOIR, (barre_x, barre_y, barre_largeur, barre_hauteur), 2)
        
        # Liste des transactions
        y_tx = y + 130
        for i, tx in enumerate(self.transactions_bloc_actuel[-8:]):
            for util in self.utilisateurs:
                if util.adresse == tx.destinataire:
                    destinataire = util.nom
                if util.adresse == tx.expediteur:
                    expediteur = util.nom
            texte_tx = self.font_petit.render(f"{tx.montant:.2f} BTC : {expediteur} -> {destinataire}", True, NOIR)
            self.ecran.blit(texte_tx, (x + 20, y_tx + i * 25))
    
    def dessiner_mineurs(self):
        """Dessine les mineurs"""
        for i, (mineur, (x, y)) in enumerate(zip(self.mineurs, self.positions_mineurs)):
            largeur, hauteur = 150, 120
            
            # Couleur en fonction de l'état
            if self.animation.mineur_gagnant == i and (time.time() - self.animation.mineur_gagnant_timer) < 2.0:
                # Animation de victoire
                couleur_fond = GRIS_FONCE
                couleur_bord = JAUNE
                couleur_texte = JAUNE
                epaisseur = 5
                
                # Effet de pulsation
                pulse = int(10 * abs(math.sin((time.time() - self.animation.mineur_gagnant_timer) * 8)))
                pygame.draw.rect(self.ecran, JAUNE, 
                               (x - pulse, y - pulse, largeur + 2*pulse, hauteur + 2*pulse), 2)
            elif self.minage_en_cours:
                couleur_fond = GRIS_FONCE
                couleur_bord = JAUNE
                couleur_texte = JAUNE
                epaisseur = 3
            else:
                couleur_fond = GRIS_FONCE
                couleur_bord = GRIS
                couleur_texte = GRIS
                epaisseur = 2
            
            # Rectangle du mineur
            pygame.draw.rect(self.ecran, couleur_fond, (x, y, largeur, hauteur))
            pygame.draw.rect(self.ecran, couleur_bord, (x, y, largeur, hauteur), epaisseur)
            
            # Nom
            nom_texte = self.font_petit.render(mineur.nom.split('_')[1], True, couleur_texte)
            rect_nom = nom_texte.get_rect(center=(x + largeur // 2, y + 25))
            self.ecran.blit(nom_texte, rect_nom)
            
            # Solde
            solde_texte = self.font_petit.render(f"{mineur.solde_btc:.2f} BTC", True, couleur_texte)
            rect_solde = solde_texte.get_rect(center=(x + largeur // 2, y + 50))
            self.ecran.blit(solde_texte, rect_solde)
            
            # État
            if self.minage_en_cours:
                etat_texte = self.font_petit.render("Mining...", True, ORANGE)
            else:
                etat_texte = self.font_petit.render("Minage off", True, GRIS)
            rect_etat = etat_texte.get_rect(center=(x + largeur // 2, y + 75))
            self.ecran.blit(etat_texte, rect_etat)
            
            # Victoire
            if self.animation.mineur_gagnant == i and (time.time() - self.animation.mineur_gagnant_timer) < 2.0:
                victoire = self.font_moyen.render("GAGNANT!", True, JAUNE)
                rect_victoire = victoire.get_rect(center=(x + largeur // 2, y + 100))
                self.ecran.blit(victoire, rect_victoire)
    
    def dessiner_animation_bloc_vers_chain(self):
        """Dessine l'animation du bloc se déplaçant vers la blockchain"""
        anim = self.animation.bloc_vers_blockchain
        if not anim:
            return
            
        bloc = anim['bloc']
        start = anim['start']
        end = anim['end']
        prog = anim['progression']
        
        # Interpolation
        # Utiliser une courbe de transition smooth (ease-in-out)
        t = prog
        ease = t * t * (3 - 2 * t)
        
        current_x = start[0] + (end[0] - start[0]) * ease
        current_y = start[1] + (end[1] - start[1]) * ease
        
        largeur_bloc = 330
        hauteur_bloc = 70
        
        # Dessiner le bloc
        rect = (current_x, current_y, largeur_bloc, hauteur_bloc)
        pygame.draw.rect(self.ecran, VERT_CLAIR, rect)
        pygame.draw.rect(self.ecran, NOIR, rect, 2)
        
        # Texte
        texte_num = self.font_moyen.render(f"Bloc #{bloc.index}", True, NOIR)
        self.ecran.blit(texte_num, (current_x + 10, current_y + 10))
        
        texte_hash = self.font_petit.render(f"Hash: {bloc.hash[:24]}...", True, NOIR)
        self.ecran.blit(texte_hash, (current_x + 10, current_y + 35))
        
        texte_tx = self.font_petit.render(f"{len(bloc.transactions)} TX", True, ORANGE)
        self.ecran.blit(texte_tx, (current_x + largeur_bloc - 80, current_y + 20))
    
    def dessiner_blockchain(self):
        """Dessine la blockchain"""
        x_start = 1050  # Décalage ajusté pour centrer les blocs plus petits (1000 -> 1050)
        y_start = 120   # Abaissé (80 -> 120)
        largeur_bloc = 330  # Réduit (380 -> 300)
        hauteur_bloc = 70   # Réduit (80 -> 70)
        
        # Titre
        titre = self.font_grand.render("Blockchain", True, NOIR)
        self.ecran.blit(titre, (x_start + 80, y_start - 50))  # Titre ajusté
        
        # Afficher les derniers blocs (plus nombreux car on a toute la hauteur)
        nb_blocs_visibles = (HAUTEUR - y_start - 20) // (hauteur_bloc + 10)
        blocs_a_afficher = self.blockchain.chaine[-nb_blocs_visibles:]
        
        for i, bloc in enumerate(blocs_a_afficher):
            y = y_start + i * (hauteur_bloc + 10)
            
            # Rectangle du bloc
            if i == len(blocs_a_afficher) - 1:
                couleur = VERT_CLAIR
            else:
                couleur = GRIS_CLAIR
            
            pygame.draw.rect(self.ecran, couleur, (x_start, y, largeur_bloc, hauteur_bloc))
            pygame.draw.rect(self.ecran, NOIR, (x_start, y, largeur_bloc, hauteur_bloc), 2)
            
            # Numéro du bloc
            texte_num = self.font_moyen.render(f"Bloc #{bloc.index}", True, NOIR)
            self.ecran.blit(texte_num, (x_start + 10, y + 10))
            
            # Hash (tronqué)
            texte_hash = self.font_petit.render(f"Hash: {bloc.hash[:24]}...", True, NOIR)
            self.ecran.blit(texte_hash, (x_start + 10, y + 35))
            
            # Nombre de transactions
            texte_tx = self.font_petit.render(
                f"{len(bloc.transactions)} TX", True, ORANGE
            )
            self.ecran.blit(texte_tx, (x_start + largeur_bloc - 80, y + 20))
            
            # Timestamp
            temps = time.strftime('%H:%M:%S', time.localtime(bloc.timestamp))
            texte_temps = self.font_petit.render(temps, True, NOIR)
            self.ecran.blit(texte_temps, (x_start + 10, y + 55))
    
    def dessiner_titre_et_stats(self):
        """Dessine le titre et les statistiques"""
        # Titre principal
        titre = self.font_titre.render("Simulation du Réseau Bitcoin", True, NOIR)
        self.ecran.blit(titre, (LARGEUR // 2 - titre.get_width() // 2, 40))
        
        # Statistiques
        stats = [
            f"Blocs: {len(self.blockchain.chaine)}",
            f"Difficulté: {self.difficulte}",
            f"Récompense: {self.recompense_bloc} BTC"
        ]
        
        y_stat = 80
        for stat in stats:
            texte = self.font_moyen.render(stat, True, NOIR)
            self.ecran.blit(texte, (20, y_stat))
            y_stat += 35
    
    def mettre_a_jour(self, dt):
        """Met à jour l'état de la simulation"""
        temps_actuel = time.time()
        
        # Créer des transactions toutes les 2 secondes
        if not self.minage_en_cours and temps_actuel - self.dernier_temps_transaction >= self.intervalle_transaction:
            if len(self.transactions_bloc_actuel) < self.max_transactions_par_bloc:
                tx = self.creer_transaction_aleatoire()
                if tx:
                    self.transactions_bloc_actuel.append(tx)
                    self.dernier_temps_transaction = temps_actuel
                    
                    # Si le bloc est plein, lancer le minage
                    if len(self.transactions_bloc_actuel) >= self.max_transactions_par_bloc:
                        self.lancer_minage_parallele()
        
        # Mettre à jour les animations de transactions
        for anim_tx in self.animation.transactions_animees[:]:
            anim_tx['progression'] += dt * 0.5
            if anim_tx['progression'] >= 1.0:
                self.animation.transactions_animees.remove(anim_tx)
        
        # Gérer l'animation du bloc vers la blockchain
        if self.animation.bloc_vers_blockchain:
            self.animation.bloc_vers_blockchain['progression'] += dt * 0.8
            if self.animation.bloc_vers_blockchain['progression'] >= 1.0:
                # Animation terminée : ajouter le bloc et réinitialiser
                bloc = self.animation.bloc_vers_blockchain['bloc']
                self.blockchain.ajouter_bloc(bloc)
                
                self.animation.bloc_vers_blockchain = None
                self.transactions_bloc_actuel = []
                self.minage_resultats = {}
                self.animation.mineur_gagnant = None
        
        # Vérifier si le minage est terminé
        elif not self.minage_en_cours and self.minage_resultats and 'bloc' in self.minage_resultats:
            # Attendre un peu pour montrer l'animation du gagnant
            if temps_actuel - self.animation.mineur_gagnant_timer > 2.0:
                # Initialiser l'animation du bloc vers la blockchain
                winner_idx = self.minage_resultats['gagnant']
                start_pos = self.positions_mineurs[winner_idx]
                
                # Calculer la position cible dans la blockchain
                x_start = 1050
                y_start = 120
                hauteur_bloc = 70
                espacement = 10
                
                nb_blocs_visibles = (HAUTEUR - y_start - 20) // (hauteur_bloc + espacement)
                
                # Index visuel cible
                if len(self.blockchain.chaine) < nb_blocs_visibles:
                    target_idx = len(self.blockchain.chaine)
                else:
                    target_idx = nb_blocs_visibles - 1
                
                target_y = y_start + target_idx * (hauteur_bloc + espacement)
                end_pos = (x_start, target_y)
                
                self.animation.bloc_vers_blockchain = {
                    'bloc': self.minage_resultats['bloc'],
                    'start': start_pos,
                    'end': end_pos,
                    'progression': 0.0
                }
    
    def dessiner(self):
        """Dessine tous les éléments"""
        self.ecran.fill(BLANC)
        
        # Titre et stats
        self.dessiner_titre_et_stats()
        
        # Utilisateurs en cercle
        for i, (utilisateur, position) in enumerate(zip(self.utilisateurs, self.positions_utilisateurs)):
            self.dessiner_utilisateur(position, utilisateur, i)
        
        # Transactions animées
        for anim_tx in self.animation.transactions_animees:
            self.dessiner_transaction_animee(anim_tx)
        
        # Bloc temporaire
        self.dessiner_bloc_temporaire()
        
        # Mineurs
        self.dessiner_mineurs()
        
        # Blockchain
        self.dessiner_blockchain()
        
        # Animation bloc vers blockchain
        self.dessiner_animation_bloc_vers_chain()
        
        pygame.display.flip()
    
    def run(self):
        """Boucle principale"""
        running = True
        
        while running:
            dt = self.horloge.tick(FPS) / 1000.0
            
            for evenement in pygame.event.get():
                if evenement.type == pygame.QUIT:
                    running = False
                elif evenement.type == pygame.KEYDOWN:
                    if evenement.key == pygame.K_ESCAPE:
                        running = False
            
            self.mettre_a_jour(dt)
            self.dessiner()
        
        # Arrêter tous les threads de minage
        self.minage_en_cours = False
        for thread in self.minage_threads:
            if thread.is_alive():
                thread.join(timeout=1.0)
        
        pygame.quit()


def main():
    interface = InterfaceVisuelle()
    interface.run()


if __name__ == "__main__":
    main()

