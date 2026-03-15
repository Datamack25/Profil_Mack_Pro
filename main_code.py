import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
import io
import json
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors as rl_colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                  TableStyle, HRFlowable, KeepTogether, PageBreak)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

# ─── ANTHROPIC API KEY (intégrée) ──────────────────────────────────────────────
# Remplacez cette valeur par votre clé API Anthropic si vous en avez une
ANTHROPIC_API_KEY_DEFAULT = ""  # ex: "sk-ant-api03-..."

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
  .bio-period.phase5::before { background:linear-gradient(180deg,#00B4D8,#0077B6); }
  .bio-phase-label { font-size:0.72rem; letter-spacing:2px; text-transform:uppercase; font-weight:600; margin-bottom:6px; }
  .phase1 .bio-phase-label { color:#4A9EFF; }
  .phase2 .bio-phase-label { color:var(--gold); }
  .phase3 .bio-phase-label { color:var(--warn); }
  .phase4 .bio-phase-label { color:#9B59B6; }
  .phase5 .bio-phase-label { color:#00B4D8; }
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
  .save-btn button {
    background:linear-gradient(135deg,#2ECC71,#27AE60) !important;
    color:white !important;
  }
  #MainMenu,footer,[data-testid="stHeader"] { display:none !important; }
  .block-container { padding-top:2rem !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PERSISTENCE — sauvegarde locale en JSON
# ═══════════════════════════════════════════════════════════════════════════════
SAVE_FILE = "mackenson_profile_data.json"

def save_profile():
    """Sauvegarde toutes les données éditables dans un fichier JSON."""
    data = {k: st.session_state[k] for k in st.session_state
            if k.startswith("edit_")}
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return True

def load_profile():
    """Charge les données sauvegardées si elles existent."""
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# ═══════════════════════════════════════════════════════════════════════════════
# DONNÉES PAR DÉFAUT
# ═══════════════════════════════════════════════════════════════════════════════
DEFAULT_DATA = {
    "edit_name":     "Mackenson CINÉUS",
    "edit_title":    "Compliance Officer | Analyste Sécurité Financière (LCB-FT)",
    "edit_location": "Île-de-France, France",
    "edit_email":    "mackenson.cineus@email.com",
    "edit_phone":    "+33 6 XX XX XX XX",
    "edit_linkedin": "linkedin.com/in/mackenson-cineus",
    "edit_summary": (
        "Professionnel de la conformité financière et des marchés financiers, avec une double "
        "expérience en fintech de paiement (HiPay) et en banque privée (Delubac). MBA Trading "
        "& Marchés Financiers (ESLSCA Paris), Licence BFA (Université du Mans). Lauréat 1er Prix "
        "Hackathon Fintech Générations 2023 (France FinTech / Société Générale). Créateur du "
        "podcast INCLUTECH sur l'inclusion financière. Board Member Erasmus Expertise. Profil "
        "international Haïti / France. Trilingue : français, anglais, créole haïtien."
    ),
    "edit_cv_accroche": (
        "Compliance Officer & Analyste LCB-FT disposant d'une double expérience en fintech de "
        "paiement (HiPay SAS, agréé ACPR) et en banque privée (Banque Delubac & Cie). Expert "
        "AML/FT, KYC/KYB, KYS, déclarations Tracfin et veille réglementaire (ACPR, GAFI, CMF). "
        "Titulaire d'un MBA Finance de Marché (ESLSCA Paris). Lauréat 1er Prix Hackathon Fintech "
        "Générations 2023 — France FinTech / Société Générale. Trilingue : français (natif), "
        "anglais (courant B2/C1), créole haïtien (natif)."
    ),
    "edit_exp": [
        {
            "role":    "Compliance Officer",
            "org":     "HiPay · Levallois-Perret, France",
            "period":  "2024 – 2025",
            "url":     "https://hipay.com",
            "bullets": [
                "Gestion des alertes de conformité niveau 2 : analyse, investigation et traitement des dossiers à risque selon les procédures internes et les exigences réglementaires ACPR",
                "Traitement des dossiers KYS (Know Your Structure) : collecte documentaire, évaluation du risque structurel et décision de conformité pour les partenaires marchands",
                "Préparation, rédaction, soumission et archivage des déclarations de soupçon (DS) Tracfin auprès de la Cellule de Renseignement Financier nationale",
                "Veille réglementaire active (CMF, recommandations ACPR, normes GAFI/FATF) et élaboration des plans d'action associés pour mise en conformité",
                "Vérification des questionnaires de conformité partenaires, participation aux audits internes et contribution à la mise à jour de la documentation de risques LCB-FT",
            ],
        },
        {
            "role":    "Analyste Sécurité Financière — LCB-FT",
            "org":     "Banque Delubac & Cie · Paris",
            "period":  "2023 – 2024",
            "url":     "https://www.delubac.com",
            "bullets": [
                "Analyse et investigation des transactions suspectes (SAR/STR) : revue des alertes générées par les outils de monitoring, qualification du risque et rédaction des rapports d'analyse",
                "Évaluation des profils de risque KYC/KYB lors de l'entrée en relation et revues périodiques : collecte documentaire, vérification des bénéficiaires effectifs, scoring de risque",
                "Application opérationnelle des directives européennes AMLD5/AMLD6 : mise à jour des procédures internes, formation des équipes et suivi sous supervision ACPR/GAFI",
                "Participation aux audits de conformité internes et externes : préparation des dossiers, réponse aux demandes du superviseur et suivi des recommandations d'audit",
                "Accompagnement et mentorat de profils MBA Trading (ESLSCA) lors de leur insertion professionnelle dans le domaine de la conformité bancaire",
            ],
        },
        {
            "role":    "Co-Fondateur · Lauréat 1er Prix — Hackathon Fintech Générations",
            "org":     "France FinTech · Société Générale · Treezor · Paris",
            "period":  "Oct. 2023",
            "url":     "https://francefintech.org",
            "bullets": [
                "Co-conception et développement du projet Victoria : solution de financement innovante des rénovations énergétiques (DPE) pour les propriétaires à budget contraint",
                "Remporté la 1ère place devant plus de 1 500 participants à l'édition 2023 du Hackathon Fintech Générations (France FinTech / Société Générale / Treezor / Paris&Co)",
                "Pitch de la solution lors de l'événement Fintech R:Evolution devant investisseurs, dirigeants bancaires et écosystème fintech français",
                "Obtention d'un an de membership France FinTech et intégration dans le réseau fintech franco-européen",
            ],
        },
        {
            "role":    "Board Member",
            "org":     "Erasmus Expertise · International",
            "period":  "2021 – Présent",
            "url":     "https://erasmus-expertise.eu",
            "bullets": [
                "Membre du conseil d'administration d'Erasmus Expertise, ONG internationale dédiée au développement durable, à l'éducation et à l'inclusion sociale",
                "Participation à la gouvernance stratégique : validation des projets, définition des orientations et représentation institutionnelle internationale",
                "Contribution au projet ASPEC : développement de programmes éducatifs et d'inclusion pour les communautés vulnérables en Europe et en Haïti",
                "Réseau international d'experts et de décideurs dans les domaines de l'ESG, de la finance inclusive et des politiques publiques",
            ],
        },
        {
            "role":    "Project Manager · Fondateur — ANGAJMAN",
            "org":     "Association Jeunesse · Haïti",
            "period":  "2018 – 2019",
            "url":     "https://www.hultprize.org",
            "bullets": [
                "Fondation et direction d'ANGAJMAN, association promouvant l'engagement civique de la jeunesse haïtienne dans les 10 départements géographiques du pays",
                "Représentation d'Haïti au Hult Prize 2018 (surnommé le Nobel de l'entrepreneuriat étudiant) avec le projet WEISS : valorisation des déchets organiques en biogaz et fertilisant agricole",
                "Coordination de projets civiques multi-sites : planification, mobilisation des équipes bénévoles, gestion des ressources et reporting aux parties prenantes",
                "Engagement au Parlement Haïtien de la Jeunesse pour l'Eau et l'Assainissement (PHJEA), affilié au Parlement Mondial de l'Eau",
            ],
        },
    ],
    "edit_edu": [
        {
            "deg":    "MBA Trading & Marchés Financiers",
            "school": "ESLSCA Business School Paris",
            "yr":     "2021 – 2023",
            "url":    "https://www.eslsca.fr",
            "det":    "Gestion de portefeuille · Produits dérivés · Analyse quantitative · Conformité réglementaire · Risk management",
            "courses": [
                "Gestion de portefeuille & allocation d'actifs",
                "Produits dérivés : options, futures, swaps",
                "Analyse quantitative & modélisation financière",
                "Réglementation des marchés financiers (MiFID II, EMIR)",
                "Risk management & contrôle des risques de marché",
                "Finance comportementale & stratégies d'investissement",
            ],
        },
        {
            "deg":    "Licence Banque, Finance & Assurance",
            "school": "Université du Mans",
            "yr":     "2019 – 2021",
            "url":    "https://www.univ-lemans.fr",
            "det":    "Marchés bancaires · Risk management · Réglementation européenne · Droit bancaire · Instruments financiers",
            "courses": [
                "Marchés bancaires & financements structurés",
                "Risk management & analyse du risque de crédit",
                "Réglementation européenne bancaire (Bâle III/IV, CRD)",
                "Droit bancaire & conformité réglementaire",
                "Instruments financiers & techniques de couverture",
                "Analyse financière & diagnostic d'entreprise",
            ],
        },
        {
            "deg":    "Sciences Économiques & Gestion",
            "school": "INAGHEI · Université d'État d'Haïti",
            "yr":     "2014 – 2018",
            "url":    "https://www.ueh.edu.ht",
            "det":    "Économie · Gestion · Politiques publiques · Droit · Macroéconomie",
            "courses": [
                "Macroéconomie & économie internationale",
                "Économie du développement & politiques publiques",
                "Comptabilité générale & analyse financière",
                "Droit commercial & droit des affaires",
                "Gestion des organisations & management",
            ],
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
    "edit_lm_intro": (
        "De Port-au-Prince à Paris, mon parcours est celui d'une construction méthodique vers "
        "l'excellence en conformité financière. Compliance Officer chez HiPay (2024–2025) et "
        "Analyste LCB-FT chez Banque Delubac & Cie (2023–2024), titulaire d'un MBA Trading & "
        "Marchés Financiers (ESLSCA Paris) et lauréat du 1er Prix Hackathon Fintech Générations "
        "2023 (France FinTech / Société Générale), je me permets de soumettre ma candidature au "
        "sein de votre organisation."
    ),
    "edit_lm_para2": (
        "Chez HiPay — fintech de paiement agréée ACPR — j'ai géré les alertes de conformité "
        "niveau 2, traité les dossiers KYS, préparé les déclarations Tracfin et assuré la veille "
        "réglementaire (CMF, ACPR, GAFI). Chez Banque Delubac, j'ai analysé des transactions "
        "suspectes (SAR/STR), évalué les profils de risque KYC/KYB et appliqué les directives "
        "AMLD5/AMLD6 — deux environnements complémentaires qui m'ont conféré une maîtrise "
        "complète de la conformité bancaire et fintech."
    ),
    "edit_lm_para3": (
        "Au-delà de l'expertise technique, j'apporte une perspective distinctive : fondateur "
        "d'ANGAJMAN, représentant Haïti au Hult Prize, créateur du podcast INCLUTECH sur "
        "l'inclusion financière, et Board Member d'Erasmus Expertise. Cette double culture — "
        "entrepreneuriat social et finance institutionnelle — me permet d'aborder la conformité "
        "avec une rigueur analytique et une vision éthique rare dans un profil junior."
    ),
    "edit_lm_close": (
        "Convaincu que mon profil constituerait un atout réel pour votre organisation, je reste "
        "disponible pour un entretien à votre convenance et vous transmets en pièce jointe mon "
        "curriculum vitæ détaillé."
    ),
    "edit_bio_phases": [
        {
            "phase": "phase1",
            "label": "Phase 1 · 2014 – 2019",
            "title": "Haïti — Racines académiques & éveil entrepreneurial",
            "years": "INAGHEI · FDSE · Hult Prize 2018 · ANGAJMAN · PHJEA",
            "text": "Mackenson Cineus intègre l'INAGHEI (Institut National d'Administration de Gestion et des Hautes Études Internationales) et la FDSE à Port-au-Prince. Il enseigne à mi-temps en lycée et s'engage au Rotaract Club, conjuguant dès ses débuts exigence académique et responsabilité sociale. En 2018, il co-fonde ANGAJMAN, association promouvant l'implication citoyenne de la jeunesse haïtienne dans les 10 départements, et représente Haïti au Hult Prize avec le projet WEISS (biogaz et fertilisant agricole). Il milite également au Parlement Haïtien de la Jeunesse pour l'Eau et l'Assainissement (PHJEA), affilié au Parlement Mondial de l'Eau.",
            "tags": "INAGHEI · UEH, Hult Prize 2018, WEISS — Biogaz, ANGAJMAN, PHJEA, Rotaract",
        },
        {
            "phase": "phase2",
            "label": "Phase 2 · 2019 – 2021",
            "title": "France — Maîtriser les codes de la finance européenne",
            "years": "Université du Mans · Licence BFA · Erasmus Expertise · Podcast INCLUTECH",
            "text": "Mackenson s'installe en France et intègre l'Université du Mans en Licence Banque, Finance & Assurance (BFA) — analyse financière, marchés bancaires, réglementation européenne, risk management. En 2021, il rejoint le projet ASPEC d'Erasmus Expertise — ONG internationale dédiée au développement durable, l'éducation et l'inclusion sociale — dont il deviendra Board Member. Il lance simultanément son podcast INCLUTECH (Spotify & Apple Podcasts), explorant bi-mensuellement le rôle des fintechs dans l'inclusion financière mondiale.",
            "tags": "Université du Mans, Licence BFA, Erasmus Expertise, Podcast INCLUTECH, Spotify",
        },
        {
            "phase": "phase3",
            "label": "Phase 3 · 2021 – 2023",
            "title": "Paris — MBA élite & 1er Prix Hackathon France FinTech",
            "years": "ESLSCA Business School Paris · MBA Trading · Hackathon France FinTech",
            "text": "Mackenson rejoint l'ESLSCA Business School Paris pour un MBA spécialisé en Trading & Marchés Financiers — gestion de portefeuille, produits dérivés, analyse quantitative et réglementation des marchés. En octobre 2023, lors du Hackathon Fintech Générations organisé par France FinTech, Société Générale et Treezor, son équipe remporte la 1ère place avec Victoria — solution de financement des rénovations DPE. Récompense : pitch à Fintech R:Evolution (1 500 participants) et un an de membership France FinTech.",
            "tags": "MBA ESLSCA, Trading, Hackathon 2023 🥇, Victoria — DPE, France FinTech",
        },
        {
            "phase": "phase4",
            "label": "Phase 4 · 2023 – 2024",
            "title": "Banque Delubac — Analyste Sécurité Financière LCB-FT",
            "years": "Banque Delubac & Cie · Paris · LCB-FT / AML / AMLD6",
            "text": "Il intègre la Banque Delubac & Cie, institution bancaire privée française fondée en 1924, comme Analyste Sécurité Financière (LCB-FT). Il analyse les transactions suspectes (SAR/STR), évalue les profils de risque KYC/KYB, applique les directives AMLD5/AMLD6 et participe aux audits de conformité sous supervision ACPR. Cette expérience consolide sa maîtrise des processus LCB-FT en environnement bancaire réglementé.",
            "tags": "Banque Delubac, LCB-FT, AML · AMLD6, KYC/KYB, ACPR, Paris",
        },
        {
            "phase": "phase5",
            "label": "Phase 5 · 2024 – 2025",
            "title": "HiPay — Compliance Officer en Fintech de Paiement",
            "years": "HiPay · Levallois-Perret · Compliance · Tracfin · KYS · Paiements",
            "text": "HiPay est un prestataire de services de paiement omnicanal coté sur Euronext Growth (ALHYP), agréé par l'ACPR comme établissement de paiement, dont les clients incluent Veepee, Nocibé, Pizza Hut et Metro. Mackenson y rejoint le département Conformité à Levallois-Perret en tant que Compliance Officer. Ses responsabilités couvrent la gestion des alertes niveau 2, le traitement des dossiers KYS, la préparation des déclarations Tracfin, la vérification des questionnaires partenaires et la veille réglementaire (CMF, ACPR, GAFI). Cette expérience en fintech de paiement complète idéalement son expertise bancaire.",
            "tags": "HiPay · ALHYP, Compliance Officer, Tracfin, KYS, Paiements digitaux, ACPR/GAFI",
        },
    ],
    "edit_timeline": [
        {"year": "2014–2018", "title": "INAGHEI · Université d'État d'Haïti", "desc": "Sciences Économiques & Gestion · Faculté Droit & Sciences Éco", "url": "https://www.ueh.edu.ht", "icon": "🎓", "cat": "Éducation"},
        {"year": "2018", "title": "Hult Prize — Compétition Internationale", "desc": "Projet WEISS : transformation des déchets en biogaz & fertilisant agricole", "url": "https://www.hultprize.org", "icon": "🏆", "cat": "Entrepreneuriat"},
        {"year": "2018–2019", "title": "Parlement Haïtien Jeunesse pour l'Eau (PHJEA)", "desc": "Engagement citoyen — ressources hydriques · Parlement Mondial de l'Eau", "url": "https://www.worldwatercouncil.org", "icon": "🌊", "cat": "Social"},
        {"year": "2018–2019", "title": "Fondateur · Project Manager — ANGAJMAN", "desc": "Association jeunesse haïtienne — 10 départements · civique & environnemental", "url": "https://www.hultprize.org", "icon": "🤝", "cat": "Social"},
        {"year": "2019–2021", "title": "Université du Mans — Licence BFA", "desc": "Banque, Finance & Assurance — réglementation européenne, risk management", "url": "https://www.univ-lemans.fr", "icon": "🏫", "cat": "Éducation"},
        {"year": "2021–2023", "title": "ESLSCA Business School Paris — MBA", "desc": "Trading & Marchés Financiers — produits dérivés, gestion de portefeuille", "url": "https://www.eslsca.fr", "icon": "📈", "cat": "Éducation"},
        {"year": "2021–Présent", "title": "Board Member — Erasmus Expertise", "desc": "Gouvernance ONG : développement durable · éducation · inclusion sociale", "url": "https://erasmus-expertise.eu", "icon": "🌍", "cat": "Réseau"},
        {"year": "2021–Présent", "title": "Podcast INCLUTECH", "desc": "Finance & Inclusion Financière · bi-mensuel · Spotify & Apple Podcasts", "url": "https://open.spotify.com/show/5XvFdWYwhHWY3EguIhhf69", "icon": "🎙", "cat": "Réseau"},
        {"year": "Oct. 2023", "title": "🥇 Hackathon Fintech Générations — 1er Prix", "desc": "Projet Victoria (financement DPE) · France FinTech / Société Générale / Treezor", "url": "https://francefintech.org", "icon": "🚀", "cat": "Entrepreneuriat"},
        {"year": "2023–2024", "title": "Analyste LCB-FT — Banque Delubac & Cie", "desc": "Sécurité financière · AMLD5/AMLD6 · KYC/KYB · transactions suspectes", "url": "https://www.delubac.com", "icon": "🏦", "cat": "Professionnel"},
        {"year": "2024–2025", "title": "Compliance Officer — HiPay", "desc": "Fintech paiement · Tracfin · KYS · alertes N2 · veille réglementaire ACPR/GAFI", "url": "https://hipay.com", "icon": "💳", "cat": "Professionnel"},
    ],
}

# ─── INITIALISATION SESSION STATE ─────────────────────────────────────────────
def _init_state():
    saved = load_profile()
    for k, v in DEFAULT_DATA.items():
        if k not in st.session_state:
            st.session_state[k] = saved.get(k, v)

_init_state()

def _P():
    return {
        "name":     st.session_state.edit_name,
        "title":    st.session_state.edit_title,
        "location": st.session_state.edit_location,
        "email":    st.session_state.edit_email,
        "phone":    st.session_state.edit_phone,
        "linkedin": st.session_state.edit_linkedin,
        "summary":  st.session_state.edit_summary,
    }

# ─── DONNÉES STATIQUES ────────────────────────────────────────────────────────
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

PLATFORMS = [
    {"icon": "💼", "name": "LinkedIn", "desc": "Profil professionnel complet — expériences HiPay & Delubac, réseau finance/fintech parisien.", "url": "https://www.linkedin.com/in/mackenson-cineus", "label": "Voir le profil →"},
    {"icon": "💳", "name": "HiPay", "desc": "Fintech paiement omnicanal cotée (ALHYP) — Mackenson y était Compliance Officer 2024–2025.", "url": "https://hipay.com", "label": "Site HiPay →"},
    {"icon": "🏦", "name": "Banque Delubac & Cie", "desc": "Banque privée indépendante fondée en 1924 — Analyste LCB-FT 2023–2024.", "url": "https://www.delubac.com", "label": "Site Delubac →"},
    {"icon": "🚀", "name": "France FinTech", "desc": "Association de référence fintech française — Lauréat Hackathon 2023, membre actif.", "url": "https://francefintech.org", "label": "France FinTech →"},
    {"icon": "🏆", "name": "Hult Prize Foundation", "desc": "Compétition internationale entrepreneuriat social — Haïti 2018 · Projet WEISS.", "url": "https://www.hultprize.org", "label": "Hult Prize →"},
    {"icon": "🎓", "name": "ESLSCA Business School Paris", "desc": "MBA Trading & Marchés Financiers 2021–2023.", "url": "https://www.eslsca.fr", "label": "ESLSCA →"},
    {"icon": "🏫", "name": "Université du Mans", "desc": "Licence Banque-Finance-Assurance 2019–2021.", "url": "https://www.univ-lemans.fr", "label": "Université du Mans →"},
    {"icon": "🎙", "name": "Podcast INCLUTECH", "desc": "Finance & Inclusion Financière — Spotify & Apple Podcasts · bi-mensuel.", "url": "https://open.spotify.com/show/5XvFdWYwhHWY3EguIhhf69", "label": "Écouter →"},
    {"icon": "🌍", "name": "Erasmus Expertise", "desc": "Board Member — développement durable, éducation, inclusion sociale.", "url": "https://erasmus-expertise.eu", "label": "Erasmus Expertise →"},
    {"icon": "📸", "name": "Instagram", "desc": "@mackenson_cineus — présence personnelle et professionnelle.", "url": "https://instagram.com/mackenson_cineus", "label": "Instagram →"},
]

REGULATORS = [
    ("🇫🇷", "ACPR", "Régulateur bancaire & paiement français — LCB-FT", "https://acpr.banque-france.fr"),
    ("🌐", "FATF / GAFI", "Normes mondiales anti-blanchiment", "https://www.fatf-gafi.org"),
    ("💰", "Tracfin", "Cellule de Renseignement Financier française", "https://www.economie.gouv.fr/tracfin"),
    ("📊", "AMF", "Autorité des Marchés Financiers", "https://www.amf-france.org"),
]

# ═══════════════════════════════════════════════════════════════════════════════
# CLAUDE AI API
# ═══════════════════════════════════════════════════════════════════════════════
def call_claude(prompt: str, system: str = "") -> str:
    api_key = st.session_state.get("anthropic_api_key_input", "").strip() or ANTHROPIC_API_KEY_DEFAULT
    if not api_key:
        return ""
    try:
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": "claude-opus-4-5",
            "max_tokens": 1500,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            payload["system"] = system
        r = requests.post("https://api.anthropic.com/v1/messages",
                          json=payload, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.json()["content"][0]["text"]
        return ""
    except Exception:
        return ""

# ═══════════════════════════════════════════════════════════════════════════════
# PDF COLORS & HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
NAVY_C   = rl_colors.HexColor('#0D1B2A')
GOLD_C   = rl_colors.HexColor('#C9A84C')
GRAY_D_C = rl_colors.HexColor('#333333')
GRAY_M_C = rl_colors.HexColor('#555555')
GRAY_L_C = rl_colors.HexColor('#999999')
ACCENT_C = rl_colors.HexColor('#4A9EFF')
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
    canvas.setFillColorRGB(0.05, 0.11, 0.20)
    canvas.rect(0, H-1.55*cm, W, 1.55*cm, fill=1, stroke=0)
    canvas.setFillColor(GOLD_C)
    canvas.rect(0, H-1.55*cm, W, 0.09*cm, fill=1, stroke=0)
    canvas.setFillColor(rl_colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(1.8*cm, H-1.0*cm, "CINÉUS Mackenson")
    canvas.setFillColor(GOLD_C)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(5.8*cm, H-1.0*cm, "Finance · Compliance · Fintech · Paris")
    canvas.setFillColorRGB(0.05, 0.11, 0.20)
    canvas.rect(0, 0, W, 0.85*cm, fill=1, stroke=0)
    canvas.setFillColor(GOLD_C)
    canvas.rect(0, 0.85*cm, W, 0.07*cm, fill=1, stroke=0)
    canvas.setFillColor(rl_colors.HexColor('#888888'))
    canvas.setFont("Helvetica", 7)
    canvas.drawString(1.8*cm, 0.3*cm,
        "linkedin.com/in/mackenson-cineus  ·  Podcast INCLUTECH  ·  @mackenson_cineus")
    canvas.setFillColor(GOLD_C)
    canvas.drawRightString(W-1.8*cm, 0.3*cm, f"Page {doc.page}")
    canvas.restoreState()

# ═══════════════════════════════════════════════════════════════════════════════
# CV PDF — 1 PAGE, CENTRÉ, FORMAT FINANCE CLASSIQUE
# ═══════════════════════════════════════════════════════════════════════════════
def generate_cv_pdf(poste="", entreprise="", secteur="") -> bytes:
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.pdfbase.pdfmetrics import stringWidth

    buf = io.BytesIO()
    W, H = A4

    ss = st.session_state
    name     = ss.get("edit_name",        "Mackenson CINÉUS")
    cv_title = ss.get("edit_title",       "Compliance Officer | Analyste LCB-FT")
    location = ss.get("edit_location",    "Île-de-France, France")
    linkedin = ss.get("edit_linkedin",    "linkedin.com/in/mackenson-cineus")
    email    = ss.get("edit_email",       "mackenson.cineus@email.com")
    phone    = ss.get("edit_phone",       "+33 6 XX XX XX XX")
    exps     = ss.get("edit_exp",         [])
    edus     = ss.get("edit_edu",         [])
    skills_d = ss.get("edit_skills",      {})
    accroche = ss.get("edit_cv_accroche", "")

    ML = 50; MR = 50; MT = 52; MB = 30
    TW = W - ML - MR

    BLACK = (0.0, 0.0, 0.0)
    NAVY  = (0.05, 0.11, 0.20)
    GRAY  = (0.35, 0.35, 0.35)
    LGRAY = (0.60, 0.60, 0.60)
    LINK  = (0.10, 0.30, 0.65)

    c = rl_canvas.Canvas(buf, pagesize=A4)

    def sw(s, fn, fs): return stringWidth(str(s), fn, fs)
    def setf(*rgb): c.setFillColorRGB(*rgb)
    def sets(*rgb): c.setStrokeColorRGB(*rgb)

    def wrap(txt, x, y, mw, fn, fs, lh, color=BLACK):
        c.setFillColorRGB(*color)
        c.setFont(fn, fs)
        words = str(txt).split()
        line = ""
        for w in words:
            test = (line + " " + w).strip()
            if sw(test, fn, fs) <= mw:
                line = test
            else:
                if line:
                    c.drawString(x, y, line)
                    y -= lh
                line = w
        if line:
            c.drawString(x, y, line)
            y -= lh
        return y

    def section_header(label, y):
        c.setFont("Helvetica-Bold", 9.5)
        setf(*NAVY)
        lbl = label.upper()
        c.drawString(ML, y, lbl)
        sets(*NAVY); c.setLineWidth(0.7)
        c.line(ML, y - 3, ML + TW, y - 3)
        return y - 13

    def bullet(txt, y, max_bullets=None):
        c.setFont("Helvetica", 8.8)
        setf(*BLACK)
        c.drawString(ML + 8, y, "•")
        y2 = wrap(txt, ML + 18, y, TW - 18, "Helvetica", 8.8, 10.5)
        return y2

    # ── EN-TÊTE CENTRÉ ─────────────────────────────────────────────
    y = H - MT

    # Ligne dorée décorative en haut
    sets(0.787, 0.659, 0.298)
    c.setLineWidth(1.5)
    c.line(ML, y + 2, ML + TW, y + 2)
    y -= 4

    # NOM centré, grand
    c.setFont("Times-Bold", 22)
    setf(*NAVY)
    name_upper = name.upper()
    c.drawCentredString(W/2, y, name_upper)
    y -= 20

    # Titre centré
    target_title = poste if poste else cv_title
    c.setFont("Times-Italic", 11)
    setf(0.30, 0.47, 0.70)
    c.drawCentredString(W/2, y, target_title)
    y -= 14

    # Coordonnées centrées sur une ligne
    c.setFont("Helvetica", 8.5)
    setf(*GRAY)
    coord_line = f"{location}  ·  {phone}  ·  {email}  ·  {linkedin}"
    c.drawCentredString(W/2, y, coord_line)
    y -= 11

    # Ligne sociale centrée
    c.setFont("Helvetica", 8)
    setf(*LGRAY)
    c.drawCentredString(W/2, y, "Podcast INCLUTECH (Spotify & Apple Podcasts)  ·  @mackenson_cineus")
    y -= 10

    # Trait séparateur double
    sets(0.787, 0.659, 0.298); c.setLineWidth(1.5)
    c.line(ML, y, ML + TW, y)
    y -= 3
    sets(*LGRAY); c.setLineWidth(0.3)
    c.line(ML, y, ML + TW, y)
    y -= 11

    # ── PROFIL ─────────────────────────────────────────────────────
    y = section_header("Profil Professionnel", y)
    acc = accroche or (
        "Compliance Officer & Analyste LCB-FT — double expérience en fintech de paiement "
        "(HiPay SAS, ACPR) et banque privée (Banque Delubac & Cie). Expert AML/FT, KYC/KYB, "
        "KYS, déclarations Tracfin et veille réglementaire (ACPR, GAFI, CMF). MBA Marchés "
        "Financiers ESLSCA Paris. Lauréat 1er Prix Hackathon Fintech Générations 2023.")
    y = wrap(acc, ML, y, TW, "Helvetica", 8.8, 11)
    y -= 8

    # ── EXPÉRIENCES ────────────────────────────────────────────────
    y = section_header("Expériences Professionnelles", y)

    for exp in exps[:5]:
        if y < MB + 55: break
        role   = exp.get("role",   "")
        org    = exp.get("org",    "")
        period = exp.get("period", "")
        bullets_list = exp.get("bullets", [])

        org_parts = org.split("·")
        org_name  = org_parts[0].strip()
        org_loc   = (org_parts[-1].strip() if len(org_parts) > 1 else "France")

        # Ligne org + rôle (gauche) | période (droite)
        c.setFont("Helvetica-Bold", 9.2)
        setf(*NAVY)
        c.drawString(ML, y, f"{org_name}  —  {role}")
        c.setFont("Helvetica-Oblique", 8.5)
        setf(*GRAY)
        c.drawRightString(ML + TW, y, f"{org_loc}  ·  {period}")
        y -= 12

        for b in bullets_list[:5]:
            if y < MB + 35: break
            y = bullet(b, y)

        y -= 5

    # ── FORMATIONS ─────────────────────────────────────────────────
    if y > MB + 75:
        y = section_header("Formations Académiques", y)
        for edu in edus:
            if y < MB + 45: break
            deg    = edu.get("deg",     "")
            school = edu.get("school",  "")
            yr     = edu.get("yr",      "")
            courses = edu.get("courses", [])
            det     = edu.get("det",    "")

            school_parts = school.split("·")
            school_name  = school_parts[0].strip()

            c.setFont("Helvetica-Bold", 9.2)
            setf(*NAVY)
            c.drawString(ML, y, f"{school_name}  —  {deg}")
            c.setFont("Helvetica-Oblique", 8.5)
            setf(*GRAY)
            c.drawRightString(ML + TW, y, yr)
            y -= 12

            # Matières principales (liste compacte)
            course_list = courses[:5] if courses else []
            if course_list:
                c.setFont("Helvetica", 8.3)
                setf(*GRAY)
                courses_str = "  ·  ".join(course_list)
                y = wrap(f"Matières : {courses_str}", ML + 8, y, TW - 8, "Helvetica", 8.3, 10.5)
            elif det:
                c.setFont("Helvetica", 8.3)
                setf(*GRAY)
                y = wrap(det, ML + 8, y, TW - 8, "Helvetica", 8.3, 10.5)

            y -= 5

    # ── COMPÉTENCES & CERTIFICATIONS ───────────────────────────────
    if y > MB + 15:
        y = section_header("Compétences, Certifications & Langues", y)

        skills_keys = list(skills_d.keys())
        comp_str = "  ·  ".join(skills_keys[:6]) if skills_keys else "LCB-FT · KYC/KYB · AML · Tracfin"

        lines = [
            ("Expertise LCB-FT",          comp_str),
            ("Outils & Systèmes",          "Excel avancé · Python · Bloomberg · VBA · Pack Office · Looker Studio"),
            ("Certifications",             "MBA Trading & Marchés Financiers (ESLSCA) · Licence BFA · En cours : CAMS · AMF"),
            ("Langues",                    "Français (Natif) · Créole haïtien (Natif) · Anglais (Courant — B2/C1)"),
            ("Récompenses & Distinctions", "1er Prix Hackathon Fintech Générations 2023 (France FinTech / SG) · Hult Prize 2018 (Haïti)"),
        ]
        for lbl, val in lines:
            if y < MB: break
            c.setFont("Helvetica-Bold", 8.8)
            setf(*BLACK)
            lbl_full = f"{lbl} : "
            c.drawString(ML + 6, y, lbl_full)
            lw = sw(lbl_full, "Helvetica-Bold", 8.8)
            y = wrap(val, ML + 6 + lw, y, TW - 6 - lw, "Helvetica", 8.8, 10.5)

    # Trait bas
    sets(0.787, 0.659, 0.298); c.setLineWidth(1.0)
    c.line(ML, MB - 4, ML + TW, MB - 4)
    c.setFont("Helvetica", 6.5)
    setf(*LGRAY)
    c.drawCentredString(W/2, MB - 13, f"{name}  ·  {location}  ·  {email}  ·  {linkedin}")

    c.save()
    buf.seek(0)
    return buf.read()

# ═══════════════════════════════════════════════════════════════════════════════
# LETTRE DE MOTIVATION PDF
# ═══════════════════════════════════════════════════════════════════════════════
def generate_lettre_pdf(poste="", entreprise="", secteur="", style_lm="",
                         contexte="", ai_text="") -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=2.0*cm, rightMargin=2.0*cm,
        topMargin=2.2*cm, bottomMargin=1.6*cm)

    ss = st.session_state
    name      = ss.get("edit_name",     "Mackenson CINÉUS")
    title_lm  = ss.get("edit_title",    "Compliance Officer | LCB-FT")
    location  = ss.get("edit_location", "Île-de-France, France")
    linkedin  = ss.get("edit_linkedin", "linkedin.com/in/mackenson-cineus")
    email     = ss.get("edit_email",    "mackenson.cineus@email.com")
    phone     = ss.get("edit_phone",    "+33 6 XX XX XX XX")
    p_intro   = ss.get("edit_lm_intro", "")
    p2        = ss.get("edit_lm_para2", "")
    p3        = ss.get("edit_lm_para3", "")
    p_close   = ss.get("edit_lm_close", "")

    story = []
    hl = Paragraph(
        f"<b>{name}</b><br/>"
        f"<font color='#C9A84C'>{title_lm}</font><br/>"
        f"{location} · {phone}<br/>{email}<br/>{linkedin}",
        _s('hl', fontSize=8.8, leading=13))
    hr = Paragraph(
        f"<b>Direction des Ressources Humaines</b><br/>"
        f"{entreprise or '[Entreprise]'}<br/>{secteur or '[Secteur]'}<br/>France",
        _s('hr', fontSize=8.8, leading=13, alignment=TA_RIGHT))
    ht = Table([[hl, hr]], colWidths=[9*cm, 8.7*cm])
    ht.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'), ('TOPPADDING',(0,0),(-1,-1),0)]))
    story.append(ht)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Paris, le 14 mars 2026",
                            _s('dt', fontSize=8.5, textColor=GRAY_M_C, alignment=TA_RIGHT)))
    story.append(Spacer(1, 0.3*cm))

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
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Madame, Monsieur,", _s('sal', fontSize=9.3, spaceAfter=10)))

    body_style = _s('body', fontSize=9.2, leading=14.5, alignment=TA_JUSTIFY, spaceAfter=10)

    if ai_text and len(ai_text) > 100:
        for para in ai_text.split("\n\n"):
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
    else:
        intro = p_intro or (
            f"De Port-au-Prince à Paris, mon parcours est celui d'une construction méthodique "
            f"vers l'excellence en conformité financière. Compliance Officer chez <b>HiPay</b> "
            f"(2024–2025) et Analyste LCB-FT chez <b>Banque Delubac & Cie</b> (2023–2024), "
            f"titulaire d'un <b>MBA Trading & Marchés Financiers</b> (ESLSCA Paris) et lauréat "
            f"du <b>1er Prix Hackathon Fintech Générations 2023</b> (France FinTech / Société "
            f"Générale), je me permets de soumettre ma candidature"
            f"{' au poste de ' + poste if poste else ''}.")
        p2_txt = p2 or (
            f"Chez HiPay — fintech de paiement agréée ACPR — j'ai géré les alertes de "
            f"conformité niveau 2, traité les dossiers KYS, préparé les déclarations Tracfin "
            f"et assuré la veille réglementaire. Chez Banque Delubac, j'ai analysé des "
            f"transactions suspectes (SAR/STR), évalué les profils de risque KYC/KYB et "
            f"appliqué les directives AMLD5/AMLD6.")
        p3_txt = p3 or (
            f"Au-delà de l'expertise technique, j'apporte une perspective distinctive : "
            f"fondateur d'<b>ANGAJMAN</b>, représentant Haïti au <b>Hult Prize</b>, "
            f"créateur du podcast <b>INCLUTECH</b> et Board Member d'<b>Erasmus Expertise</b>.")
        pc_txt = p_close or (
            f"Convaincu que mon profil constituerait un atout réel pour "
            f"{'votre organisation ' + entreprise if entreprise else 'votre organisation'}, "
            f"je reste disponible pour un entretien à votre convenance.")

        for txt in [intro, p2_txt, p3_txt, pc_txt]:
            story.append(Paragraph(txt, body_style))

    story.append(Paragraph(
        "Dans cette attente, je vous prie d'agréer l'expression de mes salutations les plus respectueuses.",
        _s('close', fontSize=9.2, leading=14, alignment=TA_JUSTIFY, spaceAfter=18)))
    story.append(Paragraph(f"<b>{name}</b>", _s('sig', fontSize=10.5, textColor=NAVY_C, spaceAfter=2)))
    story.append(Paragraph(f"<font color='#C9A84C'>{title_lm}</font>",
                            _s('sig2', fontSize=8.5, spaceAfter=0)))
    story.append(Spacer(1, 0.5*cm))
    story.append(_hr(GRAY_L_C, 0.4))
    story.append(Paragraph(
        "<i>PJ : Curriculum Vitæ · Références disponibles sur demande</i>",
        _s('pj', fontSize=7.5, textColor=GRAY_L_C)))

    doc.build(story, onFirstPage=_page_frame, onLaterPages=_page_frame)
    buf.seek(0); return buf.read()

# ═══════════════════════════════════════════════════════════════════════════════
# BIOGRAPHIE PDF
# ═══════════════════════════════════════════════════════════════════════════════
def generate_bio_pdf() -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=1.7*cm, rightMargin=1.7*cm,
        topMargin=2.0*cm, bottomMargin=1.4*cm)

    ss = st.session_state
    name     = ss.get("edit_name",     "Mackenson CINÉUS")
    title_b  = ss.get("edit_title",    "Compliance Officer | LCB-FT")
    bio_phases = ss.get("edit_bio_phases", DEFAULT_DATA["edit_bio_phases"])

    story = []

    # Header
    t_data = [[
        Paragraph(f'<font name="Helvetica-Bold" size="24" color="#0D1B2A">{name}</font>',
                  _s('bn', fontSize=24, leading=28, spaceAfter=0)),
        Paragraph('<font color="#C9A84C" size="8">Finance · Compliance · Fintech · Paris</font>',
                  _s('bs', fontSize=8, alignment=TA_RIGHT, spaceAfter=0, textColor=GOLD_C))
    ]]
    story.append(Table(t_data, colWidths=[11.5*cm, 5.3*cm]))
    story.append(_hr(NAVY_C, 2.0, before=3, after=4))
    story.append(Paragraph(
        f'<i>"{title_b} — De Port-au-Prince à Levallois-Perret. Parcours construit avec intention."</i>',
        _s('q', fontSize=8.5, fontName='Helvetica-Oblique', textColor=NAVY_M_C,
           leading=12.5, leftIndent=6, spaceAfter=8, backColor=CREAM_C)))

    # KPI
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
        ('LINEAFTER',(0,0),(3,-1),0.3, GRAY_L_C),
    ]))
    story.append(kpi_t)
    story.append(Spacer(1, 6))

    PHASE_COLORS = {
        "phase1": "#4A9EFF", "phase2": "#C9A84C",
        "phase3": "#E67E22", "phase4": "#9B59B6", "phase5": "#00B4D8",
    }

    def phase_block(bp):
        color_hex = PHASE_COLORS.get(bp.get("phase","phase1"), "#C9A84C")
        label = bp.get("label","")
        title = bp.get("title","")
        text  = bp.get("text","")
        tags_str = bp.get("tags","")
        tags_list = [t.strip() for t in tags_str.split(",") if t.strip()]

        paras = []
        for p in text.split("\n\n") if "\n\n" in text else [text]:
            if p.strip():
                paras.append(Paragraph(p.strip(), _s('pb', fontSize=8.2, leading=12.5,
                                                       alignment=TA_JUSTIFY, spaceAfter=4)))
        if tags_list:
            paras.append(Paragraph(
                "  ·  ".join(f"<b>{t}</b>" for t in tags_list),
                _s('tg', fontSize=7, textColor=GRAY_M_C, spaceAfter=0)))

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
        inner_rows = [[p] for p in paras]
        inner = Table(inner_rows, colWidths=[16.6*cm])
        inner.setStyle(TableStyle([
            ('TOPPADDING',(0,0),(-1,-1),0), ('BOTTOMPADDING',(0,0),(-1,-1),0),
            ('LEFTPADDING',(0,0),(-1,-1),8), ('RIGHTPADDING',(0,0),(-1,-1),0),
        ]))
        return KeepTogether([header, inner, Spacer(1, 5)])

    # Phases 1-3
    for bp in bio_phases[:3]:
        story.append(phase_block(bp))

    story.append(PageBreak())

    # Phases 4-5
    for bp in bio_phases[3:]:
        story.append(phase_block(bp))

    # Synthèse
    story.append(_hr(NAVY_C, 1.5, before=4, after=4))
    story.append(Paragraph('<b><font color="#0D1B2A" size="10">Présences en ligne & Sources</font></b>',
                            _s('sh2', fontSize=10, spaceAfter=6)))

    links = [
        ("LinkedIn", "linkedin.com/in/mackenson-cineus", "500+ connexions · Réseau finance/fintech"),
        ("HiPay", "hipay.com", "Employeur 2024–2025 · Euronext Growth ALHYP"),
        ("Banque Delubac", "delubac.com", "Employeur 2023–2024 · Banque privée 1924"),
        ("INCLUTECH Spotify", "open.spotify.com/show/5XvFdWYwhHWY3EguIhhf69", "Podcast bi-mensuel"),
        ("France FinTech", "francefintech.org", "Lauréat Hackathon 2023"),
        ("ESLSCA Paris", "eslsca.fr", "MBA Trading 2021–2023"),
        ("Université du Mans", "univ-lemans.fr", "Licence BFA 2019–2021"),
        ("Erasmus Expertise", "erasmus-expertise.eu", "Board Member"),
        ("ACPR", "acpr.banque-france.fr", "Régulateur bancaire/paiement"),
        ("Tracfin", "economie.gouv.fr/tracfin", "Cellule Renseignement Financier"),
        ("GAFI / FATF", "fatf-gafi.org", "Normes mondiales anti-blanchiment"),
        ("Instagram", "instagram.com/mackenson_cineus", "@mackenson_cineus"),
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

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
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
        "✏️ Édition — Informations Générales",
        "💼 Édition — Expériences",
        "🎓 Édition — Formation",
        "⚡ Édition — Compétences",
        "✉️ Édition — Lettre de Motivation",
        "📖 Édition — Biographie",
        "📋 Édition — CV (Accroche & Contenu)",
    ], label_visibility="collapsed")

    st.divider()
    st.markdown("<div style='font-size:0.8rem;color:#C9A84C;font-weight:600;margin-bottom:4px;'>🔑 Clé API Anthropic</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.7rem;opacity:0.55;margin-bottom:6px;'>Optionnelle — pour la génération IA de lettres</div>", unsafe_allow_html=True)
    api_key_input = st.text_input("Clé API", type="password",
                                   placeholder="sk-ant-... (optionnel)",
                                   label_visibility="collapsed",
                                   key="anthropic_api_key_input")
    if api_key_input:
        st.markdown("<div style='font-size:0.7rem;color:#2ECC71;'>✅ Clé renseignée</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("<div style='font-size:0.75rem;opacity:0.5;text-align:center;padding:10px;'>© 2025 Mackenson Cineus<br>Tous droits réservés</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER — BOUTON SAUVEGARDER GLOBAL
# ═══════════════════════════════════════════════════════════════════════════════
def save_button(key_suffix=""):
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button(f"💾 Sauvegarder les modifications", key=f"global_save_{key_suffix}", use_container_width=True):
            if save_profile():
                st.success("✅ Profil sauvegardé ! Toutes les modifications sont persistées.")
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — PROFIL & BIOGRAPHIE
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Profil & Biographie":
    P = _P()
    bio_phases = st.session_state.get("edit_bio_phases", DEFAULT_DATA["edit_bio_phases"])

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

    cols = st.columns(5)
    kpis = [
        ("2",  "Postes conformité", "#C9A84C"),
        ("3",  "Pays traversés",    "#4A9EFF"),
        ("2",  "Diplômes sup.",     "#2ECC71"),
        ("🥇", "Hackathon 2023",   "#E67E22"),
        ("🎙", "Podcast INCLUTECH","#9B59B6"),
    ]
    for col, (val, lbl, color) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-top:3px solid {color};">
              <span class="metric-value" style="color:{color};font-size:2rem;">{val}</span>
              <div class="metric-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_bio, col_side = st.columns([3, 1])

    with col_bio:
        st.markdown('<p class="section-header">Biographie — Parcours en 5 phases</p>', unsafe_allow_html=True)
        for period in bio_phases:
            tags_list = [t.strip() for t in period.get("tags","").split(",") if t.strip()]
            tags_html = "".join(f'<span class="bio-tag">{t}</span>' for t in tags_list)
            text = period.get("text","")
            paras = text.split("\n\n") if "\n\n" in text else [text]
            paras_html = "".join(f'<p style="margin:0 0 12px 0;">{p.strip()}</p>' for p in paras if p.strip())
            st.markdown(f"""
            <div class="bio-period {period.get('phase','phase1')}">
              <div class="bio-phase-label">{period.get('label','')}</div>
              <div class="bio-period-title">{period.get('title','')}</div>
              <div class="bio-period-years">📍 {period.get('years','')}</div>
              <div class="bio-period-text">{paras_html}</div>
              <div style="margin-top:12px;">{tags_html}</div>
            </div>""", unsafe_allow_html=True)

    with col_side:
        st.markdown('<p class="section-header" style="font-size:1.2rem;">📥 Documents PDF</p>', unsafe_allow_html=True)
        for icon, title, desc in [
            ("📋", "CV Finance", "1 page · Format banking"),
            ("✉️", "Lettre de Motivation", "1 page · Format Harvard"),
            ("📖", "Biographie", "5 phases · 2 pages"),
        ]:
            st.markdown(f"""
            <div style="background:var(--navy-mid);border:1px solid rgba(201,168,76,0.15);
                        border-radius:10px;padding:12px;margin-bottom:10px;">
              <div style="font-size:1.3rem;">{icon}</div>
              <div style="font-size:0.88rem;font-weight:600;color:var(--gold);margin:3px 0 1px;">{title}</div>
              <div style="font-size:0.75rem;opacity:0.6;">{desc}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<br><p class="section-header" style="font-size:1.2rem;">🔗 Liens Rapides</p>', unsafe_allow_html=True)
        for icon, nm, url in [
            ("💼","LinkedIn","https://linkedin.com/in/mackenson-cineus"),
            ("💳","HiPay","https://hipay.com"),
            ("🏦","Banque Delubac","https://www.delubac.com"),
            ("🎙","INCLUTECH","https://open.spotify.com/show/5XvFdWYwhHWY3EguIhhf69"),
            ("🚀","France FinTech","https://francefintech.org"),
            ("📸","Instagram","https://instagram.com/mackenson_cineus"),
        ]:
            st.markdown(f"""
            <a href="{url}" target="_blank" style="text-decoration:none;">
              <div style="display:flex;align-items:center;gap:10px;
                          background:var(--navy-mid);border:1px solid rgba(255,255,255,0.07);
                          border-radius:8px;padding:8px 12px;margin-bottom:7px;">
                <span style="font-size:1rem;">{icon}</span>
                <span style="font-size:0.82rem;color:var(--gold);">{nm}</span>
                <span style="margin-left:auto;font-size:0.7rem;opacity:0.4;">↗</span>
              </div>
            </a>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — PARCOURS & COMPÉTENCES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "⏱ Parcours & Compétences":
    st.markdown('<p class="section-header">Parcours chronologique & Compétences</p>', unsafe_allow_html=True)
    timeline = st.session_state.get("edit_timeline", DEFAULT_DATA["edit_timeline"])
    col1, col2 = st.columns([3, 2])

    with col1:
        cats = ["Tous"] + sorted(set(t.get("cat","") for t in timeline))
        fc = st.selectbox("Filtrer", cats, label_visibility="collapsed")
        items = timeline if fc == "Tous" else [t for t in timeline if t.get("cat","") == fc]
        for item in items:
            st.markdown(f"""
            <div class="timeline-item">
              <div class="timeline-year">{item.get('icon','')} {item.get('year','')} · {item.get('cat','')}</div>
              <div class="timeline-title">{item.get('title','')}</div>
              <div class="timeline-desc">{item.get('desc','')}</div>
            </div>""", unsafe_allow_html=True)

    with col2:
        live_skills = st.session_state.get("edit_skills", SKILLS)
        st.markdown('<p class="section-header">Compétences</p>', unsafe_allow_html=True)
        for skill, level in live_skills.items():
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
        ls = st.session_state.get("edit_skills", SKILLS)
        sn = list(ls.keys()); sv = list(ls.values())
        fig = go.Figure(go.Scatterpolar(r=sv+[sv[0]], theta=sn+[sn[0]], fill='toself',
            fillcolor='rgba(201,168,76,0.15)', line=dict(color='#C9A84C', width=2), marker=dict(color='#C9A84C', size=8)))
        fig.update_layout(polar=dict(bgcolor='rgba(26,46,66,0.5)',
            radialaxis=dict(visible=True, range=[0,100], gridcolor='rgba(255,255,255,0.1)', color='#F5F0E8'),
            angularaxis=dict(gridcolor='rgba(255,255,255,0.1)', color='#F5F0E8', tickfont=dict(size=11))),
            paper_bgcolor='rgba(0,0,0,0)', font=dict(family='DM Sans', color='#F5F0E8'),
            title=dict(text='Radar des Compétences', font=dict(color='#C9A84C', size=16)), height=480)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        df = pd.DataFrame([
            {"A": "2014", "N": 10, "E": "INAGHEI Haïti"},
            {"A": "2018", "N": 35, "E": "Hult Prize — WEISS"},
            {"A": "2019", "N": 52, "E": "Univ. du Mans — BFA"},
            {"A": "2021", "N": 68, "E": "ESLSCA MBA Paris"},
            {"A": "2022", "N": 78, "E": "France FinTech"},
            {"A": "2023", "N": 88, "E": "Banque Delubac"},
            {"A": "2024", "N": 95, "E": "HiPay Compliance"},
        ])
        fig2 = go.Figure(go.Scatter(x=df["A"], y=df["N"], mode='lines+markers+text',
            line=dict(color='#C9A84C', width=3),
            marker=dict(size=14, color='#C9A84C', line=dict(color='#1A2E42', width=3)),
            text=df["E"], textposition='top center', textfont=dict(size=9, color='#F5F0E8')))
        fig2.update_layout(title=dict(text='Progression de Carrière', font=dict(color='#C9A84C', size=16)),
            yaxis=dict(title='Développement (%)', range=[0,110], gridcolor='rgba(255,255,255,0.07)', color='#F5F0E8'),
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
        clrs = {'Créole haïtien':'#2ECC71','Français':'#C9A84C','Anglais':'#4A9EFF'}
        for lang, lvl in LANGUAGES.items():
            fig5.add_trace(go.Bar(x=[lvl], y=[lang], orientation='h', marker_color=clrs.get(lang,'#C9A84C'),
                text=[f"{lvl}%"], textposition='inside', textfont=dict(color='white', size=14)))
        fig5.update_layout(title=dict(text='Maîtrise des Langues', font=dict(color='#C9A84C', size=16)),
            xaxis=dict(range=[0,110], gridcolor='rgba(255,255,255,0.07)', color='#F5F0E8'),
            yaxis=dict(color='#F5F0E8'), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(13,27,42,0.6)',
            font=dict(family='DM Sans', color='#F5F0E8'), showlegend=False, height=280)
        st.plotly_chart(fig5, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — CARTE
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
    cols = st.columns(3)
    for col, (loc, event, year) in zip(cols, zip(GEO_DATA['locations'], GEO_DATA['events'], GEO_DATA['years'])):
        with col:
            st.markdown(f"""<div class="timeline-item" style="border-left-color:#4A9EFF;">
              <div class="timeline-year">📍 {year}</div>
              <div class="timeline-title">{loc}</div>
              <div class="timeline-desc">{event}</div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — PLATEFORMES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔗 Plateformes & Liens":
    st.markdown('<p class="section-header">🔗 Plateformes & Présences en ligne</p>', unsafe_allow_html=True)
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
    col1, col2 = st.columns(2)
    for i, (icon, nm, desc, url) in enumerate(REGULATORS):
        with (col1 if i % 2 == 0 else col2):
            st.markdown(f"""
            <div class="platform-card">
              <div class="platform-icon">{icon}</div>
              <div style="flex:1;">
                <div class="platform-name">{nm}</div>
                <div class="platform-desc">{desc}</div>
                <a href="{url}" target="_blank" class="platform-link">Consulter →</a>
              </div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — GÉNÉRATEUR DE DOCUMENTS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📄 Générateur de Documents":
    st.markdown('<p class="section-header">📄 Téléchargement des Documents PDF</p>', unsafe_allow_html=True)
    tab_cv, tab_lm, tab_bio = st.tabs(["📋 CV — 1 page Finance", "✉️ Lettre de Motivation", "📖 Biographie Complète"])

    with tab_cv:
        st.markdown("""
        <div style='background:var(--navy-mid);border:1px solid rgba(201,168,76,0.2);border-radius:12px;padding:20px 24px;margin-bottom:20px;'>
          <div style='font-size:1rem;font-weight:600;color:#C9A84C;margin-bottom:6px;'>CV Professionnel — Format Finance</div>
          <div style='font-size:0.85rem;opacity:0.75;line-height:1.6;'>CV <b>une page</b>, format standard finance/banking — en-tête centré, données vérifiées, 4–5 missions par expérience, matières principales par diplôme.</div>
        </div>""", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            cv_poste = st.text_input("🎯 Poste visé", placeholder="ex: Compliance Officer, Risk Analyst…", key="cv_poste")
        with c2:
            cv_entreprise = st.text_input("🏢 Entreprise cible", placeholder="ex: BNP Paribas, KPMG…", key="cv_entreprise")
        c3, _ = st.columns(2)
        with c3:
            cv_secteur = st.selectbox("🏦 Secteur", ["Banque","Fintech","Asset Management","Assurance","Audit / Conseil","Marché des capitaux"], key="cv_sect")

        if st.button("⬇️ Générer & Télécharger le CV (PDF)", use_container_width=True, key="btn_cv"):
            with st.spinner("Génération du CV PDF…"):
                pdf_bytes = generate_cv_pdf(poste=cv_poste, entreprise=cv_entreprise, secteur=cv_secteur)
            st.success("✅ CV généré !")
            st.download_button("📥 Télécharger — Cineus_Mackenson_CV.pdf", data=pdf_bytes,
                file_name="Cineus_Mackenson_CV.pdf", mime="application/pdf",
                use_container_width=True, key="dl_cv")

    with tab_lm:
        st.markdown("""
        <div style='background:var(--navy-mid);border:1px solid rgba(74,158,255,0.2);border-radius:12px;padding:20px 24px;margin-bottom:20px;'>
          <div style='font-size:1rem;font-weight:600;color:#4A9EFF;margin-bottom:6px;'>Lettre de Motivation PDF</div>
          <div style='font-size:0.85rem;opacity:0.75;line-height:1.6;'>Lettre en 4 paragraphes Harvard. Contenu personnalisable dans la section "Édition — Lettre de Motivation". Option IA disponible avec clé API.</div>
        </div>""", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            lm_poste      = st.text_input("🎯 Poste visé", key="lm_poste")
            lm_entreprise = st.text_input("🏢 Entreprise", key="lm_ent")
        with c2:
            lm_secteur = st.selectbox("🏦 Secteur", ["Banque","Fintech","Asset Management","Assurance","Audit / Conseil"], key="lm_sect")
            lm_style   = st.selectbox("✍️ Ton", ["Professionnel & formel","Dynamique & moderne","Harvard / McKinsey"], key="lm_style")
        lm_contexte = st.text_area("💬 Instructions spécifiques", placeholder="Ex: insister sur la victoire France FinTech…", height=60, key="lm_ctx")
        use_ai = st.toggle("🤖 Personnaliser avec Claude AI", value=False, key="lm_ai")

        ai_content = ""
        if st.button("✨ Générer la Lettre (PDF)", use_container_width=True, key="btn_lm"):
            if not lm_poste:
                st.error("⚠️ Indiquez le poste visé.")
            else:
                if use_ai:
                    api_key = st.session_state.get("anthropic_api_key_input","").strip() or ANTHROPIC_API_KEY_DEFAULT
                    if api_key:
                        with st.spinner("🤖 Rédaction par Claude AI…"):
                            system = "Tu es expert en lettres de motivation finance. Style Harvard. 4 paragraphes séparés par ligne vide. Pas d'ouverture ni clôture."
                            prompt = f"Rédige le corps d'une LM pour Mackenson Cineus (Compliance Officer HiPay, LCB-FT Delubac, MBA ESLSCA, 1er Prix Hackathon FinTech 2023, Podcast INCLUTECH).\nPoste: {lm_poste}\nEntreprise: {lm_entreprise}\nTon: {lm_style}\nInstructions: {lm_contexte or 'standard'}"
                            ai_content = call_claude(prompt, system)
                    else:
                        st.warning("⚠️ Clé API non configurée.")
                with st.spinner("Génération PDF…"):
                    pdf_lm = generate_lettre_pdf(poste=lm_poste, entreprise=lm_entreprise,
                        secteur=lm_secteur, style_lm=lm_style, contexte=lm_contexte, ai_text=ai_content)
                st.success("✅ Lettre générée !")
                st.download_button("📥 Télécharger — Cineus_Mackenson_LM.pdf", data=pdf_lm,
                    file_name=f"Cineus_Mackenson_LM_{lm_poste.replace(' ','_') if lm_poste else 'Finance'}.pdf",
                    mime="application/pdf", use_container_width=True, key="dl_lm")

    with tab_bio:
        st.markdown("""
        <div style='background:var(--navy-mid);border:1px solid rgba(46,204,113,0.2);border-radius:12px;padding:20px 24px;margin-bottom:20px;'>
          <div style='font-size:1rem;font-weight:600;color:#2ECC71;margin-bottom:6px;'>Biographie Professionnelle Complète</div>
          <div style='font-size:0.85rem;opacity:0.75;line-height:1.6;'>Biographie narrative en 5 phases chronologiques · 2 pages A4 · Sources vérifiées.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("⬇️ Générer & Télécharger la Biographie (PDF)", use_container_width=True, key="btn_bio"):
            with st.spinner("Génération…"):
                pdf_bio = generate_bio_pdf()
            st.success("✅ Biographie générée !")
            st.download_button("📥 Télécharger — Cineus_Mackenson_Biographie.pdf", data=pdf_bio,
                file_name="Cineus_Mackenson_Biographie.pdf", mime="application/pdf",
                use_container_width=True, key="dl_bio")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 7 — ÉDITION INFOS GÉNÉRALES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "✏️ Édition — Informations Générales":
    st.markdown('<p class="section-header">✏️ Informations Générales</p>', unsafe_allow_html=True)
    st.info("💡 Modifiez les champs puis cliquez **Sauvegarder**. Les modifications s'appliquent partout.")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Nom complet", key="edit_name")
        st.text_input("Localisation", key="edit_location")
        st.text_input("Email", key="edit_email")
    with c2:
        st.text_input("Titre professionnel", key="edit_title")
        st.text_input("Téléphone", key="edit_phone", placeholder="+33 6 XX XX XX XX")
        st.text_input("LinkedIn (sans https://)", key="edit_linkedin")
    st.text_area("Résumé / Accroche professionnelle (affiché sur la page Profil)", key="edit_summary", height=140)
    st.markdown("---")
    save_button("infos")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 8 — ÉDITION EXPÉRIENCES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "💼 Édition — Expériences":
    st.markdown('<p class="section-header">💼 Expériences Professionnelles</p>', unsafe_allow_html=True)
    st.info("💡 Modifiez chaque expérience, puis sauvegardez en bas de page.")

    exps = st.session_state.edit_exp
    for i, exp in enumerate(exps):
        with st.expander(f"**{exp['role']}** — {exp['org']} ({exp['period']})", expanded=(i == 0)):
            c1, c2 = st.columns([2, 1])
            with c1:
                new_role = st.text_input("Poste / Rôle", value=exp["role"], key=f"exp_role_{i}")
                new_org  = st.text_input("Organisation · Ville", value=exp["org"], key=f"exp_org_{i}")
            with c2:
                new_period = st.text_input("Période", value=exp["period"], key=f"exp_period_{i}")
                new_url    = st.text_input("URL officielle", value=exp.get("url",""), key=f"exp_url_{i}")

            st.markdown("**Missions / Réalisations** — 4 à 5 lignes recommandées (une par ligne)")
            bullets_text = "\n".join(exp.get("bullets", []))
            new_bullets  = st.text_area("", value=bullets_text, height=130, key=f"exp_bullets_{i}",
                                         label_visibility="collapsed")
            if st.button(f"💾 Mettre à jour cette expérience", key=f"save_exp_{i}"):
                st.session_state.edit_exp[i] = {
                    "role":    new_role, "org": new_org, "period": new_period,
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
            new_exp_role = st.text_input("Poste", key="new_exp_role", placeholder="ex: Risk Manager")
            new_exp_org  = st.text_input("Organisation", key="new_exp_org", placeholder="ex: BNP Paribas · Paris")
        with nc2:
            new_exp_period = st.text_input("Période", key="new_exp_period", placeholder="2025 – Présent")
            new_exp_url    = st.text_input("URL", key="new_exp_url")
        new_exp_bullets = st.text_area("Missions (une par ligne, 4–5 lignes)", key="new_exp_bullets", height=100)
        if st.button("➕ Ajouter cette expérience", key="add_exp"):
            if new_exp_role and new_exp_org:
                st.session_state.edit_exp.insert(0, {
                    "role": new_exp_role, "org": new_exp_org,
                    "period": new_exp_period, "url": new_exp_url,
                    "bullets": [b.strip() for b in new_exp_bullets.split("\n") if b.strip()],
                })
                st.success(f"✅ « {new_exp_role} » ajouté !")
                st.rerun()

    st.markdown("---")
    save_button("exp")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 9 — ÉDITION FORMATION
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🎓 Édition — Formation":
    st.markdown('<p class="section-header">🎓 Formation Académique</p>', unsafe_allow_html=True)
    st.info("💡 Incluez 5+ matières pertinentes en finance pour chaque diplôme.")

    edus = st.session_state.edit_edu
    for i, e in enumerate(edus):
        with st.expander(f"**{e['deg']}** — {e['school']} ({e['yr']})", expanded=(i == 0)):
            c1, c2 = st.columns([2, 1])
            with c1:
                nd = st.text_input("Diplôme", value=e["deg"],    key=f"edu_deg_{i}")
                ns = st.text_input("École",   value=e["school"], key=f"edu_sch_{i}")
            with c2:
                ny = st.text_input("Années",  value=e["yr"],  key=f"edu_yr_{i}")
                nu = st.text_input("URL",     value=e.get("url",""), key=f"edu_url_{i}")
            nd2 = st.text_input("Description courte (résumé)", value=e.get("det",""), key=f"edu_det_{i}")
            st.markdown("**Matières principales** (une par ligne — 5 à 6 recommandées pour le CV)")
            courses_text = "\n".join(e.get("courses", []))
            new_courses  = st.text_area("", value=courses_text, height=120,
                                         key=f"edu_courses_{i}", label_visibility="collapsed")
            if st.button("💾 Mettre à jour cette formation", key=f"save_edu_{i}"):
                st.session_state.edit_edu[i] = {
                    "deg": nd, "school": ns, "yr": ny, "url": nu, "det": nd2,
                    "courses": [c.strip() for c in new_courses.split("\n") if c.strip()],
                }
                st.success(f"✅ Formation « {nd} » mise à jour !")
                st.rerun()

    st.markdown("---")
    st.markdown("#### ➕ Ajouter une formation")
    with st.expander("Nouvelle formation", expanded=False):
        nc1, nc2 = st.columns([2,1])
        with nc1:
            nf_deg    = st.text_input("Diplôme", key="nf_deg")
            nf_school = st.text_input("École",   key="nf_school")
        with nc2:
            nf_yr  = st.text_input("Années", key="nf_yr")
            nf_url = st.text_input("URL",    key="nf_url")
        nf_det     = st.text_input("Description", key="nf_det")
        nf_courses = st.text_area("Matières (une par ligne)", key="nf_courses", height=100)
        if st.button("➕ Ajouter", key="add_edu"):
            if nf_deg and nf_school:
                st.session_state.edit_edu.insert(0, {
                    "deg": nf_deg, "school": nf_school, "yr": nf_yr, "url": nf_url, "det": nf_det,
                    "courses": [c.strip() for c in nf_courses.split("\n") if c.strip()],
                })
                st.success(f"✅ « {nf_deg} » ajouté !")
                st.rerun()

    st.markdown("---")
    save_button("edu")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 10 — ÉDITION COMPÉTENCES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "⚡ Édition — Compétences":
    st.markdown('<p class="section-header">⚡ Compétences & Distinctions</p>', unsafe_allow_html=True)

    tab_sk, tab_dist, tab_tl = st.tabs(["Compétences (0–100)", "Distinctions & Prix", "Parcours chronologique"])

    with tab_sk:
        st.info("Modifiez noms et niveaux. Cliquez **Sauvegarder** pour appliquer.")
        updated_skills = {}
        for skill, level in list(st.session_state.edit_skills.items()):
            c1, c2, c3 = st.columns([4, 2, 1])
            with c1:
                new_name = st.text_input("", value=skill, key=f"sk_name_{skill}", label_visibility="collapsed")
            with c2:
                new_lvl  = st.slider("", 0, 100, level, key=f"sk_lvl_{skill}", label_visibility="collapsed")
            with c3:
                st.markdown(f"<div style='padding-top:8px;color:#C9A84C;font-weight:700;'>{new_lvl}%</div>", unsafe_allow_html=True)
            updated_skills[new_name] = new_lvl

        st.markdown("#### ➕ Ajouter une compétence")
        c1, c2 = st.columns([3, 1])
        with c1:
            new_sk_name = st.text_input("Nom", key="new_sk_name", placeholder="ex: Déclarations Tracfin")
        with c2:
            new_sk_lvl = st.slider("Niveau", 0, 100, 80, key="new_sk_lvl")

        if st.button("💾 Sauvegarder les compétences", use_container_width=True):
            if new_sk_name.strip():
                updated_skills[new_sk_name.strip()] = new_sk_lvl
            st.session_state.edit_skills = updated_skills
            if save_profile():
                st.success("✅ Compétences sauvegardées !")
            st.rerun()

    with tab_dist:
        dists = list(st.session_state.edit_distinctions)
        for i, (icon, title, desc) in enumerate(dists):
            c1, c2, c3 = st.columns([0.5, 2, 4])
            with c1: st.text_input("", value=icon,  key=f"di_i_{i}", label_visibility="collapsed")
            with c2: st.text_input("", value=title, key=f"di_t_{i}", label_visibility="collapsed")
            with c3: st.text_input("", value=desc,  key=f"di_d_{i}", label_visibility="collapsed")

        if st.button("💾 Sauvegarder les distinctions", use_container_width=True):
            new_dists = [(st.session_state.get(f"di_i_{i}", dists[i][0]),
                          st.session_state.get(f"di_t_{i}", dists[i][1]),
                          st.session_state.get(f"di_d_{i}", dists[i][2])) for i in range(len(dists))]
            st.session_state.edit_distinctions = new_dists
            save_profile()
            st.success("✅ Distinctions sauvegardées !")
            st.rerun()

        st.markdown("---")
        nc1, nc2, nc3 = st.columns([0.5, 2, 4])
        with nc1: new_di = st.text_input("Icône", key="new_di_i", value="🏅")
        with nc2: new_dt = st.text_input("Titre", key="new_di_t")
        with nc3: new_dd = st.text_input("Description", key="new_di_d")
        if st.button("➕ Ajouter une distinction", key="add_dist"):
            if new_dt.strip():
                st.session_state.edit_distinctions.append((new_di, new_dt, new_dd))
                save_profile()
                st.success(f"✅ « {new_dt} » ajouté !")
                st.rerun()

    with tab_tl:
        st.info("Modifiez les événements du parcours chronologique.")
        timeline = list(st.session_state.get("edit_timeline", DEFAULT_DATA["edit_timeline"]))
        for i, item in enumerate(timeline):
            with st.expander(f"{item.get('icon','')} {item.get('year','')} — {item.get('title','')}", expanded=False):
                c1, c2, c3 = st.columns([1, 3, 1])
                with c1:
                    new_yr  = st.text_input("Année", value=item.get("year",""), key=f"tl_yr_{i}")
                    new_ic  = st.text_input("Icône", value=item.get("icon",""), key=f"tl_ic_{i}")
                with c2:
                    new_tt  = st.text_input("Titre",       value=item.get("title",""), key=f"tl_tt_{i}")
                    new_td  = st.text_input("Description", value=item.get("desc",""),  key=f"tl_td_{i}")
                with c3:
                    cats_opt = ["Éducation","Entrepreneuriat","Social","Réseau","Professionnel"]
                    cur_cat  = item.get("cat","Professionnel")
                    new_cat  = st.selectbox("Catégorie", cats_opt,
                                            index=cats_opt.index(cur_cat) if cur_cat in cats_opt else 0,
                                            key=f"tl_cat_{i}")
                if st.button("💾 Mettre à jour", key=f"save_tl_{i}"):
                    st.session_state.edit_timeline[i] = {
                        "year": new_yr, "icon": new_ic, "title": new_tt,
                        "desc": new_td, "cat": new_cat,
                        "url": item.get("url",""),
                    }
                    save_profile()
                    st.success("✅ Mis à jour !")
                    st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 11 — ÉDITION LETTRE DE MOTIVATION
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "✉️ Édition — Lettre de Motivation":
    st.markdown('<p class="section-header">✉️ Contenu de la Lettre de Motivation</p>', unsafe_allow_html=True)
    st.info("💡 Ces textes seront utilisés par défaut dans les PDF générés. Personnalisables paragraphe par paragraphe.")

    st.markdown("#### § 1 — Introduction & Accroche")
    st.text_area("Paragraphe d'introduction (présentation, poste et titre)", key="edit_lm_intro", height=110)

    st.markdown("#### § 2 — Expérience & Expertise technique")
    st.text_area("Détail des expériences HiPay et Delubac, compétences LCB-FT", key="edit_lm_para2", height=110)

    st.markdown("#### § 3 — Valeur ajoutée & Différenciation")
    st.text_area("Hackathon, podcast INCLUTECH, Erasmus, profil international", key="edit_lm_para3", height=110)

    st.markdown("#### § 4 — Closing & Appel à l'action")
    st.text_area("Formule de clôture, disponibilité pour entretien", key="edit_lm_close", height=80)

    st.markdown("---")
    st.markdown("""
    <div style='background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.2);border-radius:8px;padding:12px;font-size:0.83rem;opacity:0.85;'>
    💡 <b>Note :</b> Lors de la génération PDF (page "Générateur de Documents"), vous pouvez remplacer ces textes
    par une version générée par Claude AI en activant l'option IA et en renseignant votre clé API.
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    save_button("lm")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 12 — ÉDITION BIOGRAPHIE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📖 Édition — Biographie":
    st.markdown('<p class="section-header">📖 Biographie — 5 Phases</p>', unsafe_allow_html=True)
    st.info("💡 Modifiez chaque phase de la biographie. Ces textes sont utilisés sur la page Profil et dans le PDF.")

    bio_phases = st.session_state.get("edit_bio_phases", DEFAULT_DATA["edit_bio_phases"])

    PHASE_LABELS = ["phase1","phase2","phase3","phase4","phase5"]
    PHASE_COLORS_MAP = {"phase1":"#4A9EFF","phase2":"#C9A84C","phase3":"#E67E22","phase4":"#9B59B6","phase5":"#00B4D8"}

    for i, bp in enumerate(bio_phases):
        color = PHASE_COLORS_MAP.get(bp.get("phase","phase1"),"#C9A84C")
        with st.expander(f"**{bp.get('label','')}** — {bp.get('title','')}", expanded=(i == 0)):
            c1, c2 = st.columns([1, 2])
            with c1:
                ph_opt  = PHASE_LABELS
                cur_ph  = bp.get("phase","phase1")
                new_ph  = st.selectbox("Phase CSS", ph_opt,
                                        index=ph_opt.index(cur_ph) if cur_ph in ph_opt else i,
                                        key=f"bp_phase_{i}")
                new_lbl = st.text_input("Label (ex: Phase 1 · 2014–2019)", value=bp.get("label",""), key=f"bp_lbl_{i}")
                new_yrs = st.text_input("Sous-titre (institutions / dates)", value=bp.get("years",""), key=f"bp_yrs_{i}")
            with c2:
                new_ttl = st.text_input("Titre de la phase", value=bp.get("title",""), key=f"bp_ttl_{i}")
                new_txt = st.text_area("Texte narratif (séparez les paragraphes par une ligne vide)",
                                        value=bp.get("text",""), height=150, key=f"bp_txt_{i}")
            new_tags = st.text_input("Tags (séparés par des virgules)",
                                      value=bp.get("tags",""), key=f"bp_tags_{i}")

            if st.button(f"💾 Mettre à jour cette phase", key=f"save_bp_{i}"):
                st.session_state.edit_bio_phases[i] = {
                    "phase": new_ph, "label": new_lbl, "title": new_ttl,
                    "years": new_yrs, "text": new_txt, "tags": new_tags,
                }
                save_profile()
                st.success(f"✅ Phase {i+1} mise à jour !")
                st.rerun()

    st.markdown("---")
    save_button("bio")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 13 — ÉDITION CV (ACCROCHE & CONTENU)
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Édition — CV (Accroche & Contenu)":
    st.markdown('<p class="section-header">📋 Contenu du CV — Accroche & Paramètres</p>', unsafe_allow_html=True)
    st.info("💡 Personnalisez l'accroche du CV et vérifiez un aperçu de la structure avant génération PDF.")

    st.markdown("#### Accroche professionnelle (section Profil du CV)")
    st.text_area(
        "Texte affiché dans la section 'Profil Professionnel' du CV (4–5 lignes recommandées)",
        key="edit_cv_accroche", height=130)

    st.markdown("---")
    st.markdown("#### Aperçu de la structure du CV")

    exps = st.session_state.get("edit_exp", [])
    edus = st.session_state.get("edit_edu", [])
    skills_d = st.session_state.get("edit_skills", {})

    col_prev1, col_prev2 = st.columns(2)
    with col_prev1:
        st.markdown("**Expériences incluses dans le CV :**")
        for i, exp in enumerate(exps[:5]):
            nb_b = len(exp.get("bullets", []))
            st.markdown(f"""
            <div style='background:var(--navy-mid);border-left:3px solid #C9A84C;padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:8px;'>
              <div style='font-size:0.85rem;font-weight:600;color:#C9A84C;'>{exp.get('role','')} — {exp.get('period','')}</div>
              <div style='font-size:0.78rem;opacity:0.75;'>{exp.get('org','')} · {nb_b} missions</div>
            </div>""", unsafe_allow_html=True)

    with col_prev2:
        st.markdown("**Formations incluses dans le CV :**")
        for edu in edus:
            nb_c = len(edu.get("courses", []))
            st.markdown(f"""
            <div style='background:var(--navy-mid);border-left:3px solid #4A9EFF;padding:10px 14px;border-radius:0 8px 8px 0;margin-bottom:8px;'>
              <div style='font-size:0.85rem;font-weight:600;color:#4A9EFF;'>{edu.get('deg','')} — {edu.get('yr','')}</div>
              <div style='font-size:0.78rem;opacity:0.75;'>{edu.get('school','')} · {nb_c} matières</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("**Compétences (premières 6) :**")
        sk_list = list(skills_d.keys())[:6]
        st.markdown(f"<div style='font-size:0.82rem;opacity:0.8;line-height:1.8;'>{'  ·  '.join(sk_list)}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Génération rapide")
    c1, c2 = st.columns(2)
    with c1:
        quick_poste = st.text_input("Poste visé", placeholder="ex: Compliance Officer", key="quick_poste")
    with c2:
        quick_ent = st.text_input("Entreprise", placeholder="ex: BNP Paribas", key="quick_ent")

    if st.button("⬇️ Générer le CV maintenant", use_container_width=True):
        with st.spinner("Génération…"):
            pdf_bytes = generate_cv_pdf(poste=quick_poste, entreprise=quick_ent)
        st.success("✅ CV généré !")
        st.download_button("📥 Télécharger le CV", data=pdf_bytes,
            file_name="Cineus_Mackenson_CV.pdf", mime="application/pdf",
            use_container_width=True, key="dl_cv_quick")

    st.markdown("---")
    save_button("cv")
