import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import io
import requests
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors as rl_colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

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
  .bio-period.phase5::before { background:linear-gradient(180deg,#C9A84C,#E8C97A); }
  .bio-phase-label { font-size:0.72rem; letter-spacing:2px; text-transform:uppercase; font-weight:600; margin-bottom:6px; }
  .phase1 .bio-phase-label { color:#4A9EFF; }
  .phase2 .bio-phase-label { color:var(--gold); }
  .phase3 .bio-phase-label { color:var(--warn); }
  .phase4 .bio-phase-label { color:#9B59B6; }
  .phase5 .bio-phase-label { color:#C9A84C; }
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
    display:flex; align-items:flex-start; gap:14px;
  }
  .platform-icon { font-size:1.6rem; flex-shrink:0; width:44px; height:44px; display:flex; align-items:center; justify-content:center; background:rgba(201,168,76,0.1); border-radius:10px; }
  .platform-name { font-size:0.95rem; font-weight:600; color:var(--gold); margin-bottom:2px; }
  .platform-desc { font-size:0.82rem; color:var(--cream); opacity:0.7; line-height:1.5; }
  .platform-link { display:inline-block; margin-top:6px; font-size:0.78rem; color:var(--accent); text-decoration:none; }
  .stButton > button {
    background:linear-gradient(135deg,var(--gold) 0%,var(--gold-light) 100%) !important;
    color:var(--navy) !important; border:none !important; border-radius:8px !important;
    font-weight:600 !important; padding:10px 24px !important;
  }
  .stTabs [data-baseweb="tab-list"] { background:var(--navy-mid); border-radius:8px; gap:4px; }
  .stTabs [data-baseweb="tab"] { color:var(--cream) !important; }
  .stTabs [aria-selected="true"] { background:rgba(201,168,76,0.2) !important; color:var(--gold) !important; }
  .stTextArea textarea,.stTextInput input { background:var(--navy-mid) !important; color:var(--cream) !important; border:1px solid rgba(201,168,76,0.3) !important; border-radius:8px !important; }
  #MainMenu,footer,[data-testid="stHeader"] { display:none !important; }
  .block-container { padding-top:2rem !important; }
  .sanction-card {
    background:var(--navy-mid); border:1px solid rgba(231,76,60,0.3);
    border-left:4px solid #E74C3C; border-radius:10px; padding:16px 20px; margin-bottom:14px;
  }
  .sanction-amount { color:#E74C3C; font-weight:700; font-size:1.1rem; }
  .sanction-entity { color:var(--gold); font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# STATE INIT
# ═══════════════════════════════════════════════════════════════════════════════

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
                    "Traitement des Examens Renforcés (ER), Profils à Détecter Supplémentaires (PDS) et rédaction d'avis sur opérations suspectes",
                    "Réalisation de l'analyse KYC, identification des bénéficiaires effectifs, contrôle de cohérence économique et rédaction de déclarations de soupçon (DS)",
                    "Analyse du bilan et du compte de résultat pour évaluer la santé financière des partenaires commerciaux",
                    "Traitement des demandes de droit de communication et des réquisitions judiciaires",
                ],
            },
            {
                "role":    "Chargé de Conformité",
                "org":     "HIPAY SAS · Levallois-Perret, France",
                "org_type": "Fintech",
                "period":  "Septembre 2024 – Septembre 2025",
                "url":     "https://hipay.com",
                "bullets": [
                    "Analyse des risques pays (GAFI) et des typologies de fraude et de blanchiment (LCB-FT) sur pays sensibles et complexes, dont pays sous sanctions internationales",
                    "Réalisation des analyses KYC : identification des bénéficiaires effectifs, PPE/PE et SOE, contrôles de cohérence économique",
                    "Traitement des alertes et réponses aux réquisitions : Tracfin, autorités judiciaires, analyses complémentaires (fraudes, sanctions)",
                    "Due Diligence des partenaires institutionnels et établissements financiers systémiques (RFI en priorité)",
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
                    "Projet Victoria : solution de financement des rénovations DPE — pitch à Fintech R:Evolution (1 500 participants : investisseurs, régulateurs, entrepreneurs)",
                ],
            },
            {
                "role":    "Directeur Financier & Directeur des Opérations",
                "org":     "Hult Prize Haïti · Haïti / International",
                "org_type": "Association",
                "period":  "2018 – 2021",
                "url":     "https://www.hultprize.org",
                "bullets": [
                    "Directeur financier : recherche de financements (Ministère des Finances, BNC), élaboration du budget, supervision des responsables régionaux",
                    "Représentant Haïti au Hult Prize 2018 — projet WEISS (transformation des déchets en biogaz & fertilisant organique)",
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
                "det":    "Gestion des Affaires, Économie, Droit, Politiques publiques",
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
            ("🥇", "Hackathon Fintech Générations 2023", "Lauréat du 1er Prix — France FinTech & Société Générale — Projet Victoria (DPE)"),
            ("🏆", "Hult Prize 2018", "Représentant Haïti — Projet WEISS (biogaz & fertilisant organique)"),
            ("🏅", "Hackathon Unleash (ODD)", "Lauréat — Objectifs de Développement Durable — équipe internationale"),
            ("🎙", "Podcast INCLUTECH", "Créateur & animateur — Finance & Inclusion Financière — Spotify & Apple Podcasts"),
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
    return {
        "name":     st.session_state.get("edit_name",     "Mackenson CINÉUS"),
        "title":    st.session_state.get("edit_title",    "Analyste LCB-FT | Compliance Officer"),
        "location": st.session_state.get("edit_location", "Île-de-France, France"),
        "email":    st.session_state.get("edit_email",    "mackenson.cineus@email.com"),
        "phone":    st.session_state.get("edit_phone",    "+33 6 XX XX XX XX"),
        "linkedin": st.session_state.get("edit_linkedin", "linkedin.com/in/mackenson-cineus"),
        "summary":  st.session_state.get("edit_summary",  ""),
    }

# ── STATIC DATA ────────────────────────────────────────────────────────────────
TIMELINE = [
    {"year":"2018–2021","title":"Hult Prize Haïti — Directeur Financier & Opérations",
     "desc":"Financement, budget, supervision régionale · Hult Prize 2018 (WEISS)","icon":"🏆","cat":"Entrepreneuriat"},
    {"year":"2019–2021","title":"Université du Mans — Licence BFA",
     "desc":"Banque, Finance & Assurance — VBA, analyse stochastique, droit fiscal","icon":"🏫","cat":"Éducation"},
    {"year":"2021–Présent","title":"Podcast INCLUTECH",
     "desc":"Finance & Inclusion Financière · bi-mensuel · Spotify & Apple Podcasts","icon":"🎙","cat":"Communication"},
    {"year":"2024–Présent","title":"MBA 2 Finance de marché — ESLSCA Paris",
     "desc":"Gestion de portefeuille · Produits dérivés · Conformité · VBA & Python","icon":"📈","cat":"Éducation"},
    {"year":"Oct. 2023","title":"🥇 Hackathon Fintech Générations — 1er Prix",
     "desc":"Projet Victoria (DPE) · France FinTech / Société Générale / Treezor","icon":"🚀","cat":"Entrepreneuriat"},
    {"year":"2024–2025","title":"Chargé de Conformité — HIPAY SAS",
     "desc":"Fintech paiement · LCB-FT · KYC/PPE · pays sensibles · Tracfin · Due Diligence","icon":"💳","cat":"Professionnel"},
    {"year":"2025–Présent","title":"Analyste LCB-FT — Banque DELUBAC & CIE",
     "desc":"Alertes N1 · ER/PDS · KYC corporate/CIB/PSP · DS · avis sur opérations","icon":"🏦","cat":"Professionnel"},
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
    "events": ["INAGHEI · Hult Prize · Podcast INCLUTECH",
               "Licence BFA · Université du Mans",
               "MBA ESLSCA · Delubac LCB-FT · HiPay Compliance"],
    "years": ["2014–2021", "2019–2021", "2021–Présent"],
    "size": [18, 14, 34],
}

BIO_PERIODS = [
    {
        "phase": "phase1",
        "label": "Phase 1 · 2014–2021 · Haïti",
        "title": "Formation académique & premiers engagements financiers",
        "years": "INAGHEI · Hult Prize · Podcast INCLUTECH",
        "text": [
            'Mackenson Cineus intègre l\'<a href="https://www.ueh.edu.ht" target="_blank" style="color:#C9A84C;"><b>INAGHEI</b></a> '
            '(Institut National d\'Administration de Gestion et des Hautes Études Internationales) '
            'en Gestion des Affaires, tout en poursuivant un double cursus en Sciences Économiques à la <b>FDSE</b>.',
            'Il rejoint <a href="https://www.hultprize.org" target="_blank" style="color:#C9A84C;"><b>Hult Prize Haïti</b></a> '
            'comme Directeur Financier : recherche de financements (Ministère des Finances, BNC), '
            'élaboration du budget, supervision de responsables dans 10 départements. '
            'Il représente Haïti au <b>Hult Prize international 2018</b> avec le projet <b>WEISS</b>.',
        ],
        "tags": ["INAGHEI · UEH", "Hult Prize 2018 · WEISS", "Finance publique", "Budget & Fundraising"],
    },
    {
        "phase": "phase2",
        "label": "Phase 2 · 2019–2024 · France",
        "title": "Formation Finance européenne & lancement du Podcast INCLUTECH",
        "years": "Université du Mans · MBA ESLSCA · Podcast INCLUTECH",
        "text": [
            'Arrivé en France, Mackenson obtient une <b>Licence Banque, Finance & Assurance</b> à '
            'l\'<a href="https://www.univ-lemans.fr" target="_blank" style="color:#C9A84C;"><b>Université du Mans</b></a> '
            '(2019–2021 : marchés bancaires, analyse stochastique, droit fiscal, VBA), '
            'puis intègre le MBA 2 Finance de marché à '
            'l\'<a href="https://www.eslsca.fr" target="_blank" style="color:#C9A84C;"><b>ESLSCA Business School Paris</b></a> '
            '(2024–2026). Son mémoire de 80 pages porte sur l\'impact de la réglementation ESG et non-ESG sur la performance des portefeuilles.',
            'Il lance le podcast <a href="https://open.spotify.com/show/5XvFdWYwhHWY3EguIhhf69" target="_blank" style="color:#C9A84C;"><b>INCLUTECH</b></a> '
            '(Spotify & Apple Podcasts, bi-mensuel) sur l\'inclusion financière et le rôle des fintechs. '
            'En octobre 2023, son équipe remporte la <b>1ère place du Hackathon Fintech Générations</b> '
            'organisé par <b>France FinTech / Société Générale / Treezor</b> avec le projet <b>Victoria</b> — pitch à Fintech R:Evolution (1 500 participants).',
        ],
        "tags": ["Licence BFA · Le Mans", "MBA ESLSCA · Paris", "Podcast INCLUTECH", "Hackathon 2023 🥇 · Victoria"],
    },
    {
        "phase": "phase3",
        "label": "Phase 3 · 2024–2025 · HiPay SAS",
        "title": "Chargé de Conformité — Fintech de paiement agréée ACPR",
        "years": "HiPay SAS · Levallois-Perret · LCB-FT · Pays sensibles · PPE · Tracfin",
        "text": [
            '<a href="https://hipay.com" target="_blank" style="color:#C9A84C;"><b>HiPay</b></a> '
            'est un prestataire de services de paiement omnicanal coté sur Euronext Growth (ALHYP), '
            'agréé par l\'<a href="https://acpr.banque-france.fr" target="_blank" style="color:#C9A84C;"><b>ACPR</b></a>. '
            'Mackenson y intervient comme <b>Chargé de Conformité</b> à Levallois-Perret.',
            'Ses missions : analyse des risques pays (<b>GAFI</b>) sur des <b>pays sensibles et complexes</b> '
            '(incluant pays sous sanctions) ; analyses KYC avec identification des bénéficiaires effectifs, '
            '<b>PPE/PE et SOE</b> ; réponse aux réquisitions <b>Tracfin</b> et judiciaires ; '
            'Due Diligence des partenaires institutionnels (établissements systémiques, RFI en priorité).',
        ],
        "tags": ["HiPay · ALHYP", "Chargé de Conformité", "LCB-FT · Pays sensibles", "PPE / PE / SOE", "Tracfin", "Due Diligence RFI"],
    },
    {
        "phase": "phase4",
        "label": "Phase 4 · 2025–Présent · Banque DELUBAC & CIE",
        "title": "Analyste LCB-FT — Clientèle corporate, CIB, PSP",
        "years": "Banque DELUBAC & CIE · Paris · Alertes N1 · ER · KYC · DS",
        "text": [
            '<a href="https://www.delubac.com" target="_blank" style="color:#C9A84C;"><b>Banque Delubac & Cie</b></a> '
            '(fondée 1924) est une banque indépendante de plein exercice. Mackenson y est '
            '<b>Analyste LCB-FT</b> en alternance dans le cadre de son MBA 2 Finance de Marché (ESLSCA).',
            'Ses missions : <b>traitement des alertes de niveau 1 LCB-FT</b> sur clientèle corporate, CIB, '
            'asset management, banque privée, PSP ; <b>Examens Renforcés (ER)</b>, Profils à Détecter '
            'Supplémentaires (PDS) et avis sur opérations ; analyse KYC, bénéficiaires effectifs, '
            'cohérence économique et <b>déclarations de soupçon (DS)</b> ; '
            'analyse du bilan et compte de résultat ; réquisitions judiciaires.',
            'Le dashboard Excel développé reflète 205 analyses couvrant l\'intégralité des typologies '
            'LCB-FT pour un volume total de <b>24 892 285,50 € examinés</b>.',
        ],
        "tags": ["Banque DELUBAC", "Analyste LCB-FT", "Alertes N1 · ER · PDS", "KYC corporate/CIB/PSP", "DS · Déclarations soupçon", "ACPR · GAFI"],
    },
    {
        "phase": "phase5",
        "label": "Profil & Compétences transversales",
        "title": "Ce que je suis",
        "years": "Leadership · Rigueur analytique · Finance & Conformité",
        "text": [
            f'<b style="color:#C9A84C;">{st.session_state.get("edit_personality", "Analyste rigoureux à l\'esprit entrepreneurial, qui transforme les contraintes réglementaires en leviers de valeur.")}</b>',
            'Son parcours révèle deux dimensions complémentaires : <b>l\'analyste financier rigoureux</b> '
            '(LCB-FT, KYC, marchés financiers, analyse bilan) et <b>le communicant pédagogue</b> '
            '(podcast INCLUTECH, Hackathon Fintech). '
            'Son style de leadership qu\'il nomme « <b>leadership de mérite et d\'utilité</b> » '
            'est le fil conducteur de toutes ses expériences.',
        ],
        "tags": ["Trilingue", "Compliance & Finance", "Entrepreneuriat", "Pédagogie", "Impact"],
    },
]

PLATFORMS = [
    {"icon":"💼","name":"LinkedIn","desc":"Profil professionnel — réseau finance/compliance parisien.","url":"https://www.linkedin.com/in/mackenson-cineus","label":"LinkedIn →"},
    {"icon":"💳","name":"HiPay","desc":"Fintech paiement omnicanal agréée ACPR — 2024–2025.","url":"https://hipay.com","label":"HiPay →"},
    {"icon":"🏦","name":"Banque Delubac","desc":"Banque indépendante — Analyste LCB-FT 2025.","url":"https://www.delubac.com","label":"Delubac →"},
    {"icon":"🏆","name":"Hult Prize","desc":"Représentant Haïti 2018 · projet WEISS.","url":"https://www.hultprize.org","label":"Hult Prize →"},
    {"icon":"🎓","name":"ESLSCA Paris","desc":"MBA 2 Finance de marché 2024–2026.","url":"https://www.eslsca.fr","label":"ESLSCA →"},
    {"icon":"🏫","name":"Université du Mans","desc":"Licence BFA 2019–2021.","url":"https://www.univ-lemans.fr","label":"Univ. du Mans →"},
    {"icon":"🎙","name":"Podcast INCLUTECH","desc":"Finance & Inclusion · Spotify & Apple.","url":"https://open.spotify.com/show/5XvFdWYwhHWY3EguIhhf69","label":"Écouter →"},
    {"icon":"📸","name":"Instagram","desc":"@mackenson_cineus","url":"https://instagram.com/mackenson_cineus","label":"Instagram →"},
]

REGULATORS = [
    ("🇫🇷","ACPR","Régulateur bancaire & paiement · LCB-FT","https://acpr.banque-france.fr"),
    ("🌐","FATF / GAFI","Normes mondiales anti-blanchiment","https://www.fatf-gafi.org"),
    ("💰","Tracfin","Cellule de Renseignement Financier","https://www.economie.gouv.fr/tracfin"),
    ("📊","AMF","Autorité des Marchés Financiers","https://www.amf-france.org"),
]

# ── SANCTIONS DATA ─────────────────────────────────────────────────────────────
SANCTIONS_DATA = [
    {
        "date": "2023",
        "entite": "Société Générale",
        "pays": "🇫🇷 France",
        "autorite": "ACPR",
        "montant": "3 000 000 €",
        "montant_raw": 3000000,
        "motif": "Défaillances dans le dispositif LCB-FT : insuffisances dans la surveillance des transactions, lacunes dans les procédures KYC et la détection des PPE.",
        "type": "LCB-FT / KYC",
        "gravite": "Majeure",
    },
    {
        "date": "2023",
        "entite": "Binance",
        "pays": "🇺🇸 USA / International",
        "autorite": "FinCEN / DOJ",
        "montant": "4 300 000 000 $",
        "montant_raw": 4300000000,
        "motif": "Violations massives des règles LCB-FT : absence de programme AML, transactions suspectes non déclarées, facilitation de blanchiment via crypto-actifs.",
        "type": "AML / Crypto",
        "gravite": "Critique",
    },
    {
        "date": "2022",
        "entite": "BNP Paribas",
        "pays": "🇫🇷 France",
        "autorite": "ACPR",
        "montant": "1 300 000 €",
        "montant_raw": 1300000,
        "motif": "Manquements aux obligations de vigilance LCB-FT sur certaines catégories de clientèle et insuffisances dans le contrôle des opérations.",
        "type": "LCB-FT / Vigilance",
        "gravite": "Significative",
    },
    {
        "date": "2022",
        "entite": "Deutsche Bank",
        "pays": "🇩🇪 Allemagne / 🇺🇸 USA",
        "autorite": "FED / BaFin",
        "montant": "186 000 000 $",
        "montant_raw": 186000000,
        "motif": "Insuffisances dans les contrôles AML, défaillances du dispositif de surveillance des transactions et lacunes dans le reporting Tracfin/FinCEN.",
        "type": "AML / Reporting",
        "gravite": "Majeure",
    },
    {
        "date": "2023",
        "entite": "Crédit Agricole",
        "pays": "🇫🇷 France",
        "autorite": "ACPR",
        "montant": "800 000 €",
        "montant_raw": 800000,
        "motif": "Manquements dans la mise à jour des dossiers KYC, insuffisances dans l'identification des bénéficiaires effectifs et le contrôle des PPE.",
        "type": "KYC / PPE",
        "gravite": "Modérée",
    },
    {
        "date": "2023",
        "entite": "Revolut",
        "pays": "🇬🇧 Royaume-Uni",
        "autorite": "FCA",
        "montant": "Avertissement public",
        "montant_raw": 0,
        "motif": "Lacunes dans le programme AML, insuffisances dans la détection des transactions suspectes et dans la gestion des alertes LCB-FT.",
        "type": "AML / Fintech",
        "gravite": "Modérée",
    },
    {
        "date": "2022",
        "entite": "Western Union",
        "pays": "🇺🇸 USA",
        "autorite": "FinCEN / DOJ",
        "montant": "400 000 000 $",
        "montant_raw": 400000000,
        "motif": "Manquements systémiques dans le programme AML, complicité involontaire de fraudes et blanchiment via le réseau de transferts internationaux.",
        "type": "AML / Fraude",
        "gravite": "Critique",
    },
    {
        "date": "2024",
        "entite": "N26",
        "pays": "🇩🇪 Allemagne",
        "autorite": "BaFin",
        "montant": "9 200 000 €",
        "montant_raw": 9200000,
        "motif": "Insuffisances graves dans le dispositif LCB-FT : retards dans les déclarations de soupçon, lacunes KYC, défaillances dans la surveillance des transactions.",
        "type": "LCB-FT / Néobanque",
        "gravite": "Majeure",
    },
    {
        "date": "2024",
        "entite": "Natixis",
        "pays": "🇫🇷 France",
        "autorite": "ACPR",
        "montant": "1 500 000 €",
        "montant_raw": 1500000,
        "motif": "Manquements dans le dispositif de surveillance LCB-FT, insuffisances dans les procédures de gel des avoirs et contrôle des listes de sanctions.",
        "type": "Sanctions / Gel avoirs",
        "gravite": "Significative",
    },
    {
        "date": "2024",
        "entite": "Worldline",
        "pays": "🇫🇷 France / 🇧🇪 Belgique",
        "autorite": "ACPR / NBB",
        "montant": "2 400 000 €",
        "montant_raw": 2400000,
        "motif": "Défaillances dans les procédures KYC des marchands, insuffisances dans la détection des transactions suspectes sur la plateforme de paiement.",
        "type": "KYC / Paiement",
        "gravite": "Significative",
    },
    {
        "date": "2023",
        "entite": "Coinbase",
        "pays": "🇺🇸 USA",
        "autorite": "NYDFS / FinCEN",
        "montant": "100 000 000 $",
        "montant_raw": 100000000,
        "motif": "Grave backlog KYC (100 000+ dossiers non traités), défaillances dans le programme AML et insuffisances dans la surveillance des transactions crypto.",
        "type": "AML / Crypto / KYC",
        "gravite": "Critique",
    },
    {
        "date": "2022",
        "entite": "Caisse d'Épargne CEPAC",
        "pays": "🇫🇷 France",
        "autorite": "ACPR",
        "montant": "600 000 €",
        "montant_raw": 600000,
        "motif": "Insuffisances dans le dispositif LCB-FT, manquements dans la détection et déclaration des opérations atypiques, lacunes KYC sur clientèle sensible.",
        "type": "LCB-FT / KYC",
        "gravite": "Modérée",
    },
]

# ─── PDF COLOR CONSTANTS ───────────────────────────────────────────────────────
NAVY_C   = rl_colors.HexColor('#0D1B2A')
GOLD_C   = rl_colors.HexColor('#C9A84C')
GRAY_D_C = rl_colors.HexColor('#333333')
GRAY_L_C = rl_colors.HexColor('#999999')
CREAM_C  = rl_colors.HexColor('#F8F6F2')
NAVY_M_C = rl_colors.HexColor('#1A2E42')

def _s(name, **kw):
    d = dict(fontName='Helvetica', fontSize=9, textColor=GRAY_D_C, leading=13, spaceAfter=3)
    d.update(kw)
    return ParagraphStyle(name, **d)

def _hr(color=GOLD_C, t=1.0, before=2, after=5):
    return HRFlowable(width="100%", thickness=t, color=color, spaceBefore=before, spaceAfter=after)

def _page_frame(canvas, doc):
    W, H = A4
    canvas.saveState()
    canvas.setFillColor(NAVY_C); canvas.rect(0, H-1.4*cm, W, 1.4*cm, fill=1, stroke=0)
    canvas.setFillColor(GOLD_C); canvas.rect(0, H-1.4*cm, W, 0.08*cm, fill=1, stroke=0)
    canvas.setFillColor(rl_colors.white); canvas.setFont("Helvetica-Bold", 8.5)
    canvas.drawString(1.6*cm, H-0.9*cm, "CINÉUS Mackenson")
    canvas.setFillColor(GOLD_C); canvas.setFont("Helvetica", 7)
    canvas.drawString(5.4*cm, H-0.9*cm, "Finance · Compliance · Fintech · Paris")
    canvas.setFillColor(NAVY_C); canvas.rect(0, 0, W, 0.75*cm, fill=1, stroke=0)
    canvas.setFillColor(GOLD_C); canvas.rect(0, 0.75*cm, W, 0.06*cm, fill=1, stroke=0)
    canvas.setFillColor(rl_colors.HexColor('#888888')); canvas.setFont("Helvetica", 6.5)
    canvas.drawString(1.6*cm, 0.27*cm, "linkedin.com/in/mackenson-cineus  ·  Podcast INCLUTECH")
    canvas.setFillColor(GOLD_C)
    canvas.drawRightString(W-1.6*cm, 0.27*cm, f"Page {doc.page}")
    canvas.restoreState()

# ═══════════════════════════════════════════════════════════════════════════════
# CV PDF — 1 PAGE PLEINE
# ═══════════════════════════════════════════════════════════════════════════════
def generate_cv_pdf(poste="", entreprise="", secteur="") -> bytes:
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.pdfbase.pdfmetrics import stringWidth

    buf = io.BytesIO()
    W, H = A4

    ss     = st.session_state
    name   = ss.get("edit_name",    "Mackenson CINÉUS")
    title_p= ss.get("edit_title",   "Analyste LCB-FT | Compliance Officer")
    loc    = ss.get("edit_location","Île-de-France, France")
    email  = ss.get("edit_email",   "mackenson.cineus@email.com")
    phone  = ss.get("edit_phone",   "+33 6 XX XX XX XX")
    lk     = ss.get("edit_linkedin","linkedin.com/in/mackenson-cineus")
    exps   = ss.get("edit_exp",     [])
    edus   = ss.get("edit_edu",     [])
    certifs= ss.get("edit_certifs", [])
    tech   = ss.get("edit_tech",    "Excel avancé – VBA – Python – Bloomberg – Looker – Jura")
    ints   = ss.get("edit_interests","Sécurité financière – Modèles financiers – Trading NASDAQ – Fintech")
    dists  = ss.get("edit_distinctions", [])
    memoir = ss.get("edit_memoir_title", "Impact of ESG and Non-ESG Regulation on Portfolio Performance in Terms of Risk and Return")
    target = poste if poste else title_p

    ML = 42; MR = 42; MT = 36; MB = 24
    TW = W - ML - MR

    BLACK = (0.0, 0.0, 0.0)
    DGRAY = (0.18, 0.18, 0.18)
    MGRAY = (0.40, 0.40, 0.40)
    LGRAY = (0.60, 0.60, 0.60)
    VGRAY = (0.82, 0.82, 0.82)

    c = rl_canvas.Canvas(buf, pagesize=A4)

    def sw(s, fn, fs): return stringWidth(str(s), fn, fs)
    def setf(*rgb): c.setFillColorRGB(*rgb)
    def sets(*rgb): c.setStrokeColorRGB(*rgb)
    def f(fn, fs): c.setFont(fn, fs)

    def line_h(y, x1=None, x2=None, width=0.5, color=BLACK):
        if x1 is None: x1 = ML
        if x2 is None: x2 = ML + TW
        sets(*color); c.setLineWidth(width)
        c.line(x1, y, x2, y)

    def wrap(txt, x, y, mw, fn, fs, lh, col=BLACK, indent=0):
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

    def section(label, y, space_before=5):
        y -= space_before
        f("Times-Bold", 9.5); setf(*BLACK)
        c.drawString(ML, y, label.upper())
        y -= 3
        sets(*BLACK); c.setLineWidth(1.1)
        c.line(ML, y, ML + TW, y)
        return y - 8

    def bullet(txt, y, x=ML, mw=None, fs=8.6, lh=10.2, col=DGRAY):
        if mw is None: mw = TW
        f("Times-Roman", fs); setf(*col)
        c.drawString(x + 8, y, "•")
        return wrap(txt, x + 19, y, mw - 19, "Times-Roman", fs, lh, col)

    # ── EN-TÊTE ────────────────────────────────────────────────────
    y = H - MT

    f("Times-Bold", 21); setf(*BLACK)
    name_up = name.upper()
    c.drawString((W - sw(name_up, "Times-Bold", 21)) / 2, y, name_up)
    y -= 14

    f("Times-Italic", 9.8); setf(*DGRAY)
    c.drawString((W - sw(target, "Times-Italic", 9.8)) / 2, y, target)
    y -= 12

    line_h(y, color=MGRAY, width=0.4); y -= 8

    f("Times-Roman", 8.3); setf(*MGRAY)
    line1 = f"{loc}  ·  {phone}  ·  {email}"
    line2 = f"{lk}  ·  Podcast INCLUTECH (Spotify & Apple Podcasts)"
    c.drawString((W - sw(line1, "Times-Roman", 8.3)) / 2, y, line1); y -= 9
    c.drawString((W - sw(line2, "Times-Roman", 8.3)) / 2, y, line2); y -= 9

    line_h(y, color=BLACK, width=0.9); y -= 1.5
    line_h(y, color=BLACK, width=0.3); y -= 7

    # ── PROFIL ────────────────────────────────────────────────────
    y = section("Profil", y, space_before=2)
    profil = (
        "Analyste LCB-FT en alternance (Banque Delubac & Cie, depuis 2025) — clientèle corporate, CIB, "
        "asset management, banque privée, PSP. Précédente expérience de Chargé de Conformité en fintech "
        "de paiement agréée ACPR (HiPay SAS, 2024–2025) : risques pays GAFI, KYC/PPE/SOE, pays sensibles, "
        "Tracfin, Due Diligence. MBA 2 Finance de marché en cours (ESLSCA Paris). "
        "Lauréat 1er Prix Hackathon Fintech Générations 2023 — France FinTech / Société Générale. "
        "Mémoire (80 p., anglais) : « " + memoir[:72] + ("…" if len(memoir) > 72 else "") + " ». "
        "Trilingue : français · anglais · créole haïtien."
    )
    y = wrap(profil, ML, y, TW, "Times-Roman", 8.6, 11.2, DGRAY); y -= 3

    # ── EXPÉRIENCES ────────────────────────────────────────────────
    y = section("Expériences Professionnelles", y)

    # Only finance/compliance-related experiences
    PRO_TYPES = {"Banque", "Fintech", "Compétition"}
    pro_exps = [e for e in exps if e.get("org_type", "") in PRO_TYPES][:4]

    for idx_e, exp in enumerate(pro_exps):
        if y < MB + 50: break

        org_raw   = exp.get("org", "")
        org_parts = org_raw.split("·")
        org_name  = org_parts[0].strip()
        org_loc   = org_parts[-1].strip() if len(org_parts) > 1 else "France"
        role      = exp.get("role", "")
        period    = exp.get("period", "")

        # Row 1: Org bold left | Location right
        f("Times-Bold", 9.3); setf(*BLACK)
        c.drawString(ML, y, org_name)
        f("Times-Roman", 8.3); setf(*LGRAY)
        c.drawRightString(ML + TW, y, org_loc)
        y -= 11

        # Row 2: Role italic | Period right — on SAME line, then separator below
        f("Times-BoldItalic", 8.8); setf(*DGRAY)
        c.drawString(ML, y, role)
        f("Times-Italic", 8.3); setf(*LGRAY)
        c.drawRightString(ML + TW, y, period)
        y -= 3
        # thin rule under role line, clearly separating header from bullets
        line_h(y, x1=ML, x2=ML + TW, width=0.25, color=VGRAY)
        y -= 7

        for b in exp.get("bullets", [])[:5]:
            if y < MB + 28: break
            y = bullet(b, y, fs=8.5, lh=10.2)

        y -= 4
        if idx_e < len(pro_exps) - 1:
            line_h(y, color=VGRAY, width=0.3); y -= 5

    # ── MÉMOIRE ────────────────────────────────────────────────────
    if y > MB + 68:
        y = section("Mémoire de Fin d'Études", y)
        f("Times-BoldItalic", 8.8); setf(*BLACK)
        lbl = "Titre : "
        c.drawString(ML, y, lbl)
        lbl_w = sw(lbl, "Times-BoldItalic", 8.8)
        f("Times-Italic", 8.8); setf(*DGRAY)
        memoir_full = f"« {memoir} »"
        y = wrap(memoir_full, ML + lbl_w, y, TW - lbl_w, "Times-Italic", 8.8, 10.8, DGRAY)
        f("Times-Roman", 8.3); setf(*MGRAY)
        c.drawString(ML, y, "Mémoire de 80 pages · Rédigé en anglais · MBA 2 Finance de marché · ESLSCA Business School Paris")
        y -= 10
        c.drawString(ML, y, "Thématique : Performance des portefeuilles sous contrainte réglementaire ESG/non-ESG — risque & rendement")
        y -= 10

    # ── FORMATIONS ─────────────────────────────────────────────────
    if y > MB + 62:
        y = section("Formations", y)

        formations = []
        ss_edus = [e for e in edus if "INAGHEI" not in e.get("school","")]
        for e in ss_edus[:2]:
            s_parts = e.get("school","").split("·")
            formations.append({
                "deg":    e.get("deg",""),
                "school": s_parts[0].strip(),
                "loc":    s_parts[-1].strip() if len(s_parts)>1 else "France",
                "yr":     e.get("yr",""),
                "cours":  e.get("det",""),
            })

        for idx_f, fm in enumerate(formations):
            if y < MB + 36: break

            f("Times-Bold", 9.3); setf(*BLACK)
            c.drawString(ML, y, fm["school"] + "  —  " + fm["deg"])
            f("Times-Roman", 8.3); setf(*LGRAY)
            c.drawRightString(ML + TW, y, fm["loc"])
            y -= 11

            f("Times-Italic", 8.3); setf(*LGRAY)
            c.drawRightString(ML + TW, y, fm["yr"])
            cours_lbl = "Cours : "
            f("Times-Roman", 8.5); setf(*BLACK)
            c.drawString(ML, y, cours_lbl)
            clbl_w = sw(cours_lbl, "Times-Roman", 8.5)
            sets(*BLACK); c.setLineWidth(0.22)
            c.line(ML, y - 1, ML + clbl_w, y - 1)
            f("Times-Roman", 8.5); setf(*MGRAY)
            y = wrap(fm["cours"], ML + clbl_w, y, TW - clbl_w, "Times-Roman", 8.5, 10.8, MGRAY)
            y -= 5

    # ── CERTIFICATIONS / COMPÉTENCES / LANGUES / RÉCOMPENSES ───────
    if y > MB + 4:
        y = section("Certifications, Compétences, Langues & Récompenses", y)

        certif_str = " – ".join(certifs) if certifs else "AMF – CFA Level 1 (candidat) – CAMS (en cours)"
        dist_str   = " | ".join(f"{ic} {t}" for ic, t, _ in dists[:3])

        rows = [
            ("Certifications en cours", f": {certif_str}"),
            ("Outils & Informatique",   f": {tech}"),
            ("Langues",                 ": Français (Natif C1) – Créole haïtien (Natif) – Anglais (Avancé)"),
            ("Intérêts",                f": {ints}"),
            ("Distinctions",            f": {dist_str}"),
        ]

        for lbl, val in rows:
            if y < MB + 2: break
            f("Times-Bold", 8.6); setf(*BLACK)
            lbl_w = sw(lbl, "Times-Bold", 8.6)
            c.drawString(ML + 5, y, lbl)
            sets(*BLACK); c.setLineWidth(0.22)
            c.line(ML + 5, y - 1, ML + 5 + lbl_w, y - 1)
            f("Times-Roman", 8.6); setf(*MGRAY)
            y = wrap(val, ML + 5 + lbl_w, y, TW - 5 - lbl_w, "Times-Roman", 8.6, 10.5, MGRAY)

    # ── FOOTER ─────────────────────────────────────────────────────
    sets(*VGRAY); c.setLineWidth(0.3)
    c.line(ML, MB + 4, ML + TW, MB + 4)
    f("Helvetica", 5.8); setf(*LGRAY)
    footer = f"{name}  ·  {email}  ·  {lk}"
    c.drawString((W - sw(footer, "Helvetica", 5.8)) / 2, MB - 4, footer)

    c.save(); buf.seek(0); return buf.read()


# ═══════════════════════════════════════════════════════════════════════════════
# CV WORD
# ═══════════════════════════════════════════════════════════════════════════════
def generate_cv_docx(poste="", entreprise="", secteur="") -> bytes:
    ss     = st.session_state
    name   = ss.get("edit_name",    "Mackenson CINÉUS")
    title_p= ss.get("edit_title",   "Analyste LCB-FT | Compliance Officer")
    loc    = ss.get("edit_location","Île-de-France, France")
    email  = ss.get("edit_email",   "mackenson.cineus@email.com")
    phone  = ss.get("edit_phone",   "+33 6 XX XX XX XX")
    lk     = ss.get("edit_linkedin","linkedin.com/in/mackenson-cineus")
    exps   = ss.get("edit_exp",     [])
    edus   = ss.get("edit_edu",     [])
    certifs= ss.get("edit_certifs", [])
    tech   = ss.get("edit_tech",    "Excel avancé – VBA – Python – Bloomberg")
    ints   = ss.get("edit_interests","Sécurité financière – Trading – Fintech")
    dists  = ss.get("edit_distinctions", [])
    memoir = ss.get("edit_memoir_title", "Impact of ESG and Non-ESG Regulation on Portfolio Performance")
    target = poste if poste else title_p

    doc = Document()

    # ── Margins ──
    for section in doc.sections:
        section.top_margin    = Cm(1.5)
        section.bottom_margin = Cm(1.5)
        section.left_margin   = Cm(2.0)
        section.right_margin  = Cm(2.0)

    def add_heading(text, size=22, bold=True, center=True, color=None):
        p = doc.add_paragraph()
        if center: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.bold = bold
        run.font.size = Pt(size)
        if color:
            run.font.color.rgb = RGBColor(*color)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(0)
        return p

    def add_section_title(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after  = Pt(1)
        run = p.add_run(text.upper())
        run.bold = True
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(0, 0, 0)
        # Bottom border
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '12')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), '000000')
        pBdr.append(bottom)
        pPr.append(pBdr)
        return p

    def add_exp_row(left, right, left_bold=True, left_size=10, right_size=9, left_italic=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after  = Pt(1)
        run_l = p.add_run(left)
        run_l.bold = left_bold
        run_l.italic = left_italic
        run_l.font.size = Pt(left_size)
        run_l.font.color.rgb = RGBColor(30, 30, 30)
        # Tab stop for right alignment
        tab_stops = p.paragraph_format.tab_stops
        from docx.oxml import OxmlElement as OE
        from docx.oxml.ns import qn as Q
        pPr = p._p.get_or_add_pPr()
        tabs = OE('w:tabs')
        tab = OE('w:tab')
        tab.set(Q('w:val'), 'right')
        tab.set(Q('w:pos'), '9070')  # ~16cm
        tabs.append(tab)
        pPr.append(tabs)
        run_tab = p.add_run('\t')
        run_r = p.add_run(right)
        run_r.italic = True
        run_r.font.size = Pt(right_size)
        run_r.font.color.rgb = RGBColor(120, 120, 120)
        return p

    def add_bullet_item(text, size=9.5):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.left_indent    = Cm(0.5)
        p.paragraph_format.space_before   = Pt(0)
        p.paragraph_format.space_after    = Pt(1)
        run = p.add_run(text)
        run.font.size = Pt(size)
        run.font.color.rgb = RGBColor(50, 50, 50)
        return p

    def add_separator():
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after  = Pt(1)
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '4')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), 'CCCCCC')
        pBdr.append(bottom)
        pPr.append(pBdr)

    # ── NAME ──
    add_heading(name.upper(), 20, color=(0,0,0))
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_title.add_run(target)
    r.italic = True; r.font.size = Pt(11)
    r.font.color.rgb = RGBColor(60, 60, 60)
    p_title.paragraph_format.space_after = Pt(2)

    p_coords = doc.add_paragraph()
    p_coords.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p_coords.add_run(f"{loc}  ·  {phone}  ·  {email}")
    r2.font.size = Pt(8.5); r2.font.color.rgb = RGBColor(100,100,100)
    p_coords.paragraph_format.space_after = Pt(1)

    p_coords2 = doc.add_paragraph()
    p_coords2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r3 = p_coords2.add_run(f"{lk}  ·  Podcast INCLUTECH")
    r3.font.size = Pt(8.5); r3.font.color.rgb = RGBColor(100,100,100)
    p_coords2.paragraph_format.space_after = Pt(4)

    # ── PROFIL ──
    add_section_title("Profil")
    p_profil = doc.add_paragraph()
    p_profil.paragraph_format.space_after = Pt(3)
    run_profil = p_profil.add_run(
        f"Analyste LCB-FT en alternance (Banque Delubac & Cie) sur clientèle corporate, CIB, asset management, PSP. "
        f"Expérience de Chargé de Conformité en fintech de paiement agréée ACPR (HiPay SAS) : risques pays GAFI, "
        f"KYC/PPE/SOE, pays sensibles, Tracfin, Due Diligence. MBA 2 Finance de marché (ESLSCA Paris). "
        f"Lauréat 1er Prix Hackathon Fintech Générations 2023. Trilingue."
    )
    run_profil.font.size = Pt(9.5)
    run_profil.font.color.rgb = RGBColor(40,40,40)

    # ── EXPÉRIENCES ──
    add_section_title("Expériences Professionnelles")
    PRO_TYPES = {"Banque", "Fintech", "Compétition"}
    pro_exps = [e for e in exps if e.get("org_type","") in PRO_TYPES][:4]

    for idx_e, exp in enumerate(pro_exps):
        org_raw   = exp.get("org","")
        org_parts = org_raw.split("·")
        org_name  = org_parts[0].strip()
        org_loc   = org_parts[-1].strip() if len(org_parts) > 1 else "France"

        add_exp_row(org_name, org_loc, left_bold=True, left_size=10)
        add_exp_row(exp.get("role",""), exp.get("period",""), left_bold=False, left_italic=True, left_size=9.5)

        for b in exp.get("bullets",[])[:5]:
            add_bullet_item(b)

        if idx_e < len(pro_exps) - 1:
            add_separator()

    # ── MÉMOIRE ──
    add_section_title("Mémoire de Fin d'Études")
    pm = doc.add_paragraph()
    pm.paragraph_format.space_after = Pt(1)
    r_ml = pm.add_run("Titre : ")
    r_ml.bold = True; r_ml.font.size = Pt(9.5)
    r_mv = pm.add_run(f"« {memoir} »")
    r_mv.italic = True; r_mv.font.size = Pt(9.5)
    r_mv.font.color.rgb = RGBColor(50,50,50)
    pm2 = doc.add_paragraph()
    pm2.paragraph_format.space_after = Pt(3)
    r_pm2 = pm2.add_run("80 pages · Rédigé en anglais · MBA 2 Finance de marché · ESLSCA Paris — Performance des portefeuilles sous contrainte réglementaire ESG/non-ESG")
    r_pm2.font.size = Pt(8.8); r_pm2.font.color.rgb = RGBColor(100,100,100)

    # ── FORMATIONS ──
    add_section_title("Formations")
    ss_edus = [e for e in edus if "INAGHEI" not in e.get("school","")]
    for e in ss_edus[:2]:
        s_parts = e.get("school","").split("·")
        school = s_parts[0].strip()
        loc_e  = s_parts[-1].strip() if len(s_parts)>1 else "France"
        add_exp_row(f"{school}  —  {e.get('deg','')}", loc_e, left_bold=True, left_size=10)
        pc = doc.add_paragraph()
        pc.paragraph_format.space_after = Pt(2)
        r_yr = pc.add_run(f"{e.get('yr','')}  |  ")
        r_yr.font.size = Pt(8.5); r_yr.font.color.rgb = RGBColor(120,120,120)
        r_det = pc.add_run(e.get("det",""))
        r_det.font.size = Pt(8.5); r_det.font.color.rgb = RGBColor(80,80,80)

    # ── CERTIFICATIONS ETC. ──
    add_section_title("Certifications, Compétences, Langues & Distinctions")
    certif_str = " – ".join(certifs) if certifs else "AMF – CFA Level 1 (candidat) – CAMS (en cours)"
    dist_str   = " | ".join(f"{ic} {t}" for ic, t, _ in dists[:3])
    rows_doc = [
        ("Certifications en cours", certif_str),
        ("Outils & Informatique", tech),
        ("Langues", "Français (Natif C1) – Créole haïtien (Natif) – Anglais (Avancé)"),
        ("Intérêts", ints),
        ("Distinctions", dist_str),
    ]
    for lbl, val in rows_doc:
        p_row = doc.add_paragraph()
        p_row.paragraph_format.space_after = Pt(1)
        rl = p_row.add_run(f"{lbl} : ")
        rl.bold = True; rl.font.size = Pt(9.5)
        rv = p_row.add_run(val)
        rv.font.size = Pt(9.5); rv.font.color.rgb = RGBColor(60,60,60)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()


# ═══════════════════════════════════════════════════════════════════════════════
# LETTRE DE MOTIVATION PDF
# ═══════════════════════════════════════════════════════════════════════════════
def generate_lettre_pdf(poste="", entreprise="", secteur="", style_lm="", contexte="", ai_text="") -> bytes:
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.pdfbase.pdfmetrics import stringWidth

    buf = io.BytesIO()
    W, H = A4

    ss     = st.session_state
    name   = ss.get("edit_name",    "Mackenson CINÉUS")
    title  = ss.get("edit_title",   "Analyste LCB-FT | Compliance Officer")
    loc    = ss.get("edit_location","Île-de-France, France")
    email  = ss.get("edit_email",   "mackenson.cineus@email.com")
    phone  = ss.get("edit_phone",   "+33 6 XX XX XX XX")
    lk     = ss.get("edit_linkedin","linkedin.com/in/mackenson-cineus")
    memoir = ss.get("edit_memoir_title","Impact of ESG and Non-ESG Regulation on Portfolio Performance")
    target = poste or "Analyste LCB-FT / Compliance Officer"
    ent    = entreprise or "[Nom de l'établissement]"
    sect   = secteur or "Finance / Conformité"

    ML, MR, MT, MB = 50, 50, 42, 30
    TW = W - ML - MR

    BLACK = (0.0, 0.0, 0.0)
    DGRAY = (0.20, 0.20, 0.20)
    MGRAY = (0.42, 0.42, 0.42)
    LGRAY = (0.62, 0.62, 0.62)
    VGRAY = (0.82, 0.82, 0.82)

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

    y = H - MT

    # Header
    f("Times-Bold", 14); setf(*BLACK)
    nw = sw(name.upper(), "Times-Bold", 14)
    c.drawString((W - nw) / 2, y, name.upper()); y -= 14
    f("Times-Italic", 9.5); setf(*DGRAY)
    tw_ = sw(title, "Times-Italic", 9.5)
    c.drawString((W - tw_) / 2, y, title); y -= 11
    f("Times-Roman", 8.8); setf(*MGRAY)
    l1 = f"{loc}  ·  {phone}  ·  {email}"
    l2 = f"{lk}  ·  Podcast INCLUTECH"
    c.drawString((W - sw(l1,"Times-Roman",8.8)) / 2, y, l1); y -= 10
    c.drawString((W - sw(l2,"Times-Roman",8.8)) / 2, y, l2); y -= 10
    line_h(y, col=BLACK, w=0.8); y -= 2
    line_h(y, col=VGRAY, w=0.3); y -= 14

    # Destinataire + date
    f("Times-Roman", 9.5); setf(*BLACK)
    c.drawString(ML, y, "Direction des Ressources Humaines")
    f("Times-Italic", 9); setf(*MGRAY)
    c.drawRightString(ML + TW, y, "Paris, le 28 mars 2026")
    y -= 11
    f("Times-Bold", 9.5); setf(*BLACK)
    c.drawString(ML, y, ent); y -= 11
    f("Times-Roman", 9); setf(*DGRAY)
    c.drawString(ML, y, sect); y -= 16

    # Objet
    f("Times-Bold", 9.5); setf(*BLACK)
    obj_lbl = "Objet : "
    c.drawString(ML, y, obj_lbl)
    f("Times-Roman", 9.5)
    c.drawString(ML + sw(obj_lbl,"Times-Bold",9.5), y, f"Candidature — {target}")
    y -= 11
    f("Times-Bold", 9.5)
    ref_lbl = "Réf.   : "
    c.drawString(ML, y, ref_lbl)
    f("Times-Roman", 9); setf(*DGRAY)
    c.drawString(ML + sw(ref_lbl,"Times-Bold",9.5), y, "Profil LCB-FT/AML — alternance MBA 2 Finance de marché (ESLSCA Paris)")
    y -= 14
    line_h(y, col=BLACK, w=0.6); y -= 14
    f("Times-Roman", 9.8); setf(*BLACK)
    c.drawString(ML, y, "Madame, Monsieur,"); y -= 16

    LH = 13.5; FS = 9.8; IND = 18

    if ai_text and len(ai_text) > 200:
        for p_txt in ai_text.split("\n\n"):
            if p_txt.strip() and y > MB + 20:
                y = wrap(p_txt.strip(), ML, y, TW, "Times-Roman", FS, LH, DGRAY, IND)
                y -= 9
    else:
        p1 = (
            f"Actuellement en alternance comme Analyste LCB-FT à la Banque Delubac & Cie, "
            f"où j'interviens sur la clientèle corporate, CIB, asset management, banque privée et PSP, "
            f"et fort d'une première expérience de Chargé de Conformité chez HiPay SAS — fintech de "
            f"paiement agréée ACPR —, je me permets de vous adresser ma candidature au poste de "
            f"{target} au sein de {ent}. Préparant un MBA 2 Finance de marché à l'ESLSCA Business School "
            f"Paris en parallèle de mon alternance, je combine une double expertise opérationnelle en "
            f"conformité bancaire et fintech directement mobilisable dans le cadre de vos enjeux réglementaires."
        )
        y = wrap(p1, ML, y, TW, "Times-Roman", FS, LH, DGRAY, IND); y -= 9

        p2 = (
            "Mes deux expériences en conformité m'ont permis d'acquérir une maîtrise opérationnelle complète "
            "des processus AML/FT : chez Delubac, je traite quotidiennement les alertes de niveau 1 LCB-FT, "
            "les Examens Renforcés (ER), les Profils à Détecter Supplémentaires (PDS) et rédige des avis sur "
            "opérations ; je réalise les analyses KYC, identifie les bénéficiaires effectifs, contrôle la "
            "cohérence économique des transactions et prépare les déclarations de soupçon (DS). "
            "Chez HiPay, j'ai analysé les risques pays GAFI sur des pays sensibles et complexes incluant "
            "des pays sous sanctions, réalisé des analyses KYC/PPE/PE/SOE, traité les réquisitions Tracfin "
            "et conduit des Due Diligence sur des établissements financiers systémiques et RFI. "
            "Cette double expérience banque–fintech me confère une vision transversale rare de la conformité LCB-FT, "
            "illustrée par le traitement de 205 analyses représentant 24 892 285,50 € examinés à ce jour."
        )
        y = wrap(p2, ML, y, TW, "Times-Roman", FS, LH, DGRAY, IND); y -= 9

        p3 = (
            "Au-delà de la maîtrise réglementaire, je mets à votre disposition une dimension analytique "
            "renforcée par ma formation en finance de marché : mon mémoire de recherche de 80 pages, "
            f"intitulé « {memoir[:65]}{'…' if len(memoir)>65 else ''} », témoigne de ma capacité à traiter "
            "des problématiques complexes à l'intersection de la réglementation, du risque et de la performance "
            "financière. Lauréat du 1er Prix Hackathon Fintech Générations 2023 (France FinTech / Société Générale), "
            "créateur du podcast INCLUTECH sur l'inclusion financière, j'apporte une vision entrepreneuriale "
            "et pédagogique qui complète la rigueur analytique attendue dans un poste de conformité. "
            "Mes compétences en Excel avancé, VBA, Python, Bloomberg, Looker et Jura me permettent "
            "d'automatiser les tâches d'analyse et d'améliorer l'efficacité des processus de surveillance."
        )
        y = wrap(p3, ML, y, TW, "Times-Roman", FS, LH, DGRAY, IND); y -= 9

        p4 = (
            f"La réputation de {ent} dans le domaine de la conformité financière, la qualité de ses équipes "
            "et son positionnement au cœur des enjeux réglementaires actuels constituent pour moi des arguments "
            "déterminants. Convaincu que la conformité LCB-FT est non seulement une obligation réglementaire "
            "mais un véritable avantage concurrentiel, je souhaite m'investir pleinement dans votre dispositif "
            "de sécurité financière pour contribuer à son renforcement et à son évolution. "
            "Disponible pour un entretien à votre convenance, je reste à votre disposition pour vous présenter "
            "en détail mon parcours. Dans l'attente de votre retour, je vous prie d'agréer, Madame, Monsieur, "
            "l'expression de mes salutations distinguées."
        )
        y = wrap(p4, ML, y, TW, "Times-Roman", FS, LH, DGRAY, IND); y -= 14

    # Signature
    f("Times-Bold", 10.5); setf(*BLACK)
    c.drawString(ML, y, name); y -= 12
    f("Times-Italic", 9); setf(*DGRAY)
    c.drawString(ML, y, title); y -= 10
    f("Times-Roman", 8.8); setf(*MGRAY)
    c.drawString(ML, y, f"{phone}  ·  {email}"); y -= 9
    c.drawString(ML, y, lk)

    # Footer PJ
    sets(*VGRAY); c.setLineWidth(0.3)
    c.line(ML, MB + 8, ML + TW, MB + 8)
    f("Times-Italic", 8.2); setf(*LGRAY)
    pj = "PJ : Curriculum Vitæ  ·  Mémoire disponible sur demande  ·  Podcast INCLUTECH"
    pjw = sw(pj, "Times-Italic", 8.2)
    c.drawString((W - pjw) / 2, MB - 2, pj)

    c.save(); buf.seek(0); return buf.read()


# ═══════════════════════════════════════════════════════════════════════════════
# LETTRE DE MOTIVATION WORD
# ═══════════════════════════════════════════════════════════════════════════════
def generate_lettre_docx(poste="", entreprise="", secteur="", contexte="") -> bytes:
    ss     = st.session_state
    name   = ss.get("edit_name",    "Mackenson CINÉUS")
    title  = ss.get("edit_title",   "Analyste LCB-FT | Compliance Officer")
    loc    = ss.get("edit_location","Île-de-France, France")
    email  = ss.get("edit_email",   "mackenson.cineus@email.com")
    phone  = ss.get("edit_phone",   "+33 6 XX XX XX XX")
    lk     = ss.get("edit_linkedin","linkedin.com/in/mackenson-cineus")
    memoir = ss.get("edit_memoir_title","Impact of ESG and Non-ESG Regulation on Portfolio Performance")
    target = poste or "Analyste LCB-FT / Compliance Officer"
    ent    = entreprise or "[Nom de l'établissement]"
    sect   = secteur or "Finance / Conformité"

    doc = Document()
    for section in doc.sections:
        section.top_margin    = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin   = Cm(2.5)
        section.right_margin  = Cm(2.5)

    def p(text="", bold=False, italic=False, size=11, align=WD_ALIGN_PARAGRAPH.LEFT, color=None, space_after=3):
        para = doc.add_paragraph()
        para.alignment = align
        para.paragraph_format.space_after = Pt(space_after)
        para.paragraph_format.space_before = Pt(0)
        if text:
            run = para.add_run(text)
            run.bold = bold; run.italic = italic
            run.font.size = Pt(size)
            if color: run.font.color.rgb = RGBColor(*color)
        return para

    # Header
    p(name.upper(), bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, color=(0,0,0), space_after=2)
    p(title, italic=True, size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, color=(60,60,60), space_after=2)
    p(f"{loc}  ·  {phone}  ·  {email}", size=9, align=WD_ALIGN_PARAGRAPH.CENTER, color=(100,100,100), space_after=1)
    p(f"{lk}  ·  Podcast INCLUTECH", size=9, align=WD_ALIGN_PARAGRAPH.CENTER, color=(100,100,100), space_after=8)

    # Destinataire + date
    para_dest = doc.add_paragraph()
    para_dest.paragraph_format.space_after = Pt(1)
    r1 = para_dest.add_run("Direction des Ressources Humaines")
    r1.font.size = Pt(10.5)
    # date right — use tab
    from docx.oxml import OxmlElement as OE
    from docx.oxml.ns import qn as Q
    pPr = para_dest._p.get_or_add_pPr()
    tabs = OE('w:tabs')
    tab = OE('w:tab')
    tab.set(Q('w:val'), 'right')
    tab.set(Q('w:pos'), '9070')
    tabs.append(tab)
    pPr.append(tabs)
    r_tab = para_dest.add_run('\t')
    r_date = para_dest.add_run("Paris, le 28 mars 2026")
    r_date.italic = True; r_date.font.size = Pt(10)
    r_date.font.color.rgb = RGBColor(100,100,100)

    p(ent, bold=True, size=10.5, space_after=1)
    p(sect, italic=True, size=10, color=(80,80,80), space_after=6)

    # Objet
    para_obj = doc.add_paragraph()
    para_obj.paragraph_format.space_after = Pt(2)
    r_ol = para_obj.add_run("Objet : ")
    r_ol.bold = True; r_ol.font.size = Pt(10.5)
    r_ov = para_obj.add_run(f"Candidature — {target}")
    r_ov.font.size = Pt(10.5)

    para_ref = doc.add_paragraph()
    para_ref.paragraph_format.space_after = Pt(8)
    r_rl = para_ref.add_run("Réf.   : ")
    r_rl.bold = True; r_rl.font.size = Pt(10)
    r_rv = para_ref.add_run("Profil LCB-FT/AML — alternance MBA 2 Finance de marché (ESLSCA Paris)")
    r_rv.font.size = Pt(10); r_rv.font.color.rgb = RGBColor(80,80,80)

    p("Madame, Monsieur,", size=11, space_after=8)

    paragraphs = [
        (f"Actuellement en alternance comme Analyste LCB-FT à la Banque Delubac & Cie, où j'interviens sur la "
         f"clientèle corporate, CIB, asset management, banque privée et PSP, et fort d'une première expérience de "
         f"Chargé de Conformité chez HiPay SAS — fintech de paiement agréée ACPR —, je me permets de vous adresser "
         f"ma candidature au poste de {target} au sein de {ent}. Préparant un MBA 2 Finance de marché à l'ESLSCA "
         f"Business School Paris en parallèle de mon alternance, je combine une double expertise opérationnelle en "
         f"conformité bancaire et fintech directement mobilisable dans le cadre de vos enjeux réglementaires."),

        ("Mes deux expériences en conformité m'ont permis d'acquérir une maîtrise opérationnelle complète des "
         "processus AML/FT : chez Delubac, je traite quotidiennement les alertes de niveau 1 LCB-FT, les Examens "
         "Renforcés (ER), les Profils à Détecter Supplémentaires (PDS) et rédige des avis sur opérations ; je "
         "réalise les analyses KYC, identifie les bénéficiaires effectifs, contrôle la cohérence économique et "
         "prépare les déclarations de soupçon (DS). Chez HiPay, j'ai analysé les risques pays GAFI sur des pays "
         "sensibles incluant des pays sous sanctions, réalisé des analyses KYC/PPE/PE/SOE et conduit des Due "
         "Diligence sur des établissements financiers systémiques. Cette double expérience banque–fintech me confère "
         "une vision transversale rare, illustrée par le traitement de 205 analyses représentant 24 892 285,50 € examinés."),

        (f"Au-delà de la maîtrise réglementaire, je mets à votre disposition une dimension analytique renforcée "
         f"par ma formation en finance de marché : mon mémoire de recherche de 80 pages, intitulé "
         f"« {memoir[:65]}{'…' if len(memoir)>65 else ''} », témoigne de ma capacité à traiter des problématiques "
         f"complexes à l'intersection de la réglementation, du risque et de la performance financière. "
         f"Lauréat du 1er Prix Hackathon Fintech Générations 2023 (France FinTech / Société Générale) et créateur "
         f"du podcast INCLUTECH sur l'inclusion financière, j'apporte une vision entrepreneuriale et pédagogique "
         f"qui complète la rigueur analytique attendue dans un poste de conformité."),

        (f"La réputation de {ent} dans le domaine de la conformité financière et son positionnement au cœur des "
         f"enjeux réglementaires actuels constituent pour moi des arguments déterminants. Convaincu que la conformité "
         f"LCB-FT est un véritable avantage concurrentiel, je souhaite m'investir pleinement dans votre dispositif "
         f"de sécurité financière. Disponible pour un entretien à votre convenance, je vous prie d'agréer, "
         f"Madame, Monsieur, l'expression de mes salutations distinguées."),
    ]

    for para_text in paragraphs:
        para_p = doc.add_paragraph()
        para_p.paragraph_format.first_line_indent = Cm(0.5)
        para_p.paragraph_format.space_after = Pt(8)
        run_p = para_p.add_run(para_text)
        run_p.font.size = Pt(11)
        run_p.font.color.rgb = RGBColor(30,30,30)

    # Signature
    p("", space_after=4)
    p(name, bold=True, size=11, space_after=1)
    p(title, italic=True, size=10, color=(60,60,60), space_after=1)
    p(f"{phone}  ·  {email}", size=9.5, color=(100,100,100), space_after=1)
    p(lk, size=9.5, color=(100,100,100), space_after=4)
    p("PJ : Curriculum Vitæ  ·  Mémoire disponible sur demande", italic=True, size=9, color=(120,120,120))

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()


# ═══════════════════════════════════════════════════════════════════════════════
# BIOGRAPHIE PDF
# ═══════════════════════════════════════════════════════════════════════════════
def generate_bio_pdf() -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=1.7*cm, rightMargin=1.7*cm,
        topMargin=2.0*cm, bottomMargin=1.4*cm)

    story = []

    t_data = [[
        Paragraph('<font name="Helvetica-Bold" size="24" color="#0D1B2A">CINÉUS</font>  <font name="Helvetica" size="24" color="#0D1B2A">Mackenson</font>',
                  _s('bn', fontSize=24, leading=28, spaceAfter=0)),
        Paragraph('<font color="#C9A84C" size="8">Finance · Compliance · Fintech · Paris</font>',
                  _s('bs', fontSize=8, alignment=TA_RIGHT, spaceAfter=0, textColor=GOLD_C))
    ]]
    story.append(Table(t_data, colWidths=[11.5*cm, 5.3*cm]))
    story.append(_hr(NAVY_C, 2.0, before=3, after=4))

    story.append(Paragraph(
        '<i>"De Port-au-Prince à Levallois-Perret — Analyste LCB-FT en banque privée, '
        'Chargé de Conformité en fintech de paiement, lauréat d\'un hackathon Fintech Générations, '
        'créateur d\'un podcast sur l\'inclusion financière. Un parcours construit avec intention."</i>',
        _s('q', fontSize=8.5, fontName='Helvetica-Oblique', textColor=NAVY_M_C, leading=12.5, leftIndent=6, spaceAfter=8, backColor=CREAM_C)))

    kpis = [
        ("💳","HiPay","Compliance Officer\n2024–2025"),
        ("🏦","Delubac","Analyste LCB-FT\n2025–Présent"),
        ("🥇","Hackathon 2023","1er Prix · Victoria\nFrance FinTech"),
        ("🎙","INCLUTECH","Podcast Finance\nSpotify & Apple"),
        ("📈","MBA ESLSCA","Finance de marché\n2024–2026"),
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
        ('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[CREAM_C]),
        ('LINEAFTER',(0,0),(3,-1),0.3,GRAY_L_C),
    ]))
    story.append(kpi_t)
    story.append(Spacer(1, 6))

    def phase_block(label, title, color_hex, paras_html, sources):
        src_parts = []
        for name_s, url_s in sources:
            src_parts.append(f'<font color="#4A9EFF"><u>{name_s}</u></font> <font size="6" color="#888888">({url_s})</font>')
        src_line = "  ·  ".join(src_parts)
        body_paras = []
        for txt in paras_html:
            body_paras.append(Paragraph(txt, _s('pb', fontSize=8.2, leading=12.5, alignment=TA_JUSTIFY, spaceAfter=4)))
        if src_line:
            body_paras.append(Paragraph(f'<font size="6.5" color="#888888"><i>Sources : {src_line}</i></font>', _s('src', fontSize=6.5, spaceAfter=0)))
        header = Table([["", Paragraph(
            f'<font color="{color_hex}" size="6.5"><b>{label.upper()}</b></font><br/>'
            f'<font size="10" color="#0D1B2A"><b>{title}</b></font>',
            _s('ph', fontSize=10, leading=13.5, spaceAfter=0))]], colWidths=[0.22*cm, 16.3*cm])
        header.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(0,-1),rl_colors.HexColor(color_hex)),
            ('BACKGROUND',(1,0),(1,-1),CREAM_C),
            ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
            ('LEFTPADDING',(1,0),(1,-1),7),('RIGHTPADDING',(1,0),(1,-1),5),
        ]))
        inner = Table([[p] for p in body_paras], colWidths=[16.6*cm])
        inner.setStyle(TableStyle([
            ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0),
            ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),0),
        ]))
        return KeepTogether([header, inner, Spacer(1, 5)])

    story.append(phase_block("Phase 1 · 2014–2021 · Haïti","Formation Académique & Premiers Engagements Financiers","#4A9EFF",
        ["Mackenson Cineus intègre l'<b>INAGHEI</b> et la <b>FDSE</b> à l'Université d'État d'Haïti — double cursus Gestion des Affaires & Sciences Économiques.",
         "Il rejoint <b>Hult Prize Haïti</b> comme Directeur Financier : recherche de financements (Ministère des Finances, BNC), élaboration du budget, supervision de 10 départements. Représentant Haïti au <b>Hult Prize international 2018</b> avec le projet <b>WEISS</b> (transformation des déchets en biogaz & fertilisant organique)."],
        [("INAGHEI / UEH","ueh.edu.ht"),("Hult Prize","hultprize.org")]))

    story.append(phase_block("Phase 2 · 2019–2024 · France","Formation Finance Européenne & Podcast INCLUTECH","#C9A84C",
        ["Mackenson obtient une <b>Licence Banque, Finance & Assurance</b> à l'<b>Université du Mans</b> (marchés bancaires, risk management, VBA, réglementation), puis intègre le <b>MBA 2 Finance de marché à l'ESLSCA Business School Paris</b> (2024–2026).",
         "Il lance le podcast <b>INCLUTECH</b> (Spotify & Apple Podcasts, bi-mensuel) sur l'inclusion financière et le rôle des fintechs. En octobre 2023, son équipe remporte la <b>1ère place du Hackathon Fintech Générations</b> organisé par <b>France FinTech, Société Générale et Treezor</b> — projet <b>Victoria</b> (financement DPE), pitché à Fintech R:Evolution devant 1 500 participants."],
        [("Université du Mans","univ-lemans.fr"),("ESLSCA Paris","eslsca.fr"),("INCLUTECH","open.spotify.com/show/5XvFdWYwhHWY3EguIhhf69")]))

    story.append(phase_block("Phase 3 · 2024–2025 · HiPay SAS","Chargé de Conformité — Fintech de Paiement Agréée ACPR","#E67E22",
        ["<b>HiPay</b> est un prestataire de services de paiement omnicanal coté sur Euronext Growth (ALHYP), agréé par l'<b>ACPR</b>. Mackenson y est <b>Chargé de Conformité</b> à Levallois-Perret.",
         "Missions : analyse des risques pays (<b>GAFI</b>) sur pays sensibles et complexes (dont sous sanctions) ; analyses <b>KYC/PPE/PE/SOE</b> ; réponse aux réquisitions <b>Tracfin</b> et judiciaires ; Due Diligence des partenaires institutionnels systémiques."],
        [("HiPay","hipay.com"),("ACPR","acpr.banque-france.fr"),("Tracfin","economie.gouv.fr/tracfin"),("GAFI","fatf-gafi.org")]))

    story.append(PageBreak())

    story.append(phase_block("Phase 4 · 2025–Présent · Banque DELUBAC & CIE","Analyste LCB-FT — Clientèle Corporate, CIB, PSP","#9B59B6",
        ["<b>Banque Delubac & Cie</b> (fondée 1924, banque indépendante de plein exercice) — <b>Analyste LCB-FT</b> en alternance MBA 2 Finance de marché (ESLSCA).",
         "Missions : <b>alertes de niveau 1 LCB-FT</b> (corporate, CIB, asset management, banque privée, PSP) ; <b>Examens Renforcés (ER)</b>, PDS, avis sur opérations ; analyse KYC, bénéficiaires effectifs, cohérence économique, <b>déclarations de soupçon (DS)</b> ; analyse bilan & compte de résultat ; réquisitions judiciaires.",
         "Dashboard Excel : <b>205 analyses</b> réalisées — typologies LCB-FT complètes — volume total <b>24 892 285,50 € examinés</b>."],
        [("Banque Delubac","delubac.com"),("ACPR","acpr.banque-france.fr"),("GAFI","fatf-gafi.org")]))

    story.append(_hr(NAVY_C, 1.5, before=4, after=4))
    story.append(Paragraph('<b><font color="#0D1B2A" size="10">Présences en ligne & Sources</font></b>', _s('sh2', fontSize=10, spaceAfter=6)))

    links = [
        ("LinkedIn","linkedin.com/in/mackenson-cineus","Réseau finance/compliance franco-international"),
        ("HiPay","hipay.com","Employeur 2024–2025 · Paiement omnicanal · Euronext Growth ALHYP"),
        ("Banque Delubac","delubac.com","Employeur 2025 · Banque privée fondée 1924"),
        ("INCLUTECH Spotify","open.spotify.com/show/5XvFdWYwhHWY3EguIhhf69","Podcast bi-mensuel · Finance & Inclusion"),
        ("ESLSCA Paris","eslsca.fr","MBA Finance de marché 2024–2026"),
        ("Université du Mans","univ-lemans.fr","Licence BFA 2019–2021"),
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
                row.append(Paragraph(f"<b>{n}</b>  <font color='#4A9EFF' size='7'>{u}</font><br/><font size='6.8' color='#666666'>{d}</font>", _s('lnk', fontSize=7, leading=10, spaceAfter=0)))
            else:
                row.append(Paragraph("", _s('x')))
        link_rows.append(row)
    link_t = Table(link_rows, colWidths=[8.5*cm, 8.5*cm])
    link_t.setStyle(TableStyle([
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[CREAM_C, rl_colors.white]),
        ('LINEAFTER',(0,0),(0,-1),0.3,GRAY_L_C),
        ('INNERGRID',(0,0),(-1,-1),0.2,rl_colors.HexColor('#EEEEEE')),
        ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
    ]))
    story.append(link_t)

    doc.build(story, onFirstPage=_page_frame, onLaterPages=_page_frame)
    buf.seek(0)
    return buf.read()


