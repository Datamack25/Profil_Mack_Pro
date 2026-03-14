import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests

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
PROFILE = {
    "name": "Mackenson Cineus",
    "title": "Analyste Sécurité Financière (LCB-FT)",
    "location": "Paris, France",
    "summary": (
        "Professionnel de la finance internationale alliant rigueur analytique et vision sociale. "
        "Passionné par la conformité bancaire, les marchés financiers et l'innovation fintech, "
        "avec un parcours couvrant Haïti, la France et les réseaux internationaux."
    ),
}

BIO_PERIODS = [
    {
        "phase": "phase1",
        "label": "Phase 1 · 2014 – 2019",
        "title": "Racines haïtiennes & premier éveil entrepreneurial",
        "years": "Université d'État d'Haïti · Hult Prize 2018 · Parlement Jeunesse Eau",
        "text": [
            "Mackenson Cineus débute son parcours académique à la Faculté de Droit et des Sciences Économiques "
            "de l'Université d'État d'Haïti, l'une des institutions les plus prestigieuses du pays. Immergé dans "
            "les réalités socio-économiques haïtiennes — déchets non traités, accès à l'eau, dépendance au charbon — "
            "il forge très tôt une conscience aiguë des enjeux de développement durable.",

            "En 2018, cette sensibilité se cristallise lors du Hult Prize, la plus grande compétition "
            "d'entrepreneuriat social étudiant au monde. Avec son équipe, il développe le projet WEISS "
            "(We Integrate Sustainable Solutions) : transformer les déchets organiques en biogaz et fertilisant "
            "agricole, réduire la déforestation et la pollution urbaine. Cette expérience révèle un talent naturel "
            "pour l'innovation à impact social.",

            "Parallèlement, il s'engage au Parlement Haïtien de la Jeunesse pour l'Eau et l'Assainissement, "
            "militant pour l'accès équitable à l'eau potable. Ces années fondatrices témoignent d'un homme "
            "mu par des convictions profondes et une volonté de transformer les défis en opportunités.",
        ],
        "tags": ["Entrepreneuriat social", "Hult Prize", "Développement durable", "Leadership étudiant", "Haïti"],
    },
    {
        "phase": "phase2",
        "label": "Phase 2 · 2019 – 2021",
        "title": "Transition internationale — maîtriser les codes de la finance",
        "years": "Université du Mans · Licence Banque-Finance-Assurance",
        "text": [
            "Le passage en France marque un tournant décisif. Mackenson choisit l'Université du Mans pour y "
            "décrocher une Licence en Banque, Finance et Assurance — une formation rigoureuse qui lui ouvre "
            "les portes du système financier européen.",

            "Loin de sa terre natale, il s'impose un rythme exigeant : maîtriser les marchés financiers, "
            "la réglementation bancaire, l'analyse du risque et les instruments de couverture. Cette période "
            "est celle de la transformation — du militant social à l'analyste capable de lire un bilan, "
            "de modéliser un portefeuille et de comprendre les rouages de la conformité bancaire.",

            "C'est aussi une immersion culturelle profonde. En naviguant entre ses codes haïtiens et la "
            "rigueur académique française, Mackenson développe une double lecture du monde — un atout rare "
            "dans un secteur financier de plus en plus globalisé.",
        ],
        "tags": ["Banque", "Finance", "Assurance", "Réglementation", "Mobilité internationale"],
    },
    {
        "phase": "phase3",
        "label": "Phase 3 · 2021 – 2023",
        "title": "Spécialisation élite — marchés financiers & compétition France FinTech",
        "years": "ESLSCA Business School Paris · MBA Trading · Compétition France FinTech",
        "text": [
            "L'ESLSCA Business School Paris accueille Mackenson pour un MBA spécialisé en Trading et Marchés "
            "Financiers — une formation d'élite qui l'immerge dans la réalité des salles de marché, la gestion "
            "quantitative et la conformité réglementaire internationale.",

            "C'est durant cette période qu'il intègre activement l'écosystème France FinTech, association de "
            "référence regroupant les startups et acteurs de l'innovation financière française. Il participe "
            "à la compétition France FinTech, concours reconnu qui met en lumière les solutions les plus "
            "disruptives du secteur — confirmant son positionnement à l'intersection entre technologie, "
            "réglementation et finance.",

            "Ces deux années sont celles de la maturation professionnelle : Mackenson affine sa vision "
            "stratégique du secteur financier, construit son réseau parisien et se forge une identité "
            "de professionnel capable de naviguer entre finance traditionnelle et innovation numérique.",
        ],
        "tags": ["MBA", "Trading", "Marchés financiers", "France FinTech", "Compétition", "Innovation"],
    },
    {
        "phase": "phase4",
        "label": "Phase 4 · 2023 – Présent",
        "title": "Insertion professionnelle — la conformité bancaire au cœur du système",
        "years": "Banque Delubac & Cie · Analyste LCB-FT · Écosystème fintech parisien",
        "text": [
            "Aujourd'hui, Mackenson Cineus occupe le poste d'Analyste en Sécurité Financière (LCB-FT) au sein "
            "de la Banque Delubac & Cie, institution bancaire française indépendante fondée en 1924, reconnue "
            "pour son expertise en finance privée et gestion d'actifs.",

            "Sa mission au quotidien : détecter les transactions suspectes, analyser les profils de risque "
            "clients, appliquer les directives européennes anti-blanchiment (AMLD5/AMLD6) et assurer la "
            "conformité réglementaire dans un environnement hautement contrôlé. Un rôle exigeant à la fois "
            "rigueur analytique, connaissance approfondie des marchés et maîtrise des outils de surveillance "
            "financière.",

            "Ce poste est l'aboutissement logique d'un parcours construit avec intention : partir d'Haïti, "
            "comprendre les mécanismes de l'économie mondiale, se former aux standards européens les plus "
            "exigeants, et contribuer à la solidité du système financier international. Mackenson incarne "
            "la génération de professionnels qui apportent à Paris une perspective globale et une éthique "
            "forgée dans des contextes souvent bien plus complexes.",
        ],
        "tags": ["LCB-FT", "Compliance AML", "Banque Delubac", "AMLD6", "Sécurité financière", "Paris"],
    },
]

