# EditSimple — Manuel d'utilisation

[English](manual.en.md) · [Italiano](manual.it.md) · [Deutsch](manual.de.md) · **Français** · [Español](manual.es.md) · [Nederlands](manual.nl.md) · [Polski](manual.pl.md) · [Ελληνικά](manual.el.md) · [Shqip](manual.sq.md)

EditSimple est un programme de montage vidéo conçu pour ceux qui doivent
**expliquer un fait ou montrer une preuve** dans une vidéo : une remise de
main à main au milieu de la foule, un véhicule qui arrive, une personne à
suivre ou à rendre méconnaissable. Vous importez la séquence, vous indiquez ce
qui compte et le programme fait le reste : les flèches, les cadres, les points
numérotés, les zooms et les pixellisations **suivent tout seuls le sujet**
dans les images suivantes, et là où le suivi se trompe, il suffit de faire
glisser la figure au bon endroit pour le corriger. En quelques minutes, vous
obtenez un MP4 prêt à être projeté ou joint, avec diapos d'ouverture et de
fermeture, textes, logo et signature de l'opérateur.

La page **Images** fait le même travail sur les photographies : une ou
plusieurs photos sur une feuille, les mêmes annotations, les points numérotés
avec leurs notes et un bouton qui **insère la figure avec sa légende
directement dans Word**.

