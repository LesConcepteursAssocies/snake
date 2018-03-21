#!/usr/bin/env python3
# -*- coding: utf8 -*-
#
# Un snake avec Tkinter
#
# 01/2018 PG (pguillaumaud@april.org)
# (inspire de https://www.youtube.com/watch?v=JE3q1vUSbOY
#  et de http://rembound.com/articles/creating-a-snake-game-tutorial-with-html5)
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA
#
import sys, os
import pickle
import random
import time
import tkinter as TK

# --------------------------------------------------------------------------------
# Valeurs par defaut du canvas
screenWidth, screenHeight = (1024, 864)

# taille des cellules (en px)
CELL_SIZE  = 16

# lignes, colonnes
MAXLI = int(screenHeight/CELL_SIZE)
MAXCO = int(screenWidth/CELL_SIZE)

# les vecteurs de direction
vDir = { "Down": (0, +1), "Up": (0, -1), "Left": (-1, 0), "Right": (+1, 0) }

# position du bonus
Bonus = (4, 4)
# les divers bonus
# 0: image, 1: score, 2: longueur ajoutée
tBonus = { 0: ('models/pomme.png',5,1), 1: ('models/banane.png',10,2), 2: ('models/cerise.png',15,3), 3: ('models/fraise.png',20,4) }
# l'image du bonus
imgBonus = None
# le score du bonus
Bonussco = 0
# la longueur ajoutée par le bonus
Bonuslen = 1

