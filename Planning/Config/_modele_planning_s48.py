# -*- coding: utf-8 -*-
"""Générateur du planning hebdomadaire WILBOW (A4 paysage, 1 page).
Format : 1 colonne = 1 jour. Les équipes/jointeurs sont rappelés dans chaque colonne,
au-dessus de leurs JMS. Pas de colonne de gauche.

Une SEULE source de données (PLANNING, avec le code C@W attaché à chaque
prestation via caw=) alimente DEUX documents distincts :
  - le planning chantier (mode "site")
  - le Check in @ Work pour le secrétariat (mode "caw")
Comme ça les deux PDF ne peuvent plus diverger entre eux."""
import datetime, sys, os, base64, html as H
from zoneinfo import ZoneInfo

# Logo : fichier "logo_wilbow.png" place a cote de ce script
_D = os.path.dirname(os.path.abspath(__file__))
LOGO = next((os.path.join(_D, f) for f in ("logo_wilbow.jpg", "logo_wilbow.png")
             if os.path.exists(os.path.join(_D, f))), None)
LOGO_B64 = base64.b64encode(open(LOGO, "rb").read()).decode() if LOGO else None
LOGO_MIME = "jpeg" if LOGO and LOGO.endswith(".jpg") else "png"

JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]

# ----------------------------------------------------------------- RESSOURCES
RESSOURCES = [
    dict(id="E1", label="Soufflage — Équipe 1", noms=["Bolmain Mickael", "Petit Gauthier"],
         c="#1d4ed8", bg="#eff6ff"),
    dict(id="E2", label="Soufflage — Équipe 2", noms=["Dominguez Miguel", "Feller Sam"],
         c="#0f766e", bg="#f0fdfa", fin_bloc=True),
    dict(id="JM", label="Jointeur", noms=["Meurisse Johan"], c="#c2410c", bg="#fff7ed"),
    dict(id="PM", label="Jointeur", noms=["Mattiuz Pierre"], c="#be123c", bg="#fff1f2"),
    dict(id="DP", label="Jointeur", noms=["Panait Dan"], c="#0369a1", bg="#f0f9ff"),
    dict(id="FH", label="Jointeur", noms=["Hanikenne Florian"], c="#4d7c0f", bg="#f7fee7"),
    dict(id="AN", label="Jointeur", noms=["Andreï"], c="#7e22ce", bg="#faf5ff"),
    dict(id="GA", label="Magasinier", noms=["Avenia Geoffrey"], c="#57534e", bg="#fafaf9",
         defaut="Dépôt", compact=True),
]

# ------------------------------------------------------------------- DONNEES
SEMAINE = 48
LUNDI = datetime.date(2026, 11, 23)
# Horodatage automatique : date + heure de generation (heure belge)
MAJ = datetime.datetime.now(ZoneInfo("Europe/Brussels"))

# caw= : nom du code Check in @ Work (clef du dict CODES). Sert a alimenter
# automatiquement le 2e PDF (secretariat) sans dict separe a maintenir a la main.
J = lambda jms, lib, note=None, t=None, url=None, q=None, caw=None: dict(
    jms=jms, lib=lib, note=note, t=t, url=url, q=q, caw=caw)
X = lambda lib, note=None, t=None, url=None, q=None, sub=None, caw=None: dict(
    jms=None, lib=lib, note=note, t=t, url=url, q=q, sub=sub, caw=caw)
A = lambda motif, q=None: dict(ligne_abs=motif, q=q)   # absence sur une partie de la journee
NUIT  = "Nuit 22h00–06h00"
JOUR  = "Journée"
MATIN = "Matin"
AM    = "Après-midi"

# Liens monday.com : n JMS -> URL de l item (https://wilbow.monday.com/boards/<board>/pulses/<item>)
LIENS = {
    "690165": "https://wilbow.monday.com/boards/5089236279/pulses/3304713532",
    "680993": "https://wilbow.monday.com/boards/5089236279/pulses/3285668548",
    "631501": "https://wilbow.monday.com/boards/5089236279/pulses/3309938588",
    "687329": "https://wilbow.monday.com/boards/5089236279/pulses/3221987591",
    "535147": "https://wilbow.monday.com/boards/5089236279/pulses/2777940249",
    "680552": "https://wilbow.monday.com/boards/5089236279/pulses/3308918299",
    "645656": "https://wilbow.monday.com/boards/5089236279/pulses/3329942831",
    "677406": "https://wilbow.monday.com/boards/5089236279/pulses/2908681917",
    "649647": "https://wilbow.monday.com/boards/5089236279/pulses/3301749306",
    "652658": "https://wilbow.monday.com/boards/5089236279/pulses/2967044016",
    "662190": "https://wilbow.monday.com/boards/5089236279/pulses/3332057368",
    "675238": "https://wilbow.monday.com/boards/5089236279/pulses/3158202616",
    "688836": "https://wilbow.monday.com/boards/5089236279/pulses/3211258684",
    "690640": "https://wilbow.monday.com/boards/5089236279/pulses/3263534972",
    "679615": "https://wilbow.monday.com/boards/5089236279/pulses/3361311624",
    "667920": "https://wilbow.monday.com/boards/5089236279/pulses/3051265437",
}
# Liens des chantiers sans numero JMS
CAT   = "https://wilbow.monday.com/boards/5089236279/pulses/3012698475"  # Fibre connexion Caterpillar Gensets
SIGN  = "https://wilbow.monday.com/boards/5089236279/pulses/2832088996"  # SignaDyn - Zone D - Soufflage et Soudage reste zone D
FH32  = "https://wilbow.monday.com/boards/5089236279/pulses/2986868036"  # FH 32 FEED-IN
FH40 = "https://wilbow.monday.com/boards/5089236279/pulses/3288631715"  # FH 40 Feed-In
NR1083A = "https://wilbow.monday.com/boards/5089236279/pulses/3372322753"  # NR1083A
ROP   = "https://wilbow.monday.com/boards/5089236279/pulses/2697093519"  # ROP BTV
HERON = "https://wilbow.monday.com/boards/5089236279/pulses/3151190410"  # SWDE TEGEC Test pression Héron
MOVE41 = "https://wilbow.monday.com/boards/5089236279/pulses/3218880657"  # Vérification Move Rop 41FEX
VICINAL = "https://wilbow.monday.com/boards/5089236279/pulses/3159304163"  # 603753 + 671456, rue Du Vicinal, Clavier
FH44 = "https://wilbow.monday.com/boards/5089236279/pulses/3241665311"  # FH 44 Feed-in
HT1517C = "https://wilbow.monday.com/boards/5089236279/pulses/3264374398"  # HT 1517C
BORNESLG = "https://wilbow.monday.com/boards/5089236279/pulses/3297165250"  # Bornes Liege Expo
VALBENOIT = "https://wilbow.monday.com/boards/5089236279/pulses/3292906173"  # Val Benoit et Grosses-Battes CCTV
DIGN = "https://wilbow.monday.com/boards/5089236279/pulses/2725054102"  # 4020 Leman/Digneffe CA120
FEXHE = "https://wilbow.monday.com/boards/5089236279/pulses/2958713654"  # 622272 - IS_MP Cable definitif branche 12835


