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
    dict(id="YN", label="Jointeur", noms=["Noville Yves"], c="#6d28d9", bg="#f5f3ff"),
    dict(id="PM", label="Jointeur", noms=["Mattiuz Pierre"], c="#be123c", bg="#fff1f2"),
    dict(id="DP", label="Jointeur", noms=["Panait Dan"], c="#0369a1", bg="#f0f9ff"),
    dict(id="FH", label="Jointeur", noms=["Hanikenne Florian"], c="#4d7c0f", bg="#f7fee7"),
    dict(id="GA", label="Magasinier", noms=["Avenia Geoffrey"], c="#57534e", bg="#fafaf9",
         defaut="Dépôt", compact=True),
]

# ------------------------------------------------------------------- DONNEES
SEMAINE = 34
LUNDI = datetime.date(2026, 8, 17)
# Horodatage automatique : date + heure de generation (heure belge)
MAJ = datetime.datetime.now(ZoneInfo("Europe/Brussels"))

# caw= : nom du code Check in @ Work (clef du dict CODES). Sert a alimenter
# automatiquement le 2e PDF (secretariat) sans dict separe a maintenir a la main.
J = lambda jms, lib, note=None, t=None, url=None, q=None, caw=None: dict(
    jms=jms, lib=lib, note=note, t=t, url=url, q=q, caw=caw)
X = lambda lib, note=None, t=None, url=None, q=None, sub=None, caw=None: dict(
    jms=None, lib=lib, note=note, t=t, url=url, q=q, sub=sub, caw=caw)
A = lambda motif, q=None: dict(ligne_abs=motif, q=q)   # absence sur une partie de la journee
NUIT  = "Nuit 21h00–04h30"
JOUR  = "Journée"
MATIN = "Matin"
AM    = "Après-midi"

# Liens monday.com : n JMS -> URL de l item (https://wilbow.monday.com/boards/<board>/pulses/<item>)
LIENS = {
    "682400": "https://wilbow.monday.com/boards/5089236279/pulses/3110973936",
    "685230": "https://wilbow.monday.com/boards/5089236279/pulses/3055683760",
    "668465": "https://wilbow.monday.com/boards/5089236279/pulses/3055687803",
    "652658": "https://wilbow.monday.com/boards/5089236279/pulses/2967044016",
    "682102": "https://wilbow.monday.com/boards/5089236279/pulses/3029383528",
    "600683": "https://wilbow.monday.com/boards/5089236279/pulses/3029368324",
    "654898": "https://wilbow.monday.com/boards/5089236279/pulses/2987883453",
}
# Liens des chantiers sans numero JMS
CAT  = "https://wilbow.monday.com/boards/5089236279/pulses/3012698475"  # Fibre connexion Caterpillar Gensets
SIGN = "https://wilbow.monday.com/boards/5089236279/pulses/2832088996"  # SignaDyn - Zone D - Soufflage et Soudage reste zone D
FH32 = "https://wilbow.monday.com/boards/5089236279/pulses/2986868036"  # FH 32 FEED-IN
ROP  = "https://wilbow.monday.com/boards/5089236279/pulses/2697093519"  # ROP BTV
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

