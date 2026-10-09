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
SEMAINE = 42
LUNDI = datetime.date(2026, 10, 12)
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
    "685239": "https://wilbow.monday.com/boards/5089236279/pulses/3136655230",
    "662275": "https://wilbow.monday.com/boards/5089236279/pulses/3174723480",
    "553176": "https://wilbow.monday.com/boards/5089236279/pulses/3166049312",
    "675238": "https://wilbow.monday.com/boards/5089236279/pulses/3158202616",
    "688116": "https://wilbow.monday.com/boards/5089236279/pulses/3206269235",
    "683464": "https://wilbow.monday.com/boards/5089236279/pulses/3195329407",
    "622272": "https://wilbow.monday.com/boards/5089236279/pulses/2958713654",
    "622268": "https://wilbow.monday.com/boards/5089236279/pulses/2924899531",
    "680608": "https://wilbow.monday.com/boards/5089236279/pulses/3181043528",
    "586382": "https://wilbow.monday.com/boards/5089236279/pulses/2987797757",
    "656373": "https://wilbow.monday.com/boards/5089236279/pulses/2987894869",
    "672861": "https://wilbow.monday.com/boards/5089236279/pulses/3196268739",
    "687978": "https://wilbow.monday.com/boards/5089236279/pulses/3212938322",
    "590458": "https://wilbow.monday.com/boards/5089236279/pulses/3174254132",
    "622386": "https://wilbow.monday.com/boards/5089236279/pulses/3183700075",
    "647240": "https://wilbow.monday.com/boards/5089236279/pulses/3139752774",
    "599588": "https://wilbow.monday.com/boards/5089236279/pulses/3006164733",
    "685230": "https://wilbow.monday.com/boards/5089236279/pulses/3055683760",
    "523547": "https://wilbow.monday.com/boards/5089236279/pulses/2987923297",
    "675043": "https://wilbow.monday.com/boards/5089236279/pulses/2987880677",
    "635054": "https://wilbow.monday.com/boards/5089236279/pulses/3262247942",
    "582528": "https://wilbow.monday.com/boards/5089236279/pulses/3202011232",
}
# Liens des chantiers sans numero JMS
CAT   = "https://wilbow.monday.com/boards/5089236279/pulses/3012698475"  # Fibre connexion Caterpillar Gensets
SIGN  = "https://wilbow.monday.com/boards/5089236279/pulses/2832088996"  # SignaDyn - Zone D - Soufflage et Soudage reste zone D
FH32  = "https://wilbow.monday.com/boards/5089236279/pulses/2986868036"  # FH 32 FEED-IN
ROP   = "https://wilbow.monday.com/boards/5089236279/pulses/2697093519"  # ROP BTV
HERON = "https://wilbow.monday.com/boards/5089236279/pulses/3151190410"  # SWDE TEGEC Test pression Héron
MOVE41 = "https://wilbow.monday.com/boards/5089236279/pulses/3218880657"  # Vérification Move Rop 41FEX
VICINAL = "https://wilbow.monday.com/boards/5089236279/pulses/3159304163"  # 603753 + 671456, rue Du Vicinal, Clavier
FH44 = "https://wilbow.monday.com/boards/5089236279/pulses/3241665311"  # FH 44 Feed-in
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
}

# Wilson, etudiant en stage : il accompagne une equipe chaque jour. Il n a pas
# de ligne RESSOURCES propre et figure donc dans l entete de celle qu il suit.
# Noms surlignes dans l entete : les renforts ponctuels qui ne font pas
# partie de l equipe et qu il ne faut pas oublier d emmener.
MISE_EN_EVIDENCE = {"Wilson (stage)"}