TIMELINE = [
    {"year": "2014–2017", "title": "Université d'État d'Haïti", "desc": "Faculté de Droit et des Sciences Économiques — Économie & Politiques publiques", "icon": "🎓", "cat": "Éducation"},
    {"year": "2018", "title": "Hult Prize — Compétition Internationale", "desc": "Projet WEISS : transformation des déchets en biogaz & fertilisant agricole", "icon": "🏆", "cat": "Entrepreneuriat"},
    {"year": "2018–2019", "title": "Parlement Haïtien de la Jeunesse pour l'Eau", "desc": "Engagement citoyen — sensibilisation aux ressources hydriques et assainissement", "icon": "🌊", "cat": "Social"},
    {"year": "2019–2021", "title": "Université du Mans — Licence BFA", "desc": "Banque, Finance & Assurance — analyse financière, marchés, réglementation européenne", "icon": "🏫", "cat": "Éducation"},
    {"year": "2021–2023", "title": "ESLSCA Business School Paris — MBA", "desc": "Spécialisation Trading & Marchés Financiers — produits dérivés, gestion de portefeuille", "icon": "📈", "cat": "Éducation"},
    {"year": "2022–2023", "title": "Compétition France FinTech", "desc": "Participation au concours national fintech — innovation en finance numérique & réglementation", "icon": "🚀", "cat": "Entrepreneuriat"},
    {"year": "2023–Présent", "title": "Banque Delubac & Cie — Analyste LCB-FT", "desc": "Sécurité financière, transactions suspectes, conformité AMLD5/AMLD6, KYC", "icon": "🏦", "cat": "Professionnel"},
    {"year": "2023–Présent", "title": "Membre — France FinTech", "desc": "Écosystème fintech parisien — événements, veille, networking innovation financière", "icon": "💡", "cat": "Réseau"},
]