PLANNING = {
    # --- SOUFFLAGE ---
    ("E1", 0): [J("685230", "Remplacement 12641 WELK — DOL", caw="PANDA+")],
    ("E1", 1): [J("685230", "Remplacement 12641 WELK — DOL", caw="PANDA+")],
    ("E1", 2): [J("685230", "Remplacement 12641 WELK — DOL", caw="PANDA+")],
    ("E1", 3): [J("685230", "Remplacement 12641 WELK — DOL", caw="PANDA+")],
    ("E1", 4): [J("685230", "Remplacement 12641 WELK — DOL", caw="PANDA+")],

    ("E2", 0): [J("668465", "Bovigny 105 — Gouvy", caw="PANDA+")],
    ("E2", 1): [X("BTO", caw="BTO")],
    ("E2", 2): [X("BTO", caw="BTO")],
    ("E2", 3): [X("BTO", caw="BTO")],
    ("E2", 4): [J("668465", "Bovigny 105 — Gouvy", caw="PANDA+")],

    # --- JOINTEURS ---
    ("JM", 0): [X("Francorchamps", caw="CIRCUIT FANCORCHAMPS")],
    ("JM", 1): [J("682400", "OL BELMEDIS Avenue de l'énergie 33 — ANS", q=MATIN, caw="PANDA+"),
                X("Fexhe", q=AM, caw="PANDA+")],
    ("JM", 2): [X("Fexhe", caw="PANDA+")],
    ("JM", 3): [X("Francorchamps", "+ P. Mattiuz", "commun", caw="CIRCUIT FANCORCHAMPS")],
    ("JM", 4): [X("Fexhe", caw="PANDA+")],

    ("YN", 0): [J("682102", "Grand'Route 100A-100B — Crisnée", "+ P. Mattiuz", "commun", q=AM, caw="PANDA+")],
    ("YN", 1): [X("BTO", caw="BTO")],
    ("YN", 2): BARRE,
    ("YN", 3): BARRE,
    ("YN", 4): BARRE,

    ("PM", 0): [J("682102", "Grand'Route 100A-100B — Crisnée", "+ Y. Noville (après-midi)", "commun", caw="PANDA+")],
    ("PM", 1): [J("682102", "Grand'Route 100A-100B — Crisnée", caw="PANDA+")],
    ("PM", 2): [J("652658", "Rue du Ruisseau 28-26-24 — Donceel", caw="PANDA+")],
    ("PM", 3): [X("Francorchamps", "+ J. Meurisse", "commun", caw="CIRCUIT FANCORCHAMPS")],
    ("PM", 4): [J("654898", "Rue Pierre Joseph Antoine — Herstal (Embuild)", caw="PANDA+")],

    ("GA", 2): [J("654898", "Rue Pierre Joseph Antoine — Herstal (Embuild)", "+ Fabrice", "commun", caw="PANDA+")],
    ("GA", 3): [X("Héron", "+ Fabrice", "commun", url=HERON, q=MATIN, caw="PANDA+"),
                X("Francorchamps", "+ Fabrice", "commun", q=AM, caw="CIRCUIT FANCORCHAMPS")],

    ("DP", 0): [X("BTO", caw="BTO")],
    ("DP", 1): [X("BTO", caw="BTO")],
    ("DP", 2): [X("BTO", caw="BTO")],
    ("DP", 3): [X("BTO", caw="BTO")],
    ("DP", 4): [X("BTO", caw="BTO")],

    ("FH", 0): [X("BTO", caw="BTO")],
    ("FH", 1): [X("BTO", caw="BTO")],
    ("FH", 2): [X("BTO", caw="BTO")],
    ("FH", 3): [X("BTO", caw="BTO")],
    ("FH", 4): [X("BTO", caw="BTO")],
    # Dan 24/08 et Geoffrey Avenia 24/08 : cette semaine (17/08) n'est pas concernée,
    # ce sera pour S35 (semaine du 24/08).
}

# --------------------------------------------------------------------- RENDU
NB_JOURS = 6 if any(k[1] == 5 for k in PLANNING) else 5
LARG = 100 / NB_JOURS

ABS_STYLE = {
    "CONGÉ":     ("#e2e8f0", "#475569"),
    "MALADIE":   ("#fee2e2", "#b91c1c"),
    "FORMATION": ("#ede9fe", "#5b21b6"),
    "RÉCUP":     ("#cffafe", "#0e7490"),
    "ABSENT":    ("#e2e8f0", "#475569"),
    "EN ATTENTE":("#fef3c7", "#92400e"),
    "→ ÉQUIPE 1":("#dbeafe", "#1d4ed8"),
}

