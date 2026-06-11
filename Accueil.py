import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration globale de l'application
st.set_page_config(
    page_title="DRC MacroData Hub",
    page_icon="🇨🇩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fonction de chargement globale (utilisée sur toutes les pages)
@st.cache_data
def load_data():
    file_path = "Base de données 3.xlsx"
    
    # 1. Données Annuelles
    df_annuel = pd.read_excel(file_path, sheet_name='RDC  Donnees annuelles')
    unites_annuelles = df_annuel.iloc[0]
    # Nettoyage des en-têtes Excel (Lignes 0 et 1)
    df_annuel_clean = df_annuel.iloc[2:].copy()
    df_annuel_clean['Code'] = pd.to_numeric(df_annuel_clean['Code'], errors='coerce')
    df_annuel_clean = df_annuel_clean.dropna(subset=['Code'])
    df_annuel_clean['Code'] = df_annuel_clean['Code'].astype(int)
    
    # 2. Données Mensuelles (Taux de change)
    df_tc_mensuel = pd.read_excel(file_path, sheet_name='Taux de change mensuel')
    
    # 3. Marchés Mondiaux
    df_marches = pd.read_excel(file_path, sheet_name='Marchés mondiaux mensuel')
    
    return df_annuel_clean, df_tc_mensuel, df_marches, unites_annuelles

# Initialisation et chargement
try:
    df_annuel, df_tc, df_marches, unites = load_data()
except Exception as e:
    st.error(f"❌ Erreur critique lors du chargement de la base de données : {e}")
    st.stop()

# --- HEADER PRINCIPAL ---
st.title("🇨🇩 DRC MacroData Hub")
st.markdown("""
**Plateforme interactive d'analyse macroéconomique de la République Démocratique du Congo.** Inspirée des systèmes d'information de la Banque mondiale, cette interface centralise, traite et valorise les données des secteurs réel, monétaire et extérieur de la RDC pour soutenir la recherche et l'aide à la décision.
""")
st.markdown("---")

# --- SECTION 1 : DASHBOARD CONJONCTUREL (KPI) ---
st.subheader("📌 Indicateurs Macroéconomiques Récents")

# Extraction de la dernière année disponible dotée de données réelles
df_valid_pib = df_annuel.dropna(subset=['CROISSANCE_PIB_PCT'])
if not df_valid_pib.empty:
    latest_row = df_valid_pib.iloc[-1]
    latest_year = int(latest_row['Code'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label=f"Croissance du PIB réel ({latest_year})", 
            value=f"{float(latest_row['CROISSANCE_PIB_PCT']):.1f} %",
            delta=f"{float(latest_row['CROISSANCE_PIB_PCT']) - float(df_valid_pib.iloc[-2]['CROISSANCE_PIB_PCT']):.1f} % vs An-1"
        )
    with col2:
        inflation = latest_row['INFLATION_PCT']
        st.metric(
            label=f"Taux d'inflation moyen ({latest_year})", 
            value=f"{float(inflation):.1f} %" if pd.notna(inflation) else "N/A"
        )
    with col3:
        pib_usd = float(latest_row['PIB_NOM_USD']) / 1_000_000_000
        st.metric(
            label=f"PIB Nominal ({latest_year})", 
            value=f"{pib_usd:.2f} Md $"
        )
    with col4:
        pop = float(latest_row['POP_TOT']) / 1_000_000
        st.metric(
            label=f"Population totale ({latest_year})", 
            value=f"{pop:.1f} M hab."
        )
else:
    st.warning("Données annuelles indisponibles ou mal formatées.")

st.markdown("---")

# --- SECTION 2 : VISUALISATION DE LA CROISSANCE ---
st.subheader("📊 Dynamique historique du PIB")

col_fs1, col_fs2 = st.columns([1, 4])
with col_fs1:
    st.markdown("**Filtres temporels**")
    min_y, max_y = int(df_annuel['Code'].min()), int(df_annuel['Code'].max())
    year_range = st.slider("Sélectionnez la période", min_y, max_y, (2000, max_y))

df_filtered = df_annuel[(df_annuel['Code'] >= year_range[0]) & (df_annuel['Code'] <= year_range[1])].copy()
df_filtered['CROISSANCE_PIB_PCT'] = pd.to_numeric(df_filtered['CROISSANCE_PIB_PCT'], errors='coerce')

with col_fs2:
    fig_pib = px.area(
        df_filtered, 
        x='Code', 
        y='CROISSANCE_PIB_PCT',
        title=f"Évolution du taux de croissance du PIB réel ({year_range[0]} - {year_range[1]})",
        labels={'Code': 'Année', 'CROISSANCE_PIB_PCT': 'Taux de croissance (%)'},
        markers=True
    )
    fig_pib.update_layout(hovermode="x unified", title_x=0.1)
    st.plotly_chart(fig_pib, use_container_width=True)

# Pied de page institutionnel
st.markdown("---")
st.caption("Source des données : Banque mondiale / Banque Centrale du Congo (BCC) | Unité de recherche FASE - UPC")
