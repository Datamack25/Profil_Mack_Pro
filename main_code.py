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
        "edit_title":    "Analyste LCB-FT | Compliance Officer",
        "edit_location": "Île-de-France, France",
        "edit_email":    "mackenson.cineus@email.com",
        "edit_phone":    "+33 6 XX XX XX XX",
        "edit_linkedin": "linkedin.com/in/mackenson-cineus",
        "edit_summary": (
            "Analyste LCB-FT en alternance avec expérience en banque (clientèle corporate, "
            "CIB, asset management, banque privée, PSP) et en fintech de paiement agréée ACPR. "
            "MBA 2 Finance de Marché (ESLSCA Paris, en cours). Titulaire d'une Licence Banque, "
            "Finance & Assurance (Université du Mans). Lauréat 1er Prix Hackathon Fintech "
            "Générations 2023 — France FinTech / Société Générale. Trilingue."
        ),
        "edit_memoir_title": (
            "Impact of ESG and Non-ESG Regulation on Portfolio Performance in Terms "
            "of Risk and Return"
        ),
        "edit_memoir_desc": (
            "Mémoire de 80 pages rédigé en anglais dans le cadre du MBA 2 Finance de Marché "
            "(ESLSCA Business School Paris). Étude comparative de l'impact de la réglementation "
            "ESG et non-ESG sur la performance des portefeuilles en termes de risque et rendement."
        ),
        "edit_exp": [
            {
                "role":    "Analyste LCB-FT",
                "org":     "Banque DELUBAC & CIE · Paris, France",
                "org_type": "Banque",
                "period":  "Septembre 2025 – Aujourd'hui",
                "url":     "https://www.delubac.com",
                "bullets": [
                    "Traitement des alertes de niveau 1 LCB-FT sur la clientèle (corporate, CIB, asset management, banque privée, PSP) — analyse de la situation financière, économique et juridique",
                    "Traitement des Examens Renforcés (ER), Profils à Détecter Supplémentaires (PDS) et rédaction d'avis sur opérations",
                    "Réalisation de l'analyse KYC, identification des bénéficiaires effectifs, contrôle de la cohérence économique des transactions et rédaction de déclarations de soupçon",
                    "Analyse du bilan et du compte de résultat pour évaluer la santé financière des partenaires",
                    "Traitement des demandes de droit de communication et des réquisitions judiciaires",
                    "Réalisation des examens renforcés et préparation des déclarations de soupçon (DS)",
                ],
            },
            {
                "role":    "Chargé de conformité",
                "org":     "HIPAY SAS · Nantes-Paris, France",
                "org_type": "Fintech",
                "period":  "Septembre 2024 – Septembre 2025",
                "url":     "https://hipay.com",
                "bullets": [
                    "Analyse des risques pays (GAFI) et des typologies de fraude et de blanchiment (LCB-FT) sur des pays sensibles et complexes, dont pays sous sanctions internationales",
                    "Réalisation des analyses KYC : identification des bénéficiaires effectifs, PPE/PE et SOE, contrôles de cohérence économique — attention particulière aux Personnes Politiquement Exposées (PPE)",
                    "Traitement des alertes et réponses aux réquisitions : Tracfin, autorités judiciaires, analyses complémentaires (fraudes, sanctions, demandes judiciaires)",
                    "Due Diligence des partenaires institutionnels et des établissements financiers systémiques et établissements de monnaie électronique (RFI en priorité)",
                    "Mise à jour de la documentation de risques de non-conformité (LCB-FT) et participation aux audits internes",
                ],
            },
            {
                "role":    "Lauréat 1er Prix — Hackathon Fintech Générations 2023",
                "org":     "France FinTech · Société Générale · Treezor · Paris&Co",
                "org_type": "Compétition",
                "period":  "Octobre 2023",
                "url":     "https://francefintech.org",
                "bullets": [
                    "Projet Victoria : solution de financement des rénovations DPE par financement privé — pitch à Fintech R:Evolution (1 500 participants : investisseurs, régulateurs, entrepreneurs)",
                ],
            },
            {
                "role":    "Board Member",
                "org":     "Erasmus Expertise · International",
                "org_type": "ONG",
                "period":  "2021 – Présent",
                "url":     "https://erasmus-expertise.eu",
                "bullets": [
                    "Gouvernance ONG internationale : développement durable, éducation, inclusion sociale — accompagnement linguistique et administratif de 7 étudiants internationaux",
                ],
            },
            {
                "role":    "Directeur Financier & Directeur des Opérations",
                "org":     "Hult Prize Haïti · Haïti / République Dominicaine",
                "org_type": "Association",
                "period":  "2018 – 2021",
                "url":     "https://www.hultprize.org",
                "bullets": [
                    "Directeur financier : recherche de financements (Ministère des Finances, BNC), élaboration du budget de l'association, supervision des responsables régionaux",
                    "Représentant Haïti au Hult Prize 2018 — projet WEISS (transformation des déchets en biogaz & fertilisant organique) ; volontariat international en République Dominicaine",
                ],
            },
            {
                "role":    "Directeur Exécutif & Fondateur",
                "org":     "ANGAJMAN · Haïti",
                "org_type": "Association",
                "period":  "2018 – 2021",
                "url":     "https://www.hultprize.org",
                "bullets": [
                    "Création, planification et exécution de projets citoyens dans les 10 départements d'Haïti : campagne COVID-19 (50 jeunes, 10 vidéos virales), projets environnementaux et entrepreneuriaux",
                ],
            },
            {
                "role":    "Président — Groupe Économie & Finance",
                "org":     "ACTIVEH · Haïti",
                "org_type": "Association",
                "period":  "2016 – 2018",
                "url":     "https://www.hultprize.org",
                "bullets": [
                    "Leadership d'une équipe de 15+ bénévoles — organisation de conférences (économie, entrepreneuriat), projet « Goud la se Pa m » (sensibilisation à la souveraineté monétaire, 50+ participants, musée BRH, 3 émissions radio)",
                ],
            },
        ],
        "edit_edu": [
            {
                "deg":    "MBA 2 Finance de marché",
                "school": "ESLSCA Business School Paris · Paris, France",
                "yr":     "Septembre 2024 – Septembre 2026",
                "url":    "https://www.eslsca.fr",
                "det":    "Audit, Comptabilité approfondie, Gestion des risques, Gestion de Portefeuille, Pricing d'option, Produits dérivés, Analyse financière, Conformité, Évaluation d'actifs, Machine learning, VBA & Python",
                "mention": "",
            },
            {
                "deg":    "Licence en Banque, Finance et Assurance",
                "school": "Université du Mans · Le Mans, France",
                "yr":     "Septembre 2022 – Juin 2024",
                "url":    "https://www.univ-lemans.fr",
                "det":    "Analyse et gestion de portefeuille, droit commercial, droit fiscal, VBA & analyse stochastique, Comptabilité de gestion",
                "mention": "",
            },
            {
                "deg":    "Licence en Sciences Économiques & Gestion des Affaires",
                "school": "INAGHEI · Université d'État d'Haïti",
                "yr":     "2014 – 2018",
                "url":    "https://www.ueh.edu.ht",
                "det":    "Gestion des Affaires, Économie, Droit, Politiques publiques — double cursus INAGHEI & FDSE",
                "mention": "",
            },
        ],
        "edit_skills": {
            "LCB-FT / AML / AMLD5-6":       95,
            "KYC / KYB / Due Diligence":     92,
            "Analyse de risques pays (GAFI)": 90,
            "Déclarations de soupçon (DS)":  88,
            "Réglementation ACPR / GAFI":    90,
            "Marchés Financiers & Trading":  82,
            "Analyse financière (bilan, CR)": 80,
            "Excel / VBA / Python":           75,
            "Bloomberg / Looker / Jura":      68,
        },
        "edit_certifs": [
            "AMF (en préparation)",
            "CFA Level 1 (candidat en cours)",
            "CAMS – Anti-Money Laundering (en cours)",
        ],
        "edit_tech": "Excel avancé – VBA – Python – Bloomberg – Pack Microsoft Office – Looker – Jura",
        "edit_interests": "Sécurité financière – Création de modèles financiers – Programmation – Fintech & RegTech – Trading NASDAQ – Veille économique",
        "edit_distinctions": [
            ("🥇", "Hackathon Fintech Générations 2023",
             "Lauréat du 1er Prix — France FinTech & Société Générale — Projet Victoria (DPE)"),
            ("🏆", "Hult Prize 2018",
             "Représentant Haïti — Projet WEISS (biogaz & fertilisant organique)"),
            ("🏅", "Hackathon Unleash (ODD)",
             "Lauréat — Objectifs de Développement Durable — équipe internationale"),
            ("🎙", "Podcast INCLUTECH",
             "Créateur & animateur — Finance & Inclusion Financière — Spotify & Apple Podcasts"),
            ("🌍", "Board Member — Erasmus Expertise",
             "Conseil d'administration ONG internationale — développement durable & éducation"),
        ],
        "edit_personality": (
            "Analyste rigoureux à l'esprit entrepreneurial, qui transforme les contraintes "
            "réglementaires en leviers de valeur et les défis en opportunités — de Port-au-Prince "
            "aux salles de marché parisiennes."
        ),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

def _P():
    return {k: st.session_state.get(k, v)
            for k, v in {
                "name": "Mackenson CINÉUS",
                "title": "Analyste LCB-FT | Compliance Officer",
                "location": "Île-de-France, France",
                "email": "mackenson.cineus@email.com",
                "phone": "+33 6 XX XX XX XX",
                "linkedin": "linkedin.com/in/mackenson-cineus",
                "summary": "",
            }.items()}

PROFILE = _P()