def cellule(r, i, DATA=None, mode="site"):
    if len(r["noms"]) > 1:   # equipe : label sur sa ligne + noms en dessous
        noms = "<br>".join(H.escape(n) for n in r["noms"])
        hdr = (f'<div class="rlabel" style="color:{r["c"]};">{H.escape(r["label"])}</div>'
               f'<div class="rname">{noms}</div>')
    else:                    # individuel : nom + role sur la meme ligne
        hdr = (f'<div class="rname">{H.escape(r["noms"][0])}'
               f'<span class="rtag" style="color:{r["c"]};">{H.escape(r["label"])}</span></div>')
    v = (DATA if DATA is not None else PLANNING).get((r["id"], i))

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
        jobs = []
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
            jobs.append(f'<div class="job">{per}<div class="{cls}">{titre}</div>{lib}{n}</div>')
        body = '<div class="body">' + "".join(jobs) + "</div>"

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
@page {{ size:A4 landscape; margin:4mm 7mm 3mm 7mm; }}
* {{ box-sizing:border-box; }}
body {{ font-family:"DejaVu Sans",Arial,sans-serif; margin:0; color:#111827; }}
.head {{ display:flex; align-items:center; justify-content:space-between;
        border-bottom:2.5pt solid #0f172a; padding-bottom:1.2mm; margin-bottom:1.6mm; }}
.brand {{ font-size:17pt; font-weight:800; letter-spacing:2.5pt; color:#0f172a; line-height:1;
         flex:0 0 auto; }}
.brand img {{ display:block; height:9mm; width:auto; border-radius:1mm; }}
.brand small {{ display:block; font-size:6.1pt; font-weight:600; letter-spacing:1.3pt; color:#64748b; margin-top:.7mm; }}
.title {{ text-align:center; }}
.title .wk {{ font-size:13pt; font-weight:800; color:#0f172a; letter-spacing:.5pt; }}
.title .dt {{ font-size:8.3pt; color:#475569; margin-top:.7mm; font-weight:600; }}
.badge {{ text-align:right; }}
.badge .tag {{ display:inline-block; background:#15803d; color:#fff; font-size:7.8pt; font-weight:800;
              padding:1.3mm 2.8mm; border-radius:1.2mm; letter-spacing:.6pt; }}
.badge .maj {{ font-size:6.6pt; color:#64748b; margin-top:1.1mm; }}

table {{ width:100%; border-collapse:collapse; table-layout:fixed; }}
col {{ width:{LARG:.4f}%; }}
th.day {{ background:#0f172a; color:#fff; font-size:9.3pt; font-weight:800; letter-spacing:.7pt;
         padding:1mm 1mm; border:0.7pt solid #0f172a; text-transform:uppercase; text-align:center; }}
th.day span {{ display:block; font-size:7.6pt; font-weight:600; color:#cbd5e1; letter-spacing:0; }}

td {{ border:0.7pt solid #cbd5e1; border-left-width:2.4pt; border-left-style:solid;
     border-bottom:1.6pt solid #0f172a; vertical-align:top; padding:1.0mm 1.4mm; height:{HLIGNE}mm; }}
tr.grp-end td {{ border-bottom:3pt solid #0f172a; }}
tr.compact td {{ height:auto; }}
tr:last-child td {{ border-bottom:1.6pt solid #0f172a; }}
.hdr {{ padding-bottom:.3mm; margin-bottom:.5mm; border-bottom:0.7pt solid rgba(15,23,42,.18); }}
.rlabel {{ font-size:5.8pt; font-weight:800; letter-spacing:.8pt; text-transform:uppercase; }}
.rtag {{ font-size:5.6pt; font-weight:800; letter-spacing:.7pt; text-transform:uppercase; margin-left:1.4mm; }}
.rname {{ font-size:7.6pt; font-weight:700; color:#0f172a; line-height:1.1; margin-top:.3mm; }}

.body {{ }}
.body.empty {{ background:#eef2f6; border:0.6pt solid #d5dde5; border-radius:.8mm;
              text-align:center; padding:.8mm 0; }}
.body.abs {{ border-radius:.8mm; text-align:center; padding:1.5mm 0; }}
.absl {{ font-size:8.5pt; font-weight:800; letter-spacing:1.2pt; }}
.job {{ line-height:1.2; }}
.job + .job {{ margin-top:.35mm; padding-top:.35mm; border-top:0.6pt dashed #94a3b8; }}
.jms {{ font-size:8.1pt; font-weight:800; color:#0f172a; }}
.jms.nonum {{ font-size:7.9pt; line-height:1.18; letter-spacing:.25pt; }}
.jms a, .jms.nonum a {{ color:#1d4ed8; text-decoration:none; }}
.ext {{ font-size:6.6pt; margin-left:.8mm; color:#1d4ed8; }}
.lib {{ font-size:6.9pt; color:#334155; margin-top:.2mm; line-height:1.15; }}
.lib.code {{ letter-spacing:.3pt; color:#1e293b; }}
.note {{ display:inline-block; font-size:6.1pt; font-weight:700; padding:.35mm 1.2mm;
        border-radius:.8mm; margin-top:.6mm; letter-spacing:.3pt; }}
.n-renfort {{ background:#fef3c7; color:#92400e; border:0.5pt solid #fcd34d; }}
.n-commun {{ background:#e0e7ff; color:#3730a3; border:0.5pt solid #a5b4fc; }}
.n-prov {{ background:#fff7ed; color:#c2410c; border:0.6pt dashed #fb923c; }}
.n-alt {{ background:#f1f5f9; color:#475569; border:0.6pt dashed #94a3b8; }}
.note.inline {{ margin-top:0; margin-left:1.2mm; }}
.perline {{ margin-bottom:.2mm; }}
.per {{ display:inline-block; font-size:5.6pt; font-weight:800; letter-spacing:.6pt;
      text-transform:uppercase; padding:.3mm 1.2mm; border-radius:.7mm; }}
.per.jour {{ background:#e2e8f0; color:#334155; }}
.per.nuit {{ background:#1e293b; color:#fff; }}
.compactabs {{ display:flex; align-items:center; justify-content:space-between; gap:1.5mm; }}
.qui {{ font-size:7.4pt; font-weight:700; color:#0f172a; }}
.statut {{ font-size:6.2pt; font-weight:800; letter-spacing:.6pt; padding:.35mm 1.4mm;
         border-radius:.8mm; white-space:nowrap; }}
.job + .job.compactabs {{ margin-top:.6mm; padding-top:.6mm; }}
.ligneabs {{ font-size:7.4pt; font-weight:800; letter-spacing:.9pt; text-align:center;
           border-radius:.8mm; padding:.7mm 0; }}
.dash {{ font-size:7.6pt; color:#8a97a6; font-weight:600; }}
.barre-overlay {{ position:absolute; top:0; left:0; right:0; bottom:0; pointer-events:none;
  background:linear-gradient(to top right, transparent calc(50% - 0.5mm), #94a3b8 calc(50% - 0.5mm),
  #94a3b8 calc(50% + 0.5mm), transparent calc(50% + 0.5mm)); }}

.foot {{ display:flex; justify-content:space-between; align-items:center; margin-top:1.2mm;
        padding-top:1mm; border-top:1pt solid #cbd5e1; font-size:6.6pt; color:#64748b; }}
.foot b {{ color:#334155; }}
.key {{ display:inline-block; width:3mm; height:2.2mm; background:#eef2f6; border:0.6pt solid #d5dde5;
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

def rendre(rows, chemin, badge, soustitre, pied2, cle_vide):
    def pages(h):
        open("/tmp/_pl34.html", "w", encoding="utf-8").write(
            build(h, rows, badge, soustitre, pied2))
        return len(W(filename="/tmp/_pl34.html").render().pages)
    lo, hi = 4.0, 40.0
    if pages(lo) > 1:
        raise SystemExit(f"Contenu trop dense pour une page : {chemin}")
    for _ in range(12):
        mid = (lo + hi) / 2
        if pages(mid) == 1: lo = mid
        else: hi = mid
    lo = math.floor(lo * 10) / 10
    while lo > 4 and pages(lo) > 1: lo -= 0.1
    open("/tmp/_pl34.html", "w", encoding="utf-8").write(
        build(round(lo, 1), rows, badge, soustitre, pied2))
    W(filename="/tmp/_pl34.html").write_pdf(chemin)
    print(f"OK -> {chemin}  (hauteur ligne {lo:.1f}mm)")

out_chantier = sys.argv[1] if len(sys.argv) > 1 else "planning_s34.pdf"
out_caw      = sys.argv[2] if len(sys.argv) > 2 else "planning_s34_caw.pdf"

rendre(make_rows(PLANNING, "site"), out_chantier, "PLANNING CONFIRMÉ", None, None, True)
rendre(make_rows(PLANNING, "caw"), out_caw, "CHECK IN @ WORK",
       " — CHECK IN @ WORK",
       "Le code sous chaque intitulé = référence à encoder dans Check in @ Work", False)
