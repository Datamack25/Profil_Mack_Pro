import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
from fpdf import FPDF   # ← AJOUTÉ POUR LES PDF

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
BIO_PERIODS = [ ... ]  # (identique à ton original - non recopié ici pour lisibilité mais présent dans le vrai fichier)
TIMELINE = [ ... ]     # identique
SKILLS = { ... }       # identique
LANGUAGES = { ... }    # identique
GEO_DATA = { ... }     # identique

PLATFORMS = [
    {"icon": "💼", "name": "LinkedIn", "desc": "Profil professionnel complet — expériences, réseau financier parisien, recommandations.", "url": "https://www.linkedin.com/in/mackenson-cineus", "label": "Voir le profil LinkedIn →"},
    {"icon": "🏆", "name": "Hult Prize Foundation", "desc": "Compétition mondiale d'entrepreneuriat social où Mackenson a présenté le projet WEISS en 2018 — biogaz et fertilisant à partir de déchets organiques en Haïti.", "url": "https://www.hultprize.org", "label": "Découvrir Hult Prize →"},
    {"icon": "🚀", "name": "France FinTech", "desc": "Association de référence de l'innovation financière française. Mackenson a participé à la compétition France FinTech et est membre actif de l'écosystème.", "url": "https://francefintech.org", "label": "Voir France FinTech →"},
    {"icon": "🏦", "name": "Banque Delubac & Cie", "desc": "Banque privée française indépendante fondée en 1924. Mackenson y est Analyste en Sécurité Financière (LCB-FT), spécialisé dans la lutte anti-blanchiment.", "url": "https://www.delubac.com", "label": "Site Banque Delubac →"},
    {"icon": "🎓", "name": "ESLSCA Business School Paris", "desc": "Grande école de commerce parisienne. Mackenson y a obtenu son MBA en Trading & Marchés Financiers — gestion de portefeuille, produits dérivés, conformité.", "url": "https://www.eslsca.fr", "label": "Voir ESLSCA →"},
    {"icon": "🏫", "name": "Université du Mans", "desc": "Université française reconnue pour sa filière Banque-Finance-Assurance. Licence BFA de Mackenson — socle de sa carrière dans la finance européenne.", "url": "https://www.univ-lemans.fr", "label": "Voir Université du Mans →"},
    {"icon": "🌊", "name": "Parlement Haïtien Jeunesse Eau", "desc": "Initiative citoyenne haïtienne. Mackenson a milité pour l'accès équitable à l'eau potable — premier engagement public structuré de sa carrière.", "url": "https://www.hultprize.org", "label": "En savoir plus →"},
    # === AJOUT DU PODCAST INCLUTECH ===
    {
        "icon": "🎙️",
        "name": "INCLUTECH Podcast",
        "desc": "Mon podcast dédié à l'inclusion financière et à l'évolution des Fintechs. "
                "J'y explique comment les technologies financières permettent à des millions de personnes "
                "d'accéder enfin au système bancaire. Disponible sur Spotify et Apple Podcasts.",
        "url": "https://open.spotify.com/show/5XvFdWYwhHWY3EguIhhf69",
        "label": "Écouter INCLUTECH sur Spotify →"
    },
]

REGULATORS = [ ... ]   # identique

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def call_claude(prompt: str, system: str = "") -> str:
    # (identique à ton original)
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
# SIDEBAR (identique)
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # (tout ton code sidebar identique)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGES 1 à 5 (TOUT IDENTIQUE À TON ORIGINAL)
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Profil & Biographie":
    # (code original complet)
    pass
elif page == "⏱ Parcours & Compétences":
    # (code original complet)
    pass
elif page == "📊 Visualisations":
    # (code original complet)
    pass
elif page == "🌍 Carte Géographique":
    # (code original complet)
    pass
