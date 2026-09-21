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
SEMAINE = 39
LUNDI = datetime.date(2026, 9, 21)
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
    "680608": "https://wilbow.monday.com/boards/5089236279/pulses/3181043528",
    "586382": "https://wilbow.monday.com/boards/5089236279/pulses/2987797757",
}
# Liens des chantiers sans numero JMS
CAT   = "https://wilbow.monday.com/boards/5089236279/pulses/3012698475"  # Fibre connexion Caterpillar Gensets
SIGN  = "https://wilbow.monday.com/boards/5089236279/pulses/2832088996"  # SignaDyn - Zone D - Soufflage et Soudage reste zone D
FH32  = "https://wilbow.monday.com/boards/5089236279/pulses/2986868036"  # FH 32 FEED-IN
ROP   = "https://wilbow.monday.com/boards/5089236279/pulses/2697093519"  # ROP BTV
HERON = "https://wilbow.monday.com/boards/5089236279/pulses/3151190410"  # SWDE TEGEC Test pression Héron

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

# Feller Sam absent toute la semaine 39 : personne ne le remplace a cote de
# Miguel, l entete Equipe 2 affiche donc "Dominguez Miguel" seul les 5 jours.
NOMS_OVERRIDE = {
    # Lundi 21/09 : Bolmain malade, Gauthier Petit rejoint Miguel en Equipe 2.
    ("E2", 0): ["Dominguez Miguel", "Petit Gauthier"],
    ("E1", 0): ["Bolmain Mickael"],
    ("E2", 1): ["Dominguez Miguel"],
    ("E2", 2): ["Dominguez Miguel"],
    ("E2", 3): ["Dominguez Miguel"],
    ("E2", 4): ["Dominguez Miguel"],
}