SKILLS = {
    "LCB-FT / Compliance AML": 92,
    "Analyse financière": 88,
    "Réglementation bancaire": 85,
    "Trading & Marchés": 82,
    "Gestion des risques": 80,
    "Entrepreneuriat social": 78,
    "Fintech & Innovation": 75,
    "Analyse de données": 72,
}

LANGUAGES = {"Créole haïtien": 100, "Français": 95, "Anglais": 85}

GEO_DATA = {
    "locations": ["Port-au-Prince, Haïti", "Le Mans, France", "Paris, France"],
    "lat": [18.5432, 47.9960, 48.8566],
    "lon": [-72.3388, 0.1966, 2.3522],
    "events": ["Formation initiale + Hult Prize + Engagement social", "Licence Banque-Finance-Assurance", "MBA + Banque Delubac + France FinTech"],
    "years": ["2014–2019", "2019–2021", "2021–Présent"],
    "size": [20, 15, 32],
}

PLATFORMS = [
    {"icon": "💼", "name": "LinkedIn", "desc": "Profil professionnel complet — expériences, réseau financier parisien, recommandations.", "url": "https://www.linkedin.com/in/mackenson-cineus", "label": "Voir le profil LinkedIn →"},
    {"icon": "🏆", "name": "Hult Prize Foundation", "desc": "Compétition mondiale d'entrepreneuriat social où Mackenson a présenté le projet WEISS en 2018 — biogaz et fertilisant à partir de déchets organiques en Haïti.", "url": "https://www.hultprize.org", "label": "Découvrir Hult Prize →"},
    {"icon": "🚀", "name": "France FinTech", "desc": "Association de référence de l'innovation financière française. Mackenson a participé à la compétition France FinTech et est membre actif de l'écosystème.", "url": "https://francefintech.org", "label": "Voir France FinTech →"},
    {"icon": "🏦", "name": "Banque Delubac & Cie", "desc": "Banque privée française indépendante fondée en 1924. Mackenson y est Analyste en Sécurité Financière (LCB-FT), spécialisé dans la lutte anti-blanchiment.", "url": "https://www.delubac.com", "label": "Site Banque Delubac →"},
    {"icon": "🎓", "name": "ESLSCA Business School Paris", "desc": "Grande école de commerce parisienne. Mackenson y a obtenu son MBA en Trading & Marchés Financiers — gestion de portefeuille, produits dérivés, conformité.", "url": "https://www.eslsca.fr", "label": "Voir ESLSCA →"},
    {"icon": "🏫", "name": "Université du Mans", "desc": "Université française reconnue pour sa filière Banque-Finance-Assurance. Licence BFA de Mackenson — socle de sa carrière dans la finance européenne.", "url": "https://www.univ-lemans.fr", "label": "Voir Université du Mans →"},
    {"icon": "🌊", "name": "Parlement Haïtien Jeunesse Eau", "desc": "Initiative citoyenne haïtienne. Mackenson a milité pour l'accès équitable à l'eau potable — premier engagement public structuré de sa carrière.", "url": "https://www.hultprize.org", "label": "En savoir plus →"},
]