# ── TIMELINE (updated) ────────────────────────────────────────────────────────
TIMELINE = [
    {"year":"2016–2018","title":"ACTIVEH — Président Groupe Économie & Finance",
     "desc":"Leadership 15+ bénévoles · projet Goud la se Pa m · conférences économie","url":"","icon":"🤝","cat":"Social"},
    {"year":"2018–2021","title":"Hult Prize Haïti — Directeur Financier & Opérations",
     "desc":"Financement, budget, supervision régionale · volontariat RD · Hult Prize 2018 (WEISS)","url":"https://www.hultprize.org","icon":"🏆","cat":"Entrepreneuriat"},
    {"year":"2018–2021","title":"ANGAJMAN — Directeur Exécutif & Fondateur",
     "desc":"Projets citoyens 10 dép. Haïti · campagne COVID-19 · 50 jeunes","url":"","icon":"🤝","cat":"Social"},
    {"year":"2018–2021","title":"PHJEA — Section Finance",
     "desc":"Parlement Haïtien Jeunesse Eau & Assainissement · Parlement Mondial de l'Eau","url":"","icon":"🌊","cat":"Social"},
    {"year":"2021","title":"Unleash Hackathon ODD — Lauréat",
     "desc":"Hackathon Objectifs Développement Durable · équipe internationale · rôle mentor","url":"","icon":"🌍","cat":"Entrepreneuriat"},
    {"year":"2019–2021","title":"Université du Mans — Licence BFA",
     "desc":"Banque, Finance & Assurance — VBA, analyse stochastique, droit fiscal","url":"https://www.univ-lemans.fr","icon":"🏫","cat":"Éducation"},
    {"year":"2021–Présent","title":"Erasmus Expertise — Board Member",
     "desc":"ONG internationale · tuteur 7 étudiants · groupe conversation français · CA 2023","url":"https://erasmus-expertise.eu","icon":"🌍","cat":"Réseau"},
    {"year":"2021–Présent","title":"Podcast INCLUTECH",
     "desc":"Finance & Inclusion Financière · bi-mensuel · Spotify & Apple Podcasts","url":"https://open.spotify.com/show/5XvFdWYwhHWY3EguIhhf69","icon":"🎙","cat":"Réseau"},
    {"year":"2024–Présent","title":"MBA 2 Finance de marché — ESLSCA Paris",
     "desc":"Gestion de portefeuille · Produits dérivés · Conformité · VBA & Python · Machine learning","url":"https://www.eslsca.fr","icon":"📈","cat":"Éducation"},
    {"year":"Oct. 2023","title":"🥇 Hackathon Fintech Générations — 1er Prix",
     "desc":"Projet Victoria (DPE) · France FinTech / Société Générale / Treezor · Fintech R:Evolution","url":"https://francefintech.org","icon":"🚀","cat":"Entrepreneuriat"},
    {"year":"2024–2025","title":"Chargé de conformité — HIPAY SAS",
     "desc":"Fintech paiement · LCB-FT · KYC/PPE · pays sensibles · Tracfin · Due Diligence","url":"https://hipay.com","icon":"💳","cat":"Professionnel"},
    {"year":"2025–Présent","title":"Analyste LCB-FT — Banque DELUBAC & CIE",
     "desc":"Alertes N1 · ER/PDS · KYC corporate/CIB/PSP · DS · avis sur opérations","url":"https://www.delubac.com","icon":"🏦","cat":"Professionnel"},
]

SKILLS = {k: v for k, v in st.session_state.get("edit_skills", {
    "LCB-FT / AML":95,"KYC/KYB":92,"Risques pays GAFI":90,
    "DS / Tracfin":88,"ACPR/GAFI":90,"Marchés Financiers":82,
    "Analyse financière":80,"Excel/VBA/Python":75,
}).items()}

LANGUAGES = {"Créole haïtien": 100, "Français": 95, "Anglais": 85}

GEO_DATA = {
    "locations": ["Port-au-Prince, Haïti", "Le Mans, France", "Paris / Levallois-Perret"],
    "lat": [18.5432, 47.9960, 48.8924],
    "lon": [-72.3388, 0.1966, 2.2873],
    "events": ["INAGHEI · ACTIVEH · Hult Prize · ANGAJMAN · PHJEA · Unleash",
               "Licence BFA · Université du Mans",
               "MBA ESLSCA · Delubac LCB-FT · HiPay Compliance · France FinTech"],
    "years": ["2014–2021", "2019–2021", "2021–Présent"],
    "size": [18, 14, 34],
}

BIO_PERIODS = [
    {
        "phase": "phase1",
        "label": "Phase 1 · 2014–2021 · Haïti",
        "title": "Racines académiques, leadership associatif & entrepreneuriat social",
        "years": "INAGHEI · ACTIVEH · Hult Prize · ANGAJMAN · PHJEA · Unleash",
        "text": [
            'Mackenson Cineus intègre l\'<a href="https://www.ueh.edu.ht" target="_blank" style="color:#C9A84C;"><b>INAGHEI</b></a> '
            '(Institut National d\'Administration de Gestion et des Hautes Études Internationales) '
            'en Gestion des Affaires, tout en poursuivant un double cursus en Sciences Économiques à la <b>FDSE</b> '
            '(Faculté de Droit et des Sciences Économiques), deux branches de l\'Université d\'État d\'Haïti. '
            'Il enseigne à mi-temps en lycée et s\'engage au <b>Rotaract Club</b>.',

            'Dès 2016, il intègre <b>ACTIVEH</b> comme co-leader du pôle « Partenariat & Développement », '
            'puis devient <b>Président du Groupe Économie & Finance</b> — organisant des conférences, '
            'lançant le projet « <b>Goud la se Pa m</b> » (sensibilisation à la souveraineté monétaire haïtienne '
            'via visite du musée BRH, 3 émissions radio, campagnes scolaires). En parallèle, il rejoint '
            '<a href="https://www.hultprize.org" target="_blank" style="color:#C9A84C;"><b>Hult Prize Haïti</b></a> '
            'comme Directeur des Opérations puis <b>Directeur Financier</b> : recherche de financements '
            '(Ministère des Finances, BNC), supervision de responsables dans 10 départements.',

            'Il représente Haïti au <b>Hult Prize international 2018</b> avec le projet <b>WEISS</b> '
            '(transformation des déchets en biogaz & fertilisant organique) et effectue un volontariat '
            'en République Dominicaine. Il co-fonde <b>ANGAJMAN</b> comme Directeur Exécutif (campagne '
            'COVID-19 : 50 jeunes, 10 dép.), milite au '
            '<a href="https://www.worldwatercouncil.org" target="_blank" style="color:#C9A84C;"><b>PHJEA</b></a> '
            '(section finance) et remporte le <b>Hackathon Unleash</b> (ODD) avec une équipe internationale, '
            'avant de jouer le rôle de mentor lors d\'un second hackathon.',
        ],
        "tags": ["INAGHEI · UEH", "ACTIVEH", "Hult Prize 2018 · WEISS", "ANGAJMAN", "PHJEA", "Unleash · ODD", "Rotaract"],
    },
    {
        "phase": "phase2",
        "label": "Phase 2 · 2019–2024 · France",
        "title": "Formation Finance & Engagement associatif international",
        "years": "Université du Mans · Erasmus Expertise · Podcast INCLUTECH · MBA ESLSCA",
        "text": [
            'Arrivé en France, Mackenson obtient une <b>Licence Banque, Finance & Assurance</b> à '
            'l\'<a href="https://www.univ-lemans.fr" target="_blank" style="color:#C9A84C;"><b>Université du Mans</b></a> '
            '(2019–2021), puis intègre le MBA 2 Finance de marché à '
            'l\'<a href="https://www.eslsca.fr" target="_blank" style="color:#C9A84C;"><b>ESLSCA Business School Paris</b></a> '
            '(2024–2026). Son mémoire de 80 pages, rédigé en anglais, porte sur l\'impact de la '
            'réglementation ESG et non-ESG sur la performance des portefeuilles.',

            'En 2021, il rejoint '
            '<a href="https://erasmus-expertise.eu" target="_blank" style="color:#C9A84C;"><b>Erasmus Expertise</b></a> '
            'comme tuteur (7 étudiants accompagnés, groupe de conversation français), avant d\'être nommé '
            '<b>Board Member</b> en 2023. Il lance simultanément le podcast '
            '<a href="https://open.spotify.com/show/5XvFdWYwhHWY3EguIhhf69" target="_blank" style="color:#C9A84C;"><b>INCLUTECH</b></a> '
            '(Spotify & Apple Podcasts, bi-mensuel) sur l\'inclusion financière et le rôle des fintechs.',

            'En octobre 2023, son équipe remporte la <b>1ère place du Hackathon Fintech Générations</b> '
            'organisé par <a href="https://francefintech.org" target="_blank" style="color:#C9A84C;"><b>France FinTech</b></a>, '
            'Société Générale, Treezor et Paris&Co — avec le projet <b>Victoria</b> (financement des '
            'rénovations DPE). Invitation à pitcher à <b>Fintech R:Evolution</b> (1 500 participants).',
        ],
        "tags": ["Licence BFA · Le Mans", "MBA ESLSCA · Paris", "Erasmus Expertise · Board Member", "Podcast INCLUTECH", "Hackathon 2023 🥇 · Victoria"],
    },
    {
        "phase": "phase3",
        "label": "Phase 3 · 2024–2025 · HiPay SAS",
        "title": "Chargé de conformité — Fintech de paiement agréée ACPR",
        "years": "HiPay SAS · Levallois-Perret · LCB-FT · Pays sensibles · PPE · Tracfin",
        "text": [
            '<a href="https://hipay.com" target="_blank" style="color:#C9A84C;"><b>HiPay</b></a> '
            'est un prestataire de services de paiement omnicanal coté sur Euronext Growth (ALHYP), '
            'agréé par l\'<a href="https://acpr.banque-france.fr" target="_blank" style="color:#C9A84C;"><b>ACPR</b></a> '
            'comme établissement de paiement. Mackenson y intervient comme <b>Chargé de Conformité</b> à Levallois-Perret.',

            'Ses missions : analyse des risques pays (<a href="https://www.fatf-gafi.org" target="_blank" style="color:#C9A84C;"><b>GAFI</b></a>) '
            'et des typologies de fraude et blanchiment (LCB-FT) sur des <b>pays sensibles et complexes</b> '
            '(incluant pays sous sanctions) ; analyses KYC avec identification des bénéficiaires effectifs, '
            '<b>PPE/PE et SOE</b>, contrôles de cohérence économique ; réponse aux réquisitions '
            '<a href="https://www.economie.gouv.fr/tracfin" target="_blank" style="color:#C9A84C;"><b>Tracfin</b></a> '
            'et judiciaires ; Due Diligence des partenaires institutionnels (établissements systémiques, '
            'RFI en priorité) ; mise à jour de la documentation de risques de non-conformité.',
        ],
        "tags": ["HiPay · ALHYP", "Chargé de Conformité", "LCB-FT · Pays sensibles", "PPE / PE / SOE", "Tracfin", "Due Diligence RFI"],
    },
    {
        "phase": "phase4",
        "label": "Phase 4 · 2025–Présent · Banque DELUBAC & CIE",
        "title": "Analyste LCB-FT — Banque & Fintech (clientèle corporate, CIB, PSP)",
        "years": "Banque DELUBAC & CIE · Paris · Alertes N1 · ER · KYC · DS · Avis opérations",
        "text": [
            '<a href="https://www.delubac.com" target="_blank" style="color:#C9A84C;"><b>Banque Delubac & Cie</b></a> '
            '(fondée 1924) est une banque indépendante de plein exercice. Mackenson y est '
            '<b>Analyste LCB-FT</b> en alternance dans le cadre de son MBA 2 Finance de Marché (ESLSCA).',

            'Ses missions couvrent : le <b>traitement des alertes de niveau 1 LCB-FT</b> sur la clientèle '
            '(corporate, CIB, asset management, banque privée, PSP) ; les <b>Examens Renforcés (ER)</b>, '
            'Profils à Détecter Supplémentaires (PDS) et rédaction d\'avis sur opérations ; '
            'l\'analyse KYC, l\'identification des bénéficiaires effectifs, le contrôle de cohérence '
            'économique et la rédaction de <b>déclarations de soupçon (DS)</b> ; l\'analyse du bilan '
            'et du compte de résultat ; le traitement des demandes de droit de communication '
            'et des réquisitions judiciaires.',

            'Le dashboard de suivi développé sous Excel reflète 205 analyses réalisées couvrant '
            'l\'intégralité des typologies LCB-FT (blanchiment, travail dissimulé, abus de biens sociaux, '
            'financement du terrorisme, etc.) pour un volume total de 24 892 285,50 € examinés.',
        ],
        "tags": ["Banque DELUBAC", "Analyste LCB-FT", "Alertes N1 · ER · PDS", "KYC corporate/CIB/PSP", "DS · Déclarations soupçon", "ACPR · GAFI"],
    },
    {
        "phase": "phase5",
        "label": "Personnalité & Compétences transversales",
        "title": "Profil — Ce que je suis",
        "years": "Leadership de mérite · Entrepreneuriat social · Rigueur analytique · Impact",
        "text": [
            f'<b style="color:#C9A84C;">{st.session_state.get("edit_personality", "Analyste rigoureux à l\'esprit entrepreneurial, qui transforme les contraintes réglementaires en leviers de valeur.")}</b>',

            'Son parcours révèle trois dimensions complémentaires : <b>l\'analyste financier rigoureux</b> '
            '(LCB-FT, KYC, marchés financiers), <b>l\'entrepreneur social engagé</b> (ACTIVEH, Hult Prize, '
            'ANGAJMAN, PHJEA, Unleash) et <b>le communicant pédagogue</b> (podcast INCLUTECH, '
            'interventions publiques, tuteur Erasmus). Ce triptyque rare lui confère une lecture '
            'globale des enjeux financiers, réglementaires et humains.',

            'Son style de leadership, qu\'il nomme lui-même « <b>leadership de mérite et d\'utilité</b> » '
            '— confier les responsabilités à celui qui les mérite et peut faire avancer le collectif '
            '— est le fil conducteur de toutes ses expériences associatives et professionnelles.',
        ],
        "tags": ["Leadership de mérite", "Trilingue", "Compliance & Finance", "Entrepreneuriat social", "Pédagogie", "Impact"],
    },
]