PLANNING = {
    # Lundi 21/09 : Equipe 1 sur le dossier de Ciney, comme le mardi 15/09.
    ("E1", 0): ABS("MALADIE"),

    # Lundi 21/09 : Johan et Pierre reprennent les deux DIST d Oupeye, sans le
    # FEED 569815 qui sera termine.
    ("JM", 0): [
        J("662275", "Rue Fr. Jansen 5A>E — Oupeye", "+ P. Mattiuz", "commun", caw="PANDA+"),
        J("553176", "Rue Boyou 13 — Oupeye", "+ P. Mattiuz", "commun", caw="PANDA+"),
    ],
    ("PM", 0): [
        J("662275", "Rue Fr. Jansen 5A>E — Oupeye", "+ J. Meurisse", "commun", caw="PANDA+"),
        J("553176", "Rue Boyou 13 — Oupeye", "+ J. Meurisse", "commun", caw="PANDA+"),
    ],

    # Mercredi 23/09 : recuperation apres la nuit du mardi au mercredi.
    ("JM", 2): ABS("RÉCUP"),

    # Jeudi 24 et vendredi 25/09 : SWDE Reservoir de Nalamont avec Mike Wilvers,
    # qui n a pas de ligne propre. Le code C@W n est pas connu : il reste a
    # determiner avec lui, d ou un intitule explicite plutot qu un code devine.
    ("JM", 3): [X("SWDE Réservoir de Nalamont", "+ M. Wilvers", "commun",
                  caw="SWDE — À DÉTERMINER")],
    ("JM", 4): [X("SWDE Réservoir de Nalamont", "+ M. Wilvers", "commun",
                  caw="SWDE — À DÉTERMINER")],

    # Lundi 21/09 : Miguel rejoint l Equipe 1 sur Ciney. Le 685239 (Hannut) qui
    # lui etait prevu ce jour-la part au mercredi, avec Pierre.
    ("E2", 0): [J("675238", "BBN 12310B — Ciney-Jemelle", caw="PANDA+")],
    ("E2", 2): [J("685239", "Adm. Communale d'Hannut — Rue de Landen 23", "+ P. Mattiuz", "commun", caw="PANDA+")],
    ("PM", 2): [J("685239", "Adm. Communale d'Hannut — Rue de Landen 23", "+ Équipe 2", "commun", caw="PANDA+")],

    # Mercredi et jeudi : l Equipe 1 revient sur Ciney, comme le lundi.
    ("E1", 2): [J("675238", "BBN 12310B — Ciney-Jemelle", caw="PANDA+")],
    ("E1", 3): [J("675238", "BBN 12310B — Ciney-Jemelle", caw="PANDA+")],

    # Mardi 22/09 : 680608 (INSKY NV, Sprimont) partagé Johan + Pierre
    ("JM", 1): [J("680608", "INSKY NV — Rue des Spinettes 5, Sprimont",
                  note="+ P. Mattiuz", t="commun", caw="PANDA+"),
                # Nuit du mardi 22 au mercredi 23/09, Johan seul.
                X("EUP8756W0 — WELK OTS 5131 M", q=NUIT, caw="PANDA+")],
    ("PM", 1): [J("680608", "INSKY NV — Rue des Spinettes 5, Sprimont",
                  note="+ J. Meurisse", t="commun", caw="PANDA+")],

    # Mardi 22/09 : les 2 équipes de soufflage -> 586382 (Marché GCC, Rue de Limbourg, Verviers — PW Backbone)
    ("E1", 1): [J("586382", "Marché GCC — Verviers (PW Backbone URGENT)",
                  note="+ Équipe 2", t="commun", caw="PANDA+")],
    ("E2", 1): [J("586382", "Marché GCC — Verviers (PW Backbone URGENT)",
                  note="+ Équipe 1", t="commun", caw="PANDA+")],

    # Panait Dan et Hanikenne Florian : BTO toute la semaine. Dan fait en plus la
    # nuit du lundi 21 au mardi 22 (mesures OTDR SignaDyn, seul depuis le 15/09) et
    # recupere le mardi.
    ("DP", 0): [X("BTO", caw="BTO"),
                X("Mesures OTDR SignaDyn", "+ F. Hanikenne", "commun", q=NUIT, caw="EQUANS-CAMERA-CCTV")],
    ("DP", 1): ABS("RÉCUP"),
    ("DP", 2): [X("BTO", caw="BTO")],
    ("DP", 3): [X("BTO", caw="BTO")],
    ("DP", 4): [X("BTO", caw="BTO")],

    # Florian suit Dan : BTO et la nuit le lundi, recup le mardi.
    ("FH", 0): [X("BTO", caw="BTO"),
                X("Mesures OTDR SignaDyn", "+ D. Panait", "commun", q=NUIT, caw="EQUANS-CAMERA-CCTV")],
    ("FH", 1): ABS("RÉCUP"),
    ("FH", 2): [X("BTO", caw="BTO")],
    ("FH", 3): [X("BTO", caw="BTO")],
    ("FH", 4): [X("BTO", caw="BTO")],


    # Mardi et mercredi : le magasinier en BTO.
    ("GA", 1): [X("BTO", caw="BTO")],
    ("GA", 2): [X("BTO", caw="BTO")],

    # Jeudi 24/09 : le magasinier chez France Elevateurs, sans code C@W.
    ("GA", 3): ABS("FRANCE ÉLÉVATEURS"),

    # Andrei arrive le mardi : BTO jusqu a la fin de la semaine.
    ("AN", 1): [X("BTO", caw="BTO")],
    ("AN", 2): [X("BTO", caw="BTO")],
    ("AN", 3): [X("BTO", caw="BTO")],
    ("AN", 4): [X("BTO", caw="BTO")],

    # Reste de la semaine : à planifier au fur et à mesure.
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
    peut_cheval = (suivant is None or isinstance(suivant, list)
                   or (isinstance(suivant, dict) and "absence" in suivant))
    veille = (DATA if DATA is not None else PLANNING).get((r["id"], i - 1)) if i else None
    reports = [dict(d, _spacer=True) for d in veille
               if isinstance(d, dict) and str(d.get("q") or "").lower().startswith("nuit")
               ] if isinstance(veille, list) else []

    # Une absence se rend normalement hors de la boucle des jobs, ce qui
    # empeche d y reserver la hauteur. Quand une nuit de la veille deborde
    # ici, on la bascule dans le flux des jobs via A(), qui sait l afficher.
    if isinstance(v, dict) and "absence" in v and reports:
        v = [A(v["absence"])]
    if isinstance(v, list) and reports:
        v = v + reports

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
                if peut_cheval and (d.get("q") or "").lower().startswith("nuit"):
                    # La nuit est ancree en bas de la ligne, a cheval sur les deux
                    # journees. Le spacer invisible qui la suit reserve sa hauteur en
                    # fin de case, dans la journee de depart comme dans la suivante.
                    if not d.get("_spacer"):
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
            if peut_cheval and (d.get("q") or "").lower().startswith("nuit"):
                # La nuit est ancree en bas de la ligne, a cheval sur les deux
                # journees. Le spacer invisible qui la suit reserve sa hauteur en
                # fin de case, dans la journee de depart comme dans la suivante.
                if not d.get("_spacer"):
                    nuits.append(f'<div class="job cheval">{per}<div class="{cls}">{titre}</div>{lib}{n}</div>')
                nuits.append(f'<div class="job chevalspacer">{per}<div class="{cls}">{titre}</div>{lib}{n}</div>')
            else:
                jobs.append(f'<div class="job">{per}<div class="{cls}">{titre}</div>{lib}{n}</div>')
        body = '<div class="body">' + "".join(jobs + nuits) + "</div>"

    return (f'<td style="border-left-color:{r["c"]}; background:{r["bg"]}; position:relative;">'
            f'<div class="hdr">{hdr}</div>{body}</td>')

ths = "".join(
    f'<th class="day">{JOURS[i]}<span>{(LUNDI + datetime.timedelta(days=i)):%d/%m}</span></th>'
    for i in range(NB_JOURS))

def make_rows(DATA, mode="site"):
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
@page {{  /* S39 : polices reduites de 2% le 15/09/2026
   pour absorber les nuits et les recups sans rien supprimer. */
 size:A4 landscape; margin:4mm 7mm 3mm 7mm; }}
* {{ box-sizing:border-box; }}
body {{ font-family:"DejaVu Sans",Arial,sans-serif; margin:0; color:#111827; }}
.head {{ display:flex; align-items:center; justify-content:space-between;
        border-bottom:2.328pt solid #0f172a; padding-bottom:1.2mm; margin-bottom:1.6mm; }}
.brand {{ font-size:15.833pt; font-weight:800; letter-spacing:2.328pt; color:#0f172a; line-height:1;
         flex:0 0 auto; }}
.brand img {{ display:block; height:9mm; width:auto; border-radius:1mm; }}
.brand small {{ display:block; font-size:5.681pt; font-weight:600; letter-spacing:1.211pt; color:#64748b; margin-top:.7mm; }}
.title {{ text-align:center; }}
.title .wk {{ font-size:12.108pt; font-weight:800; color:#0f172a; letter-spacing:.4.657pt; }}
.title .dt {{ font-size:7.731pt; color:#475569; margin-top:.7mm; font-weight:600; }}
.badge {{ text-align:right; }}
.badge .tag {{ display:inline-block; background:#15803d; color:#fff; font-size:7.265pt; font-weight:800;
              padding:1.3mm 2.8mm; border-radius:1.2mm; letter-spacing:.5.588pt; }}
.badge .maj {{ font-size:6.147pt; color:#64748b; margin-top:1.1mm; }}

table {{ width:100%; border-collapse:collapse; table-layout:fixed; }}
col {{ width:{LARG:.4f}%; }}
th.day {{ background:#0f172a; color:#fff; font-size:8.662pt; font-weight:800; letter-spacing:.6.519pt;
         padding:1mm 1mm; border:0.652pt solid #0f172a; text-transform:uppercase; text-align:center; }}
th.day span {{ display:block; font-size:7.079pt; font-weight:600; color:#cbd5e1; letter-spacing:0; }}

td {{ border:0.652pt solid #cbd5e1; border-left-width:2.235pt; border-left-style:solid;
     border-bottom:1.49pt solid #0f172a; vertical-align:top; padding:1.0mm 1.4mm; height:{HLIGNE}mm; }}
tr.grp-end td {{ border-bottom:2.795pt solid #0f172a; }}
tr.compact td {{ height:auto; }}
tr:last-child td {{ border-bottom:1.49pt solid #0f172a; }}
.hdr {{ padding-bottom:.3mm; margin-bottom:.5mm; border-bottom:0.652pt solid rgba(15,23,42,.18); }}
.rlabel {{ font-size:5.402pt; font-weight:800; letter-spacing:.7.452pt; text-transform:uppercase; }}
.rtag {{ font-size:5.216pt; font-weight:800; letter-spacing:.6.519pt; text-transform:uppercase; margin-left:1.4mm; }}
.rname {{ font-size:7.079pt; font-weight:700; color:#0f172a; line-height:1.1; margin-top:.3mm; }}

.body {{ }}
.body.empty {{ background:#eef2f6; border:0.559pt solid #d5dde5; border-radius:.8mm;
              text-align:center; padding:.8mm 0; }}
.body.abs {{ border-radius:.8mm; text-align:center; padding:1.5mm 0; }}
.absl {{ font-size:7.917pt; font-weight:800; letter-spacing:1.117pt; }}
.job {{ line-height:1.2; }}
.job + .job {{ margin-top:.35mm; padding-top:.35mm; border-top:0.559pt dashed #94a3b8; }}
.jms {{ font-size:7.545pt; font-weight:800; color:#0f172a; }}
.jms.nonum {{ font-size:7.358pt; line-height:1.18; letter-spacing:.25pt; }}
.jms a, .jms.nonum a {{ color:#1d4ed8; text-decoration:none; }}
.ext {{ font-size:6.147pt; margin-left:.8mm; color:#1d4ed8; }}
.lib {{ font-size:6.426pt; color:#334155; margin-top:.2mm; line-height:1.15; }}
.lib.code {{ letter-spacing:.2.795pt; color:#1e293b; }}
.note {{ display:inline-block; font-size:5.681pt; font-weight:700; padding:.35mm 1.2mm;
        border-radius:.8mm; margin-top:.6mm; letter-spacing:.2.795pt; }}
.n-renfort {{ background:#fef3c7; color:#92400e; border:0.466pt solid #fcd34d; }}
.n-commun {{ background:#e0e7ff; color:#3730a3; border:0.466pt solid #a5b4fc; }}
.n-prov {{ background:#fff7ed; color:#c2410c; border:0.559pt dashed #fb923c; }}
.n-alt {{ background:#f1f5f9; color:#475569; border:0.559pt dashed #94a3b8; }}
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
.per {{ display:inline-block; font-size:5.216pt; font-weight:800; letter-spacing:.5.588pt;
      text-transform:uppercase; padding:.3mm 1.2mm; border-radius:.7mm; }}
.per.jour {{ background:#e2e8f0; color:#334155; }}
.per.nuit {{ background:#1e293b; color:#fff; }}
.compactabs {{ display:flex; align-items:center; justify-content:space-between; gap:1.5mm; }}
.qui {{ font-size:6.892pt; font-weight:700; color:#0f172a; }}
.statut {{ font-size:5.774pt; font-weight:800; letter-spacing:.5.588pt; padding:.35mm 1.4mm;
         border-radius:.8mm; white-space:nowrap; }}
.job + .job.compactabs {{ margin-top:.6mm; padding-top:.6mm; }}
.ligneabs {{ font-size:6.892pt; font-weight:800; letter-spacing:.8.383pt; text-align:center;
           border-radius:.8mm; padding:.7mm 0; }}
.dash {{ font-size:7.079pt; color:#8a97a6; font-weight:600; }}
.barre-overlay {{ position:absolute; top:0; left:0; right:0; bottom:0; pointer-events:none;
  background:linear-gradient(to top right, transparent calc(50% - 0.5mm), #94a3b8 calc(50% - 0.5mm),
  #94a3b8 calc(50% + 0.5mm), transparent calc(50% + 0.5mm)); }}

.foot {{ display:flex; justify-content:space-between; align-items:center; margin-top:1.2mm;
        padding-top:1mm; border-top:0.931pt solid #cbd5e1; font-size:6.147pt; color:#64748b; }}
.foot b {{ color:#334155; }}
.key {{ display:inline-block; width:3mm; height:2.2mm; background:#eef2f6; border:0.559pt solid #d5dde5;
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
        open("/tmp/_pl39.html", "w", encoding="utf-8").write(
            build(h, rows, badge, soustitre, pied2))
        return len(W(filename="/tmp/_pl39.html").render().pages)
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
    open("/tmp/_pl39.html", "w", encoding="utf-8").write(document(h1, h2))
    rendu = W(filename="/tmp/_pl39.html").render()
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

sortie = sys.argv[1] if len(sys.argv) > 1 else "Planning WILBOW - S39.pdf"
rendu.write_pdf(sortie)
print(f"OK -> {sortie}  (2 pages ; hauteurs de ligne {h1:.1f}mm et {h2:.1f}mm)")
