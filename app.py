import streamlit as st
import numpy as np
import plotly.graph_objects as go
import geostruct_engine as eng

# Configuração da página para ocupar a tela cheia
st.set_page_config(layout="wide", page_title="JocaMohr Web", page_icon="🪨")

# --- Estilização para simular o visual Desktop ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #ddd; }
    h3 { color: #2c3e50; font-size: 1.2rem !important; margin-bottom: 0.5rem; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (Equivalente ao ControlWindow) ---
with st.sidebar:
    st.title("JocaMohr")
    st.caption("Autor: João Carlos Menescal | Março 2026")
    
    with st.expander("1. ESTADO DE TENSÃO (MPa)", expanded=True):
        s1 = st.number_input("S1 (MPa)", 0.0, 400.0, 120.0)
        s3 = st.number_input("S3 (MPa)", 0.0, 300.0, 40.0)
        pp = st.number_input("P. Poros (MPa)", 0.0, 200.0, 20.0)
        alpha = st.slider("Biot (alpha)", 0.0, 1.0, 1.0, 0.05)

    with st.expander("2. PROPRIEDADES DA ROCHA", expanded=True):
        c = st.number_input("Coesão (MPa)", 0.0, 100.0, 15.0)
        phi = st.number_input("Atrito (°)", 0.0, 60.0, 30.0)
        ts = st.number_input("Tração (MPa)", 0.0, 50.0, 10.0)
        pc = st.number_input("Compressão (MPa)", 0.0, 500.0, 180.0)

    with st.expander("3. ORIENTAÇÃO DO PLANO", expanded=True):
        regime = st.selectbox("Regime Tectônico", ["Normal", "Transcorrente", "Reverso"])
        ang_s1 = st.slider("Ângulo com S1 (°)", 0.0, 90.0, 30.0)
        
    if st.button("Limpar Trajetória", use_container_width=True):
        st.cache_resource.clear()

# --- CÁLCULOS (Usando sua Engine) ---
s1_eff = s1 - (alpha * pp)
s3_eff = s3 - (alpha * pp)
centro, raio = (s1_eff + s3_eff) / 2, (s1_eff - s3_eff) / 2

x_env, y_env, xt_coll = eng.calcular_envoltoria(ts, pc, c, phi)
xr, yr, res_c, xc, yc = eng.obter_geometria_v18(centro, raio, x_env, y_env, ts, pc)

# Simulação do ponto atual (Sn, Tn)
theta_rad = np.radians(ang_s1)
sn_atual = centro - raio * np.cos(2 * theta_rad)
tn_atual = abs(raio * np.sin(2 * theta_rad))

# --- LAYOUT DE MOSAICO (Mohr em cima, 3D embaixo) ---
container_mohr = st.container()
container_3d = st.container()

with container_mohr:
    st.subheader("Análise de Estabilidade (Mohr-Coulomb)")
    fig_mohr = go.Figure()
    
    # Envoltórias (Tração, Cisalhamento, Colapso)
    fig_mohr.add_trace(go.Scatter(x=x_env[x_env<=0], y=y_env[x_env<=0], name="Tração", line=dict(color='blue', width=2)))
    fig_mohr.add_trace(go.Scatter(x=x_env[(x_env>0) & (x_env<=xt_coll)], y=y_env[(x_env>0) & (x_env<=xt_coll)], name="Cisalhamento", line=dict(color='red', width=2)))
    fig_mohr.add_trace(go.Scatter(x=x_env[x_env>xt_coll], y=y_env[x_env>xt_coll], name="Colapso", line=dict(color='green', width=2)))
    
    # Círculo de Mohr (Parte Estável e Falha)
    fig_mohr.add_trace(go.Scatter(x=xr, y=yr, name="Círculo", line=dict(color='#1f77b4', width=3)))
    
    # Ponto no plano
    fig_mohr.add_trace(go.Scatter(x=[sn_atual], y=[tn_atual], mode='markers', marker=dict(size=12, color='yellow', line=dict(width=2, color='black')), name="Estado no Plano"))

    fig_mohr.update_layout(
        xaxis_title="Tensão Normal Efetiva (MPa)", yaxis_title="Tensão Cisalhante (MPa)",
        height=450, margin=dict(l=20, r=20, t=20, b=20),
        yaxis=dict(scaleanchor="x", scaleratio=1), # Mantém proporção 1:1
        showlegend=False
    )
    st.plotly_chart(fig_mohr, use_container_width=True)

with container_3d:
    st.subheader("Visualização do Bloco 3D")
    
    # Vetores de tensão simplificados para 3D (Substituindo PyVista)
    fig_3d = go.Figure()
    # Adiciona um cubo de referência
    fig_3d.add_trace(go.Mesh3d(x=[-1,1,1,-1,-1,1,1,-1], y=[-1,-1,1,1,-1,-1,1,1], z=[-1,-1,-1,-1,1,1,1,1], 
                               i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2], j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3], k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                               opacity=0.1, color='gray'))
    
    fig_3d.update_layout(scene=dict(aspectmode='data'), height=400, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_3d, use_container_width=True)