*Andrea Cumini — www.osintinfo.net — andrea@osintinfo.net*
*EditSimple fait partie des outils de [Seity](https://www.seity.com).*

> **Avertissement sur le matériel d'exemple.** Les images de ce manuel
> utilisent une vidéo d'archive publiée sur Pexels : une rue piétonne avec des
> passants ordinaires. **Les personnes qui apparaissent ne font rien de mal** :
> les flèches, les cadres, les zooms et les pixellisations placés sur elles
> servent uniquement à montrer le fonctionnement du programme, et les sujets
> ont été choisis au hasard. Les deux photographies de la page Images sont
> d'[Andrea Dalle Piatte](https://www.pexels.com/it-it/@andreadallepiatte/),
> publiées sur Pexels.

## Sommaire

1. [Ce que l'on peut faire](#1-ce-que-lon-peut-faire)
2. [Installation et premier démarrage](#2-installation-et-premier-démarrage)
3. [La fenêtre](#3-la-fenêtre)
4. [Page Configurer](#4-page-configurer)
5. [Un exemple complet, pas à pas](#5-un-exemple-complet-pas-à-pas)
6. [Corriger le suivi avec les images clés](#6-corriger-le-suivi-avec-les-images-clés)
7. [La chronologie](#7-la-chronologie)
8. [L'aperçu : agrandir et détacher](#8-laperçu--agrandir-et-détacher)
9. [Diapos d'ouverture, de fermeture et intermédiaires](#9-diapos-douverture-de-fermeture-et-intermédiaires)
10. [Textes, images, temps écoulé et numéro d'image](#10-textes-images-temps-écoulé-et-numéro-dimage)
11. [Accélérer et ralentir](#11-accélérer-et-ralentir)
12. [Couper, supprimer, arrêt sur image](#12-couper-supprimer-arrêt-sur-image)
13. [Transitions](#13-transitions)
14. [Audio](#14-audio)
15. [Exporter la vidéo](#15-exporter-la-vidéo)
16. [La page Images](#16-la-page-images)
17. [Conseils pour un bon résultat](#17-conseils-pour-un-bon-résultat)
18. [Raccourcis clavier et souris](#18-raccourcis-clavier-et-souris)
19. [Les fichiers de projet](#19-les-fichiers-de-projet)

## 1. Ce que l'on peut faire

| Fonction | En bref |
| --- | --- |
| **Suivi du sujet** | Cadres, ovales, flèches, points numérotés, zooms et pixellisations suivent une personne, un visage, un objet ou un véhicule ; ils grandissent et rapetissent avec lui s'il s'approche ou s'éloigne de la caméra ; ils se terminent tout seuls quand il sort du cadre. |
| **Images clés de correction** | Là où le suivi se trompe (un poteau, une personne qui passe devant), vous faites glisser la figure sur le sujet : le programme corrige le trajet avant et après ce point. |
| **Flèches** | Extrémités à la pointe, à la queue, des deux côtés ou aucune ; pointe pleine ou ouverte, point, petit carré, barre. Dans la vidéo, la queue peut **rester fixe** pendant que la pointe suit le sujet. |
| **Points numérotés** | Petits cercles avec un numéro (1, 2, 3) ou une lettre (A, B, C), toujours le suivant du dernier placé ; ils suivent le sujet dans la vidéo ; dans les images, ils ont une note qui se retrouve dans la légende. |
| **Zoom** | Un petit détail (les mains, une plaque d'immatriculation) agrandi de 2x à 16x dans un encart, avec un contour et une ligne qui le relient à l'objet. Rectangulaire ou ovale. |
| **Pixellisation** | Rectangulaire ou ovale, pour les visages et les plaques ; elle suit le sujet et grandit avec lui. |
| **Textes et images** | Textes sur plusieurs lignes avec fond et coins arrondis ; images superposées (une image extraite, une carte, un document). |
| **Logo et signature** | Logo et texte de l'opérateur fixes dans un coin, préparés une seule fois dans Configurer. |
| **Temps et images** | Le temps écoulé et le numéro d'image inscrits dans la vidéo, où vous voulez. |
| **Diapos** | Au début, à la fin ou au milieu ; couleur unie ou image de fond ; vous y écrivez des textes et y placez des images. |
| **Vitesse** | De 0,25x (ralenti) à 32x (avance rapide), avec l'icône d'une horloge qui indique la vitesse. |
| **Coupes** | Coupe au curseur, suppression d'une portion, arrêt sur image, réorganisation des clips. |
| **Transitions** | Apparition depuis le noir, disparition vers le noir, fondu avec le clip suivant. |
| **Audio** | Pistes ajoutées (commentaire, musique) avec volume et fondus ; audio original avec volume, fondus et suppression de passages précis. |
| **Aperçu** | Lecture avec le son, en arrière, image par image ; aperçu agrandissable et **détachable** dans une fenêtre séparée. |
| **Exportation** | MP4 (H.264 + AAC) identique à l'aperçu. |
| **Images** | Une ou plusieurs photos sur une feuille (jusqu'à quatre, onze dispositions, cinq formats), les mêmes annotations que la vidéo plus la **liaison** entre deux points, les points numérotés avec leurs notes, la légende et le bouton **Word** ; projet enregistré dans un JSON modifiable ; feuille exportée en PNG ou JPG ou copiée dans le presse-papiers. |
| **Langues et manuel** | Interface en 9 langues, modifiable sans redémarrer ; ce manuel s'ouvre dans le programme, dans la langue choisie. |

## 2. Installation et premier démarrage

**Exécutable (Windows 10/11, 64 bits).** Extrayez le zip où vous voulez et
lancez `EditSimple.exe`. Python n'est pas nécessaire.

**Depuis les sources.** Avec Python 3.11 :

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe EditSimple.py
```

**FFmpeg.** EditSimple utilise ffmpeg pour lire les fichiers et pour exporter.
Il n'est pas inclus : au premier démarrage, s'il ne le trouve pas, la page
**Configurer** s'ouvre et le bouton **Télécharger / Mettre à jour** le
télécharge (version officielle pour Windows) dans le dossier `tools\ffmpeg\` à
côté du programme. Aucune installation.

**VitTrack (facultatif).** Sur la même page, **Télécharger** récupère
VitTrack, un petit modèle (0,7 Mo) qui aide le suivi à retrouver le sujet
après un obstacle. Sans lui, le suivi fonctionne quand même.

## 3. La fenêtre

![La fenêtre d'EditSimple](images/fr/01_start.webp)

- **Barre de gauche**, avec les pages : **Vidéo** (le montage), **Images**
  (les photographies, chapitre 16), **Configurer** et **Manuel**, qui ouvre ce
  manuel dans une fenêtre séparée, dans la langue de l'interface.
- **Barre d'outils**, en quatre groupes : *Projet* (nouveau, ouvrir,
  enregistrer, annuler, rétablir), *Clip* (importer une vidéo, audio, couper,
  supprimer, arrêt sur image, diapo, vitesse), *Incrustations* (texte, image,
  logo, temps, images, cadre, ovale, flèche, numéros, lettres, zoom
  rectangulaire et ovale, pixel rectangulaire et ovale) et *Sortie* (exporter
  MP4). Chaque bouton a une info-bulle avec son raccourci.
- **Aperçu**, au centre : il montre l'image au curseur avec tous les effets,
  exactement comme dans la vidéo exportée. C'est là que vous dessinez et
  déplacez les effets.
- **Propriétés**, à droite : les valeurs de l'élément sélectionné (un clip, un
  effet, une piste audio).
- **Transport** : début, -10 images, image précédente, lecture arrière,
  lecture, image suivante, +10 images, fin ; le temps du curseur (modifiable
  au clavier) ; IN, OUT et l'effacement des marques ; à droite, le zoom de la
  chronologie.
- **Chronologie**, en bas : règle, piste **Vidéo** en pellicule, **Audio
  original**, pistes audio ajoutées et **Effets**, un par ligne.

![Le manuel s'ouvre dans le programme, avec le sommaire à gauche et le choix de la langue](images/fr/34_manual.webp)

La fenêtre du **Manuel** a le sommaire des chapitres à gauche (un clic mène au
chapitre) et, en haut, le menu de la langue ; les liens du texte fonctionnent,
et les images sont celles de ces pages. Le manuel change de langue en même
temps que l'interface.

## 4. Page Configurer

![Configurer : FFmpeg, VitTrack, logo et texte de l'opérateur](images/fr/02_settings.webp)

Elle s'ouvre depuis la barre de gauche. Elle contient :

- **FFmpeg** et **Suivi (VitTrack)** : état, téléchargement et mise à jour.
- **Exportation** : qualité de la vidéo (CRF : 15 excellente, 28 légère),
  vitesse d'encodage, qualité de l'audio, durées proposées pour l'arrêt sur
  image et les effets, taille par défaut des pixels et seuil du suivi (plus
  élevé = plus strict pour reconnaître le sujet).
- **Logo et texte de l'opérateur** : l'image du logo (PNG avec transparence
  ou JPG), le texte (nom, organisme, site), la largeur du logo, la hauteur du
  texte, la distance des bords, le coin, la disposition, les couleurs et un
  fond avec opacité et coins arrondis. Vous les préparez une seule fois ;
  ensuite, le bouton **Logo** les place dans la vidéo (et sur la feuille des
  images).

![Configurer : coins arrondis, langue et crédits](images/fr/03_settings_more.webp)

- **Coins arrondis** du fond des textes, des cadres, du zoom rectangulaire et
  de la pixellisation rectangulaire.
- **Langue** de l'interface : English, Italiano, Deutsch, Français,
  Español, Nederlands, Polski, Ελληνικά, Shqip. Le changement est immédiat.

![La langue se change d'un clic](images/fr/30_language.webp)

## 5. Un exemple complet, pas à pas

L'exemple de ce chapitre est une vidéo de 19 secondes tournée dans une rue
piétonne animée (voir l'avertissement : les passants ne font rien de mal).
En quelques étapes, nous l'enrichissons : le logo et le site de l'opérateur en
bas, un zoom sur les mains d'un homme qui suit ses mouvements, une flèche qui
désigne une personne pendant 12 secondes, deux cadres sur d'autres personnes,
la pixellisation d'un visage à la fin, un point numéroté qui suit une personne
et une flèche à queue fixe qui désigne un téléphone pendant toute la vidéo.

### 5.1 Importer la vidéo

![Vidéo importée](images/fr/04_import.webp)

**Importer une vidéo** (Ctrl+I) ouvre la séquence. La première vidéo fixe les
dimensions et la fréquence du projet (ici 1920×1080, 29,97 images par
seconde). Le clip apparaît dans la piste Vidéo sous forme de pellicule
d'images ; son audio dans la piste Audio original (cette vidéo n'en a pas).
Les autres vidéos s'ajoutent à la fin ou au curseur.

Le curseur se déplace d'un clic sur la règle, avec les flèches ← → (une
image), Ctrl+← → (dix images), Maj+← → (une seconde), Début et Fin, ou en
tapant le temps dans la case. **Espace** lance la lecture avec le son,
**Maj+Espace** lit en arrière.

### 5.2 Logo et signature de l'opérateur

![Logo et texte de l'opérateur](images/fr/05_logo.webp)

**Logo** (L) place le logo et le texte préparés dans Configurer pour toute la
vidéo (ou seulement entre IN et OUT, s'ils sont marqués). Sur l'aperçu, vous
les déplacez en les faisant glisser et les agrandissez par les coins ; dans le
panneau, vous changez le texte, les couleurs, le fond, le coin et l'opacité.

### 5.3 Un zoom qui suit les mains

![Zoom : après le rectangle sur l'objet, l'encart agrandi suit la souris](images/fr/06_zoom_place.webp)

**Zoom** (Z) s'utilise en deux étapes :

1. faites glisser un rectangle autour du détail (ici les mains de l'homme) ;
2. sous la souris apparaît l'encart agrandi avec le contenu réel : un clic le
   pose. L'agrandissement se choisit à ce moment-là avec la molette ou avec
   les touches 2, 3, 4, 6, 8 (jusqu'à 16x depuis le panneau).

Le zoom **commence aussitôt à suivre l'objet** : une fenêtre montre la
progression du suivi.

![Suivi en cours](images/fr/07_tracking.webp)

La zone agrandie suit les mains et grandit ou rapetisse si l'homme s'approche
ou s'éloigne ; l'encart agrandi reste là où vous l'avez placé. Un contour
coloré marque l'objet et une ligne le relie à l'encart. Maj+Z crée un zoom
ovale.

### 5.4 Une flèche qui suit une personne

![Flèche : on trace un rectangle autour du sujet à suivre](images/fr/09_arrow_target.webp)

**Flèche** (A) : faites glisser de la queue à la pointe. Pour qu'elle suive
une personne, appuyez sur **Suivre le sujet** dans le panneau (ou *Relancer le
suivi depuis le curseur*) et tracez un **rectangle autour du sujet** : la
flèche le suit en gardant la pointe sur lui.

![La flèche suit la personne pendant 12 secondes](images/fr/10_arrow_follow.webp)

Dans la chronologie, la barre de la flèche affiche *(suit)* et les losanges
des images clés avec lesquelles nous avons corrigé le trajet (voir le
chapitre 6).

Dans le panneau de la flèche, vous choisissez aussi les **Extrémités** (à la
pointe, à la queue, des deux côtés, aucune : la ligne seule) et le **Type
d'extrémité** : pointe pleine, pointe ouverte, point, petit carré ou barre.
Avec deux extrémités, la flèche indique un lien entre deux choses.

### 5.5 Des cadres sur les personnes

![Cadre : Suivre le sujet](images/fr/11_box.webp)

**Cadre** (R) et **Ovale** (E) : faites-les glisser sur l'aperçu. Dans le
panneau, vous choisissez la couleur, l'épaisseur, le remplissage, les coins
arrondis et l'opacité ; **Suivre le sujet** leur fait suivre ce qu'ils
contiennent. Quand la personne sort du cadre, la figure l'accompagne
jusqu'au bord et l'effet se termine.

### 5.6 La pixellisation d'un visage

![Pixellisation : jusqu'à quand suivre et taille des pixels](images/fr/12_pixel_form.webp)

**Pixel** (P rectangulaire, K ovale) : faites glisser un cadre sur le visage ;
une fenêtre demande jusqu'à quand le suivre et la taille des pixels.

![Le visage reste masqué pendant que l'homme marche vers la caméra](images/fr/13_pixelate.webp)

La pixellisation suit le visage et **grandit quand il s'approche** de la
caméra, de sorte qu'elle le couvre toujours. Si le sujet sort du cadre, la
pixellisation l'accompagne jusqu'à ce qu'il soit entièrement sorti : aucune
image ne reste découverte.

### 5.7 Un point numéroté qui suit une personne

![Point numéroté (lettre A) qui suit une personne](images/fr/31_marker_video.webp)

**Numéros** (N) et **Lettres** (Maj+N) placent un **point numéroté** : un
petit cercle contenant un numéro (1, 2, 3...) ou une lettre majuscule (A, B,
C...). Appuyez sur le bouton et cliquez là où va le point ; **chaque point
demande un nouveau clic sur le bouton**, et il prend toujours le numéro ou la
lettre qui suit le dernier placé (après Z vient AA). Dans le panneau, vous
changez le numéro ou la lettre, le diamètre, la couleur du cercle et du texte,
l'anneau blanc et l'opacité.

Comme les autres figures, le point **suit le sujet** : *Suivre le sujet* et
un rectangle autour de la personne. Dans la vidéo, les points n'ont pas de
note ; ils servent à désigner, dans le commentaire ou dans une diapo, « la
personne A », « l'objet 2 ».

### 5.8 Une flèche à queue fixe

![Flèche à queue fixe : la pointe suit le téléphone, la queue reste à côté du texte](images/fr/32_arrow_tail.webp)

Une flèche qui suit un sujet se déplace, en principe, tout entière. Le choix
**Queue** du panneau a l'alternative **Reste fixe là où vous l'avez tracée** :
la queue reste au point de la première image et seule la **pointe suit le
sujet**. C'est utile quand la queue part d'un texte ou d'un point de repère :
ici, le texte « Téléphone » reste en bas et la flèche s'allonge et se
raccourcit pour rester sur le téléphone pendant toute la vidéo.

En faisant glisser la poignée de la queue, vous la déplacez vraiment là ; en
faisant glisser la pointe ou la ligne, vous créez une image clé, comme pour
les autres figures.

## 6. Corriger le suivi avec les images clés

![Images clés sur la barre du zoom](images/fr/08_keyframes.webp)

Le suivi est automatique, mais une vraie vidéo a des obstacles : un poteau,
une personne qui passe devant, un sujet qui se retourne. Là où la figure se
trompe :

1. placez le curseur sur cette image ;
2. **faites glisser la figure sur le sujet** dans l'aperçu (ou
   redimensionnez-la par les coins).

Une **image clé** apparaît (un losange sur la barre de l'effet). Le programme
corrige le trajet avant l'image clé, de façon progressive, et **reprend le
suivi à partir de là** jusqu'à l'image clé suivante. Vous pouvez ajouter
autant d'images clés que nécessaire : le zoom de l'exemple en a 14, la
flèche 9.

Sur la barre de l'effet sélectionné, vous voyez aussi les points trouvés par
le suivi (pastilles). Un clic sélectionne un point et y place le curseur,
Maj+clic sélectionne un intervalle, Ctrl+clic ajoute ou retire ; **Suppr** ou
le clic droit effacent les points sélectionnés. Dans le panneau, la section
**Image clé** a les boutons *< Préc.* et *Suiv. >*, *Image clé ici* (fixe la
position actuelle) et *Retirer l'image clé au curseur*.

## 7. La chronologie

![Chaque effet a sa propre ligne, dans l'ordre où il a été ajouté](images/fr/33_timeline_rows.webp)

- **Barres des effets** : **chaque effet a sa propre ligne**, dans l'ordre où
  il a été ajouté, de sorte qu'aucune barre n'en couvre une autre. Elles se
  déplacent en les faisant glisser ; le bord droit modifie la durée. Avec
  beaucoup d'effets, la partie audio et effets **défile verticalement** (barre
  à droite, molette sur les noms des lignes ou Maj+molette), tandis que la
  règle et la vidéo restent fixes en haut.

![Œil : un effet masqué pendant le travail](images/fr/14_hide.webp)

- **Œil** : l'icône à gauche de chaque barre **masque ou affiche** l'effet,
  dans l'aperçu et dans la vidéo exportée. Utile quand de nombreux effets se
  superposent pendant le travail.
- **Clic droit sur une barre** : *Prolonger jusqu'au curseur* (si le curseur
  est après la fin ; si l'effet suit un sujet, le suivi continue jusqu'au
  curseur et, si le sujet est perdu avant, la figure reste immobile là où
  elle l'a vu pour la dernière fois) et *Arrêter au curseur* (si le curseur
  est à l'intérieur de l'effet).
- **Zoom de la chronologie** : Ctrl+molette, ou les boutons − + et *Ajuster*.
  De près, la pellicule montre chaque image.
- **Défilement** : molette, Alt+glisser ou glisser avec le bouton central.
- **Séparateur** : la fine bande au-dessus des commandes de lecture se fait
  glisser vers le haut ou vers le bas pour donner plus de place à la
  chronologie ou à l'aperçu.

## 8. L'aperçu : agrandir et détacher

![Aperçu agrandi avec Ctrl+molette](images/fr/15_preview_zoom.webp)

- **Ctrl+molette** sur l'aperçu l'agrandit autour de la souris, jusqu'à
  16 fois : pour poser avec précision un zoom sur un petit détail ou pour
  contrôler une pixellisation. Vous vous déplacez en faisant glisser sur un
  point vide (ou avec le bouton central) ; un double-clic avec le bouton
  central revient à la vue entière.
- **Détacher l'aperçu** : le bouton en haut à droite de l'aperçu l'ouvre dans
  une **fenêtre séparée**, à placer sur un second écran ou où vous voulez ; la
  chronologie prend toute la place. Le même bouton (ou la fermeture de la
  fenêtre) le **rattache**. Les raccourcis fonctionnent aussi dans la fenêtre
  détachée.

![Aperçu détaché dans une fenêtre séparée](images/fr/16_detached.webp)

## 9. Diapos d'ouverture, de fermeture et intermédiaires

![Nouvelle diapo : au début, au curseur ou à la fin](images/fr/17_slide_form.webp)

**Diapo** insère une diapo **au début** (ouverture), **au curseur** (au
milieu de la vidéo) ou **à la fin** (fermeture), de la durée choisie. La diapo
est un fond uni ou une **image de fond** adaptée aux dimensions de la vidéo
(remplir, entière ou étirer) ; la couleur et l'image se choisissent dans le
panneau. Les effets qui suivent sont décalés vers l'avant avec la vidéo.

Sur la diapo, vous écrivez des textes et placez des images avec les outils
**Texte** et **Image** : avec le curseur sur la diapo, ils durent autant
qu'elle.

![Le texte s'écrit sur plusieurs lignes, avec alignement, taille, couleur, ombre et fond](images/fr/18_text_form.webp)

![Diapo d'ouverture avec titre et sous-titre](images/fr/19_slide_opening.webp)

![Diapo d'ouverture, une diapo au milieu et une de fermeture dans la chronologie](images/fr/20_slides.webp)

## 10. Textes, images, temps écoulé et numéro d'image

![Un texte et une image sur la vidéo](images/fr/21_text_image.webp)

- **Texte** (T) : un clic sur l'aperçu ouvre la fenêtre du texte : plusieurs
  lignes, alignement, taille, couleur, ombre, fond (avec opacité et coins
  arrondis), centrage. Double-cliquez sur un texte pour le réécrire. Dans le
  panneau, également la police, choisie dans une liste qui affiche chaque
  police.
- **Image** : choisit un fichier (PNG, JPG...) et le place au centre ; il se
  déplace et se redimensionne sur l'aperçu ; dans le panneau, opacité et coins
  arrondis. Ici, c'est une image agrandie du sujet, mais ce peut être une
  carte, un document, une photo.

![Temps écoulé et numéro d'image en bas à droite](images/fr/22_timer_frames.webp)

- **Temps** : le temps écoulé (01:23, 00:01:23 ou avec les dixièmes), depuis
  le début de la vidéo ou depuis le début de l'effet, précédé d'un texte au
  choix. Au-delà d'une heure, les heures apparaissent.
- **Images** : le numéro d'image, à partir de 0 ou de 1, depuis le début de la
  vidéo ou de l'effet. Utile pour citer un instant avec précision.

Les deux ont un fond, une opacité et des coins arrondis, et se placent où
vous voulez d'un clic.

## 11. Accélérer et ralentir

![Vitesse de la portion IN-OUT](images/fr/23_speed_form.webp)

Marquez une portion avec **IN** et **OUT** (touches I et O) et appuyez sur
**Vitesse** (V). De **2x à 32x**, la vidéo accélère ; **0,5x et 0,25x**
ralentissent. L'option de l'**horloge** affiche une icône avec des aiguilles
qui tournent et la vitesse inscrite en dessous, pour que le spectateur sache
que le temps passe plus vite. La chronologie se raccourcit ou s'allonge ; avec
1x, on revient à la vitesse normale. La position, la taille et la couleur de
l'horloge se règlent dans le panneau du clip.

![Portion accélérée 4x avec l'horloge](images/fr/24_speed.webp)

## 12. Couper, supprimer, arrêt sur image

![Coupe au curseur et arrêt sur image](images/fr/25_cut_freeze.webp)

- **Couper** (S) divise le clip au curseur. Les clips se **réorganisent en
  les faisant glisser** dans la chronologie.
- **Supprimer** (Suppr) retire la portion entre IN et OUT, ou l'élément
  sélectionné : la suite recule, avec les effets.
- **Arrêt** (F) : l'image au curseur reste figée pendant le nombre de
  secondes choisi ; la suite est décalée vers l'avant.

Tout s'annule avec Ctrl+Z et se rétablit avec Ctrl+Y.

## 13. Transitions

![Transitions d'un clip](images/fr/26_transitions.webp)

Quand vous sélectionnez un clip, le panneau contient la section
**Transitions** :

- **Depuis le noir** : le clip apparaît depuis le noir ;
- **Vers le noir** : le clip disparaît dans le noir ;
- **Fondu avec le suiv.** : le clip se fond dans le suivant, à cheval sur la
  coupe. Le clip sortant reste figé pendant le fondu ; la durée de la vidéo ne
  change pas.

L'audio monte et descend aussi avec les transitions. 0 signifie coupe franche.

## 14. Audio

![Piste audio avec fondus d'entrée et de sortie](images/fr/27_audio.webp)

- **Audio** ajoute une piste (commentaire, musique) au curseur. Dans le
  panneau : nom, position, portion du fichier, **volume**, muet et **fondus**
  d'entrée et de sortie. Elle se déplace en la faisant glisser ; un clic sur
  son nom la sélectionne entièrement, Suppr la supprime.
- La **ligne blanche** au-dessus de chaque piste montre l'évolution du volume :
  fondus et transitions se voient d'un coup d'œil.
- **Audio original** : un clic sur le nom de la ligne sélectionne tout l'audio
  de la vidéo (volume, fondus au début et à la fin, suppression) ; un clic sur
  un morceau sélectionne seulement ce morceau (volume, fondus, muet). Avec IN
  et OUT marqués et l'audio original sélectionné, Suppr retire **seulement
  l'audio** de ce passage : la vidéo reste.
- La lecture dans l'aperçu se fait **avec le son** (mixé comme à
  l'exportation).

## 15. Exporter la vidéo

![Exportation en cours](images/fr/28_export.webp)

**Exporter MP4** (Ctrl+E) choisit le fichier et crée la vidéo avec ffmpeg :
H.264 et AAC, qualité et vitesse d'encodage dans Configurer. Le résultat est
identique à l'aperçu. L'exportation peut être annulée ; à la fin, le programme
propose d'ouvrir le dossier.

![Exportation terminée](images/fr/29_export_done.webp)

## 16. La page Images

La page **Images** (barre de gauche) sert à préparer une **figure pour un
rapport ou une présentation** à partir d'une ou plusieurs photographies : les
photos sur la feuille, les annotations par-dessus, les points numérotés avec
leurs notes et la légende, à insérer dans Word d'un clic ou à exporter comme
image. L'exemple de ce chapitre utilise deux photos d'une moto.

### 16.1 Disposition et photographies

![Le choix de la disposition : combien d'images et comment les disposer](images/fr/40_images_layout.webp)

À la première ouverture, la page demande la **disposition** : une image ;
deux côte à côte ou l'une sous l'autre ; trois en ligne, en colonne, une
grande à gauche ou une grande en haut ; quatre en grille, en ligne, une grande
à gauche ou une grande en haut. En dessous, vous choisissez le **format de la
feuille** : 16:9 (1920×1080), 4:3, carré, 9:16 portrait ou A4 portrait.
Disposition et format se changent à tout moment (**Disposition** dans la
barre, ou *Changer la disposition...* dans le panneau de la feuille) : les
images déjà placées restent.

![Deux photos chargées ; dans le panneau, l'agrandissement et la position](images/fr/41_images_loaded.webp)

Les photographies se placent avec **Charger** (une ou plusieurs, dans le cadre
choisi et dans les suivants vides), d'un **clic sur un cadre vide**, en
faisant glisser un fichier depuis l'ordinateur sur le cadre ou avec **Ctrl+V**
depuis le presse-papiers (par exemple une capture d'écran). Chaque photo
remplit son cadre : la **molette** sur la photo l'agrandit, en la **faisant
glisser** vous la déplacez dans le cadre pour cadrer le détail qui compte.
Dans le panneau de la photo se trouvent le nom du fichier, la taille, le
curseur de l'agrandissement et les boutons pour la remplacer ou la retirer.
Dans le panneau de la **feuille** (quand rien n'est sélectionné) : format,
espace entre les images et couleur de la feuille.

### 16.2 Annotations

![Les annotations sur la feuille : liaison, flèche entre deux photos, zoom, pixels, texte, logo et points numérotés](images/fr/42_images_annotations.webp)

Les outils sont les mêmes que pour la vidéo (**Texte**, **Image**, **Logo**,
**Cadre**, **Ovale**, **Flèche**, **Numéros**, **Lettres**, **Zoom**
rectangulaire et ovale, **Pixel** rectangulaire et ovale), sans durées ni
suivi, plus un nouveau :

- **Relier** (C rectangles, Maj+C ovales) : un clic sur le premier point et
  un sur le second ; autour de chacun apparaît une forme (rectangle ou ovale,
  redimensionnable par les coins) et une ligne les unit de bord à bord. Dans
  le panneau : forme, coins, couleur, épaisseur, ligne pointillée, opacité.
  Cela sert à dire « ceci est cela » : le détail d'une photo retrouvé dans
  l'autre.

Chaque annotation **appartient à la photo sur laquelle elle se trouve** : si
la photo se déplace ou s'agrandit, l'annotation la suit. Une flèche ou une
liaison entre deux photos ont une extrémité sur chacune, et chaque extrémité
suit sa photo. Une annotation à cheval sur deux photos (un texte, un cercle,
un cadre) reste entière sur la feuille.

### 16.3 Points numérotés et notes

![Un point numéroté sélectionné : dans le panneau, sa note](images/fr/43_images_marker_note.webp)

**Numéros** (N) et **Lettres** (Maj+N) fonctionnent comme dans la vidéo : un
clic sur le bouton, un clic sur la photo, et le point prend le numéro ou la
lettre qui suit le dernier. Ici, en plus, chaque point a une **Note** dans le
panneau : ce qu'il désigne. Les notes se retrouvent dans la légende, dans
l'ordre des points (d'abord les numéros, puis les lettres). Dans le panneau de
la feuille, la liste **Points numérotés** montre tous les points avec leur
note : un clic sélectionne le point.

### 16.4 Légende et Word

![La légende : le texte qui vient après « Figure N : »](images/fr/44_images_caption.webp)

Le bouton **Légende** (ou la case *Légende pour Word* dans le panneau de la
feuille) ouvre le texte de la légende : il vient juste après « Figure N : »,
et après lui viennent les notes des points numérotés. Avec le texte « Moto »
et quatre points, la légende devient :

`Figure 1 : Moto. 1) réservoir, 2) frein, A) phare, B) échappement`

![La figure insérée dans Word avec la légende](images/fr/45_images_word.webp)

Le bouton **Word** insère la figure **dans le document Word ouvert, à
l'emplacement du curseur** : l'image, aussi large que la page, et en dessous
la légende dans le style *Légende* de Word, avec le numéro automatique
(« Figure 1 », « Figure 2 »...). Le numéro est un champ de Word : les
**renvois** et la **table des illustrations** de Word fonctionnent comme pour
les figures faites à la main. Si Word n'est pas ouvert, il est lancé avec un
nouveau document ; si Word ne répond pas, l'image et la légende sont copiées
dans le presse-papiers, à coller.

### 16.5 Enregistrer, exporter, copier

![Projet enregistré ; Exporter, Copier et Word dans le groupe Sortie](images/fr/46_images_output.webp)

- **Enregistrer** (Ctrl+S, Ctrl+Maj+S sous un nom) écrit le **projet** : un
  fichier JSON avec la disposition, le format, les photos (cadrage et
  agrandissement), les annotations et la légende, et à côté un dossier
  `<nom>_file` avec les copies des photos et des images utilisées. Le JSON est
  lisible et peut être modifié à la main. **Ouvrir** (Ctrl+O) le rouvre ; à
  la fermeture, s'il y a quelque chose de non enregistré, le programme le
  demande.
- **Exporter** enregistre la feuille en **PNG ou JPG** aux dimensions du
  format.
- **Copier** place la feuille dans le **presse-papiers**, à coller dans un
  courriel, dans une présentation ou ailleurs.
- Annuler et rétablir (Ctrl+Z, Ctrl+Y) valent pour tout : photos,
  annotations, disposition et légende.

## 17. Conseils pour un bon résultat

- **L'encart du zoom se place dans une zone neutre** : l'encart agrandi
  couvre la partie de la vidéo sur laquelle il est posé, pendant toute sa
  durée. Placez-le là où il ne se passe rien d'intéressant (ciel, mur, sol).
- **Dessinez au plus près du sujet** pour les cadres, ovales et
  pixellisations : le contenu de la figure est le modèle recherché dans les
  images suivantes.
- **Pour la flèche et pour le point numéroté, un rectangle un peu plus grand**
  (tête et épaules au lieu de la tête seule) tient mieux quand d'autres
  personnes passent devant.
- **Après le suivi, parcourez la vidéo** : là où la figure se trompe,
  faites-la glisser sur le sujet. Quelques images clés suffisent, même pour de
  longs trajets.
- **Avec beaucoup d'effets**, utilisez l'œil pour masquer ceux dont vous
  n'avez pas besoin à ce moment-là, et l'aperçu détaché pour avoir plus de
  place dans la chronologie.
- **Dans les images, mettez d'abord les photos en place** (cadrage et
  agrandissement), puis les annotations : les annotations suivent la photo,
  mais il est plus commode de les dessiner sur le cadrage définitif.
- **Enregistrez souvent** (Ctrl+S) : le projet est un petit fichier JSON que
  vous pouvez rouvrir et modifier quand vous voulez.

## 18. Raccourcis clavier et souris

| Touche | Action |
| --- | --- |
| Espace / Maj+Espace | Lire ou arrêter / lire en arrière |
| ← → | Une image en arrière / en avant |
| Ctrl+← → | Dix images en arrière / en avant |
| Maj+← → | Une seconde en arrière / en avant |
| Début / Fin | Début / fin de la vidéo |
| I / O | Marquer IN / OUT |
| S | Couper au curseur |
| F | Arrêt sur image |
| V | Vitesse de la portion IN-OUT |
| T / R / E / A | Texte / cadre / ovale / flèche |
| N / Maj+N | Point numéroté avec numéros / avec lettres |
| C / Maj+C | Liaison avec rectangles / avec ovales (page Images) |
| Z / Maj+Z | Zoom rectangulaire / ovale |
| P / K | Pixellisation rectangulaire / ovale |
| L | Logo et opérateur |
| Suppr | Supprimer la sélection (ou la portion IN-OUT) |
| Échap | Annuler le tracé en cours |
| Ctrl+Z / Ctrl+Y | Annuler / rétablir |
| Ctrl+N / Ctrl+O / Ctrl+S / Ctrl+Maj+S | Nouveau / ouvrir / enregistrer / enregistrer sous (dans la page Images : le projet d'images) |
| Ctrl+I | Importer une vidéo |
| Ctrl+V | Coller une image depuis le presse-papiers (page Images) |
| Ctrl+E | Exporter MP4 |

| Souris | Où | Action |
| --- | --- | --- |
| Molette | Aperçu | Une image en avant ou en arrière |
| Ctrl+molette | Aperçu | Agrandit la vue |
| Glisser sur un point vide, bouton central | Aperçu agrandi | Déplace la vue |
| Double-clic | Texte dans l'aperçu | Réécrit le texte |
| Ctrl+molette | Chronologie | Agrandit la chronologie |
| Molette / Alt+glisser / bouton central | Chronologie | Défile horizontalement |
| Maj+molette, molette sur les noms | Chronologie | Fait défiler l'audio et les effets verticalement |
| Clic droit | Barre d'un effet | Prolonger jusqu'au curseur / arrêter au curseur |
| Clic droit | Image clé ou point | Efface |
| Molette / glisser | Photo dans la page Images | Agrandit / déplace la photo dans le cadre |
| Clic sur un cadre vide, fichier glissé | Page Images | Charge une photo |

## 19. Les fichiers de projet

Le projet **vidéo** est un fichier JSON contenant les clips, les pistes audio,
les effets (avec les trajets du suivi et les images clés) et les chemins des
fichiers utilisés. Les vidéos, les fichiers audio et les images ne sont pas
copiés dans le projet : laissez-les où ils sont tant que le travail n'est pas
terminé. La vidéo exportée, en revanche, est un MP4 autonome.

Le projet d'**images** est un fichier JSON (`kind: editsimple-images`) avec la
disposition, le format, la légende, les cadres avec leur photo et les
annotations, plus le dossier `<nom>_file` à côté avec les copies des photos,
des images superposées et du logo : le projet est autonome et peut être
déplacé avec son dossier. Les valeurs du JSON (coordonnées, couleurs, notes,
étiquettes des points) se modifient avec un éditeur de texte.

---

EditSimple est un logiciel libre, distribué sous la licence GNU GPL version 3
avec des conditions supplémentaires d'attribution de l'auteur (voir `LICENSE`
et `NOTICE`). ffmpeg et VitTrack sont des programmes séparés avec leurs
propres licences.