ABS = lambda motif: dict(absence=motif)
BARRE = dict(barre=True)  # case barrée en diagonale : personne partie / plus dispo

# ---- Codes Check in @ Work (source : "Code Check-in @ Work.pdf") -------------
CODES = {
    "BTO":                "1Y102TG6Z4BDZ",
    "APK 5.1":            "1Y102Q9PUF4RZ",
    "APK 5.2":            "1Y102Q9PUQF1Z",
    "FIFTHNET":           "1Y101P4M8XGQZ",
    "EQUANS-CAMERA-CCTV": "1Y100001PT2KZ",
    "EQUANS TEC":         "1Y102RU2G2V2Z",
    "EQUANS VILLE LIEGE": "1Y102W09AS72Z",
    "TEC VILLE LIEGE":    "1Y102VKAJXDPZ",
    "CIRCUIT FANCORCHAMPS":"1Y102HQPJ7BMZ",
    "PANDA+":             "1Y101X196YRXZ",
    "EOLIENNES SPRIMONT": "1Y102T9G0HRWZ",
    "SWDE BIERSET":       "1Y102QB6APTGZ",
    "SWDE VIELSALM":      "1Y102LLQH64XZ",
    "SWDE VILLERS":       "1Y102NZJETTAZ",
    "SWDE HUCCORGNE":     "1Y102QZML7WGZ",
    "GO FIBER":           "1Y102XHX3W2MZ",
    "CATERPILLAR":        "1Y102SV8BK22Z",
    # Releve sur la declaration de travaux affichee sur site (photo du
    # 09/11) : Bureau d Electronique Appliquee, rue Louis Plescia, Ougree.
    # Code confirme par Geoffrey le 09/11.
    "BEA OUGRÉE":         "1Y102UW3PMQCZ",
    # Prestation sans code Check in @ Work : le secretariat ne doit rien
    # encoder. Rendue explicitement plutot que laissee vide.
    "PAS DE CODE C@W":    "",
    # Le code existe mais n est pas encore connu : distinct du precedent.
    "C@W À DÉTERMINER":   "",
}

# Aucune substitution d equipe cette semaine : les entetes restent ceux de
# RESSOURCES.
# Lundi 23/11 : Fabrice Gaspard remplace Miguel Dominguez, absent.
# Lundi 23/11 : Miguel absent. Sam part avec l Equipe 1 sur le 679615, et
# l Equipe 2 devient Fabrice Gaspard, Giuseppe Caruso et Geoffrey Avenia —
# les trois nommes dans l entete, choix de Geoffrey du 20/11 (Caruso y
# figure donc, par exception a la regle de la pastille).
NOMS_OVERRIDE = {
    ("E1", 0): ["Bolmain Mickael", "Petit Gauthier", "Feller Sam"],
    ("E2", 0): ["Gaspard Fabrice", "Caruso Giuseppe", "Avenia Geoffrey"],
    # 24/11 : Miguel absent ce mardi, Sam part en Equipe 1. L Equipe 2 n a
    # donc plus personne : son entete ne garde que Miguel, sa case est barree.
    ("E1", 1): ["Bolmain Mickael", "Petit Gauthier", "Feller Sam"],
    ("E2", 1): ["Dominguez Miguel"],
}



