import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors as rl_colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Mackenson Cineus — Finance Professional",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500;600&display=swap');
  :root {
    --gold: #C9A84C; --gold-light: #E8C97A;
    --navy: #0D1B2A; --navy-mid: #1A2E42; --navy-light: #243B55;
    --cream: #F5F0E8; --white: #FFFFFF;
    --accent: #4A9EFF; --success: #2ECC71; --warn: #E67E22;
  }
  .stApp { background: var(--navy); color: var(--cream); }
  .stApp > header { background: transparent !important; }
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--navy-mid) 0%, var(--navy) 100%);
    border-right: 1px solid rgba(201,168,76,0.2);
  }
  [data-testid="stSidebar"] * { color: var(--cream) !important; }
  h1,h2,h3 { font-family: 'Playfair Display', serif !important; }
  p,div,span,label { font-family: 'DM Sans', sans-serif !important; }

  .hero-banner {
    background: linear-gradient(135deg, var(--navy-mid) 0%, var(--navy-light) 50%, var(--navy-mid) 100%);
    border: 1px solid rgba(201,168,76,0.3); border-radius: 16px;
    padding: 40px; margin-bottom: 32px; position: relative; overflow: hidden;
  }
  .hero-banner::before {
    content:''; position:absolute; top:-50%; right:-10%; width:400px; height:400px;
    background: radial-gradient(circle, rgba(201,168,76,0.08) 0%, transparent 70%); pointer-events:none;
  }
  .hero-name {
    font-family: 'Playfair Display', serif !important; font-size: 3rem !important; font-weight: 900 !important;
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-light) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1; margin: 0;
  }
  .hero-title { font-size:1.05rem; color:var(--cream); opacity:0.85; margin-top:8px; letter-spacing:2px; text-transform:uppercase; }
  .hero-badge {
    display:inline-block; background:rgba(201,168,76,0.15); border:1px solid rgba(201,168,76,0.4);
    border-radius:50px; padding:4px 14px; font-size:0.8rem; color:var(--gold-light); margin:4px;
  }
  .metric-card {
    background:linear-gradient(135deg,var(--navy-mid),var(--navy-light));
    border:1px solid rgba(201,168,76,0.2); border-radius:12px; padding:24px; text-align:center;
  }
  .metric-value { font-family:'Playfair Display',serif !important; font-size:2.5rem; font-weight:700; color:var(--gold); display:block; }
  .metric-label { font-size:0.85rem; color:var(--cream); opacity:0.7; text-transform:uppercase; letter-spacing:1px; }
  .section-header {
    font-family:'Playfair Display',serif !important; font-size:1.8rem !important; color:var(--gold) !important;
    border-bottom:1px solid rgba(201,168,76,0.3); padding-bottom:12px; margin-bottom:24px;
  }

  /* Bio periods */
  .bio-period {
    background:var(--navy-mid); border:1px solid rgba(201,168,76,0.15);
    border-radius:16px; padding:28px 32px; margin-bottom:24px;
    position:relative; overflow:hidden;
  }
  .bio-period::before { content:''; position:absolute; left:0; top:0; bottom:0; width:4px; }
  .bio-period.phase1::before { background:linear-gradient(180deg,#4A9EFF,#2ECC71); }
  .bio-period.phase2::before { background:linear-gradient(180deg,#C9A84C,#E8C97A); }
  .bio-period.phase3::before { background:linear-gradient(180deg,#E67E22,#C9A84C); }
  .bio-period.phase4::before { background:linear-gradient(180deg,#9B59B6,#4A9EFF); }
  .bio-phase-label { font-size:0.72rem; letter-spacing:2px; text-transform:uppercase; font-weight:600; margin-bottom:6px; }
  .phase1 .bio-phase-label { color:#4A9EFF; }
  .phase2 .bio-phase-label { color:var(--gold); }
  .phase3 .bio-phase-label { color:var(--warn); }
  .phase4 .bio-phase-label { color:#9B59B6; }
  .bio-period-title { font-family:'Playfair Display',serif !important; font-size:1.3rem; font-weight:700; color:var(--white); margin-bottom:8px; }
  .bio-period-years { font-size:0.8rem; color:var(--cream); opacity:0.55; margin-bottom:14px; letter-spacing:1px; }
  .bio-period-text { font-size:0.95rem; line-height:1.85; color:var(--cream); opacity:0.88; }
  .bio-tag {
    display:inline-block; background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.12);
    border-radius:4px; padding:2px 10px; font-size:0.75rem; color:var(--cream); opacity:0.7; margin:3px 2px 0;
  }

  .timeline-item {
    background:var(--navy-mid); border-left:3px solid var(--gold);
    border-radius:0 12px 12px 0; padding:16px 20px; margin-bottom:14px;
  }
  .timeline-item:hover { background:var(--navy-light); }
  .timeline-year { color:var(--gold); font-weight:600; font-size:0.85rem; letter-spacing:1px; }
  .timeline-title { font-size:1.05rem; font-weight:600; color:var(--white); margin:4px 0; }
  .timeline-desc { font-size:0.9rem; color:var(--cream); opacity:0.8; }

  .skill-bar-container { margin-bottom:12px; }
  .skill-name { font-size:0.9rem; color:var(--cream); margin-bottom:4px; }
  .skill-bar { height:8px; background:rgba(255,255,255,0.1); border-radius:4px; overflow:hidden; }
  .skill-fill { height:100%; border-radius:4px; background:linear-gradient(90deg,var(--gold),var(--gold-light)); }

  .platform-card {
    background:var(--navy-mid); border:1px solid rgba(255,255,255,0.08);
    border-radius:12px; padding:16px 20px; margin-bottom:12px;
    display:flex; align-items:flex-start; gap:14px; transition:border-color 0.3s,background 0.3s;
  }
  .platform-card:hover { border-color:rgba(201,168,76,0.4); background:var(--navy-light); }
  .platform-icon { font-size:1.6rem; flex-shrink:0; width:44px; height:44px; display:flex; align-items:center; justify-content:center; background:rgba(201,168,76,0.1); border-radius:10px; }
  .platform-name { font-size:0.95rem; font-weight:600; color:var(--gold); margin-bottom:2px; }
  .platform-desc { font-size:0.82rem; color:var(--cream); opacity:0.7; line-height:1.5; }
  .platform-link { display:inline-block; margin-top:6px; font-size:0.78rem; color:var(--accent); text-decoration:none; border-bottom:1px solid rgba(74,158,255,0.3); }

  .stButton > button {
    background:linear-gradient(135deg,var(--gold) 0%,var(--gold-light) 100%) !important;
    color:var(--navy) !important; border:none !important; border-radius:8px !important;
    font-weight:600 !important; letter-spacing:0.5px; padding:10px 24px !important;
  }
  .stButton > button:hover { box-shadow:0 8px 24px rgba(201,168,76,0.3) !important; }
  .stTabs [data-baseweb="tab-list"] { background:var(--navy-mid); border-radius:8px; gap:4px; }
  .stTabs [data-baseweb="tab"] { color:var(--cream) !important; }
  .stTabs [aria-selected="true"] { background:rgba(201,168,76,0.2) !important; color:var(--gold) !important; }
  .stTextArea textarea,.stTextInput input,.stSelectbox select {
    background:var(--navy-mid) !important; color:var(--cream) !important;
    border:1px solid rgba(201,168,76,0.3) !important; border-radius:8px !important;
  }
  .generated-doc {
    background:var(--navy-mid); border:1px solid rgba(201,168,76,0.2);
    border-radius:12px; padding:32px; line-height:1.8; white-space:pre-wrap; color:var(--cream);
  }
  .doc-header {
    font-family:'Playfair Display',serif; font-size:1.4rem; color:var(--gold);
    margin-bottom:16px; border-bottom:1px solid rgba(201,168,76,0.2); padding-bottom:12px;
  }
  #MainMenu,footer,[data-testid="stHeader"] { display:none !important; }
  .block-container { padding-top:2rem !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DATA
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# DATA — SOURCE UNIQUE DE VÉRITÉ (modifiable depuis la page "Édition")
# ═══════════════════════════════════════════════════════════════════════════════

# Initialisation session_state pour l'édition en ligne
def _init_state():
    defaults = {
        "edit_name":     "Mackenson CINÉUS",
        "edit_title":    "Compliance Officer | Analyste Sécurité Financière (LCB-FT)",
        "edit_location": "Île-de-France, France",
        "edit_email":    "mackenson.cineus@email.com",
        "edit_linkedin": "linkedin.com/in/mackenson-cineus",
        "edit_summary":  (
            "Professionnel de la conformité financière et des marchés, avec une double expérience "
            "en fintech de paiement (HiPay) et en banque privée (Delubac). MBA Trading & Marchés "
            "Financiers (ESLSCA Paris), Licence BFA (Université du Mans). Lauréat 1er Prix "
            "Hackathon Fintech Générations 2023. Créateur du podcast INCLUTECH. "
            "Board Member Erasmus Expertise. Profil international Haïti / France."
        ),
        "edit_exp": [
            {
                "role":    "Compliance Officer",
                "org":     "HiPay · Levallois-Perret, France",
                "period":  "2024 – 2025",
                "url":     "https://hipay.com",
                "bullets": [
                    "Gestion des alertes de conformité niveau 2 et traitement des dossiers KYS (Know Your Structure)",
                    "Élaboration et mise à jour de la documentation de risques de non-conformité (LCB-FT)",
                    "Préparation, soumission et archivage des déclarations Tracfin auprès de la CRF",
                    "Veille réglementaire (CMF, recommandations ACPR, GAFI) — plans d'action associés",
                    "Vérification des questionnaires partenaires et participation aux audits de conformité",
                ],
            },
            {
                "role":    "Analyste Sécurité Financière — LCB-FT",
                "org":     "Banque Delubac & Cie · Paris",
                "period":  "2023 – 2024",
                "url":     "https://www.delubac.com",
                "bullets": [
                    "Analyse des transactions suspectes (SAR/STR) et évaluation profils de risque KYC/KYB",
                    "Application des directives AMLD5/AMLD6 · supervision ACPR/GAFI · audits de conformité",
                    "Mise à jour politiques LCB-FT internes · accompagnement profils MBA Trading ESLSCA",
                ],
            },
            {
                "role":    "Co-Fondateur · Lauréat 1er Prix — Hackathon Fintech Générations",
                "org":     "France FinTech · Société Générale · Treezor",
                "period":  "Oct. 2023",
                "url":     "https://francefintech.org",
                "bullets": [
                    "Projet Victoria (financement rénovations DPE) — pitch Fintech R:Evolution (1 500 participants)",
                ],
            },
            {
                "role":    "Board Member",
                "org":     "Erasmus Expertise · International",
                "period":  "2021 – Présent",
                "url":     "https://erasmus-expertise.eu",
                "bullets": [
                    "Gouvernance ONG : développement durable · éducation · inclusion sociale internationale",
                ],
            },
            {
                "role":    "Project Manager · Fondateur ANGAJMAN",
                "org":     "Association jeunesse · Haïti",
                "period":  "2018 – 2019",
                "url":     "https://www.hultprize.org",
                "bullets": [
                    "Pilotage projets civiques (10 dép. Haïti) · Hult Prize 2018 — WEISS (biogaz & fertilisant)",
                ],
            },
        ],
        "edit_edu": [
            {
                "deg":    "MBA Trading & Marchés Financiers",
                "school": "ESLSCA Business School Paris",
                "yr":     "2021 – 2023",
                "url":    "https://www.eslsca.fr",
                "det":    "Gestion de portefeuille · Produits dérivés · Analyse quantitative · Conformité",
            },
            {
                "deg":    "Licence Banque, Finance & Assurance",
                "school": "Université du Mans",
                "yr":     "2019 – 2021",
                "url":    "https://www.univ-lemans.fr",
                "det":    "Marchés bancaires · Risk management · Réglementation européenne",
            },
            {
                "deg":    "Sciences Économiques & Gestion",
                "school": "INAGHEI · Université d'État d'Haïti",
                "yr":     "2014 – 2018",
                "url":    "https://www.ueh.edu.ht",
                "det":    "Économie · Gestion · Politiques publiques · Droit",
            },
        ],
        "edit_skills": {
            "LCB-FT / Compliance AML": 95,
            "Réglementation bancaire (ACPR/GAFI)": 92,
            "KYC / KYB / Due Diligence": 90,
            "Analyse financière": 88,
            "Trading & Marchés financiers": 82,
            "Fintech & Paiements digitaux": 80,
            "Gestion des risques": 80,
            "Analyse de données": 73,
        },
        "edit_distinctions": [
            ("🥇", "Hackathon Fintech Générations 2023", "1er Prix · France FinTech / Société Générale / Treezor — Projet Victoria (DPE)"),
            ("🏆", "Hult Prize 2018", "Représentant Haïti · Projet WEISS — biogaz & fertilisant organique"),
            ("🎙", "Podcast INCLUTECH", "Créateur & animateur · Finance & Inclusion Financière · Spotify & Apple Podcasts"),
            ("🌍", "Board Member Erasmus Expertise", "Développement durable · Éducation · Inclusion sociale"),
            ("🔄", "Rotaract Club Haïti", "Leadership étudiant · Service communautaire"),
        ],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# Alias pratiques (toujours à jour depuis session_state)
def _P():
    return {
        "name":     st.session_state.edit_name,
        "title":    st.session_state.edit_title,
        "location": st.session_state.edit_location,
        "email":    st.session_state.edit_email,
        "linkedin": st.session_state.edit_linkedin,
        "summary":  st.session_state.edit_summary,
    }

PROFILE = _P()  # snapshot initial

# ── TIMELINE ──────────────────────────────────────────────────────────────────
TIMELINE = [
    {"year": "2014–2018", "title": "INAGHEI · Université d'État d'Haïti",
     "desc": "Sciences Économiques & Gestion · Faculté Droit & Sciences Éco",
     "url": "https://www.ueh.edu.ht", "icon": "🎓", "cat": "Éducation"},
    {"year": "2018", "title": "Hult Prize — Compétition Internationale",
     "desc": "Projet WEISS : transformation des déchets en biogaz & fertilisant agricole",
     "url": "https://www.hultprize.org", "icon": "🏆", "cat": "Entrepreneuriat"},
    {"year": "2018–2019", "title": "Parlement Haïtien Jeunesse pour l'Eau (PHJEA)",
     "desc": "Engagement citoyen — ressources hydriques · Parlement Mondial de l'Eau",
     "url": "https://www.worldwatercouncil.org", "icon": "🌊", "cat": "Social"},
    {"year": "2018–2019", "title": "Fondateur · Project Manager — ANGAJMAN",
     "desc": "Association jeunesse haïtienne — 10 départements · civique & environnemental",
     "url": "https://www.hultprize.org", "icon": "🤝", "cat": "Social"},
    {"year": "2019–2021", "title": "Université du Mans — Licence BFA",
     "desc": "Banque, Finance & Assurance — réglementation européenne, risk management",
     "url": "https://www.univ-lemans.fr", "icon": "🏫", "cat": "Éducation"},
    {"year": "2021–2023", "title": "ESLSCA Business School Paris — MBA",
     "desc": "Trading & Marchés Financiers — produits dérivés, gestion de portefeuille",
     "url": "https://www.eslsca.fr", "icon": "📈", "cat": "Éducation"},
    {"year": "2021–Présent", "title": "Board Member — Erasmus Expertise",
     "desc": "Gouvernance ONG : développement durable · éducation · inclusion sociale",
     "url": "https://erasmus-expertise.eu", "icon": "🌍", "cat": "Réseau"},
    {"year": "2021–Présent", "title": "Podcast INCLUTECH",
     "desc": "Finance & Inclusion Financière · bi-mensuel · Spotify & Apple Podcasts",
     "url": "https://open.spotify.com/show/5XvFdWYwhHWY3EguIhhf69", "icon": "🎙", "cat": "Réseau"},
    {"year": "Oct. 2023", "title": "🥇 Hackathon Fintech Générations — 1er Prix",
     "desc": "Projet Victoria (financement DPE) · France FinTech / Société Générale / Treezor",
     "url": "https://francefintech.org", "icon": "🚀", "cat": "Entrepreneuriat"},
    {"year": "2023–2024", "title": "Analyste LCB-FT — Banque Delubac & Cie",
     "desc": "Sécurité financière · AMLD5/AMLD6 · KYC/KYB · transactions suspectes",
     "url": "https://www.delubac.com", "icon": "🏦", "cat": "Professionnel"},
    {"year": "2024–2025", "title": "Compliance Officer — HiPay",
     "desc": "Fintech paiement · Tracfin · KYS · alertes N2 · veille réglementaire ACPR/GAFI",
     "url": "https://hipay.com", "icon": "💳", "cat": "Professionnel"},
]

# ── SKILLS ─────────────────────────────────────────────────────────────────────
SKILLS = {
    "LCB-FT / Compliance AML": 95,
    "Réglementation bancaire": 92,
    "KYC / KYB / Due Diligence": 90,
    "Analyse financière": 88,
    "Trading & Marchés": 82,
    "Fintech & Paiements": 80,
    "Gestion des risques": 80,
    "Analyse de données": 73,
}

LANGUAGES = {"Créole haïtien": 100, "Français": 95, "Anglais": 85}

# ── GEO DATA ───────────────────────────────────────────────────────────────────
GEO_DATA = {
    "locations": ["Port-au-Prince, Haïti", "Le Mans, France", "Paris / Levallois-Perret"],
    "lat": [18.5432, 47.9960, 48.8924],
    "lon": [-72.3388, 0.1966, 2.2873],
    "events": ["Formation · INAGHEI · Hult Prize · ANGAJMAN · PHJEA",
               "Licence BFA · Univ. du Mans",
               "MBA ESLSCA · Delubac LCB-FT · HiPay Compliance · France FinTech"],
    "years": ["2014–2019", "2019–2021", "2021–Présent"],
    "size": [18, 14, 34],
}

# ── BIOGRAPHIE 5 PHASES (avec hyperliens) ─────────────────────────────────────
BIO_PERIODS = [
    {
        "phase": "phase1",
        "label": "Phase 1 · 2014 – 2019",
        "title": "Haïti — Racines académiques & éveil entrepreneurial",
        "years": "INAGHEI · FDSE · Hult Prize 2018 · ANGAJMAN · PHJEA",
        "text": [
            'Mackenson Cineus intègre l\'<a href="https://www.ueh.edu.ht" target="_blank" '
            'style="color:#C9A84C;"><b>INAGHEI</b></a> (Institut National d\'Administration de Gestion '
            'et des Hautes Études Internationales) et la <b>FDSE</b> à Port-au-Prince. Il enseigne '
            'à mi-temps en lycée et s\'engage au <a href="https://www.rotary.org/fr/get-involved/rotaract-clubs" '
            'target="_blank" style="color:#C9A84C;"><b>Rotaract Club</b></a>, conjuguant dès ses débuts '
            'exigence académique et responsabilité sociale.',

            'En 2018, il co-fonde <b>ANGAJMAN</b>, association promouvant l\'implication citoyenne de la '
            'jeunesse haïtienne dans les 10 départements, et représente Haïti au '
            '<a href="https://www.hultprize.org" target="_blank" style="color:#C9A84C;"><b>Hult Prize</b></a> '
            '— le « Nobel de l\'entrepreneuriat étudiant » — avec le projet '
            '<b>WEISS</b> (We Integrate Sustainable Solutions) : transformer des déchets organiques '
            'en biogaz et fertilisant agricole pour réduire la déforestation.',

            'Il milite également au <b>Parlement Haïtien de la Jeunesse pour l\'Eau et l\'Assainissement '
            '(<a href="https://www.worldwatercouncil.org" target="_blank" style="color:#C9A84C;">PHJEA</a>)</b>, '
            'affilié au Parlement Mondial de l\'Eau, plaidant pour l\'accès équitable à l\'eau potable.',
        ],
        "tags": ["INAGHEI · UEH", "Hult Prize 2018", "WEISS — Biogaz", "ANGAJMAN", "PHJEA", "Rotaract"],
    },
    {
        "phase": "phase2",
        "label": "Phase 2 · 2019 – 2021",
        "title": "France — Maîtriser les codes de la finance européenne",
        "years": "Université du Mans · Licence BFA · Erasmus Expertise · Podcast INCLUTECH",
        "text": [
            'Mackenson s\'installe en France et intègre l\'<a href="https://www.univ-lemans.fr" '
            'target="_blank" style="color:#C9A84C;"><b>Université du Mans</b></a> en '
            '<b>Licence Banque, Finance & Assurance (BFA)</b> — analyse financière, marchés bancaires, '
            'réglementation européenne, risk management. Une formation rigoureuse qui pose les bases '
            'de sa carrière dans la conformité financière.',

            'En 2021, il rejoint le projet ASPEC d\'<a href="https://erasmus-expertise.eu" '
            'target="_blank" style="color:#C9A84C;"><b>Erasmus Expertise</b></a> — ONG internationale '
            'dédiée au développement durable, l\'éducation et l\'inclusion sociale — dont il '
            'deviendra Board Member. Il lance simultanément son podcast '
            '<a href="https://open.spotify.com/show/5XvFdWYwhHWY3EguIhhf69" target="_blank" '
            'style="color:#C9A84C;"><b>INCLUTECH</b></a> (Spotify & Apple Podcasts), explorant '
            'bi-mensuellement le rôle des fintechs dans l\'inclusion financière mondiale.',
        ],
        "tags": ["Université du Mans", "Licence BFA", "Erasmus Expertise", "Podcast INCLUTECH", "Spotify"],
    },
    {
        "phase": "phase3",
        "label": "Phase 3 · 2021 – 2023",
        "title": "Paris — MBA élite & 1er Prix Hackathon France FinTech",
        "years": "ESLSCA Business School Paris · MBA Trading · Hackathon France FinTech",
        "text": [
            'Mackenson rejoint l\'<a href="https://www.eslsca.fr" target="_blank" '
            'style="color:#C9A84C;"><b>ESLSCA Business School Paris</b></a> pour un '
            '<b>MBA spécialisé en Trading & Marchés Financiers</b> — gestion de portefeuille, '
            'produits dérivés, analyse quantitative et réglementation des marchés.',

            'En octobre 2023, lors de la <b>3e édition du Hackathon Fintech Générations</b> organisé '
            'par <a href="https://francefintech.org" target="_blank" style="color:#C9A84C;">'
            '<b>France FinTech</b></a>, <a href="https://societegenerale.com" target="_blank" '
            'style="color:#C9A84C;"><b>Société Générale</b></a>, Paris&Co et '
            '<a href="https://www.treezor.com" target="_blank" style="color:#C9A84C;"><b>Treezor</b></a>, '
            'son équipe remporte la <b>1ère place</b> avec <b>Victoria</b> — solution de '
            'financement des rénovations DPE. Récompense : pitch à '
            '<b>Fintech R:Evolution</b> (1 500 participants) et un an de membership France FinTech.',
        ],
        "tags": ["MBA ESLSCA", "Trading", "Hackathon 2023 🥇", "Victoria — DPE", "France FinTech"],
    },
    {
        "phase": "phase4",
        "label": "Phase 4 · 2023 – 2024",
        "title": "Banque Delubac — Analyste Sécurité Financière LCB-FT",
        "years": "Banque Delubac & Cie · Paris · LCB-FT / AML / AMLD6",
        "text": [
            'Il intègre la <a href="https://www.delubac.com" target="_blank" '
            'style="color:#C9A84C;"><b>Banque Delubac & Cie</b></a>, institution bancaire privée '
            'française fondée en 1924, comme <b>Analyste Sécurité Financière (LCB-FT)</b>. '
            'Il analyse les transactions suspectes (SAR/STR), évalue les profils de risque '
            'KYC/KYB, applique les directives '
            '<a href="https://www.acpr.banque-france.fr" target="_blank" style="color:#C9A84C;">'
            '<b>AMLD5/AMLD6</b></a> et participe aux audits de conformité sous supervision ACPR.',

            'Cette expérience consolide sa maîtrise des processus LCB-FT en environnement bancaire '
            'réglementé, et lui permet de bâtir une expertise reconnue dans la surveillance des '
            'risques financiers. Il y accompagne également des profils MBA (ESLSCA) dans leur '
            'insertion professionnelle.',
        ],
        "tags": ["Banque Delubac", "LCB-FT", "AML · AMLD6", "KYC/KYB", "ACPR", "Paris"],
    },
    {
        "phase": "phase5",
        "label": "Phase 5 · 2024 – 2025",
        "title": "HiPay — Compliance Officer en Fintech de Paiement",
        "years": "HiPay · Levallois-Perret · Compliance · Tracfin · KYS · Paiements",
        "text": [
            '<a href="https://hipay.com" target="_blank" style="color:#C9A84C;"><b>HiPay</b></a> '
            'est un prestataire de services de paiement omnicanal coté sur Euronext Growth '
            '(ALHYP), agréé par l\'<a href="https://acpr.banque-france.fr" target="_blank" '
            'style="color:#C9A84C;"><b>ACPR</b></a> comme établissement de paiement, dont les '
            'clients incluent Veepee, Nocibé, Pizza Hut et Metro. Mackenson y rejoint le '
            'département Conformité à Levallois-Perret en tant que <b>Compliance Officer</b>.',

            'Ses responsabilités couvrent : la gestion des alertes de conformité <b>niveau 2</b>, '
            'le traitement des dossiers <b>KYS</b> (Know Your Structure), la préparation et '
            'soumission des <b>déclarations Tracfin</b> auprès de la Cellule de Renseignement '
            'Financier, la vérification des questionnaires partenaires, et la <b>veille '
            'réglementaire</b> (CMF, recommandations '
            '<a href="https://acpr.banque-france.fr" target="_blank" style="color:#C9A84C;">'
            'ACPR</a>, <a href="https://www.fatf-gafi.org" target="_blank" style="color:#C9A84C;">'
            'GAFI</a>) avec mise en œuvre des plans d\'action associés.',

            'Cette expérience en environnement fintech de paiement complète idéalement son '
            'expertise bancaire : Mackenson maîtrise désormais la conformité à la fois dans les '
            'établissements bancaires traditionnels et dans les acteurs tech innovants du paiement '
            'numérique — un profil doublement certifié, rare sur le marché.',
        ],
        "tags": ["HiPay · ALHYP", "Compliance Officer", "Tracfin", "KYS", "Paiements digitaux", "ACPR/GAFI"],
    },
]

# ── PLATFORMS ──────────────────────────────────────────────────────────────────
PLATFORMS = [
    {"icon": "💼", "name": "LinkedIn",
     "desc": "Profil professionnel complet — expériences HiPay & Delubac, réseau finance/fintech parisien.",
     "url": "https://www.linkedin.com/in/mackenson-cineus", "label": "Voir le profil →"},
    {"icon": "💳", "name": "HiPay",
     "desc": "Fintech paiement omnicanal cotée (ALHYP) — Mackenson y était Compliance Officer 2024–2025.",
     "url": "https://hipay.com", "label": "Site HiPay →"},
    {"icon": "🏦", "name": "Banque Delubac & Cie",
     "desc": "Banque privée indépendante fondée en 1924 — Analyste LCB-FT 2023–2024.",
     "url": "https://www.delubac.com", "label": "Site Delubac →"},
    {"icon": "🚀", "name": "France FinTech",
     "desc": "Association de référence fintech française — Lauréat Hackathon 2023, membre actif.",
     "url": "https://francefintech.org", "label": "France FinTech →"},
    {"icon": "🏆", "name": "Hult Prize Foundation",
     "desc": "Compétition internationale entrepreneuriat social — Haïti 2018 · Projet WEISS.",
     "url": "https://www.hultprize.org", "label": "Hult Prize →"},
    {"icon": "🎓", "name": "ESLSCA Business School Paris",
     "desc": "MBA Trading & Marchés Financiers 2021–2023.",
     "url": "https://www.eslsca.fr", "label": "ESLSCA →"},
    {"icon": "🏫", "name": "Université du Mans",
     "desc": "Licence Banque-Finance-Assurance 2019–2021.",
     "url": "https://www.univ-lemans.fr", "label": "Université du Mans →"},
    {"icon": "🎙", "name": "Podcast INCLUTECH",
     "desc": "Finance & Inclusion Financière — Spotify & Apple Podcasts · bi-mensuel.",
     "url": "https://open.spotify.com/show/5XvFdWYwhHWY3EguIhhf69", "label": "Écouter →"},
    {"icon": "🌍", "name": "Erasmus Expertise",
     "desc": "Board Member — développement durable, éducation, inclusion sociale.",
     "url": "https://erasmus-expertise.eu", "label": "Erasmus Expertise →"},
    {"icon": "📸", "name": "Instagram",
     "desc": "@mackenson_cineus — présence personnelle et professionnelle.",
     "url": "https://instagram.com/mackenson_cineus", "label": "Instagram →"},
]

REGULATORS = [
    ("🇫🇷", "ACPR", "Régulateur bancaire & paiement français — LCB-FT", "https://acpr.banque-france.fr"),
    ("🌐", "FATF / GAFI", "Normes mondiales anti-blanchiment", "https://www.fatf-gafi.org"),
    ("💰", "Tracfin", "Cellule de Renseignement Financier française", "https://www.economie.gouv.fr/tracfin"),
    ("📊", "AMF", "Autorité des Marchés Financiers", "https://www.amf-france.org"),
]

# ── CSS additionnel pour phase5 ─────────────────────────────────────────────
# (injecté séparément car le style est dans le bloc CSS principal)
_PHASE5_CSS = """
<style>
  .bio-period.phase5::before { background:linear-gradient(180deg,#00B4D8,#0077B6); }
  .phase5 .bio-phase-label { color:#00B4D8; }
</style>
"""

NAVY_C      = rl_colors.HexColor('#0D1B2A')
NAVY_MID_C  = rl_colors.HexColor('#1A2E42')
GOLD_C      = rl_colors.HexColor('#C9A84C')
GOLD_L_C    = rl_colors.HexColor('#E8C97A')
GRAY_D_C    = rl_colors.HexColor('#333333')
GRAY_M_C    = rl_colors.HexColor('#555555')
GRAY_L_C    = rl_colors.HexColor('#999999')
ACCENT_C    = rl_colors.HexColor('#4A9EFF')
CREAM_C     = rl_colors.HexColor('#F8F6F2')


def _page_frame(canvas, doc):
    """Minimal header/footer for all PDF pages."""
    W, H = A4
    canvas.saveState()
    # Top gold bar
    canvas.setFillColor(NAVY_C)
    canvas.rect(0, H - 1.6*cm, W, 1.6*cm, fill=1, stroke=0)
    canvas.setFillColor(GOLD_C)
    canvas.rect(0, H - 1.6*cm, W, 0.10*cm, fill=1, stroke=0)
    canvas.setFillColor(rl_colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(1.8*cm, H - 1.05*cm, "CINÉUS Mackenson")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GOLD_C)
    canvas.drawString(5.5*cm, H - 1.05*cm, "Finance · Compliance · Fintech")
    # Bottom bar
    canvas.setFillColor(NAVY_C)
    canvas.rect(0, 0, W, 0.9*cm, fill=1, stroke=0)
    canvas.setFillColor(GRAY_L_C)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(1.8*cm, 0.32*cm, "linkedin.com/in/mackenson-cineus  ·  Podcast INCLUTECH  ·  @mackenson_cineus")
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(GOLD_C)
    canvas.drawRightString(W - 1.8*cm, 0.32*cm, f"Page {doc.page}")
    canvas.restoreState()


def _s(name, **kw):
    defaults = dict(fontName='Helvetica', fontSize=9, textColor=GRAY_D_C,
                    leading=13, spaceAfter=3)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)


def _hr(color=GOLD_C, thickness=1.2):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceAfter=5, spaceBefore=3)


def _section(label):
    """A clean section header with gold underline."""
    row = [[Paragraph(f'<font color="#C9A84C"><b>{label.upper()}</b></font>',
                      _s('sh', fontSize=8.5, textColor=GOLD_C, letterSpacing=1.5))]]
    t = Table(row, colWidths=['100%'])
    t.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 1.2, GOLD_C),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    return t



# ═══════════════════════════════════════════════════════════════════════════════
# PDF GENERATION — CV (1 page), LETTRE (1 page), BIOGRAPHIE (2 pages)
# ═══════════════════════════════════════════════════════════════════════════════

NAVY_C    = rl_colors.HexColor('#0D1B2A')
GOLD_C    = rl_colors.HexColor('#C9A84C')
GRAY_D_C  = rl_colors.HexColor('#333333')
GRAY_M_C  = rl_colors.HexColor('#555555')
GRAY_L_C  = rl_colors.HexColor('#999999')
CREAM_C   = rl_colors.HexColor('#F8F6F2')
ACCENT_C  = rl_colors.HexColor('#4A9EFF')
NAVY_M_C  = rl_colors.HexColor('#1A2E42')

def _s(name, **kw):
    d = dict(fontName='Helvetica', fontSize=9, textColor=GRAY_D_C, leading=13, spaceAfter=3)
    d.update(kw)
    return ParagraphStyle(name, **d)

def _hr(color=GOLD_C, t=1.0, before=2, after=5):
    return HRFlowable(width="100%", thickness=t, color=color, spaceBefore=before, spaceAfter=after)

def _sec(label, size=7, letter=1.5):
    return [
        Paragraph(f'<font color="#C9A84C"><b>{label.upper()}</b></font>',
                  _s('sh', fontSize=size, letterSpacing=letter, spaceAfter=1, spaceBefore=7)),
        HRFlowable(width="100%", thickness=0.7, color=GOLD_C, spaceAfter=3, spaceBefore=0),
    ]

def _page_frame(canvas, doc):
    """Shared header/footer for all PDFs."""
    W, H = A4
    canvas.saveState()
    canvas.setFillColor(NAVY_C); canvas.rect(0, H-1.55*cm, W, 1.55*cm, fill=1, stroke=0)
    canvas.setFillColor(GOLD_C); canvas.rect(0, H-1.55*cm, W, 0.09*cm, fill=1, stroke=0)
    canvas.setFillColor(rl_colors.white); canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(1.8*cm, H-1.0*cm, "CINÉUS Mackenson")
    canvas.setFillColor(GOLD_C); canvas.setFont("Helvetica", 7.5)
    canvas.drawString(5.8*cm, H-1.0*cm, "Finance · Compliance · Fintech · Paris")
    canvas.setFillColor(NAVY_C); canvas.rect(0, 0, W, 0.85*cm, fill=1, stroke=0)
    canvas.setFillColor(GOLD_C); canvas.rect(0, 0.85*cm, W, 0.07*cm, fill=1, stroke=0)
    canvas.setFillColor(rl_colors.HexColor('#888888')); canvas.setFont("Helvetica", 7)
    canvas.drawString(1.8*cm, 0.3*cm,
        "linkedin.com/in/mackenson-cineus  ·  Podcast INCLUTECH  ·  @mackenson_cineus")
    canvas.setFillColor(GOLD_C)
    canvas.drawRightString(W-1.8*cm, 0.3*cm, f"Page {doc.page}")
    canvas.restoreState()


# ─────────────────────────────────────────────────────────────────────────────
# CV — 1 PAGE BICOLONNE FINANCE
# ─────────────────────────────────────────────────────────────────────────────
def generate_cv_pdf(poste="", entreprise="", secteur="", contexte="") -> bytes:
    buf = io.BytesIO()
    W, H = A4
    SB = 4.45 * cm  # sidebar width

    # Pull live data
    import streamlit as _st
    P         = _st.session_state
    name      = P.get("edit_name",     "Mackenson CINÉUS")
    title_cv  = P.get("edit_title",    "Compliance Officer | LCB-FT")
    location  = P.get("edit_location", "Île-de-France, France")
    linkedin  = P.get("edit_linkedin", "linkedin.com/in/mackenson-cineus")
    summary   = P.get("edit_summary",  "")
    exps_raw  = P.get("edit_exp",      [])
    edu_raw   = P.get("edit_edu",      [])
    skills_d  = P.get("edit_skills",   {"LCB-FT / AML": 95})
    dists     = P.get("edit_distinctions", [])

    def draw_page(canvas, doc):
        canvas.saveState()
        # Sidebar
        canvas.setFillColor(NAVY_C);  canvas.rect(0, 0, SB, H, fill=1, stroke=0)
        canvas.setFillColor(GOLD_C);  canvas.rect(SB, 0, 0.16*cm, H, fill=1, stroke=0)
        # Header bar
        canvas.setFillColor(NAVY_C);  canvas.rect(SB, H-3.0*cm, W-SB, 3.0*cm, fill=1, stroke=0)
        canvas.setFillColor(GOLD_C);  canvas.rect(SB, H-3.0*cm, W-SB, 0.09*cm, fill=1, stroke=0)
        # Name & title
        canvas.setFillColor(rl_colors.white); canvas.setFont("Helvetica-Bold", 18)
        canvas.drawString(SB+0.55*cm, H-1.45*cm, name)
        canvas.setFillColor(GOLD_C); canvas.setFont("Helvetica", 8)
        t_line = title_cv + (f"  ·  {poste}" if poste else "")
        canvas.drawString(SB+0.55*cm, H-1.95*cm, t_line)
        canvas.setFillColor(rl_colors.HexColor('#BBBBBB')); canvas.setFont("Helvetica", 6.8)
        canvas.drawString(SB+0.55*cm, H-2.5*cm,
            f"{location}  ·  {linkedin}  ·  Podcast INCLUTECH  ·  @mackenson_cineus")

        def sb_sec(label, y):
            canvas.setFillColor(GOLD_C); canvas.setFont("Helvetica-Bold", 5.8)
            canvas.drawString(0.28*cm, y, label.upper())
            canvas.rect(0.28*cm, y-0.09*cm, SB-0.55*cm, 0.045*cm, fill=1, stroke=0)

        def sb_txt(text, y, color='#CDD8E8', size=6.3, bold=False):
            if not text: return
            canvas.setFillColor(rl_colors.HexColor(color))
            canvas.setFont("Helvetica-Bold" if bold else "Helvetica", size)
            # truncate if too wide
            max_w = SB - 0.6*cm
            while canvas.stringWidth(text, "Helvetica-Bold" if bold else "Helvetica", size) > max_w and len(text) > 5:
                text = text[:-2]
            canvas.drawString(0.38*cm, y, text)

        # COMPÉTENCES
        y = H - 3.5*cm
        sb_sec("Compétences", y); y -= 0.4*cm
        for sk in list(skills_d.keys())[:10]:
            sb_txt(sk, y); y -= 9.5

        # LANGUES
        y -= 0.25*cm; sb_sec("Langues", y); y -= 0.4*cm
        for lang, lvl in [("Créole haïtien","Natif"),("Français","C2"),("Anglais","B2/C1")]:
            sb_txt(lang, y, bold=True); y -= 8.5
            sb_txt(lvl, y, color='#C9A84C', size=6); y -= 11

        # CONTACT
        y -= 0.25*cm; sb_sec("Contact", y); y -= 0.4*cm
        for line in [location, linkedin, "", "Podcast: INCLUTECH", "Spotify & Apple", "", "@mackenson_cineus"]:
            sb_txt(line, y); y -= 8.5

        # DISTINCTIONS
        y -= 0.25*cm; sb_sec("Distinctions", y); y -= 0.4*cm
        for icon, ttl, _ in dists[:5]:
            sb_txt(f"{icon} {ttl}", y); y -= 8.5

        canvas.restoreState()

    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=SB+0.55*cm, rightMargin=1.0*cm,
        topMargin=3.2*cm, bottomMargin=0.85*cm)

    def s(n, **kw):
        d = dict(fontName='Helvetica', fontSize=8.2, textColor=GRAY_D_C, leading=11.5, spaceAfter=1.5)
        d.update(kw); return ParagraphStyle(n, **d)

    story = []

    # PROFIL
    story.extend(_sec("Profil", size=6.8))
    story.append(Paragraph(
        f"Compliance Officer & Analyste LCB-FT — expérience en fintech de paiement "
        f"(<b>HiPay</b>) et banque privée (<b>Delubac</b>). "
        f"<b>MBA Trading &amp; Marchés Financiers</b> (ESLSCA Paris) · <b>Licence BFA</b> (Univ. du Mans). "
        f"<b>1er Prix Hackathon Fintech Générations 2023</b> (France FinTech / SG). "
        f"Podcast <b>INCLUTECH</b> · Board Member Erasmus Expertise · Haïti / France.",
        s('p', fontSize=7.6, leading=10.5, alignment=TA_JUSTIFY, spaceAfter=0)))

    # EXPÉRIENCES
    story.extend(_sec("Expériences Professionnelles", size=6.8))
    for exp in exps_raw:
        t = Table([[
            Paragraph(f"<b>{exp['role']}</b>",
                      s('r', fontSize=8.2, textColor=NAVY_C, spaceAfter=0)),
            Paragraph(f"<i>{exp['period']}</i>",
                      s('d', fontSize=7.2, textColor=GRAY_L_C, alignment=TA_RIGHT, spaceAfter=0)),
        ]], colWidths=['67%','33%'])
        t.setStyle(TableStyle([
            ('TOPPADDING',(0,0),(-1,-1),4), ('BOTTOMPADDING',(0,0),(-1,-1),0)]))
        story.append(t)
        story.append(Paragraph(f"<font color='#C9A84C'>{exp['org']}</font>",
                                s('o', fontSize=7.2, spaceAfter=1)))
        for b in exp['bullets']:
            story.append(Paragraph(f"▸  {b}",
                                   s('b', fontSize=7.2, leading=10, leftIndent=5, spaceAfter=1)))

    # FORMATION
    story.extend(_sec("Formation", size=6.8))
    for e in edu_raw:
        t = Table([[
            Paragraph(f"<b>{e['deg']}</b>  <font color='#999'>· {e['school']}</font>",
                      s('fd', fontSize=7.8, textColor=NAVY_C, spaceAfter=0)),
            Paragraph(f"<i>{e['yr']}</i>",
                      s('fy', fontSize=7.2, textColor=GRAY_L_C, alignment=TA_RIGHT, spaceAfter=0)),
        ]], colWidths=['72%','28%'])
        t.setStyle(TableStyle([
            ('TOPPADDING',(0,0),(-1,-1),3), ('BOTTOMPADDING',(0,0),(-1,-1),0)]))
        story.append(t)
        story.append(Paragraph(e['det'], s('det', fontSize=7.2, textColor=GRAY_M_C, spaceAfter=0)))

    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    buf.seek(0); return buf.read()


# ─────────────────────────────────────────────────────────────────────────────
# LETTRE DE MOTIVATION — 1 PAGE
# ─────────────────────────────────────────────────────────────────────────────
def generate_lettre_pdf(poste="", entreprise="", secteur="", style_lm="",
                         contexte="", ai_text="") -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=2.0*cm, rightMargin=2.0*cm,
        topMargin=2.0*cm, bottomMargin=1.6*cm)

    import streamlit as _st
    P = _st.session_state
    name     = P.get("edit_name",     "Mackenson CINÉUS")
    title_lm = P.get("edit_title",    "Compliance Officer | LCB-FT")
    location = P.get("edit_location", "Île-de-France, France")
    linkedin = P.get("edit_linkedin", "linkedin.com/in/mackenson-cineus")

    story = []

    # ── EN-TÊTE BICOLONNE ─────────────────────────────────────────────
    hl = Paragraph(
        f"<b>{name}</b><br/>"
        f"<font color='#C9A84C'>{title_lm}</font><br/>"
        f"{location}<br/>{linkedin}",
        _s('hl', fontSize=8.8, leading=13))
    hr = Paragraph(
        f"<b>Direction des Ressources Humaines</b><br/>"
        f"{entreprise or '[Entreprise]'}<br/>{secteur or '[Secteur]'}<br/>France",
        _s('hr', fontSize=8.8, leading=13, alignment=TA_RIGHT))
    ht = Table([[hl, hr]], colWidths=[9*cm, 8.7*cm])
    ht.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),
                              ('TOPPADDING',(0,0),(-1,-1),0)]))
    story.append(ht)
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Paris, le 14 mars 2026",
                            _s('dt', fontSize=8.5, textColor=GRAY_M_C, alignment=TA_RIGHT)))
    story.append(Spacer(1, 0.25*cm))

    # ── OBJET ────────────────────────────────────────────────────────
    obj_txt = f"Objet : <b>Candidature — {poste or 'Compliance Officer / Analyste Risques'}" \
              f"{' — ' + entreprise if entreprise else ''}</b>"
    obj_t = Table([[Paragraph(obj_txt, _s('obj', fontSize=9, textColor=NAVY_C))]],
                   colWidths=['100%'])
    obj_t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), CREAM_C),
        ('LINEBELOW',(0,0),(-1,-1), 1.5, GOLD_C),
        ('LINEABOVE',(0,0),(-1,-1), 0.3, GOLD_C),
        ('TOPPADDING',(0,0),(-1,-1), 7),
        ('BOTTOMPADDING',(0,0),(-1,-1), 7),
        ('LEFTPADDING',(0,0),(-1,-1), 10),
    ]))
    story.append(obj_t)
    story.append(Spacer(1, 0.35*cm))

    # ── CORPS ────────────────────────────────────────────────────────
    story.append(Paragraph("Madame, Monsieur,",
                            _s('sal', fontSize=9.3, spaceAfter=8)))

    body_style = _s('body', fontSize=9.2, leading=14.5, alignment=TA_JUSTIFY, spaceAfter=9)

    if ai_text and len(ai_text) > 100:
        for para in ai_text.split("\n\n"):
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
    else:
        story.append(Paragraph(
            f"De Port-au-Prince à Paris, mon parcours est celui d'une construction méthodique "
            f"vers l'excellence en conformité financière. Compliance Officer chez <b>HiPay</b> "
            f"(2024–2025) et Analyste LCB-FT chez <b>Banque Delubac & Cie</b> (2023–2024), "
            f"titulaire d'un <b>MBA Trading & Marchés Financiers</b> (ESLSCA Paris) et lauréat "
            f"du <b>1er Prix Hackathon Fintech Générations 2023</b> (France FinTech / Société "
            f"Générale), je me permets de soumettre ma candidature"
            f"{' au poste de ' + poste if poste else ''} au sein de votre organisation.",
            body_style))
        story.append(Paragraph(
            f"Chez HiPay — fintech de paiement agréée ACPR — j'ai géré les alertes de "
            f"conformité niveau 2, traité les dossiers KYS, préparé les déclarations Tracfin "
            f"et assuré la veille réglementaire (CMF, ACPR, GAFI). Chez Banque Delubac, j'ai "
            f"analysé des transactions suspectes (SAR/STR), évalué les profils de risque KYC/KYB "
            f"et appliqué les directives AMLD5/AMLD6 — deux environnements complémentaires qui "
            f"m'ont conféré une maîtrise complète de la conformité bancaire et fintech.",
            body_style))
        story.append(Paragraph(
            f"Au-delà de l'expertise technique, j'apporte une perspective distinctive : "
            f"fondateur d'<b>ANGAJMAN</b>, représentant Haïti au <b>Hult Prize</b>, "
            f"créateur du podcast <b>INCLUTECH</b> sur l'inclusion financière, et "
            f"Board Member d'<b>Erasmus Expertise</b>. Cette double culture — entrepreneuriat "
            f"social et finance institutionnelle — me permet d'aborder la conformité avec "
            f"une rigueur analytique et une vision éthique rare dans un profil junior.",
            body_style))
        story.append(Paragraph(
            f"Convaincu que mon profil constituerait un atout réel pour "
            f"{'votre organisation ' + entreprise if entreprise else 'votre organisation'}, "
            f"je reste disponible pour un entretien à votre convenance.",
            body_style))

    story.append(Paragraph(
        "Dans cette attente, je vous prie d'agréer l'expression de mes salutations les plus respectueuses.",
        _s('close', fontSize=9.2, leading=14, alignment=TA_JUSTIFY, spaceAfter=16)))

    story.append(Paragraph(f"<b>{name}</b>",
                            _s('sig', fontSize=10.5, textColor=NAVY_C, spaceAfter=2)))
    story.append(Paragraph(f"<font color='#C9A84C'>{title_lm}</font>",
                            _s('sig2', fontSize=8.5, spaceAfter=0)))
    story.append(Spacer(1, 0.5*cm))
    story.append(_hr(GRAY_L_C, 0.4))
    story.append(Paragraph(
        "<i>PJ : Curriculum Vitæ · Références disponibles sur demande</i>",
        _s('pj', fontSize=7.5, textColor=GRAY_L_C)))

    doc.build(story, onFirstPage=_page_frame, onLaterPages=_page_frame)
    buf.seek(0); return buf.read()