PLATFORMS = [
    {"icon":"💼","name":"LinkedIn","desc":"Profil professionnel — réseau finance/compliance parisien.","url":"https://www.linkedin.com/in/mackenson-cineus","label":"LinkedIn →"},
    {"icon":"💳","name":"HiPay","desc":"Fintech paiement omnicanal agréée ACPR — 2024–2025.","url":"https://hipay.com","label":"HiPay →"},
    {"icon":"🏦","name":"Banque Delubac","desc":"Banque indépendante — Analyste LCB-FT 2025.","url":"https://www.delubac.com","label":"Delubac →"},
    {"icon":"🚀","name":"France FinTech","desc":"Lauréat Hackathon 2023 · Membre actif.","url":"https://francefintech.org","label":"France FinTech →"},
    {"icon":"🏆","name":"Hult Prize","desc":"Représentant Haïti 2018 · projet WEISS.","url":"https://www.hultprize.org","label":"Hult Prize →"},
    {"icon":"🎓","name":"ESLSCA Paris","desc":"MBA 2 Finance de marché 2024–2026.","url":"https://www.eslsca.fr","label":"ESLSCA →"},
    {"icon":"🏫","name":"Université du Mans","desc":"Licence BFA 2019–2021.","url":"https://www.univ-lemans.fr","label":"Univ. du Mans →"},
    {"icon":"🎙","name":"Podcast INCLUTECH","desc":"Finance & Inclusion · Spotify & Apple.","url":"https://open.spotify.com/show/5XvFdWYwhHWY3EguIhhf69","label":"Écouter →"},
    {"icon":"🌍","name":"Erasmus Expertise","desc":"Board Member · ONG internationale.","url":"https://erasmus-expertise.eu","label":"Erasmus →"},
    {"icon":"📸","name":"Instagram","desc":"@mackenson_cineus","url":"https://instagram.com/mackenson_cineus","label":"Instagram →"},
]

REGULATORS = [
    ("🇫🇷","ACPR","Régulateur bancaire & paiement · LCB-FT","https://acpr.banque-france.fr"),
    ("🌐","FATF / GAFI","Normes mondiales anti-blanchiment","https://www.fatf-gafi.org"),
    ("💰","Tracfin","Cellule de Renseignement Financier","https://www.economie.gouv.fr/tracfin"),
    ("📊","AMF","Autorité des Marchés Financiers","https://www.amf-france.org"),
]

_EXTRA_CSS = """
<style>
  .bio-period.phase5::before { background:linear-gradient(180deg,#C9A84C,#E8C97A); }
  .phase5 .bio-phase-label { color:#C9A84C; }
</style>
"""

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

# ─────────────────────────────────────────────────────────────────────────────
# CV — 1 PAGE · FORMAT FINANCE EUROPÉEN STANDARD
# Mise en page entièrement dessinée sur canvas pour un contrôle parfait
# ─────────────────────────────────────────────────────────────────────────────