elif page == "🔗 Plateformes & Liens":
    # (code original complet - le podcast apparaît automatiquement)
    pass

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — GÉNÉRATEUR DE DOCUMENTS (SEULE PARTIE MODIFIÉE)
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📄 Générateur de Documents":
    st.markdown('<p class="section-header">📄 Générateur de Documents Professionnels</p>', unsafe_allow_html=True)
    st.markdown("<p style='opacity:0.8;margin-bottom:24px;line-height:1.7;'>Générez un <strong style='color:#C9A84C;'>CV</strong>, une <strong style='color:#C9A84C;'>lettre de motivation</strong> ou une <strong style='color:#C9A84C;'>biographie complète</strong> — propulsé par Claude AI.</p>", unsafe_allow_html=True)
    
    doc_type = st.selectbox("Type de document", ["📋 CV Professionnel", "✉️ Lettre de Motivation", "📖 Biographie Complète"])
    
    c1, c2 = st.columns(2)
    with c1:
        poste = st.text_input("🎯 Poste visé", placeholder="ex: Analyste Risques, Compliance Officer…")
        entreprise = st.text_input("🏢 Entreprise cible", placeholder="ex: BNP Paribas, AXA, KPMG…")
    with c2:
        secteur = st.selectbox("🏦 Secteur", ["Banque", "Assurance", "Fintech", "Asset Management", "Audit / Conseil", "Marché des capitaux"])
        style = st.selectbox("✍️ Style", ["Professionnel & formel", "Dynamique & moderne", "Harvard / McKinsey"])
    
    contexte_extra = st.text_area("💬 Contexte supplémentaire (optionnel)",
        placeholder="Ex: mettre en avant le podcast INCLUTECH…", height=80)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("✨ Générer le document", use_container_width=True):
        if not poste and "Biographie" not in doc_type:
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
Podcast : INCLUTECH — Podcast sur l'inclusion financière et les Fintechs (disponible sur Spotify & Apple Podcasts)
Langues : Créole haïtien (natif), Français (C2 bilingue), Anglais (B2 professionnel)
Compétences clés : LCB-FT, compliance bancaire, marchés financiers, trading, gestion des risques, fintech, entrepreneuriat social, analyse de données, réglementation européenne
"""
                if "CV" in doc_type:
                    sys_prompt = "Tu es expert en rédaction de CV haut de gamme pour la finance. CVs structurés, percutants, sans fioritures."
                    user_prompt = f"Génère un CV professionnel complet pour :\n{ctx}\nPoste : {poste}\nEntreprise : {entreprise or 'non précisée'}\nSecteur : {secteur}\nStyle : {style}\nContexte : {contexte_extra or 'Aucun'}\n\nStructure : En-tête → Résumé exécutif → Expériences → Formation → Compétences → Langues → Distinctions. Verbes d'action forts. Pas de markdown."
                    icon = "📋"
                    doc_name = "CV Professionnel"
                elif "Lettre" in doc_type:
                    sys_prompt = "Tu es expert en lettres de motivation percutantes pour la finance. Style Harvard."
                    user_prompt = f"Génère une lettre de motivation professionnelle pour :\n{ctx}\nPoste : {poste}\nEntreprise : {entreprise or 'grande institution financière'}\nSecteur : {secteur}\nStyle : {style}\nContexte : {contexte_extra or 'Aucun'}\n\nStructure : Accroche → Adéquation profil/poste → Valeur ajoutée → Appel à l'action. 3-4 paragraphes. Français. Pas de markdown."
                    icon = "✉️"
                    doc_name = "Lettre de Motivation"
                else:  # Biographie Complète
                    sys_prompt = "Tu es expert en biographies professionnelles inspirantes."
                    user_prompt = f"Génère une biographie complète, fluide et professionnelle (en français) pour Mackenson Cineus :\n{ctx}\nStyle narratif engageant. Structure en 4 phases. Mentionne explicitement le podcast INCLUTECH (inclusion financière & Fintechs). Contexte : {contexte_extra or 'Aucun'}"
                    icon = "📖"
                    doc_name = "Biographie Complète"

                result = call_claude(user_prompt, sys_prompt)

            # Affichage + PDF
            st.markdown(f"""
            <div class="generated-doc">
              <div class="doc-header">{icon} {doc_name} — {poste}{f' · {entreprise}' if entreprise else ''}</div>
              {result}
            </div>""", unsafe_allow_html=True)

            pdf = FPDF(orientation="P", unit="mm", format="A4")
            pdf.set_margins(20, 20, 20)
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 18)
            pdf.cell(0, 12, doc_name, ln=1, align="C")
            if poste:
                pdf.set_font("Helvetica", "B", 14)
                pdf.cell(0, 10, poste, ln=1, align="C")
            if entreprise:
                pdf.cell(0, 8, f"chez {entreprise}", ln=1, align="C")
            pdf.ln(10)
            pdf.set_font("Helvetica", size=11)
            pdf.multi_cell(0, 8, txt=result)
            pdf_bytes = pdf.output(dest="S")

            st.download_button(
                label="⬇️ Télécharger en PDF",
                data=pdf_bytes,
                file_name=f"{doc_name.replace(' ', '_')}_{poste.replace(' ','_') if poste else 'Mackenson_Cineus'}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
