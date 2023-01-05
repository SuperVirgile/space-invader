import pygame
import os
import time
import random
pygame.font.init()

#Taille fenêtre
LARGEUR, HAUTEUR = 750, 750
FEN = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption('Space Shooter')

# Charger images :
# vaisseaux ennemis :
VAISSEAU_ROUGE = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
VAISSEAU_VERT = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
VAISSEAU_BLEU = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# vaisseau joueur :
VAISSEAU_JAUNE = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers ennemis :
LASER_ROUGE = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
LASER_VERT = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
LASER_BLEU = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))

# Laser joueur :
LASER_JAUNE = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# FOND :
FOND = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (LARGEUR, HAUTEUR))

class Laser:
	def __init__(self, x, y, img):
		self.x = x
		self.y = y
		self.img = img
		self.mask = pygame.mask.from_surface(self.img)

		#draw le laser via pygame
	def dessine(self, fenetre):
		fenetre.blit(self.img, (self.x, self.y))

		#gère le mouvement via la vélocité
	def mouvement(self, vel):
		self.y += vel

		#gère l'hors écran
	def hors_ecran(self, hauteur):
		return not(self.y <= hauteur and self.y >= 0)

		#Gère la collision du laser
	def collision(self, obj):
		return impact(obj, self)



class Vaisseau:
	#cooldown du tire 30 ms
	COOLDOWN = 30

	def __init__(self, x, y, vie = 100):
		self.x = x
		self.y = y
		self.vie = vie
		self.vaisseau_img = None
		self.laser_img = None
		self.lasers = []
		self.cooldown_compte = 0

	# set le cooldown, handle le tir des ennemis (la barre de vie décrémente)
	def deplacer_lasers(self, vel, obj):
		self.cooldown()
		for laser in self.lasers:
			laser.mouvement(vel)
			if laser.hors_ecran(HAUTEUR):
				self.lasers.remove(laser)
			elif laser.collision(obj):
				obj.vie -= 10
				self.lasers.remove(laser)

				#Set up un cooldonw pour être sûr de ne pas tirer trop vite
	def cooldown(self):
		if self.cooldown_compte >= self.COOLDOWN:
			self.cooldown_compte = 0
		elif self.cooldown_compte > 0:
			self.cooldown_compte += 1

			#dessine vaisseaux et lasers
	def dessine(self, fenetre):
		fenetre.blit(self.vaisseau_img, (self.x, self.y))
		for laser in self.lasers:
			laser.dessine(fenetre)

			#tire selon le CD
	def tirer(self):
		if self.cooldown_compte == 0:
			laser = Laser(self.x, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cooldown_compte = 1

			#définit la largeur
	def largeur(self):
		return self.vaisseau_img.get_width()

		#définit la hauteur
	def hauteur(self):
		return self.vaisseau_img.get_height()

class Joueur(Vaisseau):
	def __init__(self, x, y, vie = 100):
		super().__init__(x, y, vie)
		self.vaisseau_img = VAISSEAU_JAUNE
		self.laser_img = LASER_JAUNE
		self.mask = pygame.mask.from_surface(self.vaisseau_img)
		self.vie_max = vie

		#Laser pour le joueur -> obéit au CD -> Delete si hors écran + delete ennemis qu'il touche et delete le laser
	def deplacer_lasers(self, vel, objs):
		self.cooldown()
		for laser in self.lasers:
			laser.mouvement(vel)
			if laser.hors_ecran(HAUTEUR):
				self.lasers.remove(laser)
			else:
				for obj in objs:
					if laser.collision(obj):
						objs.remove(obj)
						if laser in self.lasers:
							self.lasers.remove(laser)

						#dessine la barre de vie
	def dessine(self, fenetre):
		super().dessine(fenetre)
		self.barre_de_vie(fenetre)

						#gère la barre de vie du joueur en dessinant deux rectangles superposés, l'un vert et l'autre rouge
	def barre_de_vie(self, fenetre):
		pygame.draw.rect(fenetre, (255, 0, 0), (self.x, self.y + self.vaisseau_img.get_height() + 10, self.vaisseau_img.get_width(), 10))
		pygame.draw.rect(fenetre, (0, 255, 0), (self.x, self.y + self.vaisseau_img.get_height() + 10, self.vaisseau_img.get_width() * (self.vie / self.vie_max), 10))


#Classe vaisseau ennemi qui reprend la super classe Vaisseau
class Ennemi(Vaisseau):
	#Les couleurs, on pioche aléatoirement quand ils spawnent
	COULEUR = {
				"rouge":(VAISSEAU_ROUGE, LASER_ROUGE),
				"vert":(VAISSEAU_VERT, LASER_VERT),
				"bleu":(VAISSEAU_BLEU, LASER_BLEU)
	}


	def __init__(self, x, y, couleur, vie = 100):
		super().__init__(x, y, vie)
		self.vaisseau_img, self.laser_img = self.COULEUR[couleur]
		self.mask = pygame.mask.from_surface(self.vaisseau_img) # mask pour que les pixels touchés soient ceux que l'on voit

		#gère déplacement des vaisseaux selon la vélocité
	def deplacement(self, vel):
		self.y += vel

		#gère le tire des ennemis, -20 pixel pour bien centrer les tirs
	def tirer(self):
		if self.cooldown_compte == 0:
			laser = Laser(self.x - 20, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cooldown_compte = 1

#Gère impact via la méthode overlap
def impact(obj1, obj2):
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
	# set-up des variables necessaire, vitesse, vies, niveau, etc.
	joue = True
	perdu = False
	compte_perdu = 0
	niveau = 0
	vies = 5
	main_font = pygame.font.SysFont("Didot", 50)
	font_perdu = pygame.font.SysFont("Didot", 60)

	ennemis = []
	duree_vague = 5
	vel_ennemi = 1

	vel_joueur = 5
	vel_laser = 4

	#Spawn joueur
	joueur = Joueur(300, 630)

	# SET la vitesse du jeu 60 ms
	FPS = 60
	temps = pygame.time.Clock()

	def redessiner_fenetre():
		FEN.blit(FOND, (0, 0))

		# dessinner text
		label_vies = main_font.render(f"Vies : {vies}", 1, (255, 0, 0))
		label_niveaux = main_font.render(f"Niveau : {niveau}", 1, (0, 0, 255))

		FEN.blit(label_vies, (10, 10))
		FEN.blit(label_niveaux, (LARGEUR - label_niveaux.get_width() - 10, 10))

		#Draw les ennemis
		for ennemi in ennemis:
			ennemi.dessine(FEN)

		joueur.dessine(FEN)

			# gère l'échec
		if perdu:
			label_perdu = font_perdu.render("TU AS PERDU !!", 1, (255, 255, 255))
			FEN.blit(label_perdu, (LARGEUR/2 - label_perdu.get_width()/2, 350))

		#rafraichir le display
		pygame.display.update()



	while joue:
		#Tick FPS à 60 ms
		temps.tick(FPS)
		redessiner_fenetre()

		#gère niveau / vies
		if vies <= 0 or joueur.vie <= 0:
			perdu = True
			compte_perdu += 1

		if perdu:
			if compte_perdu > FPS * 3:
				joue = False
			else:
				continue

				#spawn des ennemis
		if len(ennemis) == 0:
			niveau += 1
			duree_vague += 5
			for i in range(duree_vague):
				ennemi = Ennemi(random.randrange(50, LARGEUR - 100), random.randrange(-1500, -100), random.choice(['rouge', 'vert', 'bleu']))
				ennemis.append(ennemi)
		
				#arrêt du jeu
		for event in pygame.event.get():
			if event.type == pygame.QUIT:  
				quit()

				#Set-up les touches + empêche le vaisseau de se retrouver en dehors de la fenêtre
		touches = pygame.key.get_pressed()
		if touches[pygame.K_q] and joueur.x - vel_joueur > 0: # gauche
			joueur.x -= vel_joueur
		if touches[pygame.K_d] and joueur.x + vel_joueur + joueur.largeur() < LARGEUR: # droite
			joueur.x += vel_joueur
		if touches[pygame.K_z] and joueur.y - vel_joueur > 0: # haut
			joueur.y -= vel_joueur
		if touches[pygame.K_s] and joueur.y + vel_joueur + joueur.hauteur() + 15 < HAUTEUR: # bas
			joueur.y += vel_joueur

		if touches[pygame.K_SPACE]:
			joueur.tirer()

			#gère l'IA des ennemis
		for ennemi in ennemis[:]:
			ennemi.deplacement(vel_ennemi)
			ennemi.deplacer_lasers(vel_laser, joueur)

			#proba que les ennemis tirent 50% des fois chaque seconde
			if random.randrange(0, 2*60) == 1:
				ennemi.tirer()

			#gère la collision des ennemis avec le joueur:
			if impact(ennemi, joueur):
				joueur.vie -= 10
				ennemis.remove(ennemi)

			#gère le cas où les ennemis arrivent en bas de l'écran / elif pour ne pas avoir à vérifier s'ils arrivent en bas de l'écran alors que le joueur les a touchés
			elif ennemi.y + ennemi.hauteur() > HAUTEUR:
				vies -= 1
				ennemis.remove(ennemi)




				#vel négatif pour que le laser aille vers le haut
		joueur.deplacer_lasers(-vel_laser, ennemis)

#MENU
def menu_principal():
	font_titre = pygame.font.SysFont("Didot", 70)
	joue = True

	while joue:
		FEN.blit(FOND, (0, 0))

		label_titre = font_titre.render("Appuyez sur la souris...", 1, (255, 255, 255))
		
		FEN.blit(label_titre, (LARGEUR - label_titre.get_width()/2, 350))

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				joue = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				main()
	pygame.quit()


menu_principal()