def generate_cv_pdf(poste="", entreprise="", secteur="", contexte="") -> bytes:
    """
    CV 1 page A4 COMPLÈTE — noir dominant, gris secondaire, zéro couleur.
    En-tête centré, pas de photo, 5 missions/entreprise, cours complets.
    """
    import streamlit as _st
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.pdfbase.pdfmetrics import stringWidth

    buf = io.BytesIO()
    W, H = A4  # 595.28 × 841.89 pts

    ss      = _st.session_state
    name    = ss.get("edit_name",    "Mackenson CINÉUS")
    title_p = ss.get("edit_title",   "Analyste LCB-FT | Compliance Officer")
    loc     = ss.get("edit_location","Île-de-France, France")
    email   = ss.get("edit_email",   "mackenson.cineus@email.com")
    phone   = ss.get("edit_phone",   "+33 6 XX XX XX XX")
    lk      = ss.get("edit_linkedin","linkedin.com/in/mackenson-cineus")
    exps    = ss.get("edit_exp",     [])
    edus    = ss.get("edit_edu",     [])
    skills  = ss.get("edit_skills",  {})
    certifs = ss.get("edit_certifs", [])
    tech    = ss.get("edit_tech",    "Excel avancé – VBA – Python – Bloomberg – Pack Office – Looker – Jura")
    ints    = ss.get("edit_interests","Sécurité financière – Modèles financiers – Trading NASDAQ – Fintech")
    dists   = ss.get("edit_distinctions", [])
    memoir  = ss.get("edit_memoir_title",
                     "Impact of ESG and Non-ESG Regulation on Portfolio Performance "
                     "in Terms of Risk and Return")
    target  = poste if poste else title_p

    # ── MARGES ───────────────────────────────────────────────────
    ML = 45; MR = 45; MT = 38; MB = 26
    TW = W - ML - MR   # ≈ 505 pts

    # ── COULEURS (noir dominant, gris secondaire) ─────────────────
    BLACK  = (0.0,  0.0,  0.0 )
    DGRAY  = (0.22, 0.22, 0.22)   # gris foncé — sous-titres
    MGRAY  = (0.42, 0.42, 0.42)   # gris moyen — corps texte secondaire
    LGRAY  = (0.62, 0.62, 0.62)   # gris clair — dates, détails
    VGRAY  = (0.80, 0.80, 0.80)   # gris très clair — lignes de séparation

    c = rl_canvas.Canvas(buf, pagesize=A4)

    # ── HELPERS ───────────────────────────────────────────────────
    def sw(s, fn, fs):
        return stringWidth(str(s), fn, fs)

    def setf(*rgb):
        c.setFillColorRGB(*rgb)

    def sets(*rgb):
        c.setStrokeColorRGB(*rgb)

    def f(fn, fs):
        c.setFont(fn, fs)

    def line_h(y, x1=ML, x2=None, width=0.5, color=BLACK):
        if x2 is None: x2 = ML + TW
        sets(*color); c.setLineWidth(width)
        c.line(x1, y, x2, y)

    def wrap(txt, x, y, mw, fn, fs, lh, col=BLACK, indent=0):
        """Wrap text, return final y."""
        c.setFillColorRGB(*col); c.setFont(fn, fs)
        words = str(txt).split(); cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if sw(test, fn, fs) <= mw - indent:
                cur = test
            else:
                if cur:
                    c.drawString(x + indent, y, cur); y -= lh; indent = 0
                cur = w
        if cur:
            c.drawString(x + indent, y, cur); y -= lh
        return y

    def section(label, y, space_before=6):
        """Section header: uppercase bold + thick underline."""
        y -= space_before
        f("Times-Bold", 9.8); setf(*BLACK)
        c.drawString(ML, y, label.upper())
        y -= 2
        sets(*BLACK); c.setLineWidth(1.0)
        c.line(ML, y, ML + TW, y)
        return y - 9

    def bullet(txt, y, x=ML, mw=None, fs=8.8, lh=10.5, col=DGRAY):
        """Bullet point."""
        if mw is None: mw = TW
        f("Times-Roman", fs); setf(*col)
        c.drawString(x + 8, y, "•")
        return wrap(txt, x + 19, y, mw - 19, "Times-Roman", fs, lh, col)

    # ════════════════════════════════════════════════════════════════
    # EN-TÊTE CENTRÉ
    # ════════════════════════════════════════════════════════════════
    y = H - MT

    # NOM — centré, très grand
    f("Times-Bold", 22); setf(*BLACK)
    name_up = name.upper()
    name_w = sw(name_up, "Times-Bold", 22)
    c.drawString((W - name_w) / 2, y, name_up)
    y -= 15

    # Titre / poste visé — centré, italique gris foncé
    f("Times-Italic", 10); setf(*DGRAY)
    tgt_w = sw(target, "Times-Italic", 10)
    c.drawString((W - tgt_w) / 2, y, target)
    y -= 13

    # Ligne séparatrice fine
    line_h(y, color=MGRAY, width=0.4); y -= 9

    # Coordonnées — une seule ligne centrée
    f("Times-Roman", 8.5); setf(*MGRAY)
    coords = f"{loc}  ·  {phone}  ·  {email}  ·  {lk}  ·  Podcast INCLUTECH"
    coords_w = sw(coords, "Times-Roman", 8.5)
    # Si trop long, deux lignes
    if coords_w > TW:
        line1 = f"{loc}  ·  {phone}  ·  {email}"
        line2 = f"{lk}  ·  Podcast INCLUTECH (Spotify & Apple Podcasts)"
        l1w = sw(line1, "Times-Roman", 8.5)
        l2w = sw(line2, "Times-Roman", 8.5)
        c.drawString((W - l1w) / 2, y, line1); y -= 10
        c.drawString((W - l2w) / 2, y, line2); y -= 10
    else:
        c.drawString((W - coords_w) / 2, y, coords); y -= 10

    # Double ligne séparatrice
    line_h(y, color=BLACK, width=0.8); y -= 2
    line_h(y, color=BLACK, width=0.3); y -= 8

    # ════════════════════════════════════════════════════════════════
    # PROFIL
    # ════════════════════════════════════════════════════════════════
    y = section("Profil", y, space_before=2)
    profil = (
        "Analyste LCB-FT en alternance (Banque Delubac & Cie) sur clientèle corporate, CIB, "
        "asset management, PSP. Expérience de Chargé de Conformité en fintech de paiement agréée ACPR "
        "(HiPay SAS) : analyse des risques pays GAFI, KYC/PPE/SOE, pays sensibles et complexes, "
        "Tracfin, Due Diligence. MBA 2 Finance de marché en cours (ESLSCA Paris). "
        "Lauréat 1er Prix Hackathon Fintech Générations 2023 — France FinTech / Société Générale. "
        "Mémoire : « " + memoir[:80] + ("…" if len(memoir) > 80 else "") + " ». "
        "Trilingue : français (C1), anglais (avancé), créole haïtien (natif)."
    )
    y = wrap(profil, ML, y, TW, "Times-Roman", 8.8, 11.5, DGRAY); y -= 4

    # ════════════════════════════════════════════════════════════════
    # EXPÉRIENCES PROFESSIONNELLES
    # ════════════════════════════════════════════════════════════════
    y = section("Expériences Professionnelles", y)

    # Sélectionner les expériences pro (exclure asso haïtiennes pour CV 1 page)
    PRO_TYPES = {"Banque", "Fintech", "Compétition", "ONG", ""}
    pro_exps = [e for e in exps
                if e.get("org_type", "") in PRO_TYPES
                and "ACTIVEH" not in e.get("org", "")
                and "ANGAJMAN" not in e.get("org", "")
                and "Hult Prize Haïti" not in e.get("org", "")][:4]

    for exp in pro_exps:
        if y < MB + 55: break

        org_raw = exp.get("org", "")
        org_parts = org_raw.split("·")
        org_name = org_parts[0].strip()
        org_loc_date = ""
        if len(org_parts) > 1:
            org_loc_date = org_parts[-1].strip()

        # Ligne 1 : Org (gras, noir) | Localisation (gris, droite)
        f("Times-Bold", 9.5); setf(*BLACK)
        c.drawString(ML, y, org_name)
        f("Times-Roman", 8.5); setf(*LGRAY)
        c.drawRightString(ML + TW, y, org_loc_date if org_loc_date else "Paris, France")
        y -= 11

        # Ligne 2 : Rôle (italique, gris foncé) | Période (droite, gris)
        role = exp.get("role", "")
        period = exp.get("period", "")
        f("Times-BoldItalic", 9); setf(*DGRAY)
        c.drawString(ML, y, role)
        f("Times-Italic", 8.5); setf(*LGRAY)
        c.drawRightString(ML + TW, y, period)
        y -= 11

        # 5 bullets missions
        for b in exp.get("bullets", [])[:5]:
            if y < MB + 30: break
            y = bullet(b, y, fs=8.7, lh=10.5)

        # Séparateur léger entre postes
        y -= 3
        line_h(y, color=VGRAY, width=0.3); y -= 5

    # ════════════════════════════════════════════════════════════════
    # MÉMOIRE DE FIN D'ÉTUDES
    # ════════════════════════════════════════════════════════════════
    if y > MB + 90:
        y = section("Mémoire de Fin d'Études", y)
        f("Times-BoldItalic", 9); setf(*BLACK)
        # Wrap memoir title on 1-2 lines
        c.drawString(ML, y, "Titre : ")
        lbl_w = sw("Titre : ", "Times-BoldItalic", 9)
        f("Times-Italic", 9); setf(*DGRAY)
        memoir_full = f"« {memoir} »"
        y = wrap(memoir_full, ML + lbl_w, y, TW - lbl_w, "Times-Italic", 9, 11, DGRAY)
        f("Times-Roman", 8.5); setf(*MGRAY)
        c.drawString(ML, y,
            "Mémoire de 80 pages rédigé en anglais — MBA 2 Finance de marché, ESLSCA Business School Paris")
        y -= 10
        c.drawString(ML, y,
            "Thématique : Performance des portefeuilles sous contrainte réglementaire ESG/non-ESG — risque & rendement")
        y -= 12

    # ════════════════════════════════════════════════════════════════
    # FORMATIONS
    # ════════════════════════════════════════════════════════════════
    if y > MB + 80:
        y = section("Formations", y)

        formations = [
            {
                "deg":    "MBA 2 Finance de marché",
                "school": "ESLSCA Business School Paris",
                "loc":    "Paris, France",
                "yr":     "Septembre 2024 – Septembre 2026",
                "cours":  ("Audit & Comptabilité approfondie · Gestion des risques financiers · Gestion de Portefeuille · "
                           "Pricing d'option & Produits dérivés · Analyse financière · Conformité réglementaire · "
                           "Évaluation d'actifs · Machine learning & IA financière · VBA & Python · Finance islamique"),
            },
            {
                "deg":    "Licence en Banque, Finance et Assurance",
                "school": "Université du Mans",
                "loc":    "Le Mans, France",
                "yr":     "Septembre 2022 – Juin 2024",
                "cours":  ("Analyse & gestion de portefeuille · Marchés financiers · Droit commercial & droit fiscal · "
                           "VBA & analyse stochastique · Comptabilité de gestion · Mathématiques financières · "
                           "Économétrie · Assurance vie & non-vie · Gestion des risques bancaires"),
            },
        ]

        # Override with session state if available (excluding INAGHEI)
        ss_edus = [e for e in edus if "INAGHEI" not in e.get("school","") and "Haïti" not in e.get("school","")]
        if ss_edus:
            formations = []
            for e in ss_edus[:2]:
                s_parts = e.get("school","").split("·")
                formations.append({
                    "deg":    e.get("deg",""),
                    "school": s_parts[0].strip(),
                    "loc":    s_parts[-1].strip() if len(s_parts)>1 else "France",
                    "yr":     e.get("yr",""),
                    "cours":  e.get("det",""),
                })

        for fm in formations:
            if y < MB + 40: break

            # Diplôme (gras) | ville (droite, gris)
            f("Times-Bold", 9.5); setf(*BLACK)
            c.drawString(ML, y, fm["school"] + "  |  " + fm["deg"])
            f("Times-Roman", 8.5); setf(*LGRAY)
            c.drawRightString(ML + TW, y, fm["loc"])
            y -= 11

            # Période | droite
            f("Times-Italic", 8.5); setf(*LGRAY)
            c.drawRightString(ML + TW, y, fm["yr"])

            # Cours principaux (soulignés)
            cours_lbl = "Cours principaux : "
            f("Times-Roman", 8.8); setf(*BLACK)
            c.drawString(ML, y, cours_lbl)
            clbl_w = sw(cours_lbl, "Times-Roman", 8.8)
            # underline
            sets(*BLACK); c.setLineWidth(0.25)
            c.line(ML, y - 1, ML + clbl_w, y - 1)
            f("Times-Roman", 8.8); setf(*MGRAY)
            y = wrap(fm["cours"], ML + clbl_w, y, TW - clbl_w, "Times-Roman", 8.8, 11, MGRAY)
            y -= 5

    # ════════════════════════════════════════════════════════════════
    # CERTIFICATIONS, COMPÉTENCES, INTÉRÊTS & ACTIVITÉS
    # ════════════════════════════════════════════════════════════════
    if y > MB + 5:
        y = section("Certifications, Compétences, Intérêts & Activités", y)

        certif_str = " – ".join(certifs) if certifs else "AMF – CFA Level 1 (candidat) – CAMS (en cours)"
        dist_str = " | ".join(f"{ic} {t}" for ic, t, _ in dists[:3])

        rows = [
            ("Certifications en préparation",
             f": {certif_str}"),
            ("Certifications détenues",
             ": MBA Finance de marché (ESLSCA) – Licence BFA (Université du Mans) – AMF"),
            ("Compétences informatiques",
             f": {tech}"),
            ("Langues",
             ": Français (Natif C1) – Créole haïtien (Natif) – Anglais (Avancé)"),
            ("Intérêts",
             f": {ints}"),
            ("Récompenses",
             f": {dist_str}"),
        ]

        for lbl, val in rows:
            if y < MB: break
            f("Times-Bold", 8.8); setf(*BLACK)
            lbl_w = sw(lbl, "Times-Bold", 8.8)
            c.drawString(ML + 6, y, lbl)
            # underline label
            sets(*BLACK); c.setLineWidth(0.25)
            c.line(ML + 6, y - 1, ML + 6 + lbl_w, y - 1)
            f("Times-Roman", 8.8); setf(*MGRAY)
            y = wrap(val, ML + 6 + lbl_w, y, TW - 6 - lbl_w, "Times-Roman", 8.8, 11, MGRAY)

    # ── PAGE FILL CHECK — if y too high, expand spacing to fill page ──
    # The content should naturally fill the page with 5 bullets per exp.

    # ── FOOTER ───────────────────────────────────────────────────
    sets(*VGRAY); c.setLineWidth(0.3)
    c.line(ML, MB + 4, ML + TW, MB + 4)
    f("Helvetica", 6); setf(*LGRAY)
    footer = f"{name}  ·  {email}  ·  {lk}"
    fw = sw(footer, "Helvetica", 6)
    c.drawString((W - fw) / 2, MB - 4, footer)

    c.save()
    buf.seek(0)
    return buf.read()