PLANNING = {
    # Le 680993 de Pierre a ete DEPLACE au vendredi 20/11, en S47 (10/11) :
    # son lundi redevient gris.

    # Lundi 23/11 : l Equipe 1 sur le 679615 (Feed out Eupen FH01 - Raeren
    # FH07), avec Sam en renfort. C@W GO FIBER confirme le 20/11.
    ("E1", 0): [J("679615", "Feed out EUPEN FH01 — RAEREN FH07", caw="GO FIBER")],

    # Mardi 24/11 : le 690165 (MB GROUPE, rue de la Vieille Fosse 60,
    # Flemalle) passe de l Equipe 2 a l Equipe 1 le 13/11. C@W PANDA+.
    ("E1", 1): [J("690165", "OL — MB GROUPE, Rue de la Vieille Fosse 60, Flémalle",
                  caw="PANDA+")],

    # 25/11 : l Equipe 1 retourne sur le 679615 (Feed out Eupen FH01 -
    # Raeren FH07) ce mercredi, puis passe au FH 32 Feed-In le jeudi 26.
    ("E1", 2): [J("679615", "Feed out EUPEN FH01 — RAEREN FH07", caw="GO FIBER")],
    # 25/11 : le FH 32 Feed-In passe au MATIN, le 680993 (Ribeaucourt,
    # Seraing) prend l APRES-MIDI du jeudi. Le vendredi, l Equipe 1 rejoint
    # l Equipe 2 sur le 680552 (Huy), qui se fait donc sur deux jours.
    ("E1", 3): [
        X("FH 32 Feed-In", url=FH32, q=MATIN, caw="FIFTHNET"),
        J("680993", "RZ FTTH E2E 4 SDU — Rue du Bief 43-49, Seraing (Ribeaucourt)",
          q=AM, caw="PANDA+"),
    ],
    ("E1", 4): [J("680552", "FQ — BB Neuron K12836, Huy (3-81CH90950)",
                  caw="PANDA+")],

    # Lundi 23 et mardi 24/11 : l Equipe 2 poursuit le 631501 (INTERCO
    # BURGRE-01 BUR50), son chantier du vendredi 20/11 en S47. Le 667920,
    # un temps pose ici, est retire (changement du 13/11). C@W PANDA+.
    # Le lundi, Miguel est absent et remplace par Fabrice Gaspard : l entete
    # du jour le dit, et la case porte l absence nominative en dessous.
    # 20/11 : le 680552 (BB Neuron, Huy) REMPLACE le 631501 le lundi. Il
    # n avait pas pu se faire en S47, Miguel etant absent les deux jours
    # prevus. Le 631501 ne reste donc qu au mardi.
    # 22/11 : a son tour le 680552 est REMPLACE par le 645656 (Burg-Reuland
    # FH01 cluster 16), C@W GO FIBER. Le trio du lundi le faisait deja les
    # 18 et 19/11 en S47. Le 680552 se retrouve donc de nouveau sans date.
    ("E2", 0): [
        J("645656", "Burg-Reuland FH01 cluster 16", caw="GO FIBER"),
        A("ABSENT", q="M. Dominguez"),
    ],
    # 20/11 : le 631501 est aussi au mercredi.
    # 24/11 : Miguel est ABSENT ce mardi et Sam passe en Equipe 1 : la case
    # du mardi est barree et le 631501 y est ANNULE. Il reste au mercredi.
    **{("E2", i): [J("631501", "INTERCO BURGRE-01 BUR50", caw="PANDA+")]
       for i in (2,)},
    ("E2", 1): ABS("ABSENT"),

    # 25/11 : l Equipe 2 reprend le 680552 (BB Neuron K12836, Huy) le jeudi
    # 26/11 — il etait sans date depuis le 22/11 — et le 667920 (FOX FEED
    # OUT BUL 1 - BUL 2) le vendredi 27/11. Le 667920 est un chantier BTO :
    # C@W BTO, et RIEN n est encode sur Monday pour lui.
    ("E2", 3): [J("680552", "FQ — BB Neuron K12836, Huy (3-81CH90950)",
                  caw="PANDA+")],
    ("E2", 4): [J("667920", "FOX FEED OUT BUL 1 - BUL 2", caw="BTO")],

    # 20/11 : replanification des chantiers perdus de la S47.
    # Lundi 23/11 : Johan reprend le 535147 et le FH 40 Feed-In.
    # 20/11 : le 677406 (Saint-Vith FH04) prend le lundi ; le 535147 et le
    # FH 40, qui y etaient, sont decales au mardi. C@W GO FIBER.
    # 23/11 : Johan est MALADE ce lundi. Sa case passe en MALADIE et le
    # 677406 est reporte au mercredi 25/11.
    ("JM", 0): ABS("MALADIE"),

    # Mardi 24/11 : Johan sur le NR1083A (chantier sans numero JMS :
    # l intitule est cliquable, C@W PANDA+), puis sur le 535147 et le
    # FH 40 Feed-In decales du lundi.
    # 20/11 : le 535147 et le FH 40 repartent au MERCREDI ; le mardi ne
    # garde que le NR1083A.
    # 24/11 : Johan est encore MALADE ce mardi. Le NR1083A passe a Pierre.
    ("JM", 1): ABS("MALADIE"),
    # 23/11 : le 535147 et le FH 40 Feed-In passent a Pierre le lundi ;
    # le mercredi de Johan recoit le 677406, reporte de son lundi de maladie.
    # 25/11 : Johan est MALADE TOUTE LA SEMAINE. Ses trois derniers jours
    # passent en MALADIE et ses chantiers sont ANNULES : le 677406 du
    # mercredi, le 688836 du jeudi et le 690640 du vendredi, ces deux
    # derniers avec M. Wilvers.
    ("JM", 2): ABS("MALADIE"),

    # Jeudi 26/11 : Pierre reprend le 687329 (DSTNY BE, Engis).
    # 26/11 : le FH 40 Feed-In s ajoute a l APRES-MIDI, apres le 687329.
    ("PM", 3): [
        J("687329", "OL — DSTNY BE, Rue du Parc Industriel 3, Engis",
          caw="PANDA+"),
        X("FH 40 Feed-In", url=FH40, q=AM, caw="FIFTHNET"),
    ],

    # 20/11 : nuit du jeudi 26 au vendredi 27/11, Johan avec Mike Wilvers
    # sur le 675238 (Ciney-Jemelle). Mike n a pas de ligne RESSOURCES : il
    # apparait en pastille. Le bloc est a cheval sur les deux jours.
    # 20/11 : la nuit passe de Johan a Dan, toujours avec Mike Wilvers.
    # Johan perd donc sa nuit du jeudi et sa recuperation du vendredi ; ses
    # deux cases recoivent les deux ROP annules le 16/11, avec M. Wilvers.
    ("JM", 3): ABS("MALADIE"),
    ("JM", 4): ABS("MALADIE"),

    # 20/11 : Pierre sur le 649647 (rue de Lexhy, Fexhe) lundi et mardi.
    # 23/11 : son lundi est ANNULE — il reprend le 535147 et le FH 40
    # Feed-In de Johan, malade. Le 649647 ne garde que le mardi.
    # 24/11 : le 649647 de Pierre passe a Florian et Andrei ; Pierre
    # reprend le NR1083A de Johan, malade.
    ("PM", 1): [X("NR1083A", url=NR1083A, caw="PANDA+")],
    ("PM", 0): [
        J("535147", "FTTH BF Liège — Feed-out FOx FH44/FH45, Rue de Visé",
          caw="PANDA+"),
        X("FH 40 Feed-In", url=FH40, caw="FIFTHNET"),
    ],

    # 25/11 : Pierre prend le FH 32 Feed-In et le FH 40 Feed-In le
    # vendredi 27/11, en jointage. Sa case du vendredi etait grise.
    ("PM", 4): [
        X("FH 32 Feed-In", url=FH32, caw="FIFTHNET"),
        X("FH 40 Feed-In", url=FH40, caw="FIFTHNET"),
    ],

    # Mercredi 25/11 : Pierre passe sur le meme 690165, apres l Equipe 2.
    ("PM", 2): [J("690165", "OL — MB GROUPE, Rue de la Vieille Fosse 60, Flémalle",
                  caw="PANDA+")],

    # Dan, Florian et Andrei : BTO les cinq jours, reconduction habituelle.
    # Lundi 23/11 : Avenia Geoffrey part en Equipe 2 : sa ligne le dit.
    ("GA", 0): ABS("→ ÉQUIPE 2"),
    # 25/11 : Geoffrey Avenia quitte le depot ce mercredi et rejoint le
    # 631501 (INTERCO BURGRE-01 BUR50) avec Fabrice Gaspard et Giuseppe
    # Caruso, en renfort de l Equipe 2 qui y est deja. C@W PANDA+.
    ("GA", 2): [J("631501", "INTERCO BURGRE-01 BUR50",
                  "+ G. Caruso · F. Gaspard", "commun", caw="PANDA+")],
    # 26/11 : le trio reste sur le 631501 le jeudi. L Equipe 2 est ailleurs
    # ce jour-la (680552) : ils y sont donc seuls.
    ("GA", 3): [J("631501", "INTERCO BURGRE-01 BUR50",
                  "+ G. Caruso · F. Gaspard", "commun", caw="PANDA+")],

    # Dan : BTO, sauf le jeudi ou il garde son BTO de jour ET fait la nuit
    # du 26 au 27/11 sur le 675238, avec Mike Wilvers (20/11). Le jeudi est
    # exclu de la comprehension, sinon elle ecraserait la nuit.
    # 24/11 : Dan est ABSENT du mardi 24 au vendredi 27/11. Son lundi 23
    # reste en BTO. Sa nuit du jeudi 26 au 27 passe a Florian.
    ("DP", 0): [X("BTO", caw="BTO")],
    **{("DP", i): ABS("ABSENT") for i in (1, 2, 3, 4)},

    # Florian : BTO, sauf le mardi 24/11 (649647, repris a Pierre) et le
    # jeudi ou il garde son BTO de jour ET fait la nuit du 26 au 27/11 sur
    # le 675238 avec Mike Wilvers, a la place de Dan absent (24/11). Les
    # deux jours sont exclus de la comprehension, sinon elle les ecraserait.
    **{("FH", i): [X("BTO", caw="BTO")] for i in (0,)},
    # 26/11 : le 662190 (Herstal) prend aussi le vendredi 27/11, pour
    # Florian comme pour Andrei. Le BTO disparait de leur vendredi.
    ("FH", 4): [J("662190", "RZ FTTH DIST Herstal — Rue Jean Vercheval 39, Bloc A",
                  caw="PANDA+")],
    ("FH", 1): [J("649647",
                  "IZ FTTH 1 MDU 20 BU + 1 BU — Rue de Lexhy, Fexhe-le-Haut-Clocher (Eloy)",
                  caw="PANDA+")],
    # 26/11 : le BTO du jeudi laisse place au 652658 (Donceel), pour
    # Florian comme pour Andrei. La nuit du 26 au 27 reste inchangee.
    # 26/11 : le 662190 (Herstal) s ajoute a l APRES-MIDI, apres le 652658.
    ("FH", 3): [
        J("652658", "Rue du Ruisseau 28-26-24 — Donceel", caw="PANDA+"),
        J("662190", "RZ FTTH DIST Herstal — Rue Jean Vercheval 39, Bloc A",
          q=AM, caw="PANDA+"),
        J("675238", "BBN 12310B — Ciney-Jemelle",
          "+ M. Wilvers", "commun", q=NUIT, caw="PANDA+"),
    ],
    # 25/11 : Florian et Andrei poursuivent le 649647 le MATIN, puis
    # enchainent sur le 652658 (Donceel) l APRES-MIDI.
    ("FH", 2): [
        J("649647",
          "IZ FTTH 1 MDU 20 BU + 1 BU — Rue de Lexhy, Fexhe-le-Haut-Clocher (Eloy)",
          q=MATIN, caw="PANDA+"),
        J("652658", "Rue du Ruisseau 28-26-24 — Donceel", q=AM, caw="PANDA+"),
    ],
    # Andrei : BTO, sauf le lundi 23/11 ou il est absent (16/11). Le lundi
    # est exclu de la comprehension, sinon elle ecraserait son absence.
    ("AN", 4): [J("662190", "RZ FTTH DIST Herstal — Rue Jean Vercheval 39, Bloc A",
                  caw="PANDA+")],
    ("AN", 3): [
        J("652658", "Rue du Ruisseau 28-26-24 — Donceel", caw="PANDA+"),
        J("662190", "RZ FTTH DIST Herstal — Rue Jean Vercheval 39, Bloc A",
          q=AM, caw="PANDA+"),
    ],
    ("AN", 2): [
        J("649647",
          "IZ FTTH 1 MDU 20 BU + 1 BU — Rue de Lexhy, Fexhe-le-Haut-Clocher (Eloy)",
          q=MATIN, caw="PANDA+"),
        J("652658", "Rue du Ruisseau 28-26-24 — Donceel", q=AM, caw="PANDA+"),
    ],
    ("AN", 0): ABS("ABSENT"),
    # 24/11 : Andrei fait le 649647 avec Florian, ce mardi seulement.
    ("AN", 1): [J("649647",
                  "IZ FTTH 1 MDU 20 BU + 1 BU — Rue de Lexhy, Fexhe-le-Haut-Clocher (Eloy)",
                  caw="PANDA+")],

    # Tout le reste de la semaine est a confirmer : cases grisees.
}