REGULATORS = [
    ("🇫🇷", "ACPR — Autorité de Contrôle Prudentiel", "Régulateur bancaire français — référence LCB-FT", "https://acpr.banque-france.fr"),
    ("🌐", "FATF / GAFI", "Normes mondiales anti-blanchiment et financement du terrorisme", "https://www.fatf-gafi.org"),
    ("📊", "AMF — Autorité des Marchés Financiers", "Régulateur des marchés financiers en France", "https://www.amf-france.org"),
    ("💡", "Banque de France — Fintech", "Innovation fintech, cryptoactifs et finance numérique", "https://www.banque-france.fr/fr/economie/fintech"),
]

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def call_claude(prompt: str, system: str = "") -> str:
    api_key = st.session_state.get("anthropic_api_key", "").strip()
    if not api_key:
        return "❌ Veuillez renseigner votre clé API Anthropic dans la barre latérale gauche."
    headers = {"Content-Type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"}
    body = {"model": "claude-sonnet-4-20250514", "max_tokens": 1000, "system": system, "messages": [{"role": "user", "content": prompt}]}
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=body, timeout=60)
        data = r.json()
        if "content" in data:
            return "".join(b.get("text", "") for b in data["content"] if b.get("type") == "text")
        return f"Erreur API : {data.get('error', {}).get('message', 'Inconnue')}"
    except Exception as e:
        return f"Erreur de connexion : {str(e)}"

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
    ], label_visibility="collapsed")

    st.divider()
    st.markdown("<div style='font-size:0.8rem;color:#C9A84C;font-weight:600;margin-bottom:6px;'>🔑 Clé API Anthropic</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.72rem;opacity:0.6;margin-bottom:8px;'>Requise uniquement pour la génération de documents</div>", unsafe_allow_html=True)
    api_key_input = st.text_input("Clé API", type="password", placeholder="sk-ant-...", label_visibility="collapsed", key="anthropic_api_key")
    if api_key_input:
        st.markdown("<div style='font-size:0.72rem;color:#2ECC71;margin-top:4px;'>✅ Clé renseignée</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:0.72rem;color:#E67E22;margin-top:4px;'>⚠️ Aucune clé (génération désactivée)</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("<div style='font-size:0.75rem;opacity:0.5;text-align:center;padding:10px;'>© 2024 Mackenson Cineus<br>Tous droits réservés</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — PROFIL & BIOGRAPHIE
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Profil & Biographie":

    st.markdown(f"""
    <div class="hero-banner">
      <p class="hero-name">{PROFILE['name']}</p>
      <p class="hero-title">{PROFILE['title']} · {PROFILE['location']}</p>
      <div style="margin-top:16px;">
        <span class="hero-badge">🏦 LCB-FT</span>
        <span class="hero-badge">📈 Trading</span>
        <span class="hero-badge">🚀 France FinTech</span>
        <span class="hero-badge">🌍 International</span>
        <span class="hero-badge">🏆 Hult Prize 2018</span>
      </div>
      <p style="margin-top:20px;max-width:720px;opacity:0.85;line-height:1.8;">{PROFILE['summary']}</p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    kpis = [("8+", "Années d'exp."), ("3", "Pays traversés"), ("2", "Diplômes sup."), ("2", "Compétitions int.")]
    for col, (val, lbl) in zip(cols, kpis):
        with col:
            st.markdown(f'<div class="metric-card"><span class="metric-value">{val}</span><div class="metric-label">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-header">Biographie — Parcours en 4 périodes</p>', unsafe_allow_html=True)
    st.markdown("<p style='opacity:0.7;margin-bottom:28px;line-height:1.7;max-width:800px;'>Le parcours de Mackenson Cineus se déploie en quatre chapitres distincts, chacun marquant une transformation profonde — du militant social haïtien au professionnel de la finance parisienne.</p>", unsafe_allow_html=True)

    for period in BIO_PERIODS:
        tags_html = "".join(f'<span class="bio-tag">{t}</span>' for t in period["tags"])
        paras_html = "".join(f'<p style="margin:0 0 14px 0;">{p}</p>' for p in period["text"])
        st.markdown(f"""
        <div class="bio-period {period['phase']}">
          <div class="bio-phase-label">{period['label']}</div>
          <div class="bio-period-title">{period['title']}</div>
          <div class="bio-period-years">📍 {period['years']}</div>
          <div class="bio-period-text">{paras_html}</div>
          <div style="margin-top:14px;">{tags_html}</div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — PARCOURS & COMPÉTENCES
# ═══════════════════════════════════════════════════════════════════════════════
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
        sn = list(SKILLS.keys()); sv = list(SKILLS.values())
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

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — GÉNÉRATEUR DE DOCUMENTS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📄 Générateur de Documents":

    st.markdown('<p class="section-header">📄 Générateur de Documents Professionnels</p>', unsafe_allow_html=True)
    st.markdown("<p style='opacity:0.8;margin-bottom:24px;line-height:1.7;'>Générez un <strong style='color:#C9A84C;'>CV professionnel</strong> ou une <strong style='color:#C9A84C;'>lettre de motivation</strong> personnalisés — propulsé par Claude AI.</p>", unsafe_allow_html=True)

    doc_type = st.selectbox("Type de document", ["📋 CV Professionnel", "✉️ Lettre de Motivation"])

    c1, c2 = st.columns(2)
    with c1:
        poste = st.text_input("🎯 Poste visé", placeholder="ex: Analyste Risques, Compliance Officer…")
        entreprise = st.text_input("🏢 Entreprise cible", placeholder="ex: BNP Paribas, AXA, KPMG…")
    with c2:
        secteur = st.selectbox("🏦 Secteur", ["Banque", "Assurance", "Fintech", "Asset Management", "Audit / Conseil", "Marché des capitaux"])
        style = st.selectbox("✍️ Style", ["Professionnel & formel", "Dynamique & moderne", "Harvard / McKinsey"])

    contexte_extra = st.text_area("💬 Contexte supplémentaire (optionnel)",
        placeholder="Ex: mettre en avant participation France FinTech, postuler en CDI…", height=80)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("✨ Générer le document", use_container_width=True):
        if not poste:
            st.error("⚠️ Veuillez indiquer le poste visé.")
        else:
            with st.spinner("⚙️ Génération en cours avec Claude AI…"):
                ctx = """
Profil : Mackenson Cineus — Analyste Sécurité Financière (LCB-FT), Paris
Formation :
  - Université d'État d'Haïti — Faculté Droit & Sciences Économiques
  - Université du Mans — Licence Banque-Finance-Assurance
  - ESLSCA Business School Paris — MBA Trading & Marchés Financiers
Expérience : Banque Delubac & Cie (2023–Présent) — LCB-FT, AML/AMLD6, KYC, transactions suspectes
Compétitions : Hult Prize 2018 (projet WEISS), Compétition France FinTech
Engagements : Parlement Haïtien Jeunesse Eau, Membre France FinTech
Langues : Créole haïtien (natif), Français (C2 bilingue), Anglais (B2 professionnel)
Compétences clés : LCB-FT, compliance bancaire, marchés financiers, trading, gestion des risques,
  fintech, entrepreneuriat social, analyse de données, réglementation européenne
"""
                if "CV" in doc_type:
                    sys_prompt = "Tu es expert en rédaction de CV haut de gamme pour la finance. CVs structurés, percutants, sans fioritures."
                    user_prompt = f"Génère un CV professionnel complet pour :\n{ctx}\nPoste : {poste}\nEntreprise : {entreprise or 'non précisée'}\nSecteur : {secteur}\nStyle : {style}\nContexte : {contexte_extra or 'Aucun'}\n\nStructure : En-tête → Résumé exécutif → Expériences → Formation → Compétences → Langues → Distinctions. Verbes d'action forts."
                else:
                    sys_prompt = "Tu es expert en lettres de motivation percutantes pour la finance. Style Harvard."
                    user_prompt = f"Génère une lettre de motivation professionnelle pour :\n{ctx}\nPoste : {poste}\nEntreprise : {entreprise or 'grande institution financière'}\nSecteur : {secteur}\nStyle : {style}\nContexte : {contexte_extra or 'Aucun'}\n\nStructure : Accroche → Adéquation profil/poste → Valeur ajoutée → Appel à l'action. 3-4 paragraphes. Français."

                result = call_claude(user_prompt, sys_prompt)

            icon = "📋" if "CV" in doc_type else "✉️"
            st.markdown(f"""
            <div class="generated-doc">
              <div class="doc-header">{icon} {doc_type} — {poste}{f' · {entreprise}' if entreprise else ''}</div>
              {result}
            </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label="⬇️ Télécharger (.txt)",
                data=result,
                file_name=f"{'CV' if 'CV' in doc_type else 'LM'}_{poste.replace(' ','_')}_MackenssonCineus.txt",
                mime="text/plain", use_container_width=True,
            )