def generate_lettre_pdf(poste="", entreprise="", secteur="", style_lm="",
                         contexte="", ai_text="") -> bytes:
    """
    Lettre de motivation 1 page A4 COMPLÈTE — noir dominant, gris secondaire.
    En-tête centré expéditeur, destinataire aligné gauche/droite, 4 paragraphes denses.
    Mots-clés AML/LCB-FT intégrés. Footer avec PJ.
    """
    import streamlit as _st
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.pdfbase.pdfmetrics import stringWidth

    buf = io.BytesIO()
    W, H = A4

    ss     = _st.session_state
    name   = ss.get("edit_name",    "Mackenson CINÉUS")
    title  = ss.get("edit_title",   "Analyste LCB-FT | Compliance Officer")
    loc    = ss.get("edit_location","Île-de-France, France")
    email  = ss.get("edit_email",   "mackenson.cineus@email.com")
    phone  = ss.get("edit_phone",   "+33 6 XX XX XX XX")
    lk     = ss.get("edit_linkedin","linkedin.com/in/mackenson-cineus")
    memoir = ss.get("edit_memoir_title",
                    "Impact of ESG and Non-ESG Regulation on Portfolio Performance "
                    "in Terms of Risk and Return")
    target = poste or "Analyste LCB-FT / Compliance Officer"
    ent    = entreprise or "[Nom de l'établissement]"
    sect   = secteur or "Finance / Conformité"

    ML, MR, MT, MB = 50, 50, 42, 30
    TW = W - ML - MR

    BLACK = (0.0, 0.0, 0.0)
    DGRAY = (0.22, 0.22, 0.22)
    MGRAY = (0.42, 0.42, 0.42)
    LGRAY = (0.62, 0.62, 0.62)
    VGRAY = (0.80, 0.80, 0.80)

    c = rl_canvas.Canvas(buf, pagesize=A4)

    def sw(s, fn, fs): return stringWidth(str(s), fn, fs)
    def setf(*rgb): c.setFillColorRGB(*rgb)
    def sets(*rgb): c.setStrokeColorRGB(*rgb)
    def f(fn, fs): c.setFont(fn, fs)
    def line_h(y, x1=ML, x2=None, w=0.5, col=BLACK):
        if x2 is None: x2 = ML + TW
        sets(*col); c.setLineWidth(w); c.line(x1, y, x2, y)

    def wrap(txt, x, y, mw, fn, fs, lh, col=BLACK, ind=0):
        c.setFillColorRGB(*col); c.setFont(fn, fs)
        words = str(txt).split(); cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if sw(test, fn, fs) <= mw - ind: cur = test
            else:
                if cur: c.drawString(x+ind, y, cur); y -= lh; ind = 0
                cur = w
        if cur: c.drawString(x+ind, y, cur); y -= lh
        return y

    def para(txt, y, lh=13.5, fs=9.8, col=DGRAY, indent_first=18):
        """Full justified paragraph with optional first-line indent."""
        return wrap(txt, ML, y, TW, "Times-Roman", fs, lh, col, indent_first)

    y = H - MT

    # ════════════════════════════════════════════════════════════════
    # EN-TÊTE EXPÉDITEUR — CENTRÉ
    # ════════════════════════════════════════════════════════════════
    f("Times-Bold", 14); setf(*BLACK)
    nw = sw(name.upper(), "Times-Bold", 14)
    c.drawString((W - nw) / 2, y, name.upper()); y -= 14

    f("Times-Italic", 9.5); setf(*DGRAY)
    tw_ = sw(title, "Times-Italic", 9.5)
    c.drawString((W - tw_) / 2, y, title); y -= 11

    f("Times-Roman", 8.8); setf(*MGRAY)
    line1 = f"{loc}  ·  {phone}  ·  {email}"
    line2 = f"{lk}  ·  Podcast INCLUTECH"
    l1w = sw(line1, "Times-Roman", 8.8)
    l2w = sw(line2, "Times-Roman", 8.8)
    c.drawString((W - l1w) / 2, y, line1); y -= 10
    c.drawString((W - l2w) / 2, y, line2); y -= 10

    line_h(y, col=BLACK, w=0.8); y -= 2
    line_h(y, col=VGRAY, w=0.3); y -= 14

    # ════════════════════════════════════════════════════════════════
    # BLOC DESTINATAIRE (gauche) + DATE (droite)
    # ════════════════════════════════════════════════════════════════
    f("Times-Roman", 9.5); setf(*BLACK)
    c.drawString(ML, y, "Direction des Ressources Humaines")
    f("Times-Italic", 9); setf(*MGRAY)
    c.drawRightString(ML + TW, y, "Paris, le 14 mars 2026")
    y -= 11
    f("Times-Bold", 9.5); setf(*BLACK)
    c.drawString(ML, y, ent); y -= 11
    f("Times-Roman", 9); setf(*DGRAY)
    c.drawString(ML, y, sect); y -= 16

    # OBJET + REF
    f("Times-Bold", 9.5); setf(*BLACK)
    obj_lbl = "Objet : "
    c.drawString(ML, y, obj_lbl)
    f("Times-Roman", 9.5)
    c.drawString(ML + sw(obj_lbl, "Times-Bold", 9.5), y,
                 f"Candidature — {target}")
    y -= 11
    f("Times-Bold", 9.5)
    ref_lbl = "Réf.   : "
    c.drawString(ML, y, ref_lbl)
    f("Times-Roman", 9); setf(*DGRAY)
    c.drawString(ML + sw(ref_lbl, "Times-Bold", 9.5), y,
                 "Profil LCB-FT/AML — alternance MBA 2 Finance de marché (ESLSCA Paris)")
    y -= 14

    line_h(y, col=BLACK, w=0.6); y -= 14

    # FORMULE D'APPEL
    f("Times-Roman", 9.8); setf(*BLACK)
    c.drawString(ML, y, "Madame, Monsieur,"); y -= 16

    # ════════════════════════════════════════════════════════════════
    # CORPS — 4 PARAGRAPHES DENSES (page pleine)
    # ════════════════════════════════════════════════════════════════
    LH = 13.5   # line height
    FS = 9.8    # font size
    IND = 18    # indent first line

    if ai_text and len(ai_text) > 200:
        for p_txt in ai_text.split("\n\n"):
            if p_txt.strip() and y > MB + 20:
                y = wrap(p_txt.strip(), ML, y, TW, "Times-Roman", FS, LH, DGRAY, IND)
                y -= 9
    else:
        # § 1 — Présentation & contexte de candidature
        p1 = (
            f"Actuellement en alternance comme Analyste LCB-FT à la Banque Delubac & Cie, "
            f"où j'interviens sur la clientèle corporate, CIB, asset management, banque privée et PSP, "
            f"et fort d'une première expérience de Chargé de Conformité chez HiPay SAS — fintech de "
            f"paiement agréée ACPR —, je me permets de vous adresser ma candidature au poste de "
            f"{target} au sein de {ent}. "
            f"Préparant un MBA 2 Finance de marché à l'ESLSCA Business School Paris en parallèle de "
            f"mon alternance, je combine une double expertise opérationnelle en conformité bancaire et "
            f"fintech qui me semble directement mobilisable dans le cadre de vos enjeux réglementaires."
        )
        y = wrap(p1, ML, y, TW, "Times-Roman", FS, LH, DGRAY, IND); y -= 9

        # § 2 — Compétences techniques LCB-FT / mots-clés
        p2 = (
            "Mes deux expériences en conformité m'ont permis d'acquérir une maîtrise complète et "
            "opérationnelle des processus AML/FT : chez Delubac, je traite quotidiennement les alertes "
            "de niveau 1 LCB-FT, les Examens Renforcés (ER), les Profils à Détecter Supplémentaires "
            "(PDS) et rédige des avis sur opérations ; je réalise les analyses KYC, identifie les "
            "bénéficiaires effectifs, contrôle la cohérence économique des transactions et prépare "
            "les déclarations de soupçon (DS). Chez HiPay, j'ai analysé les risques pays GAFI sur "
            "des pays sensibles et complexes incluant des pays sous sanctions, réalisé des analyses "
            "KYC/PPE/PE/SOE, traité les réquisitions Tracfin et conduit des Due Diligence sur des "
            "établissements financiers systémiques et RFI. Cette double expérience banque–fintech "
            "me confère une vision transversale rare de la conformité LCB-FT."
        )
        y = wrap(p2, ML, y, TW, "Times-Roman", FS, LH, DGRAY, IND); y -= 9

        # § 3 — Valeur ajoutée / distinction / mémoire
        p3 = (
            "Au-delà de la maîtrise réglementaire, je mets à votre disposition une dimension "
            "analytique renforcée par ma formation en finance de marché : mon mémoire de recherche "
            f"de 80 pages, intitulé « {memoir[:70]}{'…' if len(memoir)>70 else ''} », "
            "témoigne de ma capacité à traiter des problématiques complexes à l'intersection de la "
            "réglementation, du risque et de la performance financière. Lauréat du 1er Prix Hackathon "
            "Fintech Générations 2023 (France FinTech / Société Générale), ayant pitché le projet "
            "Victoria devant 1 500 participants lors de Fintech R:Evolution, créateur du podcast "
            "INCLUTECH sur l'inclusion financière et Board Member d'Erasmus Expertise, "
            "j'apporte une vision entrepreneuriale et pédagogique qui complète la rigueur analytique "
            "attendue dans un poste de conformité au sein d'une structure exigeante. "
            "Mes compétences en Excel avancé, VBA, Python, Bloomberg, Looker et Jura me permettent "
            "par ailleurs d'automatiser les tâches d'analyse et d'améliorer l'efficacité des processus "
            "de surveillance."
        )
        y = wrap(p3, ML, y, TW, "Times-Roman", FS, LH, DGRAY, IND); y -= 9

        # § 4 — Motivation spécifique + conclusion
        p4 = (
            f"La réputation de {ent} dans le domaine de la {sect.lower() if sect else 'conformité financière'}, "
            "la qualité de ses équipes et son positionnement au cœur des enjeux réglementaires actuels "
            "constituent pour moi des arguments déterminants. Convaincu que la conformité LCB-FT est "
            "non seulement une obligation réglementaire mais un véritable avantage concurrentiel, "
            "je souhaite m'investir pleinement dans votre dispositif de sécurité financière pour "
            "contribuer à son renforcement et à son évolution. Disponible pour un entretien à votre "
            "convenance, je reste à votre disposition pour vous présenter en détail mon parcours "
            "et vous remettre tout document complémentaire que vous jugerez utile. "
            "Dans l'attente de votre retour, je vous prie d'agréer, Madame, Monsieur, "
            "l'expression de mes salutations distinguées."
        )
        y = wrap(p4, ML, y, TW, "Times-Roman", FS, LH, DGRAY, IND); y -= 14

    # ════════════════════════════════════════════════════════════════
    # SIGNATURE
    # ════════════════════════════════════════════════════════════════
    f("Times-Bold", 10.5); setf(*BLACK)
    c.drawString(ML, y, name); y -= 12
    f("Times-Italic", 9); setf(*DGRAY)
    c.drawString(ML, y, title); y -= 10
    f("Times-Roman", 8.8); setf(*MGRAY)
    c.drawString(ML, y, f"{phone}  ·  {email}"); y -= 9
    setf(*DGRAY)
    c.drawString(ML, y, lk)

    # ════════════════════════════════════════════════════════════════
    # FOOTER — PJ
    # ════════════════════════════════════════════════════════════════
    sets(*VGRAY); c.setLineWidth(0.3)
    c.line(ML, MB + 8, ML + TW, MB + 8)
    f("Times-Italic", 8.2); setf(*LGRAY)
    pj = ("PJ : Curriculum Vitæ  ·  Mémoire disponible sur demande  ·  "
          "Portfolio projets (Hackathon Victoria, Podcast INCLUTECH, Hackathon Unleash)")
    pjw = sw(pj, "Times-Italic", 8.2)
    c.drawString((W - pjw) / 2, MB - 2, pj)

    c.save(); buf.seek(0); return buf.read()

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