# --------------------------------------------------------------------- RENDU
NB_JOURS = 6 if any(k[1] == 5 for k in PLANNING) else 5
LARG = 100 / NB_JOURS

ABS_STYLE = {
    "CONGÉ":     ("#e2e8f0", "#475569"),
    "MALADIE":   ("#fee2e2", "#b91c1c"),
    "FORMATION": ("#ede9fe", "#5b21b6"),
    # Prestation sans code C@W : rendue comme un statut, elle ne genere aucune
    # ligne sur le tableau secretariat.
    "FRANCE ÉLÉVATEURS": ("#e2e8f0", "#475569"),
    "RÉCUP":     ("#cffafe", "#0e7490"),
    "ABSENT":    ("#e2e8f0", "#475569"),
    "EN ATTENTE":("#fef3c7", "#92400e"),
    "→ ÉQUIPE 1":("#dbeafe", "#1d4ed8"),
    "→ ÉQUIPE 2":("#ccfbf1", "#0f766e"),
}

def cellule(r, i, DATA=None, mode="site"):
    noms_jour = NOMS_OVERRIDE.get((r["id"], i), r["noms"])
    if len(noms_jour) > 1:   # equipe : label sur sa ligne + noms en dessous
        noms = "<br>".join(H.escape(n) for n in noms_jour)
        hdr = (f'<div class="rlabel" style="color:{r["c"]};">{H.escape(r["label"])}</div>'
               f'<div class="rname">{noms}</div>')
    else:                    # individuel : nom + role sur la meme ligne
        hdr = (f'<div class="rname">{H.escape(noms_jour[0])}'
               f'<span class="rtag" style="color:{r["c"]};">{H.escape(r["label"])}</span></div>')
    v = (DATA if DATA is not None else PLANNING).get((r["id"], i))
    # Une nuit deborde sur la journee suivante. Pour qu elle ne masque rien,
    # la case du lendemain reserve la meme hauteur : on y rejoue la
    # prestation de la veille sous forme de spacer invisible. Inutile si
    # cette case est vide, le bloc ne recouvrant alors aucun contenu.
    # Une case d absence ne passe pas par la boucle de rendu : impossible d y
    # reserver la hauteur. Dans ce cas la nuit reste dans sa propre journee
    # plutot que de masquer le motif d absence du lendemain.
    suivant = (DATA if DATA is not None else PLANNING).get((r["id"], i + 1))
    # Le bloc de nuit s ancre au bas du CONTENU de sa propre case, pas au bas
    # de la ligne : si la case du lendemain est plus chargee, il recouvrirait
    # son texte. On ne l affiche donc a cheval que si le lendemain est vide ou
    # porte une simple absence, dont la hauteur est comparable.
    # 04/11 : le bloc de nuit est desormais TOUJOURS a cheval, meme quand le
    # lendemain porte des prestations. Le spacer invisible reserve sa hauteur
    # dans les deux cases, il se pose donc sous les chantiers de jour sans
    # recouvrir leur texte.
    peut_cheval = True
    veille = (DATA if DATA is not None else PLANNING).get((r["id"], i - 1)) if i else None
    reports = [dict(d, _spacer=True) for d in veille
               if isinstance(d, dict) and str(d.get("q") or "").lower().startswith("nuit")
               ] if isinstance(veille, list) else []

    # Une absence se rend normalement hors de la boucle des jobs, ce qui
    # empeche d y reserver la hauteur. Quand une nuit de la veille deborde
    # ici, on la bascule dans le flux des jobs via A(), qui sait l afficher.
    if isinstance(v, dict) and "absence" in v and reports:
        v = [A(v["absence"])] + reports

    # Meme probleme pour une case vide : le bandeau "aucun dossier confirme" se
    # rend hors de la boucle, donc sans reserver de hauteur, et le bloc de nuit
    # de la veille venait le recouvrir. Le bandeau est donc supprime sur ce
    # jour-la : la personne termine sa nuit ce matin, la case n est pas vide au
    # sens du planning. Seul le spacer invisible subsiste, ce qui aligne
    # exactement le bloc sur les deux journees.
    prefixe_vide = ""
    if v is None and reports:
        v = list(reports)

    # Symetrique du probleme ci-dessus, cote journee de DEPART. Le bloc de nuit
    # s ancre au bas du contenu de sa propre case. Si le lendemain porte une
    # absence, son contenu est plus haut d une pastille : le bloc remonte donc
    # au-dessus d elle et la recouvre. On reserve ici la hauteur de cette
    # pastille, en tete de la case de depart, pour aligner les deux journees.
    prefixe_nuit = ""
    # Uniquement si la case ne porte QUE la nuit : des qu elle contient aussi
    # des prestations de jour, elle est deja plus haute que la pastille du
    # lendemain et ce decalage n a plus lieu d etre — il ferait deborder la case.
    if (isinstance(v, list) and peut_cheval
            and isinstance(suivant, dict) and "absence" in suivant
            and v and all(str(d.get("q") or "").lower().startswith("nuit")
                          for d in v if isinstance(d, dict))):
        prefixe_nuit = (f'<div class="abs absspacer">'
                        f'<div class="absl">{H.escape(suivant["absence"])}</div></div>')

    if v is None:
        txt = r.get("defaut", "—")
        body = f'<div class="body empty"><div class="dash">{txt}</div></div>'
    elif isinstance(v, dict) and v.get("barre"):
        body = '<div class="body empty barre-body"></div><div class="barre-overlay"></div>'
    elif isinstance(v, dict) and "absence" in v:
        bg, fg = ABS_STYLE.get(v["absence"], ("#e2e8f0", "#475569"))
        body = (f'<div class="body abs" style="background:{bg};">'
                f'<div class="absl" style="color:{fg};">{H.escape(v["absence"])}</div></div>')
    else:
        jobs, nuits = [], []
        for d in v:
            per = ""
            n_inline = ""
            if d.get("q"):
                k = "nuit" if d["q"].lower().startswith("nuit") else "jour"
                # si une note accompagne la prestation, on la colle au badge
                # jour/nuit pour economiser une ligne
                if d.get("note"):
                    n_inline = (f'<span class="note inline n-{d["t"]}">'
                                f'{H.escape(d["note"])}</span>')
                per = (f'<div class="perline"><span class="per {k}">'
                       f'{H.escape(d["q"])}</span>{n_inline}</div>')
            if d.get("ligne_abs"):
                bg, fg = ABS_STYLE.get(d["ligne_abs"], ("#e2e8f0", "#475569"))
                if d.get("q") and not d["q"].lower().startswith(("nuit", "journ")):
                    # absence nominative : nom + statut sur une seule ligne
                    jobs.append(f'<div class="job compactabs">'
                                f'<span class="qui">{H.escape(d["q"])}</span>'
                                f'<span class="statut" style="background:{bg}; color:{fg};">'
                                f'{H.escape(d["ligne_abs"])}</span></div>')
                else:
                    jobs.append(f'<div class="job">{per}<div class="ligneabs" '
                                f'style="background:{bg}; color:{fg};">'
                                f'{H.escape(d["ligne_abs"])}</div></div>')
                continue
            n = "" if (n_inline or not d.get("note")) else \
                f'<span class="note n-{d["t"]}">{H.escape(d["note"])}</span>'

            if mode == "caw":
                # mode secretariat : on affiche le nom du code C@W en titre,
                # et le code en detail. Aucune info chantier/JMS.
                nom_caw = d.get("caw")
                titre = H.escape(nom_caw) if nom_caw else "?"
                cls = "jms nonum"
                detail = CODES.get(nom_caw, "") if nom_caw else ""
                lib = f'<div class="lib">{H.escape(detail)}</div>' if detail else ""
                if d.get("_spacer"):
                    # Hauteur reservee pour la nuit de la veille : jamais visible.
                    nuits.append(f'<div class="job chevalspacer">{per}<div class="{cls}">{titre}</div>{lib}{n}</div>')
                elif peut_cheval and (d.get("q") or "").lower().startswith("nuit"):
                    # La nuit est ancree en bas de la ligne, a cheval sur les deux
                    # journees. Le spacer invisible qui la suit reserve sa hauteur en
                    # fin de case, dans la journee de depart comme dans la suivante.
                    nuits.append(f'<div class="job cheval">{per}<div class="{cls}">{titre}</div>{lib}{n}</div>')
                    nuits.append(f'<div class="job chevalspacer">{per}<div class="{cls}">{titre}</div>{lib}{n}</div>')
                else:
                    jobs.append(f'<div class="job">{per}<div class="{cls}">{titre}</div>{lib}{n}</div>')
                continue

            url = d.get("url") or (LIENS.get(d["jms"]) if d["jms"] else None)
            titre = f'JMS {d["jms"]}' if d["jms"] else H.escape(d["lib"])
            cls = "jms" if d["jms"] else "jms nonum"
            if url:
                titre = (f'<a href="{H.escape(url, quote=True)}">{titre}'
                         f'<span class="ext">↗</span></a>')
            detail = d["lib"] if d["jms"] else d.get("sub")
            lib = f'<div class="lib">{H.escape(detail)}</div>' if detail else ""
            if d.get("_spacer"):
                # Hauteur reservee pour la nuit de la veille : jamais visible.
                nuits.append(f'<div class="job chevalspacer">{per}<div class="{cls}">{titre}</div>{lib}{n}</div>')
            elif peut_cheval and (d.get("q") or "").lower().startswith("nuit"):
                # La nuit est ancree en bas de la ligne, a cheval sur les deux
                # journees. Le spacer invisible qui la suit reserve sa hauteur en
                # fin de case, dans la journee de depart comme dans la suivante.
                nuits.append(f'<div class="job cheval">{per}<div class="{cls}">{titre}</div>{lib}{n}</div>')
                nuits.append(f'<div class="job chevalspacer">{per}<div class="{cls}">{titre}</div>{lib}{n}</div>')
            else:
                jobs.append(f'<div class="job">{per}<div class="{cls}">{titre}</div>{lib}{n}</div>')
        body = ('<div class="body">' + prefixe_vide + prefixe_nuit
                + "".join(jobs + nuits) + "</div>")

    return (f'<td style="border-left-color:{r["c"]}; background:{r["bg"]}; position:relative;">'
            f'<div class="hdr">{hdr}</div>{body}</td>')