# les murs
MAXWALL = 4
# on met chaque mur dans un quadrant de l'écran
# haut gauche, haut droit, bas droite, bas gauche
wQuad = [ [(5,5),(MAXCO//2,MAXLI//2)], [((MAXCO//2)+1,5), (MAXCO-5,(MAXLI//2)+1)],
         [((MAXCO//2)+1,(MAXLI//2)+1), (MAXCO-5,MAXLI-5)], [(5,(MAXLI//2)+1), ((MAXCO//2)+1,MAXLI-5)] ]
# tableau des positions
Walls   = []
# l'image
imgWall = None

# flag en jeu ou pas
Running  = False
GameOver = False

# le score
Score       = 0
label_score = 'Score: {0:6d}'
# le highscore
HighScore   = 0

# la tempo
Tempo = 100

# le nom du programme (sans l'extension)
name_app = os.path.splitext(os.path.basename(sys.argv[0]))[0]
# le répertoire
path_app = os.path.dirname(sys.argv[0])

# --------------------------------------------------------------------------------
# Fin du programme
def OnExit():
    SaveHighScore()
    fen.destroy()

# --------------------------------------------------------------------------------
# Sauvegarde du highscore
def SaveHighScore():
    global Score, HighScore

    if Score > HighScore:
        filename = path_app+'/'+name_app+'-highscore.bin'
        try:
            fh = open(filename, 'wb')
            pickle.dump(Score, fh)
            fh.close()
        except:
            pass

# --------------------------------------------------------------------------------
# Récupération du highscore
def ReadHighScore():
    global HighScore

    filename = path_app+'/'+name_app+'-highscore.bin'
    try:
        fh = open(filename, 'rb')
        HighScore = pickle.load(fh)
        fh.close()
    except:
        pass

# --------------------------------------------------------------------------------
# démarre le jeu
def Go():
    global Running
    Running = True
    GameLoop()

# --------------------------------------------------------------------------------
# arrète l'animation
def Stop():
    global Running
    Running = False

# --------------------------------------------------------------------------------
# Le serpent
class Snake():
    def __init__(self):
        global Running

        # le corps, démarre au centre par défaut
        self.body      = [(MAXCO//2, MAXLI//2)]
        # la longueur (4 par défaut)
        self.len       = 4
        # la direction
        self.direction = "Right"
        self.orientation = vDir[self.direction]
        # les images de la tête
        self.sprHead  = { "Down": "models/snake_head_b.png", "Up": "models/snake_head_h.png", "Left": "models/snake_head_g.png", "Right": "models/snake_head_d.png" }
        self.imgHead  = TK.PhotoImage(file=self.sprHead[self.direction])
        # les images de la queue
        self.sprQueue = { "Down": "models/snake_queue_b.png", "Up": "models/snake_queue_h.png", "Left": "models/snake_queue_g.png", "Right": "models/snake_queue_d.png" }
        self.imgQueue = TK.PhotoImage(file=self.sprQueue["Left"])
        # les images du reste du corps
        self.sprBody  = { "Ve": "models/snake_body_v.png", "Hz": "models/snake_body_h.png",
                          "BDr": "models/snake_body_bd.png", "BGa": "models/snake_body_bg.png", "HDr": "models/snake_body_hd.png", "HGa": "models/snake_body_hg.png" }
        self.imgBody  = [TK.PhotoImage(file=self.sprBody["Hz"])]
        # on place le serpent à sa taille initiale
        Running = True
        while len(self.body) < self.len:
            self.update()
        Running = False

    # changement de direction
    def changeDirTo(self, dir):
        if dir == "Right" and not self.direction == "Left":
            self.direction = "Right"
        if dir == "Left" and not self.direction == "Right":
            self.direction = "Left"
        if dir == "Up" and not self.direction == "Down":
            self.direction = "Up"
        if dir == "Down" and not self.direction == "Up":
            self.direction = "Down"
        self.orientation = vDir[self.direction]
        self.imgHead     = TK.PhotoImage(file=self.sprHead[self.direction])

    # affichage
    def draw(self):
        # la queue en position 0
        part = self.body[0]
        x = part[0]*CELL_SIZE
        y = part[1]*CELL_SIZE
        if len(self.body) > 1:
            # on détermine sa direction avec le segment suivant
            nseg = self.body[1]
            nx   = nseg[0]*CELL_SIZE
            ny   = nseg[1]*CELL_SIZE
            if ny < y:
                # Haut
                self.imgQueue = TK.PhotoImage(file=self.sprQueue["Down"])
            elif nx > x:
                # Droite
                self.imgQueue = TK.PhotoImage(file=self.sprQueue["Left"])
            elif ny > y:
                # Bas
                self.imgQueue = TK.PhotoImage(file=self.sprQueue["Up"])
            elif nx < x:
                # Gauche
                self.imgQueue = TK.PhotoImage(file=self.sprQueue["Right"])
        canvas.create_image(x, y, image=self.imgQueue, anchor = "nw")

        # le corps
        for i in range(1, len(self.body)-1):
            part = self.body[i]
            x = part[0]*CELL_SIZE
            y = part[1]*CELL_SIZE
            # détermination de l'image à utiliser
            pseg = self.body[i-1]
            nseg = self.body[i+1]

            px = pseg[0]*CELL_SIZE
            py = pseg[1]*CELL_SIZE
            nx = nseg[0]*CELL_SIZE
            ny = nseg[1]*CELL_SIZE
            if (px < x and nx > x or nx < x and px > x):
                # Horizontal
                self.imgBody[i-1] = TK.PhotoImage(file=self.sprBody["Hz"])
            elif (px < x and ny > y or nx < x and py > y):
                # Angle Haut Droit
                self.imgBody[i-1] = TK.PhotoImage(file=self.sprBody["HDr"])
            elif (py < y and ny > y or ny < y and py > y):
                # Vertical
                self.imgBody[i-1] = TK.PhotoImage(file=self.sprBody["Ve"])
            elif (py < y and nx < x or ny < y and px < x):
                # Angle Bas Droit
                self.imgBody[i-1] = TK.PhotoImage(file=self.sprBody["BDr"])
            elif (px > x and ny < y or nx > x and py < y):
                # Angle Bas Gauche
                self.imgBody[i-1] = TK.PhotoImage(file=self.sprBody["BGa"])
            elif (py > y and nx > x or ny > y and px > x):
                # Angle Haut Gauche
                self.imgBody[i-1] = TK.PhotoImage(file=self.sprBody["HGa"])

            canvas.create_image(x, y, image=self.imgBody[i-1], anchor = "nw")

        # la tête, à la fin
        part = self.body[len(self.body)-1]
        x = part[0]*CELL_SIZE
        y = part[1]*CELL_SIZE
        canvas.create_image(x, y, image=self.imgHead, anchor = "nw")

    # les déplacements
    def update(self):
        global Running, GameOver, Score

        x, y = self.body[-1]
        x += self.orientation[0]
        y += self.orientation[1]

        # les collisions/dépassements
        if not 0 <= x < MAXCO:
            if x <= 0:
                x = MAXCO-1
            elif x >= MAXCO:
                x = 0
        if not 0 <= y < MAXLI:
            if y <= 0:
                y = MAXLI-1
            elif y >= MAXLI:
                y = 0

        new_part = (x, y)
        # collision avec soi-même
        if new_part in self.body:
            Running  = False
            GameOver = True
            info.configure(text = 'Collision avec snake!')

        # collision avec un mur
        if new_part in Walls:
            Running  = False
            GameOver = True
            info.configure(text = 'Aïe, un mur!')

        if Running and not GameOver:
            self.body.append(new_part)

            # bonus mangé ?
            if new_part == Bonus:
                # on grandit
                self.len += Bonuslen
                Score    += Bonussco
                NewBonus()

            # on vérifie la longueur
            if len(self.body) > self.len:
                del self.body[0]
            # on ajuste la taille du reste du corps
            while len(self.imgBody) > (self.len-2):
                del self.imgBody[0]
            while len(self.imgBody) < (self.len-2):
                self.imgBody.append(None)

# --------------------------------------------------------------------------------
# création du bonus
def NewBonus():
    global Bonus, imgBonus, Bonussco, Bonuslen

    n = 0
    found = False
    while n < 5:
        # la position
        x = random.randint(0, MAXCO-1)
        y = random.randint(0, MAXLI-1)
        # on vérifie que la nouvelle pos
        # ne soit pas déjà occupée
        if ((x, y) not in snake.body) and ((x, y) not in Walls):
            found = True
            break
        n += 1

    if found:
        Bonus = (x, y)
        # on choisi un bonus
        idx = random.randint(0,3)
        imgBonus = TK.PhotoImage(file=tBonus[idx][0])
        Bonussco = tBonus[idx][1]
        Bonuslen = tBonus[idx][2]
    else:
        # pas de bonus
        Bonus = None

# --------------------------------------------------------------------------------
# affichage du bonus
def DrawBonus():
    global Bonus

    if Bonus is not None:
        x = Bonus[0]*CELL_SIZE
        y = Bonus[1]*CELL_SIZE
        canvas.create_image(x, y, image=imgBonus, anchor = "nw")

# --------------------------------------------------------------------------------
# Génération des murs
def GenWalls(nbm = 1):
    global Walls

    for nm in range(nbm):
        for i in range(MAXWALL):
            # orientation aléatoire
            wdir = random.choice(["Down", "Up", "Left", "Right"])
            wori = vDir[wdir]
            # le quadrant
            quad = wQuad[i]
            # longueur de 5 cases
            l = 5
            n = 0
            x = random.randint(quad[0][0], quad[1][0])
            y = random.randint(quad[0][1], quad[1][1])
            while n < l:
                # on vérifie que la nouvelle pos
                # ne soit pas déjà occupée
                new_wall = (x, y)
                if (new_wall not in Walls) and (new_wall not in snake.body) and (new_wall != Bonus):
                    Walls.append(new_wall)
                    # on déplace le mur
                    x += wori[0]
                    y += wori[1]
                    n += 1
                else:
                    x = random.randint(quad[0][0], quad[1][0])
                    y = random.randint(quad[0][1], quad[1][1])

    
# --------------------------------------------------------------------------------
# affichage des murs
def DrawWalls():
    global imgWall

    imgWall = TK.PhotoImage(file='models/mur.png')
    for wall in Walls:
        x = wall[0]*CELL_SIZE
        y = wall[1]*CELL_SIZE
        canvas.create_image(x, y, image=imgWall, anchor = "nw")

# --------------------------------------------------------------------------------
# traitement des touches
def onKey(event):
    if Running and not GameOver:
        snake.changeDirTo(event.keysym)

# --------------------------------------------------------------------------------
# affichage du jeu
def RenderGame():
    canvas.delete(TK.ALL)
    snake.draw()
    DrawBonus()
    DrawWalls()

# --------------------------------------------------------------------------------
# la boucle de jeu
def GameLoop():
    canvas.focus_set()
    # boucle du jeu
    if Running:
        snake.update()
        RenderGame()
        sc.set(label_score.format(Score))
        fen.update_idletasks()
        if Running and not GameOver:
            fen.after(Tempo,GameLoop)

# --------------------------------------------------------------------------------
# le reset
def Reset():
    global Bonus, Running, GameOver, Score, Walls, snake

    del snake
    Walls    = []
    Running  = False
    GameOver = False
    Score    = 0
    Bonus    = None
    info.configure(text = "")
    sc.set(label_score.format(Score))
    fen.update_idletasks()
    snake    = Snake()
    GenWalls(2)
    NewBonus()
    RenderGame()

# --------------------------------------------------------------------------------
if __name__ == "__main__":
    # on cree la fenêtre et le canevas
    fen = TK.Tk()
    fen.title("Snake")
    fen.protocol("WM_DELETE_WINDOW",OnExit)
    fen.resizable(False, False)

    # pour le score
    sc = TK.StringVar()
    ReadHighScore()

    canvas = TK.Canvas(fen, height=screenHeight, width=screenWidth, bd=0, bg="#808080")
    canvas.bind("<Up>", onKey)
    canvas.bind("<Down>", onKey)
    canvas.bind("<Left>", onKey)
    canvas.bind("<Right>", onKey)
    canvas.grid(row = 0, column = 1, rowspan = 8, columnspan = 3, pady = 5)

    # les bouttons
    wb = 90
    img_start = TK.PhotoImage(file = 'models/media-playback-start.png')
    b1 = TK.Button(fen, text ='Play', image = img_start, compound="left", width = wb, command = Go)
    img_rew = TK.PhotoImage(file = 'models/media-seek-backward.png')
    b2 = TK.Button(fen, text ='Reset', image = img_rew, compound="left", width = wb, command = Reset)
    img_stop = TK.PhotoImage(file = 'models/media-playback-stop.png')
    bS = TK.Button(fen, text ='Stop', image = img_stop, compound="left", width = wb, command = Stop)
    b1.grid(row = 0, column = 0)
    b2.grid(row = 1, column = 0)
    bS.grid(row = 2, column = 0)
    # Le bouton "Quitter"
    img_quit = TK.PhotoImage(file = 'models/system-log-out.png')
    bQ = TK.Button(fen, text ='Quitter', image = img_quit, compound="left", width = wb, command = OnExit)
    bQ.grid(row = 7, column = 0)

    # le label pour l'affichage du score
    sc.set(label_score.format(Score))
    affscore = TK.Label(fen, textvariable = sc, anchor = TK.E, fg = "blue", justify = TK.RIGHT)
    affscore.grid(row = 8, column = 3, sticky = "E")

    # le status
    info = TK.Label(fen, anchor = TK.W, justify = TK.LEFT)
    info.configure(text = "")
    info.grid(row = 8, column = 1, sticky = "W")

    # le highscore
    hsco = TK.Label(fen, anchor = TK.W, justify = TK.LEFT)
    hsco.configure(text = "HighScore: {0:6d}".format(HighScore))
    hsco.grid(row = 8, column = 0, sticky = "W")

    snake = Snake()
    GenWalls(2)
    NewBonus()
    RenderGame()

    fen.mainloop()
# eof