# ═══════════════════════════════════════════════════════════════════════════════
# JOB SCRAPER
# ═══════════════════════════════════════════════════════════════════════════════
def _scrape_jobs():
    return [
        {"source":"France Travail (Pôle Emploi)","icon":"🇫🇷","queries":[
            {"title":"Analyste LCB-FT / Sécurité Financière","url":"https://candidat.francetravail.fr/offres/recherche?motsCles=analyste+LCB-FT+s%C3%A9curit%C3%A9+financi%C3%A8re&lieux=75&sort=1","keywords":["LCB-FT","conformité","AML"]},
            {"title":"Compliance Officer / Conformité AML","url":"https://candidat.francetravail.fr/offres/recherche?motsCles=compliance+officer+AML+conformit%C3%A9&lieux=75&sort=1","keywords":["compliance","AML","KYC"]},
        ]},
        {"source":"LinkedIn","icon":"💼","queries":[
            {"title":"Analyste LCB-FT | AML Analyst — France","url":"https://www.linkedin.com/jobs/search/?keywords=analyste+LCB-FT+AML&location=France&sortBy=DD","keywords":["LCB-FT","AML","conformité"]},
            {"title":"Compliance Officer — Paris","url":"https://www.linkedin.com/jobs/search/?keywords=compliance+officer+securite+financiere&location=%C3%8Ele-de-France%2C+France&sortBy=DD","keywords":["compliance","sécurité financière","KYC"]},
            {"title":"AML / KYC Analyst — Luxembourg","url":"https://www.linkedin.com/jobs/search/?keywords=AML+KYC+analyst+compliance&location=Luxembourg&sortBy=DD","keywords":["AML","KYC","compliance"]},
        ]},
        {"source":"Welcome to the Jungle","icon":"🌿","queries":[
            {"title":"Compliance / Conformité AML","url":"https://www.welcometothejungle.com/fr/jobs?query=compliance+AML&sortBy=publishedAt_desc","keywords":["compliance","AML"]},
            {"title":"Sécurité Financière / LCB-FT","url":"https://www.welcometothejungle.com/fr/jobs?query=s%C3%A9curit%C3%A9+financi%C3%A8re+LCB-FT&sortBy=publishedAt_desc","keywords":["LCB-FT","sécurité financière"]},
        ]},
        {"source":"Indeed France","icon":"🔍","queries":[
            {"title":"Analyste LCB-FT Paris","url":"https://fr.indeed.com/jobs?q=analyste+LCB-FT&l=Paris&sort=date","keywords":["LCB-FT","sécurité financière"]},
            {"title":"Compliance Officer AML Paris","url":"https://fr.indeed.com/jobs?q=compliance+officer+AML&l=Paris&sort=date","keywords":["compliance","AML","KYC"]},
        ]},
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:20px 0 10px;'>
      <div style='width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#C9A84C,#4A9EFF);
                  display:flex;align-items:center;justify-content:center;font-size:2rem;
                  margin:0 auto 12px;border:3px solid rgba(201,168,76,0.4);'>MC</div>
      <div style='font-size:1.1rem;font-weight:700;color:#C9A84C;'>Mackenson Cineus</div>
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
        "⚖️ Sanctions & Amendes",
        "🔎 Offres d'Emploi",
        "✏️ Édition du Profil",
    ], label_visibility="collapsed")

    st.divider()
    st.markdown("<div style='font-size:0.8rem;color:#C9A84C;font-weight:600;margin-bottom:6px;'>🔑 Clé API Anthropic</div>", unsafe_allow_html=True)
    api_key_input = st.text_input("Clé API", type="password", placeholder="sk-ant-...", label_visibility="collapsed", key="anthropic_api_key")
    if api_key_input:
        st.markdown("<div style='font-size:0.72rem;color:#2ECC71;margin-top:4px;'>✅ Clé renseignée</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:0.72rem;color:#E67E22;margin-top:4px;'>⚠️ Aucune clé</div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<div style='font-size:0.75rem;opacity:0.5;text-align:center;padding:10px;'>© 2026 Mackenson Cineus</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — PROFIL & BIOGRAPHIE
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Profil & Biographie":
    P = _P()

    st.markdown(f"""
    <div class="hero-banner">
      <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
        <div style="width:72px;height:72px;border-radius:50%;background:linear-gradient(135deg,#C9A84C,#4A9EFF);
                    display:flex;align-items:center;justify-content:center;font-size:1.8rem;
                    border:3px solid rgba(201,168,76,0.5);flex-shrink:0;">MC</div>
        <div>
          <p class="hero-name">{P['name']}</p>
          <p class="hero-title">{P['title']} · {P['location']}</p>
        </div>
      </div>
      <div style="margin-top:16px;">
        <span class="hero-badge">💳 HiPay</span>
        <span class="hero-badge">🏦 LCB-FT / AML</span>
        <span class="hero-badge">📈 MBA Finance</span>
        <span class="hero-badge">🚀 Hackathon 2023</span>
        <span class="hero-badge">🌍 Haïti → Paris</span>
        <span class="hero-badge">🏆 Hult Prize 2018</span>
        <span class="hero-badge">🎙 Podcast INCLUTECH</span>
      </div>
      <p style="margin-top:20px;max-width:780px;opacity:0.85;line-height:1.85;font-size:0.95rem;">{P['summary']}</p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(5)
    kpis = [
        ("2","Postes conformité","#C9A84C"),
        ("3","Pays traversés","#4A9EFF"),
        ("2","Diplômes sup.","#2ECC71"),
        ("🥇","Hackathon 2023","#E67E22"),
        ("🎙","Podcast INCLUTECH","#9B59B6"),
    ]
    for col, (val, lbl, color) in zip(cols, kpis):
        with col:
            st.markdown(f"""<div class="metric-card" style="border-top:3px solid {color};">
              <span class="metric-value" style="color:{color};font-size:2rem;">{val}</span>
              <div class="metric-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_bio, col_side = st.columns([3, 1])

    with col_bio:
        st.markdown('<p class="section-header">Biographie — Parcours en 4 phases</p>', unsafe_allow_html=True)
        for period in BIO_PERIODS:
            tags_html = "".join(f'<span class="bio-tag">{t}</span>' for t in period["tags"])
            paras_html = "".join(f'<p style="margin:0 0 12px 0;">{p}</p>' for p in period["text"])
            st.markdown(f"""<div class="bio-period {period['phase']}">
              <div class="bio-phase-label">{period['label']}</div>
              <div class="bio-period-title">{period['title']}</div>
              <div class="bio-period-years">📍 {period['years']}</div>
              <div class="bio-period-text">{paras_html}</div>
              <div style="margin-top:12px;">{tags_html}</div>
            </div>""", unsafe_allow_html=True)

    with col_side:
        st.markdown('<p class="section-header" style="font-size:1.2rem;">📥 Documents PDF</p>', unsafe_allow_html=True)
        for icon, title, desc in [
            ("📋","CV Finance","1 page · Format banking"),
            ("✉️","Lettre de Motivation","Harvard · 1 page"),
            ("📖","Biographie","4 phases · 2 pages"),
        ]:
            st.markdown(f"""<div style="background:var(--navy-mid);border:1px solid rgba(201,168,76,0.15);border-radius:10px;padding:12px;margin-bottom:10px;">
              <div style="font-size:1.3rem;">{icon}</div>
              <div style="font-size:0.88rem;font-weight:600;color:var(--gold);margin:3px 0 1px;">{title}</div>
              <div style="font-size:0.75rem;opacity:0.6;">{desc}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<br><p class="section-header" style="font-size:1.2rem;">🔗 Liens Rapides</p>', unsafe_allow_html=True)
        for icon, name, url in [
            ("💼","LinkedIn","https://linkedin.com/in/mackenson-cineus"),
            ("💳","HiPay","https://hipay.com"),
            ("🏦","Banque Delubac","https://www.delubac.com"),
            ("🎙","INCLUTECH","https://open.spotify.com/show/5XvFdWYwhHWY3EguIhhf69"),
            ("📸","Instagram","https://instagram.com/mackenson_cineus"),
        ]:
            st.markdown(f"""<a href="{url}" target="_blank" style="text-decoration:none;">
              <div style="display:flex;align-items:center;gap:10px;background:var(--navy-mid);border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:8px 12px;margin-bottom:7px;">
                <span style="font-size:1rem;">{icon}</span>
                <span style="font-size:0.82rem;color:var(--gold);">{name}</span>
                <span style="margin-left:auto;font-size:0.7rem;opacity:0.4;">↗</span>
              </div></a>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — PARCOURS & COMPÉTENCES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "⏱ Parcours & Compétences":
    st.markdown('<p class="section-header">Parcours chronologique & Compétences</p>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 2])
    with col1:
        cats = ["Tous"] + sorted(set(t["cat"] for t in TIMELINE))
        fc = st.selectbox("Filtrer", cats, label_visibility="collapsed")
        items = TIMELINE if fc == "Tous" else [t for t in TIMELINE if t["cat"] == fc]
        for item in items:
            st.markdown(f"""<div class="timeline-item">
              <div class="timeline-year">{item['icon']} {item['year']} · {item['cat']}</div>
              <div class="timeline-title">{item['title']}</div>
              <div class="timeline-desc">{item['desc']}</div>
            </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown('<p class="section-header">Compétences</p>', unsafe_allow_html=True)
        for skill, level in SKILLS.items():
            st.markdown(f"""<div class="skill-bar-container">
              <div class="skill-name">{skill}<span style="float:right;color:#C9A84C;font-weight:600;">{level}%</span></div>
              <div class="skill-bar"><div class="skill-fill" style="width:{level}%;"></div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown('<br><p class="section-header">Langues</p>', unsafe_allow_html=True)
        for lang, level in LANGUAGES.items():
            st.markdown(f"""<div class="skill-bar-container">
              <div class="skill-name">{lang}<span style="float:right;color:#4A9EFF;font-weight:600;">{level}%</span></div>
              <div class="skill-bar"><div class="skill-fill" style="width:{level}%;background:linear-gradient(90deg,#4A9EFF,#7BC8FF);"></div></div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — VISUALISATIONS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Visualisations":
    st.markdown('<p class="section-header">📊 Analyses & Visualisations</p>', unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["Radar Compétences","Évolution de carrière","Répartition des axes","Langues"])

    with tab1:
        _ls = st.session_state.get("edit_skills", SKILLS)
        sn = list(_ls.keys()); sv = list(_ls.values())
        fig = go.Figure(go.Scatterpolar(r=sv+[sv[0]], theta=sn+[sn[0]], fill='toself',
            fillcolor='rgba(201,168,76,0.15)', line=dict(color='#C9A84C', width=2), marker=dict(color='#C9A84C', size=8)))
        fig.update_layout(polar=dict(bgcolor='rgba(26,46,66,0.5)',
            radialaxis=dict(visible=True, range=[0,100], gridcolor='rgba(255,255,255,0.1)', color='#F5F0E8'),
            angularaxis=dict(gridcolor='rgba(255,255,255,0.1)', color='#F5F0E8')),
            paper_bgcolor='rgba(0,0,0,0)', font=dict(family='DM Sans', color='#F5F0E8'),
            title=dict(text='Radar des Compétences', font=dict(color='#C9A84C', size=16)), height=480)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        df = pd.DataFrame([
            {"A":"2014","N":10,"E":"Université d'État d'Haïti"},
            {"A":"2018","N":35,"E":"Hult Prize — WEISS"},
            {"A":"2019","N":52,"E":"Université du Mans — BFA"},
            {"A":"2021","N":62,"E":"Podcast INCLUTECH"},
            {"A":"2023","N":80,"E":"Hackathon Fintech 🥇"},
            {"A":"2024","N":88,"E":"HiPay Compliance"},
            {"A":"2025","N":95,"E":"Banque Delubac LCB-FT"},
        ])
        fig2 = go.Figure(go.Scatter(x=df["A"], y=df["N"], mode='lines+markers+text',
            line=dict(color='#C9A84C', width=3),
            marker=dict(size=12, color='#C9A84C', line=dict(color='#1A2E42', width=3)),
            text=df["E"], textposition='top center', textfont=dict(size=9, color='#F5F0E8'),
            hovertemplate='<b>%{text}</b><br>Progression : %{y}%<extra></extra>'))
        fig2.update_layout(title=dict(text='Progression de Carrière', font=dict(color='#C9A84C', size=16)),
            yaxis=dict(range=[0,110], gridcolor='rgba(255,255,255,0.07)', color='#F5F0E8'),
            xaxis=dict(color='#F5F0E8', gridcolor='rgba(255,255,255,0.07)'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(13,27,42,0.6)',
            font=dict(family='DM Sans', color='#F5F0E8'), height=430)
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            axes = {"Finance & Conformité":55,"Entrepreneuriat Fintech":25,"Communication & Podcast":20}
            fig3 = go.Figure(go.Pie(labels=list(axes.keys()), values=list(axes.values()), hole=0.5,
                marker=dict(colors=['#C9A84C','#4A9EFF','#2ECC71'], line=dict(color='#0D1B2A', width=2)),
                textfont=dict(color='white', size=11)))
            fig3.update_layout(title=dict(text='Axes du parcours', font=dict(color='#C9A84C', size=14)),
                paper_bgcolor='rgba(0,0,0,0)', font=dict(family='DM Sans', color='#F5F0E8'),
                legend=dict(font=dict(color='#F5F0E8'), bgcolor='rgba(0,0,0,0)'), height=360)
            st.plotly_chart(fig3, use_container_width=True)
        with c2:
            countries = {"Haïti":35,"France":55,"International":10}
            fig4 = go.Figure(go.Bar(x=list(countries.keys()), y=list(countries.values()),
                marker=dict(color=['#4A9EFF','#C9A84C','#2ECC71']),
                text=[f"{v}%" for v in countries.values()], textposition='outside', textfont=dict(color='#F5F0E8')))
            fig4.update_layout(title=dict(text='Répartition géographique', font=dict(color='#C9A84C', size=14)),
                yaxis=dict(range=[0,70], gridcolor='rgba(255,255,255,0.07)', color='#F5F0E8'),
                xaxis=dict(color='#F5F0E8'), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(13,27,42,0.6)',
                font=dict(family='DM Sans', color='#F5F0E8'), height=360)
            st.plotly_chart(fig4, use_container_width=True)

    with tab4:
        fig5 = go.Figure()
        clrs = {'Créole haïtien':'#2ECC71','Français':'#C9A84C','Anglais':'#4A9EFF'}
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
    for i in range(len(coords)-1):
        fig_map.add_trace(go.Scattergeo(lat=[coords[i][0], coords[i+1][0]], lon=[coords[i][1], coords[i+1][1]],
            mode='lines', line=dict(width=2, color='rgba(201,168,76,0.5)'), showlegend=False))
    fig_map.add_trace(go.Scattergeo(lat=GEO_DATA['lat'], lon=GEO_DATA['lon'], mode='markers+text',
        marker=dict(size=GEO_DATA['size'], color=['#4A9EFF','#C9A84C','#C9A84C'], line=dict(color='white', width=2)),
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
    cols = st.columns(3)
    for col, (loc_name, event, year) in zip(cols, zip(GEO_DATA['locations'], GEO_DATA['events'], GEO_DATA['years'])):
        with col:
            st.markdown(f"""<div class="timeline-item" style="border-left-color:#4A9EFF;">
              <div class="timeline-year">📍 {year}</div>
              <div class="timeline-title">{loc_name}</div>
              <div class="timeline-desc">{event}</div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — PLATEFORMES & LIENS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔗 Plateformes & Liens":
    st.markdown('<p class="section-header">🔗 Plateformes & Présences en ligne</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    for i, p_item in enumerate(PLATFORMS):
        with (col1 if i % 2 == 0 else col2):
            st.markdown(f"""<div class="platform-card">
              <div class="platform-icon">{p_item['icon']}</div>
              <div style="flex:1;">
                <div class="platform-name">{p_item['name']}</div>
                <div class="platform-desc">{p_item['desc']}</div>
                <a href="{p_item['url']}" target="_blank" class="platform-link">{p_item['label']}</a>
              </div></div>""", unsafe_allow_html=True)

    st.markdown('<br><p class="section-header">📡 Régulateurs & Ressources sectorielles</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    for i, (icon, name_r, desc, url) in enumerate(REGULATORS):
        with (col1 if i % 2 == 0 else col2):
            st.markdown(f"""<div class="platform-card">
              <div class="platform-icon">{icon}</div>
              <div style="flex:1;">
                <div class="platform-name">{name_r}</div>
                <div class="platform-desc">{desc}</div>
                <a href="{url}" target="_blank" class="platform-link">Consulter →</a>
              </div></div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — GÉNÉRATEUR DE DOCUMENTS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📄 Générateur de Documents":
    st.markdown('<p class="section-header">📄 Générateur de Documents</p>', unsafe_allow_html=True)

    tab_cv, tab_lm, tab_bio = st.tabs(["📋 CV","✉️ Lettre de Motivation","📖 Biographie"])

    with tab_cv:
        st.markdown("""<div style='background:var(--navy-mid);border:1px solid rgba(201,168,76,0.2);border-radius:12px;padding:20px 24px;margin-bottom:20px;'>
          <div style='font-size:1rem;font-weight:600;color:#C9A84C;margin-bottom:6px;'>CV Professionnel — Format Finance (1 page)</div>
          <div style='font-size:0.85rem;opacity:0.75;'>CV une page, format standard finance/banking. Disponible en <b>PDF</b> et <b>Word (.docx)</b>.</div>
        </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            cv_poste = st.text_input("🎯 Poste visé", placeholder="ex: Compliance Officer…", key="cv_poste")
        with c2:
            cv_entreprise = st.text_input("🏢 Entreprise", placeholder="ex: BNP Paribas…", key="cv_entreprise")
        c3, c4 = st.columns(2)
        with c3:
            cv_secteur = st.selectbox("🏦 Secteur", ["Banque","Fintech","Asset Management","Assurance","Audit / Conseil","Marché des capitaux"], key="cv_sect")
        with c4:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

        col_pdf, col_word = st.columns(2)
        with col_pdf:
            gen_cv_pdf = st.button("⬇️ Télécharger CV (PDF)", use_container_width=True, key="btn_cv_pdf")
        with col_word:
            gen_cv_word = st.button("📝 Télécharger CV (Word)", use_container_width=True, key="btn_cv_word")

        if gen_cv_pdf:
            with st.spinner("Génération du CV PDF…"):
                pdf_bytes = generate_cv_pdf(poste=cv_poste, entreprise=cv_entreprise, secteur=cv_secteur)
            st.success("✅ CV PDF généré !")
            st.download_button("📥 Télécharger — Cineus_Mackenson_CV.pdf", data=pdf_bytes,
                file_name="Cineus_Mackenson_CV.pdf", mime="application/pdf", use_container_width=True, key="dl_cv_pdf")

        if gen_cv_word:
            with st.spinner("Génération du CV Word…"):
                docx_bytes = generate_cv_docx(poste=cv_poste, entreprise=cv_entreprise, secteur=cv_secteur)
            st.success("✅ CV Word généré !")
            st.download_button("📥 Télécharger — Cineus_Mackenson_CV.docx", data=docx_bytes,
                file_name="Cineus_Mackenson_CV.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True, key="dl_cv_word")

    with tab_lm:
        st.markdown("""<div style='background:var(--navy-mid);border:1px solid rgba(74,158,255,0.2);border-radius:12px;padding:20px 24px;margin-bottom:20px;'>
          <div style='font-size:1rem;font-weight:600;color:#4A9EFF;margin-bottom:6px;'>Lettre de Motivation (PDF & Word)</div>
          <div style='font-size:0.85rem;opacity:0.75;'>Lettre structurée en 4 paragraphes. Téléchargeable en PDF ou Word.</div>
        </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            lm_poste = st.text_input("🎯 Poste visé", placeholder="ex: Analyste LCB-FT…", key="lm_poste")
            lm_entreprise = st.text_input("🏢 Entreprise", placeholder="ex: BNP Paribas…", key="lm_ent")
        with c2:
            lm_secteur = st.selectbox("🏦 Secteur", ["Banque","Fintech","Asset Management","Assurance","Audit / Conseil"], key="lm_sect")
            lm_style = st.selectbox("✍️ Ton", ["Professionnel & formel","Dynamique & moderne","Harvard / McKinsey"], key="lm_style")

        lm_contexte = st.text_area("💬 Instructions spécifiques", placeholder="Ex: insister sur HiPay…", height=60, key="lm_ctx")

        col_lm_pdf, col_lm_word = st.columns(2)
        with col_lm_pdf:
            gen_lm_pdf = st.button("⬇️ Lettre (PDF)", use_container_width=True, key="btn_lm_pdf")
        with col_lm_word:
            gen_lm_word = st.button("📝 Lettre (Word)", use_container_width=True, key="btn_lm_word")

        if gen_lm_pdf:
            if not lm_poste:
                st.error("⚠️ Veuillez indiquer le poste visé.")
            else:
                with st.spinner("Génération PDF…"):
                    pdf_lm = generate_lettre_pdf(poste=lm_poste, entreprise=lm_entreprise, secteur=lm_secteur, style_lm=lm_style, contexte=lm_contexte)
                st.success("✅ Lettre PDF générée !")
                st.download_button("📥 Télécharger — Cineus_Mackenson_LM.pdf", data=pdf_lm,
                    file_name=f"Cineus_Mackenson_LM_{(lm_poste or 'Finance').replace(' ','_')}.pdf",
                    mime="application/pdf", use_container_width=True, key="dl_lm_pdf")

        if gen_lm_word:
            if not lm_poste:
                st.error("⚠️ Veuillez indiquer le poste visé.")
            else:
                with st.spinner("Génération Word…"):
                    docx_lm = generate_lettre_docx(poste=lm_poste, entreprise=lm_entreprise, secteur=lm_secteur, contexte=lm_contexte)
                st.success("✅ Lettre Word générée !")
                st.download_button("📥 Télécharger — Cineus_Mackenson_LM.docx", data=docx_lm,
                    file_name=f"Cineus_Mackenson_LM_{(lm_poste or 'Finance').replace(' ','_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True, key="dl_lm_word")

    with tab_bio:
        st.markdown("""<div style='background:var(--navy-mid);border:1px solid rgba(46,204,113,0.2);border-radius:12px;padding:20px 24px;margin-bottom:20px;'>
          <div style='font-size:1rem;font-weight:600;color:#2ECC71;margin-bottom:6px;'>Biographie Professionnelle Complète (PDF)</div>
          <div style='font-size:0.85rem;opacity:0.75;'>Biographie narrative en 4 phases chronologiques. Données réelles vérifiées.</div>
        </div>""", unsafe_allow_html=True)
        gen_bio = st.button("⬇️ Générer & Télécharger la Biographie (PDF)", use_container_width=True, key="btn_bio")
        if gen_bio:
            with st.spinner("Génération de la biographie PDF…"):
                pdf_bio = generate_bio_pdf()
            st.success("✅ Biographie générée !")
            st.download_button("📥 Télécharger — Cineus_Mackenson_Biographie.pdf", data=pdf_bio,
                file_name="Cineus_Mackenson_Biographie.pdf", mime="application/pdf",
                use_container_width=True, key="dl_bio")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 7 — SANCTIONS & AMENDES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "⚖️ Sanctions & Amendes":
    st.markdown('<p class="section-header">⚖️ Sanctions & Amendes — Sécurité Financière</p>', unsafe_allow_html=True)
    st.markdown("""
    <p style='opacity:0.75;margin-bottom:20px;line-height:1.7;max-width:750px;'>
    Recensement des principales <strong style='color:#E74C3C;'>sanctions et amendes</strong> prononcées par les autorités
    de régulation (ACPR, FinCEN, FCA, BaFin…) dans le domaine de la <strong style='color:#C9A84C;'>sécurité financière,
    LCB-FT, AML et KYC</strong>. Source de veille réglementaire essentielle pour tout professionnel de la conformité.
    </p>
    """, unsafe_allow_html=True)

    # Filtres
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filtre_type = st.selectbox("🔍 Type d'infraction", ["Tous","LCB-FT / KYC","AML / Crypto","KYC / PPE","AML / Reporting","Sanctions / Gel avoirs","AML / Fintech","AML / Fraude","LCB-FT / Néobanque","KYC / Paiement","AML / Crypto / KYC"])
    with col_f2:
        filtre_gravite = st.selectbox("⚠️ Gravité", ["Toutes","Critique","Majeure","Significative","Modérée"])
    with col_f3:
        filtre_pays = st.selectbox("🌍 Pays/Région", ["Tous","France","USA","Allemagne","Royaume-Uni","Luxembourg"])

    # Filtrage
    filtered = SANCTIONS_DATA
    if filtre_type != "Tous":
        filtered = [s for s in filtered if s["type"] == filtre_type]
    if filtre_gravite != "Toutes":
        filtered = [s for s in filtered if s["gravite"] == filtre_gravite]
    if filtre_pays != "Tous":
        filtered = [s for s in filtered if filtre_pays.lower() in s["pays"].lower()]

    # KPIs
    total_amendes = sum(s["montant_raw"] for s in filtered if s["montant_raw"] > 0)
    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    with col_k1:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #E74C3C;">
          <span class="metric-value" style="color:#E74C3C;font-size:1.8rem;">{len(filtered)}</span>
          <div class="metric-label">Sanctions recensées</div></div>""", unsafe_allow_html=True)
    with col_k2:
        montant_str = f"{total_amendes/1e9:.1f} Mrd $" if total_amendes >= 1e9 else f"{total_amendes/1e6:.0f} M €"
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #E67E22;">
          <span class="metric-value" style="color:#E67E22;font-size:1.8rem;">{montant_str}</span>
          <div class="metric-label">Amendes totales (aprox.)</div></div>""", unsafe_allow_html=True)
    with col_k3:
        critiques = len([s for s in filtered if s["gravite"] == "Critique"])
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #9B59B6;">
          <span class="metric-value" style="color:#9B59B6;font-size:1.8rem;">{critiques}</span>
          <div class="metric-label">Sanctions critiques</div></div>""", unsafe_allow_html=True)
    with col_k4:
        st.markdown(f"""<div class="metric-card" style="border-top:3px solid #C9A84C;">
          <span class="metric-value" style="color:#C9A84C;font-size:1.8rem;">2022–2024</span>
          <div class="metric-label">Période couverte</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Graphique montants
    if len(filtered) > 1:
        entities = [s["entite"] for s in filtered if s["montant_raw"] > 0]
        amounts = [s["montant_raw"] for s in filtered if s["montant_raw"] > 0]
        colors_sanction = ['#E74C3C' if s["gravite"]=="Critique" else '#E67E22' if s["gravite"]=="Majeure" else '#C9A84C' for s in filtered if s["montant_raw"] > 0]
        if entities:
            fig_s = go.Figure(go.Bar(x=entities, y=amounts,
                marker=dict(color=colors_sanction, line=dict(color='#0D1B2A', width=1)),
                text=[s["montant"] for s in filtered if s["montant_raw"] > 0],
                textposition='outside', textfont=dict(color='#F5F0E8', size=9),
                hovertemplate='<b>%{x}</b><br>Amende: %{text}<extra></extra>'))
            fig_s.update_layout(title=dict(text='Montants des amendes', font=dict(color='#C9A84C', size=14)),
                yaxis=dict(gridcolor='rgba(255,255,255,0.07)', color='#F5F0E8', title="Montant ($)"),
                xaxis=dict(color='#F5F0E8', tickangle=-20),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(13,27,42,0.6)',
                font=dict(family='DM Sans', color='#F5F0E8'), height=350)
            st.plotly_chart(fig_s, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Cartes sanctions
    gravite_colors = {"Critique":"#E74C3C","Majeure":"#E67E22","Significative":"#C9A84C","Modérée":"#4A9EFF"}
    col1, col2 = st.columns(2)
    for i, s in enumerate(filtered):
        col = col1 if i % 2 == 0 else col2
        with col:
            g_color = gravite_colors.get(s["gravite"], "#C9A84C")
            st.markdown(f"""
            <div class="sanction-card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
                <div>
                  <div class="sanction-entity">{s["entite"]}</div>
                  <div style="font-size:0.78rem;color:#888;margin-top:2px;">{s["pays"]} · {s["autorite"]} · {s["date"]}</div>
                </div>
                <div style="text-align:right;">
                  <div class="sanction-amount">{s["montant"]}</div>
                  <div style="display:inline-block;background:{g_color}22;border:1px solid {g_color}55;border-radius:4px;padding:2px 8px;font-size:0.7rem;color:{g_color};margin-top:2px;">{s["gravite"]}</div>
                </div>
              </div>
              <div style="font-size:0.8rem;color:#F5F0E8;opacity:0.8;line-height:1.5;margin-bottom:6px;">{s["motif"]}</div>
              <div style="display:inline-block;background:rgba(201,168,76,0.1);border:1px solid rgba(201,168,76,0.3);border-radius:4px;padding:2px 8px;font-size:0.72rem;color:#C9A84C;">{s["type"]}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='background:var(--navy-mid);border:1px solid rgba(201,168,76,0.2);border-radius:12px;padding:20px;margin-top:8px;'>
      <div style='font-size:0.95rem;font-weight:600;color:#C9A84C;margin-bottom:10px;'>📚 Sources & Ressources de Veille Réglementaire</div>
      <div style='font-size:0.85rem;opacity:0.8;line-height:1.8;'>
        <a href="https://acpr.banque-france.fr/sanctions" target="_blank" style="color:#4A9EFF;">ACPR — Sanctions prononcées</a>  ·
        <a href="https://www.fatf-gafi.org/fr/publications/" target="_blank" style="color:#4A9EFF;">GAFI — Publications</a>  ·
        <a href="https://www.fca.org.uk/news/news-stories/fca-enforcement-actions" target="_blank" style="color:#4A9EFF;">FCA — Enforcement</a>  ·
        <a href="https://www.fincen.gov/news/enforcement" target="_blank" style="color:#4A9EFF;">FinCEN — Enforcement</a>  ·
        <a href="https://www.bafin.de/EN/PublikationenDaten/Datenbanken/Sanktionen/sanktionen_node_en.html" target="_blank" style="color:#4A9EFF;">BaFin — Sanctions</a>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 8 — OFFRES D'EMPLOI
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔎 Offres d'Emploi":
    st.markdown('<p class="section-header">🔎 Offres d\'Emploi — Sécurité Financière · AML</p>', unsafe_allow_html=True)
    job_boards = _scrape_jobs()
    search_kw = st.text_input("🔍 Filtrer par mot-clé", placeholder="ex: LCB-FT, AML, KYC…")
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col_idx = 0
    for board in job_boards:
        for query in board["queries"]:
            if search_kw:
                all_text = query["title"].lower() + " ".join(query.get("keywords",[])).lower()
                if search_kw.lower() not in all_text:
                    continue
            col = col1 if col_idx % 2 == 0 else col2
            col_idx += 1
            kw_badges = "".join(
                f'<span style="background:rgba(201,168,76,0.15);border:1px solid rgba(201,168,76,0.3);border-radius:4px;padding:2px 7px;font-size:0.7rem;color:#C9A84C;margin:2px 2px 0 0;display:inline-block;">{k}</span>'
                for k in query.get("keywords",[]))
            with col:
                st.markdown(f"""<div style="background:var(--navy-mid);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:14px 16px;margin-bottom:12px;border-left:3px solid #C9A84C;">
                  <div style="font-size:0.7rem;color:#888;margin-bottom:3px;">{board['icon']} {board['source']}</div>
                  <div style="font-size:0.92rem;font-weight:600;color:#F5F0E8;margin-bottom:6px;">{query['title']}</div>
                  <div style="margin-bottom:8px;">{kw_badges}</div>
                  <a href="{query['url']}" target="_blank" style="display:inline-block;background:linear-gradient(135deg,#C9A84C,#E8C97A);color:#0D1B2A;padding:5px 14px;border-radius:6px;font-size:0.78rem;font-weight:700;text-decoration:none;">Voir les offres →</a>
                </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 9 — ÉDITION DU PROFIL
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "✏️ Édition du Profil":
    st.markdown('<p class="section-header">✏️ Édition du Profil</p>', unsafe_allow_html=True)

    t1, t2, t3, t4, t5, t6, t7 = st.tabs([
        "👤 Infos Générales","💼 Expériences","🎓 Formation","⚡ Compétences","🏅 Distinctions","📖 Mémoire","🧠 Personnalité"
    ])

    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Nom complet", key="edit_name")
            st.text_input("Localisation", key="edit_location")
            st.text_input("Email", key="edit_email")
        with c2:
            st.text_input("Titre professionnel", key="edit_title")
            st.text_input("Téléphone", key="edit_phone")
            st.text_input("LinkedIn (sans https://)", key="edit_linkedin")
        st.text_area("Résumé", key="edit_summary", height=110)
        if st.button("💾 Sauvegarder", use_container_width=True, key="save_infos"):
            st.success("✅ Sauvegardé !")

    with t2:
        exps = st.session_state.edit_exp
        for i, exp in enumerate(exps):
            with st.expander(f"**{exp['role']}** — {exp['org']}", expanded=(i < 2)):
                c1, c2 = st.columns([2,1])
                with c1:
                    nr = st.text_input("Rôle", value=exp["role"], key=f"er_{i}")
                    no = st.text_input("Organisation", value=exp["org"], key=f"eo_{i}")
                    nu = st.text_input("URL", value=exp.get("url",""), key=f"eu_{i}")
                with c2:
                    np = st.text_input("Période", value=exp["period"], key=f"ep_{i}")
                    nt = st.selectbox("Type", ["Banque","Fintech","Compétition","Association","ONG"],
                        index=["Banque","Fintech","Compétition","Association","ONG"].index(exp.get("org_type","Association"))
                        if exp.get("org_type","Association") in ["Banque","Fintech","Compétition","Association","ONG"] else 0,
                        key=f"et_{i}")
                nb = st.text_area("Missions", value="\n".join(exp["bullets"]), height=100, key=f"eb_{i}")
                col_s, col_d = st.columns([3,1])
                with col_s:
                    if st.button("💾 Sauvegarder", key=f"save_exp_{i}"):
                        st.session_state.edit_exp[i] = {"role":nr,"org":no,"period":np,"url":nu,"org_type":nt,"bullets":[b.strip() for b in nb.split("\n") if b.strip()]}
                        st.success("✅ Sauvegardé !"); st.rerun()
                with col_d:
                    if st.button("🗑️", key=f"del_exp_{i}", type="secondary"):
                        st.session_state.edit_exp.pop(i); st.rerun()

    with t3:
        for i, e in enumerate(st.session_state.edit_edu):
            with st.expander(f"**{e['deg']}** — {e['school']}", expanded=(i==0)):
                c1, c2 = st.columns([2,1])
                with c1:
                    nd = st.text_input("Diplôme", value=e["deg"], key=f"ed_{i}")
                    ns = st.text_input("École", value=e["school"], key=f"es_{i}")
                with c2:
                    ny = st.text_input("Années", value=e["yr"], key=f"ey_{i}")
                ndet = st.text_area("Cours", value=e["det"], key=f"edet_{i}", height=60)
                if st.button("💾 Sauvegarder", key=f"save_edu_{i}"):
                    st.session_state.edit_edu[i] = {"deg":nd,"school":ns,"yr":ny,"url":e.get("url",""),"det":ndet,"mention":""}
                    st.success("✅ Sauvegardé !"); st.rerun()

    with t4:
        updated_skills = {}
        for skill, level in list(st.session_state.edit_skills.items()):
            c1, c2, c3 = st.columns([3, 1, 0.5])
            with c1: nsn = st.text_input("", value=skill, key=f"sk_n_{skill}", label_visibility="collapsed")
            with c2: nsl = st.number_input("", min_value=0, max_value=100, value=level, key=f"sk_l_{skill}", label_visibility="collapsed")
            with c3:
                if st.button("🗑", key=f"sk_del_{skill}"):
                    d = dict(st.session_state.edit_skills); d.pop(skill, None)
                    st.session_state.edit_skills = d; st.rerun()
            updated_skills[nsn] = nsl
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1: new_sn = st.text_input("Nouvelle compétence", key="new_sk_n")
        with c2: new_sl = st.number_input("Niveau", 0, 100, 80, key="new_sk_l")
        if st.button("💾 Sauvegarder compétences", use_container_width=True, key="save_skills"):
            if new_sn.strip(): updated_skills[new_sn.strip()] = new_sl
            st.session_state.edit_skills = updated_skills
            st.success("✅ Sauvegardé !"); st.rerun()
        st.markdown("---")
        certs = st.session_state.get("edit_certifs", [])
        new_certs = st.text_area("Certifications (une par ligne)", value="\n".join(certs), height=80, key="edit_certifs_text")
        st.text_input("Outils informatiques", key="edit_tech")
        st.text_input("Intérêts", key="edit_interests")
        if st.button("💾 Sauvegarder certifications", use_container_width=True, key="save_certs"):
            st.session_state.edit_certifs = [l.strip() for l in new_certs.split("\n") if l.strip()]
            st.success("✅ Sauvegardé !")

    with t5:
        dists = list(st.session_state.edit_distinctions)
        for i, (icon_d, title_d, desc_d) in enumerate(dists):
            c1, c2, c3, c4 = st.columns([0.4, 1.8, 3.5, 0.4])
            with c1: ni = st.text_input("", value=icon_d, key=f"di_i_{i}", label_visibility="collapsed")
            with c2: nt = st.text_input("", value=title_d, key=f"di_t_{i}", label_visibility="collapsed")
            with c3: nd = st.text_input("", value=desc_d, key=f"di_d_{i}", label_visibility="collapsed")
            with c4:
                if st.button("🗑", key=f"di_del_{i}"):
                    st.session_state.edit_distinctions.pop(i); st.rerun()
        if st.button("💾 Sauvegarder distinctions", use_container_width=True, key="save_dists"):
            new_d = [(st.session_state.get(f"di_i_{i}", dists[i][0]),st.session_state.get(f"di_t_{i}", dists[i][1]),st.session_state.get(f"di_d_{i}", dists[i][2])) for i in range(len(dists))]
            st.session_state.edit_distinctions = new_d
            st.success("✅ Sauvegardé !"); st.rerun()

    with t6:
        st.text_input("Titre du mémoire", key="edit_memoir_title")
        st.text_area("Description", key="edit_memoir_desc", height=100)
        if st.button("💾 Sauvegarder mémoire", use_container_width=True, key="save_memoir"):
            st.success("✅ Sauvegardé !")

    with t7:
        st.text_area("Phrase de personnalité", key="edit_personality", height=80)
        if st.button("💾 Sauvegarder personnalité", use_container_width=True, key="save_personality"):
            st.success("✅ Sauvegardé !")