ths = "".join(
    f'<th class="day">{JOURS[i]}<span>{(LUNDI + datetime.timedelta(days=i)):%d/%m}</span></th>'
    for i in range(NB_JOURS))

def fusionner_caw(DATA):
    """Page Check in @ Work : le secretariat lit des codes, pas des chantiers.
    Deux prestations strictement identiques (meme code, meme quart, meme note)
    dans la meme case ne lui apprennent rien de plus -> on n en garde qu une.
    Rien n est fusionne des que le code, le quart ou la note different."""
    fusionne = {}
    for cle, v in DATA.items():
        if isinstance(v, list):
            vus, garde = set(), []
            for d in v:
                k = (d.get("caw"), d.get("q"), d.get("note"), d.get("ligne_abs"))
                if k in vus:
                    continue
                vus.add(k)
                garde.append(d)
            v = garde
        fusionne[cle] = v
    return fusionne

def make_rows(DATA, mode="site"):
    if mode == "caw":
        DATA = fusionner_caw(DATA)
    return "".join(
        f'<tr class="{"grp-end " if r.get("fin_bloc") else ""}{"compact" if r.get("compact") else ""}">'
        + "".join(cellule(r, i, DATA, mode) for i in range(NB_JOURS)) + "</tr>"
        for r in RESSOURCES)