# ─── JOB SCRAPER HELPERS ───────────────────────────────────────────────────
def _scrape_jobs():
    """Scrape job offers from French/Luxembourg boards via API search."""
    import urllib.request, urllib.parse, json, time

    # Use France Travail / Indeed-like public APIs + Hellowork RSS approach
    # We'll use web search via requests to fetch job listings
    jobs = []

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    queries = [
        ("Analyste LCB-FT Paris", "https://www.welcometothejungle.com/fr/jobs?query=analyste+LCB-FT&refinementList%5Boffice.country_code%5D%5B%5D=FR"),
        ("Compliance Officer AML Paris", "https://www.hellowork.com/fr-fr/emploi/recherche.html?k=compliance+officer+AML&l=Paris"),
        ("Sécurité financière AML Luxembourg", "https://www.moovijob.com/emploi?keywords=securite+financiere+AML&country=lu"),
    ]

    # Francetravail / PE API (public, no auth needed for basic search)
    pe_searches = [
        "analyste LCB-FT",
        "compliance officer sécurité financière",
        "analyste crédit AML",
        "analyste financier conformité",
    ]

    # Build structured job list from known boards
    # Since we can't authenticate to all APIs, we return structured URLs
    job_boards = [
        {
            "source": "France Travail (Pôle Emploi)",
            "icon": "🇫🇷",
            "queries": [
                {"title": "Analyste LCB-FT / Sécurité Financière", "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=analyste+LCB-FT+s%C3%A9curit%C3%A9+financi%C3%A8re&lieux=75&dureeHebdoLibelleRecherche=INDIFFERENT&nbResultatsParPage=20&sort=1", "keywords": ["LCB-FT","conformité","AML"]},
                {"title": "Compliance Officer / Conformité AML", "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=compliance+officer+AML+conformit%C3%A9&lieux=75&sort=1&nbResultatsParPage=20", "keywords": ["compliance","AML","KYC"]},
                {"title": "Analyste Crédit / Risques", "url": "https://candidat.francetravail.fr/offres/recherche?motsCles=analyste+cr%C3%A9dit+risques+financi%C3%A8re&lieux=75&sort=1", "keywords": ["crédit","risques","analyse"]},
            ]
        },
        {
            "source": "LinkedIn (France + Luxembourg)",
            "icon": "💼",
            "queries": [
                {"title": "Analyste LCB-FT | AML Analyst — France", "url": "https://www.linkedin.com/jobs/search/?keywords=analyste+LCB-FT+AML&location=France&sortBy=DD&f_TPR=r86400", "keywords": ["LCB-FT","AML","conformité"]},
                {"title": "Compliance Officer — Paris / Île-de-France", "url": "https://www.linkedin.com/jobs/search/?keywords=compliance+officer+securite+financiere&location=%C3%8Ele-de-France%2C+France&sortBy=DD&f_TPR=r604800", "keywords": ["compliance","sécurité financière","KYC"]},
                {"title": "Analyste Crédit / Risques — Luxembourg", "url": "https://www.linkedin.com/jobs/search/?keywords=analyste+credit+risques+financier&location=Luxembourg&sortBy=DD", "keywords": ["crédit","risques","financement"]},
                {"title": "AML / KYC Analyst — Luxembourg", "url": "https://www.linkedin.com/jobs/search/?keywords=AML+KYC+analyst+compliance&location=Luxembourg&sortBy=DD&f_TPR=r604800", "keywords": ["AML","KYC","compliance"]},
            ]
        },
        {
            "source": "Welcome to the Jungle",
            "icon": "🌿",
            "queries": [
                {"title": "Compliance / Conformité AML", "url": "https://www.welcometothejungle.com/fr/jobs?query=compliance+AML+conformit%C3%A9&refinementList%5Boffice.country_code%5D%5B%5D=FR&sortBy=publishedAt_desc", "keywords": ["compliance","AML"]},
                {"title": "Sécurité Financière / LCB-FT", "url": "https://www.welcometothejungle.com/fr/jobs?query=s%C3%A9curit%C3%A9+financi%C3%A8re+LCB-FT&sortBy=publishedAt_desc", "keywords": ["LCB-FT","sécurité financière"]},
                {"title": "Analyste Financier / Crédit", "url": "https://www.welcometothejungle.com/fr/jobs?query=analyste+financier+cr%C3%A9dit&refinementList%5Boffice.country_code%5D%5B%5D=FR&sortBy=publishedAt_desc", "keywords": ["analyste financier","crédit"]},
            ]
        },
        {
            "source": "Apec (Cadres)",
            "icon": "📋",
            "queries": [
                {"title": "Conformité AML / LCB-FT", "url": "https://www.apec.fr/candidat/recherche-emploi.html/emploi?motsCles=conformit%C3%A9+AML+LCB-FT&typesTeletravail=&typesContrat=&sortsBase=DATE_PUBLICATION&sortsOrder=DECREASE", "keywords": ["conformité","AML","LCB-FT"]},
                {"title": "Analyste Risques / Crédit", "url": "https://www.apec.fr/candidat/recherche-emploi.html/emploi?motsCles=analyste+risques+cr%C3%A9dit&sortsBase=DATE_PUBLICATION&sortsOrder=DECREASE", "keywords": ["risques","crédit","analyse"]},
            ]
        },
        {
            "source": "Indeed France",
            "icon": "🔍",
            "queries": [
                {"title": "Analyste LCB-FT / Sécurité Financière Paris", "url": "https://fr.indeed.com/jobs?q=analyste+LCB-FT+s%C3%A9curit%C3%A9+financi%C3%A8re&l=Paris&sort=date", "keywords": ["LCB-FT","sécurité financière"]},
                {"title": "Compliance Officer AML Paris", "url": "https://fr.indeed.com/jobs?q=compliance+officer+AML&l=Paris&sort=date", "keywords": ["compliance","AML","KYC"]},
                {"title": "Analyste Crédit Paris", "url": "https://fr.indeed.com/jobs?q=analyste+cr%C3%A9dit+risques&l=Paris&sort=date", "keywords": ["crédit","risques"]},
            ]
        },
        {
            "source": "Jobs in Luxembourg",
            "icon": "🇱🇺",
            "queries": [
                {"title": "Compliance / AML Officer Luxembourg", "url": "https://www.jobs.lu/en/job-search/?search=compliance+AML+officer&sort=date&country=LU", "keywords": ["compliance","AML"]},
                {"title": "Analyste Financier / Risques Luxembourg", "url": "https://www.jobs.lu/en/job-search/?search=financial+analyst+risk&sort=date", "keywords": ["financial analyst","risk"]},
            ]
        },
    ]
    return job_boards

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
        "🔎 Offres d'Emploi",
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

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 7 — OFFRES D'EMPLOI (France + Luxembourg)
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔎 Offres d'Emploi":

    st.markdown('<p class="section-header">🔎 Offres d\'Emploi — Sécurité Financière · AML · Analyste Crédit</p>',
                unsafe_allow_html=True)
    st.markdown("""
    <p style='opacity:0.75;margin-bottom:20px;line-height:1.7;max-width:750px;'>
    Accédez directement aux offres les plus récentes en <strong style='color:#C9A84C;'>sécurité financière,
    conformité AML/LCB-FT et analyse crédit</strong> en France et au Luxembourg.
    Cliquez sur les liens pour postuler directement sur chaque plateforme.
    </p>
    """, unsafe_allow_html=True)

    job_boards = _scrape_jobs()

    # Quick search filter
    search_kw = st.text_input("🔍 Filtrer par mot-clé", placeholder="ex: LCB-FT, AML, crédit, Luxembourg…",
                               label_visibility="visible")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    col_idx = 0

    for board in job_boards:
        for query in board["queries"]:
            # Filter
            if search_kw:
                all_text = query["title"].lower() + " ".join(query.get("keywords",[])).lower()
                if search_kw.lower() not in all_text:
                    continue

            col = col1 if col_idx % 2 == 0 else col2
            col_idx += 1

            kw_badges = "".join(
                f'<span style="background:rgba(201,168,76,0.15);border:1px solid rgba(201,168,76,0.3);'
                f'border-radius:4px;padding:2px 7px;font-size:0.7rem;color:#C9A84C;margin:2px 2px 0 0;'
                f'display:inline-block;">{k}</span>'
                for k in query.get("keywords", [])
            )

            with col:
                st.markdown(f"""
                <div style="background:var(--navy-mid);border:1px solid rgba(255,255,255,0.08);
                            border-radius:10px;padding:14px 16px;margin-bottom:12px;
                            border-left:3px solid #C9A84C;">
                  <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:8px;">
                    <div style="flex:1;">
                      <div style="font-size:0.7rem;color:#888;margin-bottom:3px;">
                        {board['icon']} {board['source']}
                      </div>
                      <div style="font-size:0.92rem;font-weight:600;color:#F5F0E8;margin-bottom:6px;">
                        {query['title']}
                      </div>
                      <div style="margin-bottom:8px;">{kw_badges}</div>
                      <a href="{query['url']}" target="_blank"
                         style="display:inline-block;background:linear-gradient(135deg,#C9A84C,#E8C97A);
                                color:#0D1B2A;padding:5px 14px;border-radius:6px;
                                font-size:0.78rem;font-weight:700;text-decoration:none;">
                        Voir les offres →
                      </a>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='background:var(--navy-mid);border:1px solid rgba(201,168,76,0.2);
                border-radius:12px;padding:20px;margin-top:8px;'>
      <div style='font-size:0.95rem;font-weight:600;color:#C9A84C;margin-bottom:10px;'>
        💡 Mots-clés à utiliser dans vos candidatures
      </div>
      <div style='display:flex;flex-wrap:wrap;gap:8px;'>
    """ + "".join(
        f'<span style="background:rgba(201,168,76,0.12);border:1px solid rgba(201,168,76,0.3);'
        f'border-radius:6px;padding:4px 12px;font-size:0.8rem;color:#E8C97A;">{kw}</span>'
        for kw in ["LCB-FT","AML","KYC/KYB","PPE/PE/SOE","Tracfin","Examens Renforcés",
                   "Déclaration de soupçon","GAFI","ACPR","Pays sensibles","Due Diligence",
                   "Conformité bancaire","Analyse financière","Risque de crédit",
                   "ESG","Portefeuille","MBA Finance de marché"]
    ) + """
      </div>
      <div style='margin-top:12px;font-size:0.82rem;opacity:0.7;line-height:1.6;'>
        💼 Plateformes recommandées pour votre profil :
        <a href="https://www.linkedin.com/jobs/" target="_blank" style="color:#4A9EFF;">LinkedIn</a> ·
        <a href="https://www.apec.fr" target="_blank" style="color:#4A9EFF;">APEC</a> ·
        <a href="https://candidat.francetravail.fr" target="_blank" style="color:#4A9EFF;">France Travail</a> ·
        <a href="https://www.welcometothejungle.com" target="_blank" style="color:#4A9EFF;">Welcome to the Jungle</a> ·
        <a href="https://www.jobs.lu" target="_blank" style="color:#4A9EFF;">Jobs.lu (Luxembourg)</a> ·
        <a href="https://www.moovijob.com" target="_blank" style="color:#4A9EFF;">Moovijob</a>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 8 — ÉDITION DU PROFIL (COMPLÈTE ET SAUVEGARDABLE)
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "✏️ Édition du Profil":

    st.markdown('<p class="section-header">✏️ Édition du Profil</p>', unsafe_allow_html=True)
    st.markdown("""
    <p style='opacity:0.75;margin-bottom:16px;line-height:1.7;max-width:700px;'>
    Toutes les modifications sont <strong style='color:#C9A84C;'>appliquées en temps réel</strong>
    sur la plateforme et dans les PDFs générés. Cliquez <strong>💾 Sauvegarder</strong> pour valider chaque section.
    </p>
    """, unsafe_allow_html=True)

    t1, t2, t3, t4, t5, t6, t7 = st.tabs([
        "👤 Infos Générales",
        "💼 Expériences",
        "🎓 Formation",
        "⚡ Compétences",
        "🏅 Distinctions",
        "📖 Mémoire",
        "🧠 Personnalité",
    ])

    # ── TAB 1 — INFOS GÉNÉRALES ─────────────────────────────────────────────
    with t1:
        st.markdown("#### Informations personnelles & professionnelles")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Nom complet", key="edit_name")
            st.text_input("Localisation", key="edit_location")
            st.text_input("Email", key="edit_email")
        with c2:
            st.text_input("Titre professionnel", key="edit_title")
            st.text_input("Téléphone", key="edit_phone")
            st.text_input("LinkedIn (sans https://)", key="edit_linkedin")

        st.text_area("Résumé / Accroche professionnelle", key="edit_summary", height=110)

        if st.button("💾 Sauvegarder les infos générales", use_container_width=True, key="save_infos"):
            st.success("✅ Infos générales sauvegardées et appliquées sur toute la plateforme !")

    # ── TAB 2 — EXPÉRIENCES ─────────────────────────────────────────────────
    with t2:
        st.markdown("#### Expériences professionnelles & associatives")

        exps = st.session_state.edit_exp
        for i, exp in enumerate(exps):
            with st.expander(f"**{exp['role']}** — {exp['org']} ({exp['period']})",
                              expanded=(i < 2)):
                c1, c2 = st.columns([2,1])
                with c1:
                    nr = st.text_input("Poste / Rôle", value=exp["role"],   key=f"er_{i}")
                    no = st.text_input("Organisation",  value=exp["org"],    key=f"eo_{i}")
                    nu = st.text_input("URL officielle", value=exp.get("url",""), key=f"eu_{i}")
                with c2:
                    np = st.text_input("Période",     value=exp["period"],  key=f"ep_{i}")
                    nt = st.selectbox("Type", ["Professionnel","Association","Compétition","ONG","Bénévolat"],
                                      index=["Banque","Fintech","Compétition","ONG","Association","Bénévolat"].index(exp.get("org_type","Association"))
                                      if exp.get("org_type","Association") in ["Banque","Fintech","Compétition","ONG","Association","Bénévolat"] else 0,
                                      key=f"et_{i}")

                st.markdown("**Missions / Réalisations** *(une par ligne)*")
                nb = st.text_area("", value="\n".join(exp["bullets"]), height=110,
                                   key=f"eb_{i}", label_visibility="collapsed")

                col_s, col_d = st.columns([3,1])
                with col_s:
                    if st.button(f"💾 Sauvegarder", key=f"save_exp_{i}"):
                        st.session_state.edit_exp[i] = {
                            "role": nr, "org": no, "period": np, "url": nu,
                            "org_type": nt,
                            "bullets": [b.strip() for b in nb.split("\n") if b.strip()],
                        }
                        st.success(f"✅ « {nr} » sauvegardé !")
                        st.rerun()
                with col_d:
                    if st.button("🗑️ Supprimer", key=f"del_exp_{i}", type="secondary"):
                        st.session_state.edit_exp.pop(i)
                        st.rerun()

        st.markdown("---")
        st.markdown("#### ➕ Ajouter une expérience")
        with st.expander("Nouvelle expérience", expanded=False):
            c1, c2 = st.columns([2,1])
            with c1:
                new_r = st.text_input("Poste",         key="new_er", placeholder="ex: Risk Manager")
                new_o = st.text_input("Organisation",  key="new_eo", placeholder="ex: BNP Paribas · Paris")
                new_u = st.text_input("URL",           key="new_eu", placeholder="https://...")
            with c2:
                new_p = st.text_input("Période",       key="new_ep", placeholder="2025–Présent")
                new_t = st.selectbox("Type", ["Professionnel","Association","Compétition","ONG","Bénévolat"], key="new_et")
            new_b = st.text_area("Missions (une par ligne)", key="new_eb", height=80)
            if st.button("➕ Ajouter", key="add_exp_btn"):
                if new_r and new_o:
                    st.session_state.edit_exp.insert(0, {
                        "role": new_r, "org": new_o, "period": new_p, "url": new_u,
                        "org_type": new_t,
                        "bullets": [b.strip() for b in new_b.split("\n") if b.strip()],
                    })
                    st.success(f"✅ « {new_r} » ajouté en tête !")
                    st.rerun()

    # ── TAB 3 — FORMATION ───────────────────────────────────────────────────
    with t3:
        st.markdown("#### Formation académique")
        for i, e in enumerate(st.session_state.edit_edu):
            with st.expander(f"**{e['deg']}** — {e['school']} ({e['yr']})", expanded=(i==0)):
                c1, c2 = st.columns([2,1])
                with c1:
                    nd = st.text_input("Diplôme",     value=e["deg"],    key=f"ed_{i}")
                    ns = st.text_input("École",        value=e["school"], key=f"es_{i}")
                    nu = st.text_input("URL",          value=e.get("url",""), key=f"edu_u_{i}")
                with c2:
                    ny = st.text_input("Années",      value=e["yr"],     key=f"ey_{i}")
                    nm = st.text_input("Mention",     value=e.get("mention",""), key=f"em_{i}")
                ndet = st.text_area("Cours / Compétences", value=e["det"], key=f"edet_{i}", height=70)
                if st.button("💾 Sauvegarder", key=f"save_edu_{i}"):
                    st.session_state.edit_edu[i] = {
                        "deg":nd,"school":ns,"yr":ny,"url":nu,"det":ndet,"mention":nm}
                    st.success(f"✅ « {nd} » sauvegardé !")
                    st.rerun()

        st.markdown("---")
        with st.expander("➕ Ajouter une formation", expanded=False):
            c1, c2 = st.columns([2,1])
            with c1:
                nfd = st.text_input("Diplôme",  key="nfd", placeholder="ex: Master Finance")
                nfs = st.text_input("École",    key="nfs", placeholder="ex: Paris Dauphine")
                nfu = st.text_input("URL",      key="nfu", placeholder="https://...")
            with c2:
                nfy = st.text_input("Années",   key="nfy", placeholder="2025–2027")
                nfm = st.text_input("Mention",  key="nfm", placeholder="ex: Mention Bien")
            nfdet = st.text_input("Cours / Compétences", key="nfdet")
            if st.button("➕ Ajouter", key="add_edu_btn"):
                if nfd and nfs:
                    st.session_state.edit_edu.insert(0,
                        {"deg":nfd,"school":nfs,"yr":nfy,"url":nfu,"det":nfdet,"mention":nfm})
                    st.success(f"✅ « {nfd} » ajouté !")
                    st.rerun()

    # ── TAB 4 — COMPÉTENCES ─────────────────────────────────────────────────
    with t4:
        st.markdown("#### Compétences techniques (niveaux 0–100)")
        updated_skills = {}
        for skill, level in list(st.session_state.edit_skills.items()):
            c1, c2, c3 = st.columns([3, 1, 0.5])
            with c1:
                nsn = st.text_input("", value=skill, key=f"sk_n_{skill}",
                                     label_visibility="collapsed")
            with c2:
                nsl = st.number_input("", min_value=0, max_value=100, value=level,
                                       key=f"sk_l_{skill}", label_visibility="collapsed")
            with c3:
                if st.button("🗑", key=f"sk_del_{skill}"):
                    d = dict(st.session_state.edit_skills)
                    d.pop(skill, None)
                    st.session_state.edit_skills = d
                    st.rerun()
            updated_skills[nsn] = nsl

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1: new_sn = st.text_input("Nouvelle compétence", key="new_sk_n",
                                          placeholder="ex: Déclarations Tracfin")
        with c2: new_sl = st.number_input("Niveau (0-100)", 0, 100, 80, key="new_sk_l")

        if st.button("💾 Sauvegarder toutes les compétences", use_container_width=True, key="save_skills"):
            if new_sn.strip():
                updated_skills[new_sn.strip()] = new_sl
            st.session_state.edit_skills = updated_skills
            st.success("✅ Compétences sauvegardées — graphiques et CV mis à jour !")
            st.rerun()

        st.markdown("---")
        st.markdown("#### Certifications")
        certs = st.session_state.get("edit_certifs", [])
        certs_text = "\n".join(certs)
        new_certs = st.text_area("Certifications (une par ligne)", value=certs_text, height=80, key="edit_certifs_text")
        st.markdown("#### Outils informatiques")
        st.text_input("Compétences informatiques", key="edit_tech",
                       placeholder="Excel avancé – VBA – Python – Bloomberg")
        st.markdown("#### Centres d'intérêt")
        st.text_input("Intérêts", key="edit_interests")
        if st.button("💾 Sauvegarder certifications & outils", use_container_width=True, key="save_certs"):
            st.session_state.edit_certifs = [l.strip() for l in new_certs.split("\n") if l.strip()]
            st.success("✅ Certifications et outils sauvegardés !")

    # ── TAB 5 — DISTINCTIONS ────────────────────────────────────────────────
    with t5:
        st.markdown("#### Distinctions & Récompenses")
        dists = list(st.session_state.edit_distinctions)
        for i, (icon, title_d, desc) in enumerate(dists):
            c1, c2, c3, c4 = st.columns([0.4, 1.8, 3.5, 0.4])
            with c1: ni = st.text_input("", value=icon,    key=f"di_i_{i}", label_visibility="collapsed")
            with c2: nt = st.text_input("", value=title_d, key=f"di_t_{i}", label_visibility="collapsed")
            with c3: nd = st.text_input("", value=desc,    key=f"di_d_{i}", label_visibility="collapsed")
            with c4:
                if st.button("🗑", key=f"di_del_{i}"):
                    st.session_state.edit_distinctions.pop(i); st.rerun()

        if st.button("💾 Sauvegarder les distinctions", use_container_width=True, key="save_dists"):
            new_d = []
            for i in range(len(dists)):
                new_d.append((
                    st.session_state.get(f"di_i_{i}", dists[i][0]),
                    st.session_state.get(f"di_t_{i}", dists[i][1]),
                    st.session_state.get(f"di_d_{i}", dists[i][2]),
                ))
            st.session_state.edit_distinctions = new_d
            st.success("✅ Distinctions sauvegardées !")
            st.rerun()

        st.markdown("---")
        st.markdown("#### ➕ Ajouter une distinction")
        c1, c2, c3 = st.columns([0.4, 2, 4])
        with c1: ndi = st.text_input("Icône", key="new_di_i", value="🏅")
        with c2: ndt = st.text_input("Titre", key="new_di_t", placeholder="Prix / Engagement")
        with c3: ndd = st.text_input("Description", key="new_di_d")
        if st.button("➕ Ajouter", key="add_dist_btn"):
            if ndt.strip():
                st.session_state.edit_distinctions.append((ndi, ndt, ndd))
                st.success(f"✅ « {ndt} » ajouté !")
                st.rerun()

    # ── TAB 6 — MÉMOIRE ─────────────────────────────────────────────────────
    with t6:
        st.markdown("#### Mémoire de fin d'études")
        st.markdown("""
        <div style='background:var(--navy-mid);border:1px solid rgba(201,168,76,0.2);
                    border-radius:10px;padding:16px;margin-bottom:16px;'>
          <div style='font-size:0.85rem;color:#C9A84C;font-weight:600;margin-bottom:6px;'>
            📖 Titre actuel du mémoire
          </div>
          <div style='font-size:0.9rem;font-style:italic;opacity:0.9;line-height:1.6;'>
            "Impact of ESG and Non-ESG Regulation on Portfolio Performance in Terms of Risk and Return"
          </div>
          <div style='font-size:0.78rem;opacity:0.55;margin-top:6px;'>
            80 pages · Rédigé en anglais · MBA 2 Finance de marché · ESLSCA Paris
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.text_input("Titre du mémoire (en anglais)", key="edit_memoir_title")
        st.text_area("Description / Résumé du mémoire", key="edit_memoir_desc", height=100)

        if st.button("💾 Sauvegarder le mémoire", use_container_width=True, key="save_memoir"):
            st.success("✅ Mémoire sauvegardé — intégré dans le CV et la lettre de motivation !")

    # ── TAB 7 — PERSONNALITÉ ────────────────────────────────────────────────
    with t7:
        st.markdown("#### Phrase de personnalité / profil type")
        st.markdown("""
        <p style='opacity:0.75;line-height:1.7;margin-bottom:16px;'>
        Cette phrase résume votre profil en une ligne — affichée dans la biographie et
        potentiellement utilisée en accroche de lettre de motivation.
        </p>
        """, unsafe_allow_html=True)

        st.text_area("Phrase de personnalité", key="edit_personality", height=80)

        st.markdown("---")
        st.markdown("#### 🧠 Analyse de personnalité — Type MBTI / Compétences clés")
        st.markdown("""
        <div style='background:var(--navy-mid);border:1px solid rgba(201,168,76,0.2);
                    border-radius:12px;padding:20px;'>
          <div style='font-size:1rem;font-weight:600;color:#C9A84C;margin-bottom:12px;'>
            Mackenson CINÉUS — Profil de personnalité
          </div>
          <div style='display:grid;grid-template-columns:1fr 1fr;gap:16px;'>
            <div>
              <div style='font-size:0.85rem;font-weight:600;color:#4A9EFF;margin-bottom:6px;'>Type de profil</div>
              <div style='font-size:0.9rem;opacity:0.9;line-height:1.7;'>
                <b>ENTJ / Commandant</b> — leadership structuré, vision long terme,
                capacité à motiver des équipes vers des objectifs concrets.
              </div>
            </div>
            <div>
              <div style='font-size:0.85rem;font-weight:600;color:#2ECC71;margin-bottom:6px;'>Forces distinctives</div>
              <div style='font-size:0.9rem;opacity:0.9;line-height:1.7;'>
                Rigueur analytique · Entrepreneuriat social · Leadership de mérite ·
                Pédagogie · Résilience (parcours international)
              </div>
            </div>
            <div>
              <div style='font-size:0.85rem;font-weight:600;color:#E67E22;margin-bottom:6px;'>Valeur ajoutée unique</div>
              <div style='font-size:0.9rem;opacity:0.9;line-height:1.7;'>
                Seul profil compliance junior combinant : expérience Banque + Fintech paiement +
                MBA Finance de marché + Hackathon Fintech + Podcast + ONG internationale.
              </div>
            </div>
            <div>
              <div style='font-size:0.85rem;font-weight:600;color:#9B59B6;margin-bottom:6px;'>En une phrase</div>
              <div style='font-size:0.9rem;opacity:0.9;line-height:1.7;font-style:italic;'>
                « Analyste rigoureux à l'esprit entrepreneurial — transforme les contraintes
                réglementaires en leviers de valeur. »
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("💾 Sauvegarder la personnalité", use_container_width=True, key="save_personality"):
            st.success("✅ Profil de personnalité sauvegardé !")
