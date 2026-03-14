import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import requests
from datetime import datetime

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
    --gold: #C9A84C;
    --gold-light: #E8C97A;
    --navy: #0D1B2A;
    --navy-mid: #1A2E42;
    --navy-light: #243B55;
    --cream: #F5F0E8;
    --white: #FFFFFF;
    --accent: #4A9EFF;
    --success: #2ECC71;
  }

  .stApp { background: var(--navy); color: var(--cream); }
  .stApp > header { background: transparent !important; }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--navy-mid) 0%, var(--navy) 100%);
    border-right: 1px solid rgba(201,168,76,0.2);
  }
  [data-testid="stSidebar"] * { color: var(--cream) !important; }

  /* Typography */
  h1, h2, h3 { font-family: 'Playfair Display', serif !important; }
  p, div, span, label { font-family: 'DM Sans', sans-serif !important; }

  /* Hero Banner */
  .hero-banner {
    background: linear-gradient(135deg, var(--navy-mid) 0%, var(--navy-light) 50%, var(--navy-mid) 100%);
    border: 1px solid rgba(201,168,76,0.3);
    border-radius: 16px;
    padding: 40px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
  }
  .hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(201,168,76,0.08) 0%, transparent 70%);
    pointer-events: none;
  }
  .hero-name {
    font-family: 'Playfair Display', serif !important;
    font-size: 3rem !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-light) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
    margin: 0;
  }
  .hero-title {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1.1rem;
    color: var(--cream);
    opacity: 0.85;
    margin-top: 8px;
    letter-spacing: 2px;
    text-transform: uppercase;
  }
  .hero-badge {
    display: inline-block;
    background: rgba(201,168,76,0.15);
    border: 1px solid rgba(201,168,76,0.4);
    border-radius: 50px;
    padding: 4px 14px;
    font-size: 0.8rem;
    color: var(--gold-light);
    margin: 4px;
    font-family: 'DM Sans', sans-serif !important;
  }

  /* Cards */
  .metric-card {
    background: linear-gradient(135deg, var(--navy-mid), var(--navy-light));
    border: 1px solid rgba(201,168,76,0.2);
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    transition: border-color 0.3s;
  }
  .metric-card:hover { border-color: rgba(201,168,76,0.6); }
  .metric-value {
    font-family: 'Playfair Display', serif !important;
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--gold);
    display: block;
  }
  .metric-label {
    font-size: 0.85rem;
    color: var(--cream);
    opacity: 0.7;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
  }

  /* Section headers */
  .section-header {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.8rem !important;
    color: var(--gold) !important;
    border-bottom: 1px solid rgba(201,168,76,0.3);
    padding-bottom: 12px;
    margin-bottom: 24px;
  }

  /* Timeline items */
  .timeline-item {
    background: var(--navy-mid);
    border-left: 3px solid var(--gold);
    border-radius: 0 12px 12px 0;
    padding: 16px 20px;
    margin-bottom: 16px;
    transition: background 0.3s;
  }
  .timeline-item:hover { background: var(--navy-light); }
  .timeline-year { color: var(--gold); font-weight: 600; font-size: 0.85rem; letter-spacing: 1px; }
  .timeline-title { font-size: 1.05rem; font-weight: 600; color: var(--white); margin: 4px 0; }
  .timeline-desc { font-size: 0.9rem; color: var(--cream); opacity: 0.8; }

  /* Skill bars */
  .skill-bar-container { margin-bottom: 12px; }
  .skill-name { font-size: 0.9rem; color: var(--cream); margin-bottom: 4px; }
  .skill-bar { height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; }
  .skill-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, var(--gold), var(--gold-light)); }

  /* Buttons */
  .stButton > button {
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-light) 100%) !important;
    color: var(--navy) !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px;
    padding: 10px 24px !important;
    transition: all 0.3s !important;
  }
  .stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(201,168,76,0.3) !important;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] { background: var(--navy-mid); border-radius: 8px; gap: 4px; }
  .stTabs [data-baseweb="tab"] { color: var(--cream) !important; font-family: 'DM Sans', sans-serif !important; }
  .stTabs [aria-selected="true"] { background: rgba(201,168,76,0.2) !important; color: var(--gold) !important; }

  /* Text areas & inputs */
  .stTextArea textarea, .stTextInput input, .stSelectbox select {
    background: var(--navy-mid) !important;
    color: var(--cream) !important;
    border: 1px solid rgba(201,168,76,0.3) !important;
    border-radius: 8px !important;
  }

  /* Generated document */
  .generated-doc {
    background: var(--navy-mid);
    border: 1px solid rgba(201,168,76,0.2);
    border-radius: 12px;
    padding: 32px;
    font-family: 'DM Sans', sans-serif;
    line-height: 1.8;
    white-space: pre-wrap;
    color: var(--cream);
  }
  .doc-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    color: var(--gold);
    margin-bottom: 16px;
    border-bottom: 1px solid rgba(201,168,76,0.2);
    padding-bottom: 12px;
  }

  /* Hide streamlit defaults */
  #MainMenu, footer, [data-testid="stHeader"] { display: none !important; }
  .block-container { padding-top: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# ─── DATA ──────────────────────────────────────────────────────────────────────
PROFILE = {
    "name": "Mackenson Cineus",
    "title": "Analyste Sécurité Financière (LCB-FT)",
    "location": "Paris, France",
    "email": "mackenson.cineus@email.com",
    "phone": "+33 6 XX XX XX XX",
    "linkedin": "linkedin.com/in/mackenson-cineus",
    "summary": (
        "Professionnel de la finance internationale alliant rigueur analytique et vision sociale. "
        "Passionné par la conformité bancaire, les marchés financiers et l'innovation fintech, "
        "avec une expérience couvrant Haïti, la France et les réseaux internationaux."
    ),
}

TIMELINE = [
    {"year": "2014–2017", "title": "Université d'État d'Haïti", "desc": "Faculté de Droit et des Sciences Économiques — Économie & Politiques publiques", "icon": "🎓", "cat": "Éducation"},
    {"year": "2018", "title": "Hult Prize — Compétition Internationale", "desc": "Projet WEISS : transformation des déchets en biogaz & fertilisant agricole", "icon": "🏆", "cat": "Entrepreneuriat"},
    {"year": "2018–2019", "title": "Parlement Haïtien de la Jeunesse pour l'Eau", "desc": "Engagement citoyen — sensibilisation aux ressources hydriques", "icon": "🌊", "cat": "Social"},
    {"year": "2019–2021", "title": "Université du Mans — Licence BFA", "desc": "Banque, Finance & Assurance — analyse financière, marchés, réglementation", "icon": "🏫", "cat": "Éducation"},
    {"year": "2021–2023", "title": "ESLSCA Business School Paris — MBA", "desc": "Spécialisation Trading & Marchés Financiers — gestion de portefeuille", "icon": "📈", "cat": "Éducation"},
    {"year": "2023–Présent", "title": "Banque Delubac & Cie", "desc": "Analyste Sécurité Financière — LCB-FT, transactions suspectes, conformité", "icon": "🏦", "cat": "Professionnel"},
    {"year": "2023–Présent", "title": "France FinTech", "desc": "Participation active à l'écosystème fintech parisien", "icon": "💡", "cat": "Réseau"},
]

SKILLS = {
    "LCB-FT / Compliance": 92,
    "Analyse financière": 88,
    "Trading & Marchés": 82,
    "Réglementation bancaire": 85,
    "Gestion des risques": 80,
    "Fintech & Innovation": 75,
    "Entrepreneuriat social": 78,
    "Analyse de données": 72,
}

LANGUAGES = {"Français": 95, "Anglais": 85, "Créole haïtien": 100}

GEO_DATA = {
    "locations": ["Port-au-Prince, Haïti", "Le Mans, France", "Paris, France"],
    "lat": [18.5432, 47.9960, 48.8566],
    "lon": [-72.3388, 0.1966, 2.3522],
    "events": ["Formation initiale + Entrepreneuriat", "Licence BFA", "MBA + Carrière bancaire"],
    "years": ["2014–2019", "2019–2021", "2021–Présent"],
    "size": [20, 15, 30],
}

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def call_claude(prompt: str, system: str = "") -> str:
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    headers = {"Content-Type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"}
    body = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=body, timeout=60)
        data = r.json()
        if "content" in data:
            return "".join(b.get("text", "") for b in data["content"] if b.get("type") == "text")
        return f"Erreur API : {data.get('error', {}).get('message', 'Inconnue')}"
    except Exception as e:
        return f"Erreur de connexion : {str(e)}"