# ─────────────────────────────────────────────────────────────────────────────
# BIOGRAPHIE — 2 PAGES avec hyperliens sources
# ─────────────────────────────────────────────────────────────────────────────
def generate_bio_pdf() -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=1.7*cm, rightMargin=1.7*cm,
        topMargin=2.0*cm, bottomMargin=1.4*cm)

    story = []

    # ── PAGE 1 : COVER + PHASES 1–3 ──────────────────────────────────
    # Title block
    t_data = [[
        Paragraph(
            '<font name="Helvetica-Bold" size="26" color="#0D1B2A">CINÉUS</font>'
            '  <font name="Helvetica" size="26" color="#0D1B2A">Mackenson</font>',
            _s('bn', fontSize=26, leading=30, spaceAfter=0)),
        Paragraph(
            '<font color="#C9A84C" size="8">Finance · Compliance · Fintech · Paris</font>',
            _s('bs', fontSize=8, alignment=TA_RIGHT, spaceAfter=0,
               textColor=rl_colors.HexColor('#C9A84C')))
    ]]
    story.append(Table(t_data, colWidths=[11.5*cm, 5.3*cm]))
    story.append(_hr(NAVY_C, 2.0, before=3, after=4))

    story.append(Paragraph(
        '<i>"De Port-au-Prince à Levallois-Perret — Compliance Officer en fintech de paiement, '
        'analyste LCB-FT en banque privée, lauréat d\'un hackathon France FinTech, créateur d\'un '
        'podcast sur l\'inclusion financière. Un parcours construit avec intention."</i>',
        _s('q', fontSize=8.5, fontName='Helvetica-Oblique', textColor=NAVY_M_C,
           leading=12.5, leftIndent=6, spaceAfter=8, backColor=CREAM_C)))

    # ── KPI ROW ──────────────────────────────────────────────────────
    kpis = [
        ("💳", "HiPay", "Compliance Officer\n2024–2025"),
        ("🏦", "Delubac", "Analyste LCB-FT\n2023–2024"),
        ("🥇", "Hackathon 2023", "1er Prix · Victoria\nFrance FinTech"),
        ("🎙", "INCLUTECH", "Podcast Fintech\nSpotify & Apple"),
        ("🌍", "Erasmus", "Board Member\nONG internationale"),
    ]
    kpi_cells = []
    for icon, ttl, sub in kpis:
        kpi_cells.append(Paragraph(
            f'<font size="12">{icon}</font><br/>'
            f'<b><font size="7.5" color="#C9A84C">{ttl}</font></b><br/>'
            f'<font size="6.5" color="#888888">{sub.replace(chr(10),"<br/>")}</font>',
            _s('kc', fontSize=6.5, leading=9.5, alignment=TA_CENTER)))
    kpi_t = Table([kpi_cells], colWidths=[3.33*cm]*5)
    kpi_t.setStyle(TableStyle([
        ('ALIGN',(0,0),(-1,-1),'CENTER'), ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[CREAM_C]),
        ('LINEAFTER',(0,0),(3,-1),0.3,GRAY_L_C),
    ]))
    story.append(kpi_t)
    story.append(Spacer(1, 6))

    def phase_block(label, title, color_hex, paras_html, sources):
        """Render one phase block with colored left bar."""
        # Sources line
        src_parts = []
        for name_s, url_s in sources:
            src_parts.append(
                f'<font color="#4A9EFF"><u>{name_s}</u></font> '
                f'<font size="6" color="#888888">({url_s})</font>')
        src_line = "  ·  ".join(src_parts)

        body_paras = []
        for txt in paras_html:
            body_paras.append(
                Paragraph(txt, _s('pb', fontSize=8.2, leading=12.5,
                                   alignment=TA_JUSTIFY, spaceAfter=4)))
        if src_line:
            body_paras.append(Paragraph(
                f'<font size="6.5" color="#888888"><i>Sources : {src_line}</i></font>',
                _s('src', fontSize=6.5, spaceAfter=0)))

        header = Table([[
            "",
            Paragraph(
                f'<font color="{color_hex}" size="6.5"><b>{label.upper()}</b></font><br/>'
                f'<font size="10" color="#0D1B2A"><b>{title}</b></font>',
                _s('ph', fontSize=10, leading=13.5, spaceAfter=0))
        ]], colWidths=[0.22*cm, 16.3*cm])
        header.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(0,-1), rl_colors.HexColor(color_hex)),
            ('BACKGROUND',(1,0),(1,-1), CREAM_C),
            ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
            ('LEFTPADDING',(1,0),(1,-1),7), ('RIGHTPADDING',(1,0),(1,-1),5),
        ]))

        inner_rows = [[p] for p in body_paras]
        inner = Table(inner_rows, colWidths=[16.6*cm])
        inner.setStyle(TableStyle([
            ('TOPPADDING',(0,0),(-1,-1),0), ('BOTTOMPADDING',(0,0),(-1,-1),0),
            ('LEFTPADDING',(0,0),(-1,-1),8), ('RIGHTPADDING',(0,0),(-1,-1),0),
        ]))

        return KeepTogether([header, inner, Spacer(1, 5)])

    # ── PHASE 1 ──────────────────────────────────────────────────────
    story.append(phase_block(
        "Phase 1 · 2014–2019 · Haïti",
        "Racines Académiques & Éveil Entrepreneurial",
        "#4A9EFF",
        [
            "Mackenson Cineus intègre l'<b>INAGHEI</b> (Institut National d'Administration de "
            "Gestion et des Hautes Études Internationales) et la <b>FDSE</b> à l'Université "
            "d'État d'Haïti. Il enseigne à mi-temps en lycée et s'engage au <b>Rotaract Club</b>.",

            "En 2018, il co-fonde <b>ANGAJMAN</b> (projets civiques dans 10 départements) et "
            "représente Haïti au <b>Hult Prize</b> avec le projet <b>WEISS</b> — biogaz et "
            "fertilisant organique à partir de déchets. Il milite au <b>Parlement Haïtien de "
            "la Jeunesse pour l'Eau (PHJEA)</b> pour l'accès équitable à l'eau potable.",
        ],
        [("INAGHEI / UEH", "ueh.edu.ht"), ("Hult Prize", "hultprize.org"),
         ("Rotary / Rotaract", "rotary.org")]))

    # ── PHASE 2 ──────────────────────────────────────────────────────
    story.append(phase_block(
        "Phase 2 · 2019–2021 · Le Mans",
        "Transition Internationale — Finance Européenne & Podcast INCLUTECH",
        "#C9A84C",
        [
            "Mackenson décroche une <b>Licence Banque, Finance & Assurance</b> à l'<b>Université "
            "du Mans</b> — marchés bancaires, risk management, réglementation européenne.",

            "Il rejoint <b>Erasmus Expertise</b> (projet ASPEC) et lance le podcast "
            "<b>INCLUTECH</b> (Spotify & Apple Podcasts) : bi-mensuel, dédié au rôle des "
            "fintechs dans l'inclusion financière des populations non bancarisées.",
        ],
        [("Université du Mans", "univ-lemans.fr"),
         ("Erasmus Expertise", "erasmus-expertise.eu"),
         ("INCLUTECH Spotify", "open.spotify.com/show/5XvFdWYwhHWY3EguIhhf69")]))

    # ── PHASE 3 ──────────────────────────────────────────────────────
    story.append(phase_block(
        "Phase 3 · 2021–2023 · Paris",
        "MBA ESLSCA & 1er Prix Hackathon Fintech Générations 2023",
        "#E67E22",
        [
            "<b>MBA Trading & Marchés Financiers</b> à l'<b>ESLSCA Business School Paris</b> "
            "— gestion de portefeuille, produits dérivés, analyse quantitative, conformité.",

            "Octobre 2023 : <b>1er Prix Hackathon Fintech Générations</b> organisé par "
            "<b>France FinTech, Société Générale, Treezor et Paris&Co</b> avec le projet "
            "<b>Victoria</b> (financement rénovations DPE). Invitation à pitcher à "
            "<b>Fintech R:Evolution</b> (1 500 participants). Nommé <b>Board Member "
            "d'Erasmus Expertise</b>.",
        ],
        [("ESLSCA Paris", "eslsca.fr"), ("France FinTech", "francefintech.org"),
         ("Société Générale", "societegenerale.com"), ("Treezor", "treezor.com")]))

    # ── PAGE BREAK ───────────────────────────────────────────────────
    from reportlab.platypus import PageBreak
    story.append(PageBreak())

    # ── PAGE 2 : PHASES 4–5 + SYNTHÈSE ──────────────────────────────
    story.append(phase_block(
        "Phase 4 · 2023–2024 · Paris",
        "Banque Delubac & Cie — Analyste Sécurité Financière LCB-FT",
        "#9B59B6",
        [
            "<b>Banque Delubac & Cie</b> (fondée 1924, banque privée & gestion d'actifs) — "
            "<b>Analyste Sécurité Financière LCB-FT</b> : analyse transactions suspectes "
            "(SAR/STR), évaluation profils de risque KYC/KYB, application directives "
            "<b>AMLD5/AMLD6</b> sous supervision ACPR/GAFI.",

            "Il consolide sa maîtrise des processus LCB-FT en environnement bancaire réglementé "
            "et accompagne des profils MBA ESLSCA dans leur insertion professionnelle.",
        ],
        [("Banque Delubac", "delubac.com"),
         ("ACPR", "acpr.banque-france.fr"), ("GAFI", "fatf-gafi.org")]))

    story.append(phase_block(
        "Phase 5 · 2024–2025 · Levallois-Perret",
        "HiPay — Compliance Officer en Fintech de Paiement",
        "#00B4D8",
        [
            "<b>HiPay</b> est un prestataire de services de paiement omnicanal coté sur "
            "<b>Euronext Growth (ALHYP)</b>, agréé par l'<b>ACPR</b> comme établissement de "
            "paiement. Clients : Veepee, Nocibé, Pizza Hut, Metro.",

            "Mackenson y est <b>Compliance Officer</b> : gestion des alertes niveau 2, "
            "traitement dossiers <b>KYS</b> (Know Your Structure), préparation des "
            "<b>déclarations Tracfin</b> (CRF), vérification questionnaires partenaires, "
            "<b>veille réglementaire</b> (CMF, ACPR, GAFI) avec plans d'action associés.",

            "Cette expérience en fintech de paiement complète idéalement son expertise "
            "bancaire : Mackenson maîtrise désormais la conformité dans les établissements "
            "bancaires traditionnels ET les acteurs tech du paiement numérique.",
        ],
        [("HiPay", "hipay.com"), ("ACPR", "acpr.banque-france.fr"),
         ("Tracfin", "economie.gouv.fr/tracfin"), ("GAFI", "fatf-gafi.org")]))

    # ── SYNTHÈSE FINALE ───────────────────────────────────────────────
    story.append(_hr(NAVY_C, 1.5, before=4, after=4))
    story.append(Paragraph(
        '<b><font color="#0D1B2A" size="10">Synthèse — Présences en ligne & Sources</font></b>',
        _s('sh2', fontSize=10, spaceAfter=6)))

    links = [
        ("LinkedIn",    "linkedin.com/in/mackenson-cineus",
         "500+ connexions · Réseau finance/fintech franco-international"),
        ("HiPay",       "hipay.com",
         "Employeur 2024–2025 · Paiement omnicanal · Euronext Growth ALHYP"),
        ("Banque Delubac","delubac.com",
         "Employeur 2023–2024 · Banque privée fondée 1924"),
        ("INCLUTECH Spotify","open.spotify.com/show/5XvFdWYwhHWY3EguIhhf69",
         "Podcast bi-mensuel · Finance & Inclusion · Spotify & Apple Podcasts"),
        ("France FinTech","francefintech.org",
         "Lauréat Hackathon 2023 · Membre actif · Fintech R:Evolution"),
        ("ESLSCA Paris","eslsca.fr","MBA Trading & Marchés Financiers 2021–2023"),
        ("Université du Mans","univ-lemans.fr","Licence BFA 2019–2021"),
        ("Erasmus Expertise","erasmus-expertise.eu","Board Member · ONG internationale"),
        ("Instagram","instagram.com/mackenson_cineus","@mackenson_cineus"),
        ("ACPR","acpr.banque-france.fr","Régulateur bancaire/paiement · Référence LCB-FT"),
        ("Tracfin","economie.gouv.fr/tracfin","Cellule de Renseignement Financier française"),
        ("GAFI / FATF","fatf-gafi.org","Normes mondiales anti-blanchiment"),
    ]
    link_rows = []
    for i in range(0, len(links), 2):
        row = []
        for j in range(2):
            if i+j < len(links):
                n, u, d = links[i+j]
                row.append(Paragraph(
                    f"<b>{n}</b>  <font color='#4A9EFF' size='7'>{u}</font><br/>"
                    f"<font size='6.8' color='#666666'>{d}</font>",
                    _s('lnk', fontSize=7, leading=10, spaceAfter=0)))
            else:
                row.append(Paragraph("", _s('x')))
        link_rows.append(row)

    link_t = Table(link_rows, colWidths=[8.5*cm, 8.5*cm])
    link_t.setStyle(TableStyle([
        ('TOPPADDING',(0,0),(-1,-1),4), ('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[CREAM_C, rl_colors.white]),
        ('LINEAFTER',(0,0),(0,-1),0.3, GRAY_L_C),
        ('INNERGRID',(0,0),(-1,-1),0.2, rl_colors.HexColor('#EEEEEE')),
        ('LEFTPADDING',(0,0),(-1,-1),6), ('RIGHTPADDING',(0,0),(-1,-1),6),
    ]))
    story.append(link_t)

    doc.build(story, onFirstPage=_page_frame, onLaterPages=_page_frame)
    buf.seek(0); return buf.read()

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:20px 0 10px;'>
      <div style='width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#C9A84C,#4A9EFF);
                  display:flex;align-items:center;justify-content:center;font-size:2rem;
                  margin:0 auto 12px;border:3px solid rgba(201,168,76,0.4);'>MC</div>
      <div style='font-family:Playfair Display,serif;font-size:1.1rem;font-weight:700;color:#C9A84C;'>Mackenson Cineus</div>
      <div style='font-size:0.78rem;color:#F5F0E8;opacity:0.7;margin-top:4px;'>Finance · Compliance · Fintech</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    page = st.radio("Navigation", [
        "🏠 Profil & Biographie",
        "⏱ Parcours & Compétences",
        "📊 Visualisations",
        "🌍 Carte Géographique",
        "🔗 Plateformes & Liens",
        "📄 Générateur de Documents",
        "✏️ Édition du Profil",
    ], label_visibility="collapsed")

    st.divider()
    st.markdown("<div style='font-size:0.8rem;color:#C9A84C;font-weight:600;margin-bottom:6px;'>🔑 Clé API Anthropic</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.72rem;opacity:0.6;margin-bottom:8px;'>Requise pour la génération IA</div>", unsafe_allow_html=True)
    api_key_input = st.text_input("Clé API", type="password", placeholder="sk-ant-...", label_visibility="collapsed", key="anthropic_api_key")
    if api_key_input:
        st.markdown("<div style='font-size:0.72rem;color:#2ECC71;margin-top:4px;'>✅ Clé renseignée</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:0.72rem;color:#E67E22;margin-top:4px;'>⚠️ Aucune clé</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("<div style='font-size:0.75rem;opacity:0.5;text-align:center;padding:10px;'>© 2025 Mackenson Cineus<br>Tous droits réservés</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — PROFIL & BIOGRAPHIE
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Profil & Biographie":

    P = _P()  # live data from session_state
    st.markdown(_PHASE5_CSS, unsafe_allow_html=True)

    # ── HERO BANNER ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero-banner">
      <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
        <div style="width:72px;height:72px;border-radius:50%;
                    background:linear-gradient(135deg,#C9A84C,#4A9EFF);
                    display:flex;align-items:center;justify-content:center;
                    font-size:1.8rem;border:3px solid rgba(201,168,76,0.5);
                    flex-shrink:0;">MC</div>
        <div>
          <p class="hero-name">{P['name']}</p>
          <p class="hero-title">{P['title']} · {P['location']}</p>
        </div>
      </div>
      <div style="margin-top:16px;">
        <span class="hero-badge">💳 HiPay</span>
        <span class="hero-badge">🏦 LCB-FT / AML</span>
        <span class="hero-badge">📈 MBA Trading</span>
        <span class="hero-badge">🚀 France FinTech</span>
        <span class="hero-badge">🌍 Haïti → Paris</span>
        <span class="hero-badge">🏆 Hult Prize 2018</span>
        <span class="hero-badge">🎙 Podcast INCLUTECH</span>
      </div>
      <p style="margin-top:20px;max-width:780px;opacity:0.85;line-height:1.85;font-size:0.95rem;">
        {P['summary']}
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI CARDS ────────────────────────────────────────────────────────
    cols = st.columns(5)
    kpis = [
        ("2",   "Postes conformité", "#C9A84C"),
        ("3",   "Pays traversés",    "#4A9EFF"),
        ("2",   "Diplômes sup.",      "#2ECC71"),
        ("🥇",  "Hackathon 2023",    "#E67E22"),
        ("🎙",  "Podcast INCLUTECH", "#9B59B6"),
    ]
    for col, (val, lbl, color) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-top:3px solid {color};">
              <span class="metric-value" style="color:{color};font-size:2rem;">{val}</span>
              <div class="metric-label">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_bio, col_side = st.columns([3, 1])

    with col_bio:
        st.markdown('<p class="section-header">Biographie — Parcours en 5 phases</p>', unsafe_allow_html=True)
        st.markdown("""
        <p style='opacity:0.7;margin-bottom:20px;line-height:1.7;'>
        De Port-au-Prince à Levallois-Perret — cinq chapitres d'une trajectoire construite avec
        intention, de l'entrepreneuriat social haïtien à la conformité en fintech de paiement.
        Tous les liens renvoient vers les sources officielles.
        </p>
        """, unsafe_allow_html=True)

        for period in BIO_PERIODS:
            tags_html = "".join(f'<span class="bio-tag">{t}</span>' for t in period["tags"])
            paras_html = "".join(f'<p style="margin:0 0 12px 0;">{p}</p>' for p in period["text"])
            st.markdown(f"""
            <div class="bio-period {period['phase']}">
              <div class="bio-phase-label">{period['label']}</div>
              <div class="bio-period-title">{period['title']}</div>
              <div class="bio-period-years">📍 {period['years']}</div>
              <div class="bio-period-text">{paras_html}</div>
              <div style="margin-top:12px;">{tags_html}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_side:
        st.markdown('<p class="section-header" style="font-size:1.2rem;">📥 Documents PDF</p>', unsafe_allow_html=True)
        for icon, title, desc in [
            ("📋", "CV Finance", "1 page · Format banking"),
            ("✉️", "Lettre de Motivation", "Harvard · 1 page"),
            ("📖", "Biographie", "5 phases · 2 pages"),
        ]:
            st.markdown(f"""
            <div style="background:var(--navy-mid);border:1px solid rgba(201,168,76,0.15);
                        border-radius:10px;padding:12px;margin-bottom:10px;">
              <div style="font-size:1.3rem;">{icon}</div>
              <div style="font-size:0.88rem;font-weight:600;color:var(--gold);margin:3px 0 1px;">{title}</div>
              <div style="font-size:0.75rem;opacity:0.6;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<br><p class="section-header" style="font-size:1.2rem;">🔗 Liens Rapides</p>', unsafe_allow_html=True)
        for icon, name, url in [
            ("💼", "LinkedIn",        "https://linkedin.com/in/mackenson-cineus"),
            ("💳", "HiPay",           "https://hipay.com"),
            ("🏦", "Banque Delubac",  "https://www.delubac.com"),
            ("🎙", "INCLUTECH",       "https://open.spotify.com/show/5XvFdWYwhHWY3EguIhhf69"),
            ("🚀", "France FinTech",  "https://francefintech.org"),
            ("📸", "Instagram",       "https://instagram.com/mackenson_cineus"),
        ]:
            st.markdown(f"""
            <a href="{url}" target="_blank" style="text-decoration:none;">
              <div style="display:flex;align-items:center;gap:10px;
                          background:var(--navy-mid);border:1px solid rgba(255,255,255,0.07);
                          border-radius:8px;padding:8px 12px;margin-bottom:7px;">
                <span style="font-size:1rem;">{icon}</span>
                <span style="font-size:0.82rem;color:var(--gold);">{name}</span>
                <span style="margin-left:auto;font-size:0.7rem;opacity:0.4;">↗</span>
              </div>
            </a>
            """, unsafe_allow_html=True)

elif page == "⏱ Parcours & Compétences":

    st.markdown('<p class="section-header">Parcours chronologique & Compétences</p>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 2])

    with col1:
        cats = ["Tous"] + sorted(set(t["cat"] for t in TIMELINE))
        fc = st.selectbox("Filtrer par catégorie", cats, label_visibility="collapsed")
        items = TIMELINE if fc == "Tous" else [t for t in TIMELINE if t["cat"] == fc]
        for item in items:
            st.markdown(f"""
            <div class="timeline-item">
              <div class="timeline-year">{item['icon']} {item['year']} · {item['cat']}</div>
              <div class="timeline-title">{item['title']}</div>
              <div class="timeline-desc">{item['desc']}</div>
            </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown('<p class="section-header">Compétences</p>', unsafe_allow_html=True)
        for skill, level in SKILLS.items():
            st.markdown(f"""
            <div class="skill-bar-container">
              <div class="skill-name">{skill}<span style="float:right;color:#C9A84C;font-weight:600;">{level}%</span></div>
              <div class="skill-bar"><div class="skill-fill" style="width:{level}%;"></div></div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<br><p class="section-header">Langues</p>', unsafe_allow_html=True)
        for lang, level in LANGUAGES.items():
            st.markdown(f"""
            <div class="skill-bar-container">
              <div class="skill-name">{lang}<span style="float:right;color:#4A9EFF;font-weight:600;">{level}%</span></div>
              <div class="skill-bar"><div class="skill-fill" style="width:{level}%;background:linear-gradient(90deg,#4A9EFF,#7BC8FF);"></div></div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — VISUALISATIONS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Visualisations":

    st.markdown('<p class="section-header">📊 Analyses & Visualisations</p>', unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["Radar Compétences", "Évolution de carrière", "Répartition des axes", "Langues"])

    with tab1:
        _live_skills = st.session_state.get("edit_skills", SKILLS)
        sn = list(_live_skills.keys()); sv = list(_live_skills.values())
        fig = go.Figure(go.Scatterpolar(r=sv+[sv[0]], theta=sn+[sn[0]], fill='toself',
            fillcolor='rgba(201,168,76,0.15)', line=dict(color='#C9A84C', width=2), marker=dict(color='#C9A84C', size=8)))
        fig.update_layout(polar=dict(bgcolor='rgba(26,46,66,0.5)',
            radialaxis=dict(visible=True, range=[0,100], gridcolor='rgba(255,255,255,0.1)', color='#F5F0E8'),
            angularaxis=dict(gridcolor='rgba(255,255,255,0.1)', color='#F5F0E8', tickfont=dict(size=11))),
            paper_bgcolor='rgba(0,0,0,0)', font=dict(family='DM Sans', color='#F5F0E8'),
            title=dict(text='Radar des Compétences Professionnelles', font=dict(color='#C9A84C', size=16)), height=480)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        df = pd.DataFrame([
            {"A": "2014", "N": 10, "E": "Université d'État d'Haïti"},
            {"A": "2018", "N": 35, "E": "Hult Prize — WEISS"},
            {"A": "2019", "N": 52, "E": "Université du Mans — BFA"},
            {"A": "2021", "N": 68, "E": "ESLSCA MBA Paris"},
            {"A": "2022", "N": 78, "E": "Compétition France FinTech"},
            {"A": "2023", "N": 92, "E": "Banque Delubac — LCB-FT"},
        ])
        fig2 = go.Figure(go.Scatter(x=df["A"], y=df["N"], mode='lines+markers+text',
            line=dict(color='#C9A84C', width=3),
            marker=dict(size=14, color='#C9A84C', line=dict(color='#1A2E42', width=3)),
            text=df["E"], textposition='top center', textfont=dict(size=9, color='#F5F0E8'),
            hovertemplate='<b>%{text}</b><br>Progression : %{y}%<extra></extra>'))
        fig2.update_layout(title=dict(text='Progression de Carrière', font=dict(color='#C9A84C', size=16)),
            yaxis=dict(title='Développement professionnel (%)', range=[0,110], gridcolor='rgba(255,255,255,0.07)', color='#F5F0E8'),
            xaxis=dict(color='#F5F0E8', gridcolor='rgba(255,255,255,0.07)'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(13,27,42,0.6)',
            font=dict(family='DM Sans', color='#F5F0E8'), height=430)
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            axes = {"Finance & Conformité": 45, "Entrepreneuriat Social": 22, "Innovation Fintech": 18, "Engagement Citoyen": 15}
            fig3 = go.Figure(go.Pie(labels=list(axes.keys()), values=list(axes.values()), hole=0.5,
                marker=dict(colors=['#C9A84C','#4A9EFF','#E67E22','#2ECC71'], line=dict(color='#0D1B2A', width=2)),
                textfont=dict(color='white', size=11)))
            fig3.update_layout(title=dict(text='Axes du parcours', font=dict(color='#C9A84C', size=14)),
                paper_bgcolor='rgba(0,0,0,0)', font=dict(family='DM Sans', color='#F5F0E8'),
                legend=dict(font=dict(color='#F5F0E8'), bgcolor='rgba(0,0,0,0)'), height=360)
            st.plotly_chart(fig3, use_container_width=True)
        with c2:
            countries = {"Haïti": 38, "France": 52, "International": 10}
            fig4 = go.Figure(go.Bar(x=list(countries.keys()), y=list(countries.values()),
                marker=dict(color=['#4A9EFF','#C9A84C','#2ECC71'], line=dict(color='#0D1B2A', width=1)),
                text=[f"{v}%" for v in countries.values()], textposition='outside', textfont=dict(color='#F5F0E8')))
            fig4.update_layout(title=dict(text='Répartition géographique', font=dict(color='#C9A84C', size=14)),
                yaxis=dict(range=[0,70], gridcolor='rgba(255,255,255,0.07)', color='#F5F0E8'),
                xaxis=dict(color='#F5F0E8'), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(13,27,42,0.6)',
                font=dict(family='DM Sans', color='#F5F0E8'), height=360)
            st.plotly_chart(fig4, use_container_width=True)

    with tab4:
        fig5 = go.Figure()
        clrs = {'Créole haïtien': '#2ECC71', 'Français': '#C9A84C', 'Anglais': '#4A9EFF'}
        for lang, lvl in LANGUAGES.items():
            fig5.add_trace(go.Bar(x=[lvl], y=[lang], orientation='h', marker_color=clrs.get(lang,'#C9A84C'),
                text=[f"{lvl}%"], textposition='inside', textfont=dict(color='white', size=14),
                hovertemplate=f'{lang}: {lvl}%<extra></extra>'))
        fig5.update_layout(title=dict(text='Maîtrise des Langues', font=dict(color='#C9A84C', size=16)),
            xaxis=dict(range=[0,110], gridcolor='rgba(255,255,255,0.07)', color='#F5F0E8'),
            yaxis=dict(color='#F5F0E8'), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(13,27,42,0.6)',
            font=dict(family='DM Sans', color='#F5F0E8'), showlegend=False, height=280, barmode='overlay')
        st.plotly_chart(fig5, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — CARTE GÉOGRAPHIQUE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🌍 Carte Géographique":

    st.markdown('<p class="section-header">🌍 Parcours Géographique International</p>', unsafe_allow_html=True)

    fig_map = go.Figure()
    coords = list(zip(GEO_DATA['lat'], GEO_DATA['lon']))
    for i in range(len(coords) - 1):
        fig_map.add_trace(go.Scattergeo(lat=[coords[i][0], coords[i+1][0]], lon=[coords[i][1], coords[i+1][1]],
            mode='lines', line=dict(width=2, color='rgba(201,168,76,0.5)'), showlegend=False))
    fig_map.add_trace(go.Scattergeo(lat=GEO_DATA['lat'], lon=GEO_DATA['lon'], mode='markers+text',
        marker=dict(size=GEO_DATA['size'], color=['#4A9EFF','#C9A84C','#C9A84C'], line=dict(color='white', width=2), opacity=0.9),
        text=GEO_DATA['locations'], textposition=['bottom right','bottom left','top right'],
        textfont=dict(size=12, color='white'),
        customdata=list(zip(GEO_DATA['events'], GEO_DATA['years'])),
        hovertemplate='<b>%{text}</b><br>%{customdata[0]}<br>%{customdata[1]}<extra></extra>'))
    fig_map.update_geos(projection_type="natural earth",
        showcoastlines=True, coastlinecolor='rgba(255,255,255,0.2)',
        showland=True, landcolor='rgba(26,46,66,0.8)',
        showocean=True, oceancolor='rgba(13,27,42,0.9)',
        showcountries=True, countrycolor='rgba(255,255,255,0.1)',
        center=dict(lat=30, lon=-20), projection_scale=2.5)
    fig_map.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(family='DM Sans', color='#F5F0E8'),
        height=500, margin=dict(l=0,r=0,t=20,b=0), geo=dict(bgcolor='rgba(0,0,0,0)'))
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown('<br>', unsafe_allow_html=True)
    cols = st.columns(3)
    for col, (loc, event, year) in zip(cols, zip(GEO_DATA['locations'], GEO_DATA['events'], GEO_DATA['years'])):
        with col:
            st.markdown(f"""<div class="timeline-item" style="border-left-color:#4A9EFF;">
              <div class="timeline-year">📍 {year}</div>
              <div class="timeline-title">{loc}</div>
              <div class="timeline-desc">{event}</div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — PLATEFORMES & LIENS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔗 Plateformes & Liens":

    st.markdown('<p class="section-header">🔗 Plateformes & Présences en ligne</p>', unsafe_allow_html=True)
    st.markdown("<p style='opacity:0.75;margin-bottom:28px;line-height:1.7;max-width:700px;'>Retrouvez Mackenson Cineus sur les plateformes professionnelles, compétitions et institutions qui jalonnent son parcours — de l'entrepreneuriat haïtien à la finance parisienne.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    for i, p in enumerate(PLATFORMS):
        with (col1 if i % 2 == 0 else col2):
            st.markdown(f"""
            <div class="platform-card">
              <div class="platform-icon">{p['icon']}</div>
              <div style="flex:1;">
                <div class="platform-name">{p['name']}</div>
                <div class="platform-desc">{p['desc']}</div>
                <a href="{p['url']}" target="_blank" class="platform-link">{p['label']}</a>
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-header">📡 Régulateurs & Ressources sectorielles</p>', unsafe_allow_html=True)
    st.markdown("<p style='opacity:0.7;margin-bottom:20px;'>Les instances de référence dans l'univers professionnel de Mackenson — conformité, marchés et fintech.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    for i, (icon, name, desc, url) in enumerate(REGULATORS):
        with (col1 if i % 2 == 0 else col2):
            st.markdown(f"""
            <div class="platform-card">
              <div class="platform-icon">{icon}</div>
              <div style="flex:1;">
                <div class="platform-name">{name}</div>
                <div class="platform-desc">{desc}</div>
                <a href="{url}" target="_blank" class="platform-link">Consulter →</a>
              </div>
            </div>""", unsafe_allow_html=True)


elif page == "📄 Générateur de Documents":

    st.markdown('<p class="section-header">📄 Téléchargement des Documents PDF</p>', unsafe_allow_html=True)

    # ── TAB SELECTOR ──
    tab_cv, tab_lm, tab_bio = st.tabs(["📋 CV — 1 page Finance", "✉️ Lettre de Motivation", "📖 Biographie Complète"])

    # ────────────────────────────────────────────────────────────────────────
    # TAB 1 — CV
    # ────────────────────────────────────────────────────────────────────────
    with tab_cv:
        st.markdown("""
        <div style='background:var(--navy-mid);border:1px solid rgba(201,168,76,0.2);border-radius:12px;
                    padding:20px 24px;margin-bottom:20px;'>
          <div style='font-size:1rem;font-weight:600;color:#C9A84C;margin-bottom:6px;'>CV Professionnel — Format Finance</div>
          <div style='font-size:0.85rem;opacity:0.75;line-height:1.6;'>
            CV <b>une page</b>, format standard finance/banking — structure épurée, données réelles vérifiées.
            Personnalisez le poste cible et téléchargez directement en <b>PDF haute qualité</b>.
          </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            cv_poste = st.text_input("🎯 Poste visé (optionnel)", placeholder="ex: Compliance Officer, Risk Analyst…", key="cv_poste")
        with c2:
            cv_entreprise = st.text_input("🏢 Entreprise cible (optionnel)", placeholder="ex: BNP Paribas, KPMG…", key="cv_entreprise")

        c3, c4 = st.columns(2)
        with c3:
            cv_secteur = st.selectbox("🏦 Secteur", ["Banque", "Fintech", "Asset Management", "Assurance", "Audit / Conseil", "Marché des capitaux"], key="cv_sect")
        with c4:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            generate_cv = st.button("⬇️ Générer & Télécharger le CV (PDF)", use_container_width=True, key="btn_cv")

        if generate_cv:
            with st.spinner("Génération du CV PDF…"):
                pdf_bytes = generate_cv_pdf(
                    poste=cv_poste, entreprise=cv_entreprise,
                    secteur=cv_secteur)

            st.success("✅ CV généré avec succès !")
            st.download_button(
                label="📥 Télécharger le CV — Cineus_Mackenson_CV.pdf",
                data=pdf_bytes,
                file_name="Cineus_Mackenson_CV.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="dl_cv",
            )
            st.markdown("""
            <div style='background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.2);
                        border-radius:8px;padding:12px 16px;margin-top:12px;font-size:0.82rem;opacity:0.8;'>
            💡 <b>Format :</b> A4 · Une page · Police Helvetica · Style Finance · Bandeau Navy/Or
            </div>
            """, unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────────────────
    # TAB 2 — LETTRE DE MOTIVATION
    # ────────────────────────────────────────────────────────────────────────
    with tab_lm:
        st.markdown("""
        <div style='background:var(--navy-mid);border:1px solid rgba(74,158,255,0.2);border-radius:12px;
                    padding:20px 24px;margin-bottom:20px;'>
          <div style='font-size:1rem;font-weight:600;color:#4A9EFF;margin-bottom:6px;'>Lettre de Motivation PDF</div>
          <div style='font-size:0.85rem;opacity:0.75;line-height:1.6;'>
            Lettre structurée en 4 paragraphes Harvard. Optionnellement enrichie par Claude AI
            pour un contenu 100% personnalisé selon le poste et l'entreprise visés.
          </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            lm_poste = st.text_input("🎯 Poste visé", placeholder="ex: Analyste Risques, Compliance Officer…", key="lm_poste")
            lm_entreprise = st.text_input("🏢 Entreprise", placeholder="ex: BNP Paribas, Société Générale…", key="lm_ent")
        with c2:
            lm_secteur = st.selectbox("🏦 Secteur", ["Banque", "Fintech", "Asset Management", "Assurance", "Audit / Conseil"], key="lm_sect")
            lm_style = st.selectbox("✍️ Ton", ["Professionnel & formel", "Dynamique & moderne", "Harvard / McKinsey"], key="lm_style")

        lm_contexte = st.text_area("💬 Instructions spécifiques (optionnel)",
            placeholder="Ex: insister sur la victoire France FinTech, mentionner le podcast INCLUTECH…",
            height=70, key="lm_ctx")

        use_ai = st.toggle("🤖 Personnaliser le contenu avec Claude AI", value=False, key="lm_ai")
        if use_ai and not st.session_state.get("anthropic_api_key", "").strip():
            st.warning("⚠️ Renseignez votre clé API Anthropic dans la barre latérale pour activer la génération IA.")

        c_gen, c_dl = st.columns(2)
        with c_gen:
            gen_lm = st.button("✨ Générer la Lettre (PDF)", use_container_width=True, key="btn_lm")

        ai_content = ""
        if gen_lm:
            if not lm_poste:
                st.error("⚠️ Veuillez indiquer le poste visé.")
            else:
                if use_ai and st.session_state.get("anthropic_api_key", "").strip():
                    with st.spinner("🤖 Rédaction par Claude AI…"):
                        system = "Tu es expert en lettres de motivation pour la finance. Style percutant, Harvard. Réponds uniquement avec le corps de la lettre (sans 'Madame/Monsieur' ni formule de politesse finale), en 4 paragraphes séparés par une ligne vide."
                        prompt = f"""
Rédige le corps d'une lettre de motivation pour Mackenson Cineus, profil :
- Analyste LCB-FT Banque Delubac & Cie (Paris)
- MBA Trading & Marchés Financiers — ESLSCA Paris
- Licence BFA — Université du Mans
- 1er Prix Hackathon Fintech Générations 2023 (France FinTech / SG) — Projet Victoria
- Podcast INCLUTECH (inclusion financière)
- Board Member Erasmus Expertise
- Hult Prize 2018 (WEISS), ANGAJMAN

Poste : {lm_poste}
Entreprise : {lm_entreprise or 'non précisée'}
Secteur : {lm_secteur}
Ton : {lm_style}
Instructions : {lm_contexte or 'standard'}

4 paragraphes, français, séparés par ligne vide. Pas de formule d'ouverture ni de clôture."""
                        ai_content = call_claude(prompt, system)

                with st.spinner("Génération PDF…"):
                    pdf_bytes_lm = generate_lettre_pdf(
                        poste=lm_poste, entreprise=lm_entreprise,
                        secteur=lm_secteur, style_lm=lm_style,
                        contexte=lm_contexte, ai_text=ai_content)

                st.success("✅ Lettre générée !")
                st.download_button(
                    label="📥 Télécharger la Lettre — Cineus_Mackenson_LM.pdf",
                    data=pdf_bytes_lm,
                    file_name=f"Cineus_Mackenson_LM_{lm_poste.replace(' ','_') if lm_poste else 'Finance'}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="dl_lm",
                )

    # ────────────────────────────────────────────────────────────────────────
    # TAB 3 — BIOGRAPHIE
    # ────────────────────────────────────────────────────────────────────────
    with tab_bio:
        st.markdown("""
        <div style='background:var(--navy-mid);border:1px solid rgba(46,204,113,0.2);border-radius:12px;
                    padding:20px 24px;margin-bottom:20px;'>
          <div style='font-size:1rem;font-weight:600;color:#2ECC71;margin-bottom:6px;'>Biographie Professionnelle Complète</div>
          <div style='font-size:0.85rem;opacity:0.75;line-height:1.6;'>
            Biographie narrative en <b>4 phases chronologiques</b> enrichie par des recherches sur LinkedIn,
            France FinTech, Spotify, Apple Podcasts et Erasmus Expertise.
            Données réelles vérifiées.
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Info cards
        c1, c2, c3 = st.columns(3)
        infos = [
            ("🥇", "Hackathon France FinTech 2023", "1er Prix · Projet Victoria"),
            ("🎙", "Podcast INCLUTECH", "Spotify & Apple Podcasts"),
            ("🌍", "Board Member", "Erasmus Expertise"),
        ]
        for col, (icon, title, sub) in zip([c1,c2,c3], infos):
            with col:
                st.markdown(f"""
                <div style='background:var(--navy-mid);border:1px solid rgba(46,204,113,0.15);
                            border-radius:10px;padding:14px;text-align:center;'>
                  <div style='font-size:1.6rem;'>{icon}</div>
                  <div style='font-size:0.85rem;font-weight:600;color:#2ECC71;margin:4px 0 2px;'>{title}</div>
                  <div style='font-size:0.78rem;opacity:0.65;'>{sub}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        gen_bio = st.button("⬇️ Générer & Télécharger la Biographie (PDF)", use_container_width=True, key="btn_bio")

        if gen_bio:
            with st.spinner("Génération de la biographie PDF…"):
                pdf_bytes_bio = generate_bio_pdf()

            st.success("✅ Biographie générée !")
            st.download_button(
                label="📥 Télécharger — Cineus_Mackenson_Biographie.pdf",
                data=pdf_bytes_bio,
                file_name="Cineus_Mackenson_Biographie.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="dl_bio",
            )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 7 — ÉDITION DU PROFIL
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "✏️ Édition du Profil":

    st.markdown('<p class="section-header">✏️ Édition du Profil</p>', unsafe_allow_html=True)
    st.markdown("""
    <p style='opacity:0.75;margin-bottom:24px;line-height:1.7;max-width:700px;'>
    Mettez à jour les informations du profil en temps réel. Les modifications sont immédiatement
    répercutées sur toutes les pages de la plateforme et dans les PDF générés.
    </p>
    """, unsafe_allow_html=True)

    # ── ONGLETS D'ÉDITION ────────────────────────────────────────────────
    t1, t2, t3, t4, t5 = st.tabs([
        "👤 Infos Générales",
        "💼 Expériences",
        "🎓 Formation",
        "⚡ Compétences",
        "🏅 Distinctions",
    ])

    # ── TAB 1 — INFOS GÉNÉRALES ──────────────────────────────────────────
    with t1:
        st.markdown("#### Informations personnelles & professionnelles")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Nom complet", key="edit_name")
            st.text_input("Localisation", key="edit_location")
        with c2:
            st.text_input("Titre professionnel", key="edit_title")
            st.text_input("Email", key="edit_email")

        st.text_input("LinkedIn (sans https://)", key="edit_linkedin")
        st.text_area("Résumé / Accroche professionnelle",
                     key="edit_summary", height=120)

        st.success("✅ Les modifications sont appliquées en temps réel sur toute la plateforme.")

    # ── TAB 2 — EXPÉRIENCES ───────────────────────────────────────────────
    with t2:
        st.markdown("#### Expériences professionnelles")
        st.info("💡 Modifiez directement les champs ci-dessous. Les PDFs utiliseront ces données à la génération.")

        exps = st.session_state.edit_exp
        for i, exp in enumerate(exps):
            with st.expander(f"**{exp['role']}** — {exp['org']} ({exp['period']})", expanded=(i == 0)):
                c1, c2 = st.columns([2, 1])
                with c1:
                    new_role = st.text_input("Poste / Rôle", value=exp["role"], key=f"exp_role_{i}")
                    new_org  = st.text_input("Organisation", value=exp["org"],  key=f"exp_org_{i}")
                with c2:
                    new_period = st.text_input("Période", value=exp["period"], key=f"exp_period_{i}")
                    new_url    = st.text_input("URL officielle", value=exp["url"], key=f"exp_url_{i}")

                st.markdown("**Missions / Réalisations** (une par ligne)")
                bullets_text = "\n".join(exp["bullets"])
                new_bullets = st.text_area("", value=bullets_text, height=100, key=f"exp_bullets_{i}",
                                            label_visibility="collapsed")

                if st.button(f"💾 Sauvegarder", key=f"save_exp_{i}"):
                    st.session_state.edit_exp[i] = {
                        "role":    new_role,
                        "org":     new_org,
                        "period":  new_period,
                        "url":     new_url,
                        "bullets": [b.strip() for b in new_bullets.split("\n") if b.strip()],
                    }
                    st.success(f"✅ Expérience « {new_role} » mise à jour !")
                    st.rerun()

        st.markdown("---")
        st.markdown("#### ➕ Ajouter une nouvelle expérience")
        with st.expander("Nouvelle expérience", expanded=False):
            nc1, nc2 = st.columns([2,1])
            with nc1:
                new_exp_role   = st.text_input("Poste", key="new_exp_role", placeholder="ex: Risk Manager")
                new_exp_org    = st.text_input("Organisation", key="new_exp_org", placeholder="ex: BNP Paribas · Paris")
            with nc2:
                new_exp_period = st.text_input("Période", key="new_exp_period", placeholder="2025 – Présent")
                new_exp_url    = st.text_input("URL", key="new_exp_url", placeholder="https://bnpparibas.com")
            new_exp_bullets = st.text_area("Missions (une par ligne)", key="new_exp_bullets", height=80)
            if st.button("➕ Ajouter cette expérience", key="add_exp"):
                if new_exp_role and new_exp_org:
                    st.session_state.edit_exp.insert(0, {
                        "role":    new_exp_role,
                        "org":     new_exp_org,
                        "period":  new_exp_period,
                        "url":     new_exp_url,
                        "bullets": [b.strip() for b in new_exp_bullets.split("\n") if b.strip()],
                    })
                    st.success(f"✅ « {new_exp_role} » ajouté en tête de liste !")
                    st.rerun()
                else:
                    st.error("Poste et organisation requis.")

    # ── TAB 3 — FORMATION ────────────────────────────────────────────────
    with t3:
        st.markdown("#### Formation académique")
        edu = st.session_state.edit_edu
        for i, e in enumerate(edu):
            with st.expander(f"**{e['deg']}** — {e['school']} ({e['yr']})", expanded=(i == 0)):
                c1, c2 = st.columns([2, 1])
                with c1:
                    nd  = st.text_input("Diplôme", value=e["deg"],    key=f"edu_deg_{i}")
                    ns  = st.text_input("École",   value=e["school"], key=f"edu_sch_{i}")
                with c2:
                    ny  = st.text_input("Années",  value=e["yr"],  key=f"edu_yr_{i}")
                    nu  = st.text_input("URL",     value=e["url"], key=f"edu_url_{i}")
                ndet = st.text_input("Détails (compétences, spécialisation)", value=e["det"], key=f"edu_det_{i}")
                if st.button("💾 Sauvegarder", key=f"save_edu_{i}"):
                    st.session_state.edit_edu[i] = {"deg":nd,"school":ns,"yr":ny,"url":nu,"det":ndet}
                    st.success(f"✅ Formation « {nd} » mise à jour !")
                    st.rerun()

        st.markdown("---")
        st.markdown("#### ➕ Ajouter une formation")
        with st.expander("Nouvelle formation", expanded=False):
            nc1, nc2 = st.columns([2,1])
            with nc1:
                nf_deg    = st.text_input("Diplôme", key="nf_deg",    placeholder="ex: Master Finance")
                nf_school = st.text_input("École",   key="nf_school", placeholder="ex: Paris Dauphine")
            with nc2:
                nf_yr  = st.text_input("Années", key="nf_yr",  placeholder="2025–2027")
                nf_url = st.text_input("URL",    key="nf_url",  placeholder="https://dauphine.psl.eu")
            nf_det = st.text_input("Détails", key="nf_det", placeholder="Matières, spécialisation...")
            if st.button("➕ Ajouter", key="add_edu"):
                if nf_deg and nf_school:
                    st.session_state.edit_edu.insert(0,
                        {"deg":nf_deg,"school":nf_school,"yr":nf_yr,"url":nf_url,"det":nf_det})
                    st.success(f"✅ « {nf_deg} » ajouté !")
                    st.rerun()

    # ── TAB 4 — COMPÉTENCES ───────────────────────────────────────────────
    with t4:
        st.markdown("#### Compétences techniques — niveaux (0–100)")
        st.info("💡 Modifiez les valeurs et cliquez Sauvegarder pour mettre à jour les graphiques et le CV.")

        updated_skills = {}
        skills_items = list(st.session_state.edit_skills.items())
        for skill, level in skills_items:
            c1, c2 = st.columns([3, 1])
            with c1:
                new_skill_name = st.text_input("", value=skill, key=f"sk_name_{skill}",
                                                label_visibility="collapsed")
            with c2:
                new_level = st.number_input("", min_value=0, max_value=100,
                                             value=level, key=f"sk_lvl_{skill}",
                                             label_visibility="collapsed")
            updated_skills[new_skill_name] = new_level

        c1, c2 = st.columns(2)
        with c1:
            new_sk_name = st.text_input("Nouvelle compétence", key="new_sk_name",
                                         placeholder="ex: Déclarations Tracfin")
        with c2:
            new_sk_lvl = st.number_input("Niveau (0-100)", min_value=0, max_value=100,
                                          value=80, key="new_sk_lvl")

        if st.button("💾 Sauvegarder toutes les compétences", use_container_width=True):
            if new_sk_name.strip():
                updated_skills[new_sk_name.strip()] = new_sk_lvl
            st.session_state.edit_skills = updated_skills
            st.success("✅ Compétences mises à jour — graphiques et CV mis à jour !")
            st.rerun()

    # ── TAB 5 — DISTINCTIONS ─────────────────────────────────────────────
    with t5:
        st.markdown("#### Distinctions & Engagements")
        dists = list(st.session_state.edit_distinctions)
        for i, (icon, title, desc) in enumerate(dists):
            c1, c2, c3 = st.columns([0.5, 2, 4])
            with c1:
                ni = st.text_input("", value=icon,  key=f"di_i_{i}", label_visibility="collapsed")
            with c2:
                nt = st.text_input("", value=title, key=f"di_t_{i}", label_visibility="collapsed")
            with c3:
                nd = st.text_input("", value=desc,  key=f"di_d_{i}", label_visibility="collapsed")

        if st.button("💾 Sauvegarder les distinctions", use_container_width=True):
            new_dists = []
            for i in range(len(dists)):
                new_dists.append((
                    st.session_state.get(f"di_i_{i}", dists[i][0]),
                    st.session_state.get(f"di_t_{i}", dists[i][1]),
                    st.session_state.get(f"di_d_{i}", dists[i][2]),
                ))
            st.session_state.edit_distinctions = new_dists
            st.success("✅ Distinctions mises à jour !")
            st.rerun()

        st.markdown("---")
        st.markdown("#### ➕ Ajouter une distinction")
        nc1, nc2, nc3 = st.columns([0.5, 2, 4])
        with nc1: new_di = st.text_input("Icône", key="new_di_i", value="🏅")
        with nc2: new_dt = st.text_input("Titre", key="new_di_t", placeholder="Prix / Engagement")
        with nc3: new_dd = st.text_input("Description", key="new_di_d", placeholder="Détails...")
        if st.button("➕ Ajouter", key="add_dist"):
            if new_dt.strip():
                st.session_state.edit_distinctions.append((new_di, new_dt, new_dd))
                st.success(f"✅ « {new_dt} » ajouté !")
                st.rerun()
