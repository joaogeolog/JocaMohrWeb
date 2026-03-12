import streamlit as st
import numpy as np
import plotly.graph_objects as go
import geostruct_engine as eng # Sua lógica original

# 1. Configuração para ocupar a largura total da tela
st.set_page_config(layout="wide", page_title="JocaMohr Geomech", page_icon="⚒️")

# --- CSS para remover espaços brancos e fixar o layout ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; padding-left: 2rem; padding-right: 2rem; }
    [data-testid="stExpander"] { border: 1px solid #d1d1d1; border-radius: 5px; background: white; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: Equivalente ao seu 'control_window.py' ---
# Ela fica fixa à esquerda, ocupando o espaço que você definiu no mosaico
with st.sidebar:
    st.title("⚒️ JocaMohr Web")
    st.info("Geólogo: João Carlos Menescal")
    
    with st.expander("TENSÕES (MPa)", expanded=True):
        s1 = st.number_input("S1", value=120.0)
        s3 = st.number_input("S3", value=40.0)
        pp = st.number_input("P. Poros", value=20.0)
        alpha = st.slider("Biot (α)", 0.0, 1.0, 1.0)

    with st.expander("ROCHA", expanded=True):
        c = st.number_input("Coesão", value=15.0)
        phi = st.number_input("Atrito (°)", value=30.0)
        ts = st.number_input("Tração", value=10.0)
        pc = st.number_input("Compressão", value=180.0)

    regime = st.selectbox("Regime", ["Normal", "Transcorrente", "Reverso"])
    ang_s1 = st.slider("Ângulo c/ S1 (°)", 0.0, 90.0, 30.0)

# --- ÁREA PRINCIPAL: Integração do Mohr e Bloco 3D ---
# Criamos uma única coluna que empilha os dois widgets, mantendo a ordem do seu main.py
col_content = st.container()

with col_content:
    # 2. Equivalente ao 'mohr_window.py' (Topo Direito)
    with st.expander("DIAGRAMA DE MOHR-COULOMB", expanded=True):
        # Cálculos usando sua engine
        s1_eff, s3_eff = s1 - (alpha*pp), s3 - (alpha*pp)
        x_env, y_env, xt_coll = eng.calcular_envoltoria(ts, pc, c, phi)
        
        fig_mohr = go.Figure()
        # Adiciona a envoltória (exemplo simplificado da sua lógica)
        fig_mohr.add_trace(go.Scatter(x=x_env, y=y_env, name="Falha", line=dict(color='red')))
        
        # Desenha o Círculo
        centro, raio = (s1_eff + s3_eff)/2, (s1_eff - s3_eff)/2
        t = np.linspace(0, np.pi, 100)
        fig_mohr.add_trace(go.Scatter(x=centro + raio*np.cos(t), y=raio*np.sin(t), fill='toself', name="Estado Atual"))

        fig_mohr.update_layout(
            height=380, # Altura controlada para caber no mosaico
            margin=dict(l=10, r=10, t=30, b=10),
            yaxis=dict(scaleanchor="x", scaleratio=1),
            showlegend=False
        )
        st.plotly_chart(fig_mohr, use_container_width=True)

    # 3. Equivalente ao 'fracture_window.py' (Base Direito)
    with st.expander("VISUALIZAÇÃO DO BLOCO 3D", expanded=True):
        # Aqui entra a visualização 3D do Plotly substituindo o PyVista
        fig_3d = go.Figure(data=[go.Mesh3d(
            x=[0, 1, 2, 0], y=[0, 2, 1, 2], z=[0, 1, 2, 3],
            opacity=0.5, color='lightblue'
        )])
        
        fig_3d.update_layout(
            height=380,
            margin=dict(l=0, r=0, t=30, b=0),
            scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z')
        )
        st.plotly_chart(fig_3d, use_container_width=True)