NOMS_OVERRIDE = {
    ("E1", 0): ["Bolmain Mickael", "Petit Gauthier", "Wilson (stage)"],
    ("E1", 1): ["Bolmain Mickael", "Petit Gauthier", "Wilson (stage)"],
    ("E1", 2): ["Bolmain Mickael", "Petit Gauthier", "Wilson (stage)"],
    ("E2", 3): ["Dominguez Miguel", "Feller Sam", "Wilson (stage)"],
    ("E2", 4): ["Dominguez Miguel", "Feller Sam", "Wilson (stage)"],
}

PLANNING = {
    # Le HT1673A du mardi 13/10 a ete annule le 07/10.

    # Lundi 12/10 : Johan et Pierre reprennent les deux JMS du BBN Fexhe, le
    # chantier du mercredi 07/10. Ils y reviennent de nuit le jeudi 15/10.
    ("JM", 0): [
        J("622272", "IS MP — Câble définitif branche 12835", "+ P. Mattiuz", "commun", caw="PANDA+"),
        J("622268", "IS MP — Câble définitif branche 12352", "+ P. Mattiuz", "commun", caw="PANDA+"),
    ],
    ("PM", 0): [
        J("622272", "IS MP — Câble définitif branche 12835", "+ J. Meurisse", "commun", caw="PANDA+"),
        J("622268", "IS MP — Câble définitif branche 12352", "+ J. Meurisse", "commun", caw="PANDA+"),
    ],

    # Mardi 13/10 : Johan sur le 675238, a la place du HT1673A annule. Pierre
    # passe sur le FH 44 Feed-in ; son 523547 est reporte au jeudi apres-midi.
    ("JM", 1): [J("675238", "BBN 12310B — Ciney-Jemelle", caw="PANDA+")],
    ("PM", 1): [X("FH 44 Feed-in", url=FH44, caw="FIFTHNET")],

    # Nuit du jeudi 15 au vendredi 16/10 : BBN Fexhe, Meurisse Johan et
    # Mattiuz Pierre. Deux JMS (622272 et 622268) pour un seul bloc de nuit :
    # le titre les porte tous les deux et le lien pointe sur le 622272.
    # Mercredi 14/10 : Johan sur le 675043, Pierre sur le 656373, tous deux a
    # Orp-Jauche mais sur des dossiers distincts.
    ("JM", 2): [J("675043", "Assoc. Eugène Malève — Place de Maret 1, Orp-Jauche",
                  caw="PANDA+")],
    ("PM", 2): [J("656373", "FMROP C/107 — Rue d'Orp 62, Orp-Jauche", caw="PANDA+")],

    # Le jeudi 15/10, ils font d abord le 688116 le matin.
    ("JM", 3): [
        J("688116", "FQ — Remplacement câble Antenne Orange LL03703136",
          "+ P. Mattiuz", "commun", q=MATIN, caw="PANDA+"),
        J("683464", "GB BUILD — Route du Condroz 211, Neupré", q=AM, caw="PANDA+"),
        X("JMS 622272 · 622268 — BBN Fexhe", "+ P. Mattiuz", "commun",
          url=FEXHE, q=NUIT, caw="PANDA+"),
    ],
    ("PM", 3): [
        J("688116", "FQ — Remplacement câble Antenne Orange LL03703136",
          "+ J. Meurisse", "commun", q=MATIN, caw="PANDA+"),
        J("523547", "RZ FTTH RFT — Hermalle-sous-Argenteau, Bloc G",
          q=AM, caw="PANDA+"),
        X("JMS 622272 · 622268 — BBN Fexhe", "+ J. Meurisse", "commun",
          url=FEXHE, q=NUIT, caw="PANDA+"),
    ],

    # Mardi 13/10 : l Equipe 2 sur le 683464 (GB BUILD, Neupre).
    ("E2", 1): [J("683464", "GB BUILD — Route du Condroz 211, Neupré", caw="PANDA+")],

    # Mercredi 14/10 : l Equipe 2 en BTO.
    ("E2", 2): [X("BTO", caw="BTO")],

    # Dan, Florian et Andrei : BTO les cinq jours.
    **{("DP", i): [X("BTO", caw="BTO")] for i in range(5)},
    **{("FH", i): [X("BTO", caw="BTO")] for i in range(5)},
    **{("AN", i): [X("BTO", caw="BTO")] for i in range(5)},

    # Le reste de la semaine est a confirmer : cases grisees.
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
}