fin = LUNDI + datetime.timedelta(days=NB_JOURS - 1)
MOIS = ["janvier","février","mars","avril","mai","juin","juillet","août",
        "septembre","octobre","novembre","décembre"]
if LUNDI.month == fin.month:
    periode = f"Du lundi {LUNDI.day} au {JOURS[NB_JOURS-1].lower()} {fin.day} {MOIS[fin.month-1]} {fin.year}"
else:
    periode = (f"Du lundi {LUNDI.day} {MOIS[LUNDI.month-1]} au {JOURS[NB_JOURS-1].lower()} "
               f"{fin.day} {MOIS[fin.month-1]} {fin.year}")

PIED_JMS = ('<b style="color:#1d4ed8;">JMS en bleu ↗</b>'
            ' = cliquable, ouvre le dossier dans monday.com')

def build(HLIGNE, rows, badge="PLANNING CONFIRMÉ", soustitre=None, pied2=None):
  return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><style>
@page {{  /* S43 : polices reduites de 2% le 15/09/2026
   pour absorber les nuits et les recups sans rien supprimer. */
 size:A4 landscape; margin:4mm 7mm 3mm 7mm; }}
* {{ box-sizing:border-box; }}
body {{ font-family:"DejaVu Sans",Arial,sans-serif; margin:0; color:#111827; }}
.head {{ display:flex; align-items:center; justify-content:space-between;
        border-bottom:2.235pt solid #0f172a; padding-bottom:1.2mm; margin-bottom:1.6mm; }}
.brand {{ font-size:13pt; font-weight:800; letter-spacing:2.235pt; color:#0f172a; line-height:1;
         flex:0 0 auto; }}
.brand img {{ display:block; height:9mm; width:auto; border-radius:1mm; }}
.brand small {{ display:block; font-size:4.67pt; font-weight:600; letter-spacing:1.163pt; color:#64748b; margin-top:.7mm; }}
.title {{ text-align:center; }}
.title .wk {{ font-size:9.88pt; font-weight:800; color:#0f172a; letter-spacing:.4.471pt; }}
.title .dt {{ font-size:6.37pt; color:#475569; margin-top:.7mm; font-weight:600; }}
.badge {{ text-align:right; }}
.badge .tag {{ display:inline-block; background:#15803d; color:#fff; font-size:5.98pt; font-weight:800;
              padding:1.3mm 2.8mm; border-radius:1.2mm; letter-spacing:.5.364pt; }}
.badge .maj {{ font-size:5.06pt; color:#64748b; margin-top:1.1mm; }}

table {{ width:100%; border-collapse:collapse; table-layout:fixed; }}
col {{ width:{LARG:.4f}%; }}
th.day {{ background:#0f172a; color:#fff; font-size:7.12pt; font-weight:800; letter-spacing:.6.258pt;
         padding:1mm 1mm; border:0.626pt solid #0f172a; text-transform:uppercase; text-align:center; }}
th.day span {{ display:block; font-size:5.83pt; font-weight:600; color:#cbd5e1; letter-spacing:0; }}

td {{ border:0.626pt solid #cbd5e1; border-left-width:2.146pt; border-left-style:solid;
     border-bottom:1.43pt solid #0f172a; vertical-align:top; padding:1.0mm 1.4mm; height:{HLIGNE}mm; }}
tr.grp-end td {{ border-bottom:2.683pt solid #0f172a; }}
tr.compact td {{ height:auto; }}
tr:last-child td {{ border-bottom:1.43pt solid #0f172a; }}
.hdr {{ padding-bottom:.3mm; margin-bottom:.5mm; border-bottom:0.626pt solid rgba(15,23,42,.18); }}
.rlabel {{ font-size:4.45pt; font-weight:800; letter-spacing:.7.154pt; text-transform:uppercase; }}
.rtag {{ font-size:4.29pt; font-weight:800; letter-spacing:.6.258pt; text-transform:uppercase; margin-left:1.4mm; }}
.rname {{ font-size:5.83pt; font-weight:700; color:#0f172a; line-height:1.1; margin-top:.3mm; }}

.body {{ }}
.body.empty {{ background:#eef2f6; border:0.537pt solid #d5dde5; border-radius:.8mm;
              text-align:center; padding:.8mm 0; }}
.body.abs {{ border-radius:.8mm; text-align:center; padding:1.5mm 0; }}
/* Bandeau "aucun dossier" d une case vide qui doit en plus reserver la
   hauteur d une nuit de la veille : meme aspect que .body.empty. */
.dashbar {{ background:#eef2f6; border:0.537pt solid #d5dde5; border-radius:.8mm;
           text-align:center; padding:.8mm 0; }}
/* Hauteur reservee pour la pastille d absence du lendemain, dans la case qui
   porte la nuit : jamais visible. */
.absspacer {{ visibility:hidden; border-radius:.8mm; text-align:center; padding:1.5mm 0; }}
.absl {{ font-size:6.52pt; font-weight:800; letter-spacing:1.072pt; }}
.job {{ line-height:1.2; }}
.job + .job {{ margin-top:.35mm; padding-top:.35mm; border-top:0.537pt dashed #94a3b8; }}
.jms {{ font-size:6.21pt; font-weight:800; color:#0f172a; }}
.jms.nonum {{ font-size:6.05pt; line-height:1.18; letter-spacing:.25pt; }}
.jms a, .jms.nonum a {{ color:#1d4ed8; text-decoration:none; }}
.ext {{ font-size:5.06pt; margin-left:.8mm; color:#1d4ed8; }}
.lib {{ font-size:5.29pt; color:#334155; margin-top:.2mm; line-height:1.15; }}
.lib.code {{ letter-spacing:.2.683pt; color:#1e293b; }}
.note {{ display:inline-block; font-size:4.67pt; font-weight:700; padding:.35mm 1.2mm;
        border-radius:.8mm; margin-top:.6mm; letter-spacing:.2.683pt; }}
.n-renfort {{ background:#fef3c7; color:#92400e; border:0.447pt solid #fcd34d; }}
.n-commun {{ background:#e0e7ff; color:#3730a3; border:0.447pt solid #a5b4fc; }}
.n-prov {{ background:#fff7ed; color:#c2410c; border:0.537pt dashed #fb923c; }}
.n-alt {{ background:#f1f5f9; color:#475569; border:0.537pt dashed #94a3b8; }}
.note.inline {{ margin-top:0; margin-left:1.2mm; }}
/* Prestation de nuit : bloc a cheval sur la frontiere des deux journees.
   Le bloc visible est en position absolue ; le spacer, invisible mais dans le
   flux, reserve exactement la meme hauteur pour que la ligne ne deborde pas. */
.job.cheval {{ position:absolute; left:50%; width:100%; bottom:0.8mm; z-index:5; margin-top:0;
        background:#0f172a; border-radius:1.2mm; padding:0.7mm 1.4mm; border-top:0;
        box-shadow:0 0 0 .6mm #ffffff; }}
.job.cheval .jms {{ color:#93c5fd; }}
.job.cheval .lib {{ color:#cbd5e1; }}
.job.cheval .per.nuit {{ background:#334155; color:#fff; }}
.job.chevalspacer {{ visibility:hidden; padding:0.7mm 1.4mm; border-top:0; margin-top:0; }}
.perline {{ margin-bottom:.2mm; }}
.per {{ display:inline-block; font-size:4.29pt; font-weight:800; letter-spacing:.5.364pt;
      text-transform:uppercase; padding:.3mm 1.2mm; border-radius:.7mm; }}
.per.jour {{ background:#e2e8f0; color:#334155; }}
.per.nuit {{ background:#1e293b; color:#fff; }}
.compactabs {{ display:flex; align-items:center; justify-content:space-between; gap:1.5mm; }}
.qui {{ font-size:5.68pt; font-weight:700; color:#0f172a; }}
.statut {{ font-size:4.76pt; font-weight:800; letter-spacing:.5.364pt; padding:.35mm 1.4mm;
         border-radius:.8mm; white-space:nowrap; }}
.job + .job.compactabs {{ margin-top:.6mm; padding-top:.6mm; }}
.ligneabs {{ font-size:5.68pt; font-weight:800; letter-spacing:.8.048pt; text-align:center;
           border-radius:.8mm; padding:.7mm 0; }}
.dash {{ font-size:5.83pt; color:#8a97a6; font-weight:600; }}
.barre-overlay {{ position:absolute; top:0; left:0; right:0; bottom:0; pointer-events:none;
  background:linear-gradient(to top right, transparent calc(50% - 0.5mm), #94a3b8 calc(50% - 0.5mm),
  #94a3b8 calc(50% + 0.5mm), transparent calc(50% + 0.5mm)); }}

.foot {{ display:flex; justify-content:space-between; align-items:center; margin-top:1.2mm;
        padding-top:1mm; border-top:0.894pt solid #cbd5e1; font-size:5.06pt; color:#64748b; }}
.foot b {{ color:#334155; }}
.key {{ display:inline-block; width:3mm; height:2.2mm; background:#eef2f6; border:0.537pt solid #d5dde5;
       vertical-align:-.3mm; margin-right:.8mm; }}
</style></head><body>
<div class="head">
  <div class="brand">{('<img src="data:image/' + LOGO_MIME + ';base64,' + LOGO_B64 + '" alt="SA Wilbow">')
                      if LOGO_B64 else 'WILBOW<small>PLANNING DE SEMAINE</small>'}</div>
  <div class="title"><div class="wk">SEMAINE {SEMAINE}{soustitre or ""}</div><div class="dt">{periode}</div></div>
  <div class="badge"><div class="tag">{badge}</div>
    <div class="maj">Mis à jour le {MAJ:%d/%m/%Y} à {MAJ:%Hh%M}</div></div>
</div>
<table><colgroup>{'<col>' * NB_JOURS}</colgroup>
<tr>{ths}</tr>
{rows}
</table>
<div class="foot">
  <div><span class="key"></span><b>Case grisée</b> = aucun dossier confirmé à ce jour</div>
  <div>{pied2 or PIED_JMS}</div>
  <div>La version la plus récente fait foi</div>
</div></body></html>"""

from weasyprint import HTML as W
import math

def hauteur_page(rows, badge, soustitre, pied2, quoi):
    """Cherche la hauteur de ligne la plus confortable qui tienne sur UNE page."""
    def pages(h):
        open("/tmp/_pl47.html", "w", encoding="utf-8").write(
            build(h, rows, badge, soustitre, pied2))
        return len(W(filename="/tmp/_pl47.html").render().pages)
    lo, hi = 4.0, 40.0
    if pages(lo) > 1:
        raise SystemExit(f"Contenu trop dense pour une page : {quoi}")
    for _ in range(12):
        mid = (lo + hi) / 2
        if pages(mid) == 1: lo = mid
        else: hi = mid
    lo = math.floor(lo * 10) / 10
    while lo > 4 and pages(lo) > 1: lo -= 0.1
    return round(lo, 1)

def corps(html):
    """Contenu du <body>, pour concatener les deux pages dans un seul document."""
    return html.split("<body>", 1)[1].rsplit("</body>", 1)[0]

# Un SEUL fichier PDF, deux pages : page 1 le planning chantier, page 2 le
# Check in @ Work. Les deux viennent du meme dict PLANNING, donc ils ne peuvent
# pas diverger. Chaque page garde sa propre hauteur de ligne optimale.
ROWS_SITE = make_rows(PLANNING, "site")
ROWS_CAW  = make_rows(PLANNING, "caw")
CAW_ST    = " — CHECK IN @ WORK"
CAW_PIED  = "Le code sous chaque intitulé = référence à encoder dans Check in @ Work"

h1 = hauteur_page(ROWS_SITE, "PLANNING CONFIRMÉ", None, None, "page 1 (planning chantier)")
h2 = hauteur_page(ROWS_CAW, "CHECK IN @ WORK", CAW_ST, CAW_PIED, "page 2 (Check in @ Work)")

def document(a, b):
    """Assemble les deux pages en un seul document."""
    d = build(a, ROWS_SITE, "PLANNING CONFIRMÉ", None, None)
    p2 = corps(build(b, ROWS_CAW, "CHECK IN @ WORK", CAW_ST, CAW_PIED))
    return d.replace("</body>", '<div style="break-before:page;">' + p2 + "</div></body>")

# Chaque page tient sur une feuille prise isolement, mais leur reunion peut en
# demander une troisieme. On resserre alors la plus haute des deux jusqu a
# obtenir exactement deux pages.
for _ in range(80):
    open("/tmp/_pl47.html", "w", encoding="utf-8").write(document(h1, h2))
    rendu = W(filename="/tmp/_pl47.html").render()
    if len(rendu.pages) == 2:
        break
    if h1 >= h2 and h1 > 4.0:
        h1 = round(h1 - 0.2, 1)
    elif h2 > 4.0:
        h2 = round(h2 - 0.2, 1)
    else:
        raise SystemExit("Impossible de tenir en deux pages meme au minimum.")
else:
    raise SystemExit("Convergence impossible vers deux pages.")

sortie = sys.argv[1] if len(sys.argv) > 1 else "Planning WILBOW - S43.pdf"
rendu.write_pdf(sortie)
print(f"OK -> {sortie}  (2 pages ; hauteurs de ligne {h1:.1f}mm et {h2:.1f}mm)")