def plotly_dark_layout(fig):
    fig.update_layout(
        paper_bgcolor="rgba(13,27,42,0)",
        plot_bgcolor="rgba(13,27,42,0)",
        font=dict(family="DM Sans", color="#F5F0E8"),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px;'>
      <div style='width:80px; height:80px; border-radius:50%; background:linear-gradient(135deg,#C9A84C,#4A9EFF);
                  display:flex; align-items:center; justify-content:center; font-size:2rem;
                  margin:0 auto 12px; border:3px solid rgba(201,168,76,0.4);'>MC</div>
      <div style='font-family:Playfair Display,serif; font-size:1.1rem; font-weight:700; color:#C9A84C;'>
        Mackenson Cineus
      </div>
      <div style='font-size:0.78rem; color:#F5F0E8; opacity:0.7; margin-top:4px;'>
        Finance · Compliance · Fintech
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    page = st.radio(
        "Navigation",
        ["🏠 Profil & Parcours", "📊 Visualisations", "🌍 Carte Géographique", "📄 Générateur de Documents"],
        label_visibility="collapsed"
    )
    st.divider()
    st.markdown("<div style='font-size:0.75rem; opacity:0.5; text-align:center; padding:10px;'>© 2024 Mackenson Cineus<br>Tous droits réservés</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — PROFIL & PARCOURS
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Profil & Parcours":

    # Hero
    st.markdown(f"""
    <div class="hero-banner">
      <p class="hero-name">{PROFILE['name']}</p>
      <p class="hero-title">{PROFILE['title']} · {PROFILE['location']}</p>
      <div style="margin-top:16px;">
        <span class="hero-badge">🏦 LCB-FT</span>
        <span class="hero-badge">📈 Trading</span>
        <span class="hero-badge">💡 Fintech</span>
        <span class="hero-badge">🌍 International</span>
        <span class="hero-badge">🏆 Hult Prize 2018</span>
      </div>
      <p style="margin-top:20px; max-width:700px; opacity:0.85; line-height:1.7; font-family:'DM Sans',sans-serif;">
        {PROFILE['summary']}
      </p>
    </div>
    """, unsafe_allow_html=True)

    # KPI cards
    cols = st.columns(4)
    kpis = [
        ("8+", "Années d'expérience"),
        ("3", "Pays traversés"),
        ("2", "Diplômes sup."),
        ("1", "Prix international"),
    ]
    for col, (val, lbl) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <span class="metric-value">{val}</span>
              <div class="metric-label">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Timeline + Skills side by side
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<p class="section-header">Parcours chronologique</p>', unsafe_allow_html=True)
        cats = ["Tous"] + sorted(set(t["cat"] for t in TIMELINE))
        filter_cat = st.selectbox("Filtrer par catégorie", cats, label_visibility="collapsed")
        items = TIMELINE if filter_cat == "Tous" else [t for t in TIMELINE if t["cat"] == filter_cat]
        for item in items:
            st.markdown(f"""
            <div class="timeline-item">
              <div class="timeline-year">{item['icon']} {item['year']} · {item['cat']}</div>
              <div class="timeline-title">{item['title']}</div>
              <div class="timeline-desc">{item['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown('<p class="section-header">Compétences clés</p>', unsafe_allow_html=True)
        for skill, level in SKILLS.items():
            st.markdown(f"""
            <div class="skill-bar-container">
              <div class="skill-name">{skill} <span style="float:right; color:#C9A84C; font-weight:600;">{level}%</span></div>
              <div class="skill-bar"><div class="skill-fill" style="width:{level}%;"></div></div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<br><p class="section-header">Langues</p>', unsafe_allow_html=True)
        for lang, level in LANGUAGES.items():
            st.markdown(f"""
            <div class="skill-bar-container">
              <div class="skill-name">{lang} <span style="float:right; color:#4A9EFF; font-weight:600;">{level}%</span></div>
              <div class="skill-bar"><div class="skill-fill" style="width:{level}%; background:linear-gradient(90deg,#4A9EFF,#7BC8FF);"></div></div>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — VISUALISATIONS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Visualisations":

    st.markdown('<p class="section-header">📊 Analyses & Visualisations</p>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Radar Compétences", "Évolution de carrière", "Répartition des axes", "Langues"])

    # ── Radar chart ──
    with tab1:
        skills_names = list(SKILLS.keys())
        skills_vals = list(SKILLS.values())
        fig = go.Figure(go.Scatterpolar(
            r=skills_vals + [skills_vals[0]],
            theta=skills_names + [skills_names[0]],
            fill='toself',
            fillcolor='rgba(201,168,76,0.15)',
            line=dict(color='#C9A84C', width=2),
            marker=dict(color='#C9A84C', size=8),
        ))
        fig.update_layout(
            polar=dict(
                bgcolor='rgba(26,46,66,0.5)',
                radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(255,255,255,0.1)', color='#F5F0E8'),
                angularaxis=dict(gridcolor='rgba(255,255,255,0.1)', color='#F5F0E8', tickfont=dict(size=11)),
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='DM Sans', color='#F5F0E8'),
            title=dict(text='Radar des Compétences Professionnelles', font=dict(color='#C9A84C', size=16)),
            height=480,
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Career progression timeline ──
    with tab2:
        df_timeline = pd.DataFrame([
            {"Période": "2014", "Niveau": 10, "Étape": "Université d'État d'Haïti", "Pays": "Haïti"},
            {"Période": "2018", "Niveau": 35, "Étape": "Hult Prize / WEISS", "Pays": "International"},
            {"Période": "2019", "Niveau": 50, "Étape": "Université du Mans — BFA", "Pays": "France"},
            {"Période": "2021", "Niveau": 70, "Étape": "ESLSCA Paris — MBA", "Pays": "France"},
            {"Période": "2023", "Niveau": 90, "Étape": "Banque Delubac — LCB-FT", "Pays": "France"},
        ])
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_timeline["Période"], y=df_timeline["Niveau"],
            mode='lines+markers+text',
            line=dict(color='#C9A84C', width=3),
            marker=dict(size=14, color='#C9A84C', line=dict(color='#1A2E42', width=3)),
            text=df_timeline["Étape"], textposition='top center',
            textfont=dict(size=10, color='#F5F0E8'),
            hovertemplate='<b>%{text}</b><br>Progression : %{y}%<extra></extra>',
        ))
        fig2.update_layout(
            title=dict(text='Progression de Carrière', font=dict(color='#C9A84C', size=16)),
            yaxis=dict(title='Niveau de développement professionnel (%)', range=[0, 110], gridcolor='rgba(255,255,255,0.07)', color='#F5F0E8'),
            xaxis=dict(title='Année', color='#F5F0E8', gridcolor='rgba(255,255,255,0.07)'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(13,27,42,0.6)',
            font=dict(family='DM Sans', color='#F5F0E8'),
            height=430,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Pie chart axes ──
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            axes = {"Finance & Conformité": 45, "Entrepreneuriat Social": 25, "Engagement Citoyen": 15, "Innovation Fintech": 15}
            fig3 = go.Figure(go.Pie(
                labels=list(axes.keys()), values=list(axes.values()),
                hole=0.5,
                marker=dict(colors=['#C9A84C', '#4A9EFF', '#2ECC71', '#E67E22'],
                            line=dict(color='#0D1B2A', width=2)),
                textfont=dict(color='white', size=12),
            ))
            fig3.update_layout(
                title=dict(text='Répartition des axes du parcours', font=dict(color='#C9A84C', size=14)),
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='DM Sans', color='#F5F0E8'),
                legend=dict(font=dict(color='#F5F0E8'), bgcolor='rgba(0,0,0,0)'),
                height=380,
            )
            st.plotly_chart(fig3, use_container_width=True)

        with col2:
            countries = {"Haïti": 40, "France": 50, "International": 10}
            fig4 = go.Figure(go.Bar(
                x=list(countries.keys()), y=list(countries.values()),
                marker=dict(color=['#4A9EFF', '#C9A84C', '#2ECC71'],
                            line=dict(color='#0D1B2A', width=1)),
                text=[f"{v}%" for v in countries.values()],
                textposition='outside', textfont=dict(color='#F5F0E8'),
            ))
            fig4.update_layout(
                title=dict(text='Répartition géographique du parcours', font=dict(color='#C9A84C', size=14)),
                yaxis=dict(range=[0, 70], gridcolor='rgba(255,255,255,0.07)', color='#F5F0E8'),
                xaxis=dict(color='#F5F0E8'),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(13,27,42,0.6)',
                font=dict(family='DM Sans', color='#F5F0E8'),
                height=380,
            )
            st.plotly_chart(fig4, use_container_width=True)

    # ── Languages ──
    with tab4:
        fig5 = go.Figure()
        colors = {'Créole haïtien': '#2ECC71', 'Français': '#C9A84C', 'Anglais': '#4A9EFF'}
        for lang, lvl in LANGUAGES.items():
            fig5.add_trace(go.Bar(
                x=[lvl], y=[lang], orientation='h',
                marker_color=colors.get(lang, '#C9A84C'),
                text=[f"{lvl}%"], textposition='inside',
                textfont=dict(color='white', size=14, family='Playfair Display'),
                hovertemplate=f'{lang}: {lvl}%<extra></extra>',
            ))
        fig5.update_layout(
            title=dict(text='Maîtrise des Langues', font=dict(color='#C9A84C', size=16)),
            xaxis=dict(range=[0, 110], gridcolor='rgba(255,255,255,0.07)', color='#F5F0E8'),
            yaxis=dict(color='#F5F0E8'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(13,27,42,0.6)',
            font=dict(family='DM Sans', color='#F5F0E8'),
            showlegend=False, height=300, barmode='overlay',
        )
        st.plotly_chart(fig5, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — CARTE GÉOGRAPHIQUE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🌍 Carte Géographique":
    st.markdown('<p class="section-header">🌍 Parcours Géographique International</p>', unsafe_allow_html=True)

    df_geo = pd.DataFrame(GEO_DATA)

    fig_map = go.Figure()

    # Connection lines
    coords = list(zip(GEO_DATA['lat'], GEO_DATA['lon']))
    for i in range(len(coords) - 1):
        fig_map.add_trace(go.Scattergeo(
            lat=[coords[i][0], coords[i+1][0]],
            lon=[coords[i][1], coords[i+1][1]],
            mode='lines',
            line=dict(width=2, color='rgba(201,168,76,0.5)'),
            showlegend=False,
        ))

    # Markers
    fig_map.add_trace(go.Scattergeo(
        lat=GEO_DATA['lat'], lon=GEO_DATA['lon'],
        mode='markers+text',
        marker=dict(
            size=GEO_DATA['size'],
            color=['#4A9EFF', '#C9A84C', '#C9A84C'],
            line=dict(color='white', width=2),
            opacity=0.9,
        ),
        text=GEO_DATA['locations'],
        textposition=['bottom right', 'bottom left', 'top right'],
        textfont=dict(size=12, color='white'),
        customdata=list(zip(GEO_DATA['events'], GEO_DATA['years'])),
        hovertemplate='<b>%{text}</b><br>%{customdata[0]}<br>%{customdata[1]}<extra></extra>',
    ))

    fig_map.update_geos(
        projection_type="natural earth",
        showcoastlines=True, coastlinecolor='rgba(255,255,255,0.2)',
        showland=True, landcolor='rgba(26,46,66,0.8)',
        showocean=True, oceancolor='rgba(13,27,42,0.9)',
        showlakes=False,
        showcountries=True, countrycolor='rgba(255,255,255,0.1)',
        center=dict(lat=30, lon=-20),
        projection_scale=2.5,
    )
    fig_map.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans', color='#F5F0E8'),
        height=500,
        margin=dict(l=0, r=0, t=20, b=0),
        geo=dict(bgcolor='rgba(0,0,0,0)'),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Summary below map
    st.markdown('<br>', unsafe_allow_html=True)
    cols = st.columns(3)
    for col, (loc, event, year) in zip(cols, zip(GEO_DATA['locations'], GEO_DATA['events'], GEO_DATA['years'])):
        with col:
            st.markdown(f"""
            <div class="timeline-item" style="border-left-color:#4A9EFF;">
              <div class="timeline-year">📍 {year}</div>
              <div class="timeline-title">{loc}</div>
              <div class="timeline-desc">{event}</div>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — GÉNÉRATEUR DE DOCUMENTS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📄 Générateur de Documents":

    st.markdown('<p class="section-header">📄 Générateur de Documents Professionnels</p>', unsafe_allow_html=True)
    st.markdown("""
    <p style='opacity:0.8; margin-bottom:24px;'>
    Générez un <strong style='color:#C9A84C;'>CV professionnel</strong> ou une 
    <strong style='color:#C9A84C;'>lettre de motivation</strong> personnalisés pour des postes 
    en finance, compliance ou fintech, powered by Claude AI.
    </p>
    """, unsafe_allow_html=True)

    doc_type = st.selectbox(
        "Type de document",
        ["📋 CV Professionnel", "✉️ Lettre de Motivation"],
        label_visibility="visible",
    )

    col1, col2 = st.columns(2)
    with col1:
        poste = st.text_input("🎯 Poste visé", placeholder="ex: Analyste Risques, Compliance Officer…")
        entreprise = st.text_input("🏢 Entreprise cible", placeholder="ex: BNP Paribas, AXA, KPMG…")
    with col2:
        secteur = st.selectbox("🏦 Secteur", ["Banque", "Assurance", "Fintech", "Asset Management", "Audit / Conseil", "Marché des capitaux"])
        style = st.selectbox("✍️ Style", ["Professionnel & formel", "Dynamique & moderne", "Harvard / McKinsey"])

    contexte_extra = st.text_area(
        "💬 Contexte supplémentaire (optionnel)",
        placeholder="Ex: je souhaite mettre en avant mon expérience LCB-FT, postuler en CDI, …",
        height=80,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(f"✨ Générer le document", use_container_width=True):
        if not poste:
            st.error("⚠️ Veuillez indiquer le poste visé.")
        else:
            with st.spinner("⚙️ Génération en cours avec Claude AI…"):
                profile_context = f"""
Profil : Mackenson Cineus
Formation : Université d'État d'Haïti (Économie) → Université du Mans (Licence Banque-Finance-Assurance) → ESLSCA Paris (MBA Trading & Marchés Financiers)
Expérience : Analyste Sécurité Financière LCB-FT chez Banque Delubac & Cie (Paris)
Expériences clés : Hult Prize 2018 (projet WEISS – biogaz/fertilisant), Parlement Haïtien de la Jeunesse pour l'Eau, France FinTech
Compétences : LCB-FT, conformité bancaire, marchés financiers, trading, gestion des risques, fintech, analyse de transactions
Langues : Créole haïtien (natif), Français (bilingue), Anglais (professionnel)
Localisation : Paris, France
Atouts distinctifs : parcours international, double culture, entrepreneuriat social, insertion dans le système financier européen
"""
                if "CV" in doc_type:
                    system = "Tu es un expert en rédaction de CV professionnels haut de gamme pour le secteur financier. Tu génères des CVs structurés, percutants et sans fioritures."
                    prompt = f"""
Génère un CV professionnel complet et détaillé pour ce profil :

{profile_context}

Poste visé : {poste}
Entreprise : {entreprise if entreprise else 'non précisée'}
Secteur : {secteur}
Style : {style}
Contexte : {contexte_extra if contexte_extra else 'Aucun'}

Structure : En-tête → Résumé exécutif → Expériences → Formation → Compétences → Langues → Activités distinctives
Langue : Français. Utilise des verbes d'action forts. Quantifie quand possible.
"""
                else:
                    system = "Tu es un expert en rédaction de lettres de motivation percutantes pour le secteur financier. Style Harvard / top consultants."
                    prompt = f"""
Génère une lettre de motivation professionnelle, structurée et convaincante pour ce profil :

{profile_context}

Poste visé : {poste}
Entreprise : {entreprise if entreprise else 'une grande institution financière'}
Secteur : {secteur}
Style : {style}
Contexte : {contexte_extra if contexte_extra else 'Aucun'}

Structure : Accroche percutante → Adéquation profil/poste → Valeur ajoutée → Conclusion avec appel à l'action
3-4 paragraphes. Langue française. Ton : {style}.
"""
                result = call_claude(prompt, system)

            icon = "📋" if "CV" in doc_type else "✉️"
            st.markdown(f"""
            <div class="generated-doc">
              <div class="doc-header">{icon} {doc_type} — {poste}{f' · {entreprise}' if entreprise else ''}</div>
              {result}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label="⬇️ Télécharger (.txt)",
                data=result,
                file_name=f"{'CV' if 'CV' in doc_type else 'LM'}_{poste.replace(' ','_')}_MackenssonCineus.txt",
                mime="text/plain",
                use_container_width=True,
            )