def cellule(r, i, DATA=None, mode="site"):
    noms_jour = NOMS_OVERRIDE.get((r["id"], i), r["noms"])

    def _nom(n):
        """Un renfort ponctuel est surligne pour qu il ne passe pas inapercu."""
        e = H.escape(n)
        return f'<span class="renfort">{e}</span>' if n in MISE_EN_EVIDENCE else e

    if len(noms_jour) > 1:   # equipe : label sur sa ligne + noms en dessous
        noms = "<br>".join(_nom(n) for n in noms_jour)
        hdr = (f'<div class="rlabel" style="color:{r["c"]};">{H.escape(r["label"])}</div>'
               f'<div class="rname">{noms}</div>')
    else:                    # individuel : nom + role sur la meme ligne
        hdr = (f'<div class="rname">{_nom(noms_jour[0])}'
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
    peut_cheval = (suivant is None
                   or (isinstance(suivant, dict) and "absence" in suivant))
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
@page {{  /* S42 : polices reduites de 2% le 15/09/2026
   pour absorber les nuits et les recups sans rien supprimer. */
 size:A4 landscape; margin:4mm 7mm 3mm 7mm; }}
* {{ box-sizing:border-box; }}
body {{ font-family:"DejaVu Sans",Arial,sans-serif; margin:0; color:#111827; }}
.head {{ display:flex; align-items:center; justify-content:space-between;
        border-bottom:2.235pt solid #0f172a; padding-bottom:1.2mm; margin-bottom:1.6mm; }}
.brand {{ font-size:15.2pt; font-weight:800; letter-spacing:2.235pt; color:#0f172a; line-height:1;
         flex:0 0 auto; }}
.brand img {{ display:block; height:9mm; width:auto; border-radius:1mm; }}
.brand small {{ display:block; font-size:5.454pt; font-weight:600; letter-spacing:1.163pt; color:#64748b; margin-top:.7mm; }}
.title {{ text-align:center; }}
.title .wk {{ font-size:11.624pt; font-weight:800; color:#0f172a; letter-spacing:.4.471pt; }}
.title .dt {{ font-size:7.422pt; color:#475569; margin-top:.7mm; font-weight:600; }}
.badge {{ text-align:right; }}
.badge .tag {{ display:inline-block; background:#15803d; color:#fff; font-size:6.974pt; font-weight:800;
              padding:1.3mm 2.8mm; border-radius:1.2mm; letter-spacing:.5.364pt; }}
.badge .maj {{ font-size:5.901pt; color:#64748b; margin-top:1.1mm; }}

table {{ width:100%; border-collapse:collapse; table-layout:fixed; }}
col {{ width:{LARG:.4f}%; }}
th.day {{ background:#0f172a; color:#fff; font-size:8.316pt; font-weight:800; letter-spacing:.6.258pt;
         padding:1mm 1mm; border:0.626pt solid #0f172a; text-transform:uppercase; text-align:center; }}
th.day span {{ display:block; font-size:6.796pt; font-weight:600; color:#cbd5e1; letter-spacing:0; }}

td {{ border:0.626pt solid #cbd5e1; border-left-width:2.146pt; border-left-style:solid;
     border-bottom:1.43pt solid #0f172a; vertical-align:top; padding:1.0mm 1.4mm; height:{HLIGNE}mm; }}
tr.grp-end td {{ border-bottom:2.683pt solid #0f172a; }}
tr.compact td {{ height:auto; }}
tr:last-child td {{ border-bottom:1.43pt solid #0f172a; }}
.hdr {{ padding-bottom:.3mm; margin-bottom:.5mm; border-bottom:0.626pt solid rgba(15,23,42,.18); }}
.rlabel {{ font-size:5.186pt; font-weight:800; letter-spacing:.7.154pt; text-transform:uppercase; }}
.rtag {{ font-size:5.007pt; font-weight:800; letter-spacing:.6.258pt; text-transform:uppercase; margin-left:1.4mm; }}
.rname {{ font-size:6.796pt; font-weight:700; color:#0f172a; line-height:1.1; margin-top:.3mm; }}

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
.absl {{ font-size:7.6pt; font-weight:800; letter-spacing:1.072pt; }}
/* Renfort ponctuel dans une equipe : surligne pour ne pas l oublier. */
.renfort {{ background:#fde047; color:#713f12; padding:0 1mm; border-radius:.6mm;
           box-shadow:0 0 0 0.537pt #ca8a04; }}
.job {{ line-height:1.2; }}
.job + .job {{ margin-top:.35mm; padding-top:.35mm; border-top:0.537pt dashed #94a3b8; }}
.jms {{ font-size:7.243pt; font-weight:800; color:#0f172a; }}
.jms.nonum {{ font-size:7.064pt; line-height:1.18; letter-spacing:.25pt; }}
.jms a, .jms.nonum a {{ color:#1d4ed8; text-decoration:none; }}
.ext {{ font-size:5.901pt; margin-left:.8mm; color:#1d4ed8; }}
.lib {{ font-size:6.169pt; color:#334155; margin-top:.2mm; line-height:1.15; }}
.lib.code {{ letter-spacing:.2.683pt; color:#1e293b; }}
.note {{ display:inline-block; font-size:5.454pt; font-weight:700; padding:.35mm 1.2mm;
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
.per {{ display:inline-block; font-size:5.007pt; font-weight:800; letter-spacing:.5.364pt;
      text-transform:uppercase; padding:.3mm 1.2mm; border-radius:.7mm; }}
.per.jour {{ background:#e2e8f0; color:#334155; }}
.per.nuit {{ background:#1e293b; color:#fff; }}
.compactabs {{ display:flex; align-items:center; justify-content:space-between; gap:1.5mm; }}
.qui {{ font-size:6.616pt; font-weight:700; color:#0f172a; }}
.statut {{ font-size:5.543pt; font-weight:800; letter-spacing:.5.364pt; padding:.35mm 1.4mm;
         border-radius:.8mm; white-space:nowrap; }}
.job + .job.compactabs {{ margin-top:.6mm; padding-top:.6mm; }}
.ligneabs {{ font-size:6.616pt; font-weight:800; letter-spacing:.8.048pt; text-align:center;
           border-radius:.8mm; padding:.7mm 0; }}
.dash {{ font-size:6.796pt; color:#8a97a6; font-weight:600; }}
.barre-overlay {{ position:absolute; top:0; left:0; right:0; bottom:0; pointer-events:none;
  background:linear-gradient(to top right, transparent calc(50% - 0.5mm), #94a3b8 calc(50% - 0.5mm),
  #94a3b8 calc(50% + 0.5mm), transparent calc(50% + 0.5mm)); }}

.foot {{ display:flex; justify-content:space-between; align-items:center; margin-top:1.2mm;
        padding-top:1mm; border-top:0.894pt solid #cbd5e1; font-size:5.901pt; color:#64748b; }}
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
        open("/tmp/_pl42.html", "w", encoding="utf-8").write(
            build(h, rows, badge, soustitre, pied2))
        return len(W(filename="/tmp/_pl42.html").render().pages)
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
    open("/tmp/_pl42.html", "w", encoding="utf-8").write(document(h1, h2))
    rendu = W(filename="/tmp/_pl42.html").render()
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

sortie = sys.argv[1] if len(sys.argv) > 1 else "Planning WILBOW - S42.pdf"
rendu.write_pdf(sortie)
print(f"OK -> {sortie}  (2 pages ; hauteurs de ligne {h1:.1f}mm et {h2:.1f}mm)")
