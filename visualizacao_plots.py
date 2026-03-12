import plotly.graph_objects as go
import streamlit as st
import numpy as np

def plot_mohr(x_env, y_env, xt_coll, xc_f, yc_f, res_c, xc_o, yc_o, sn_p, tn_p, p_x, p_y, falhou, params):
    """
    Replica fielmente o mohr_window.py original:
    - Envoltórias coloridas.
    - Círculo Estável: Azul escuro.
    - Círculo Teórico: Preto tracejado.
    - Arcos de Falha: Espessos e colapsados sobre a envoltória.
    """
    fig = go.Figure()

    # 1. Linha de Base
    fig.add_shape(type="line", x0=-50, y0=0, x1=250, y1=0, line=dict(color="black", width=2))

    # 2. Envoltórias Coloridas (Fixas)
    fig.add_trace(go.Scatter(x=x_env[x_env<=0], y=y_env[x_env<=0], 
                             line=dict(color='blue', width=1.5), hoverinfo='skip', showlegend=False))
    fig.add_trace(go.Scatter(x=x_env[(x_env>0) & (x_env<=xt_coll)], y=y_env[(x_env>0) & (x_env<=xt_coll)], 
                             line=dict(color='red', width=1.5), hoverinfo='skip', showlegend=False))
    fig.add_trace(go.Scatter(x=x_env[x_env>xt_coll], y=y_env[x_env>xt_coll], 
                             line=dict(color='green', width=1.5), hoverinfo='skip', showlegend=False))

    # 3. Máscaras de Estabilidade
    m_s = (yc_o < res_c - 1e-3) # Parte estável
    m_f = ~m_s & (yc_o > 0.05)   # Parte em falha

    # Círculo Estável (Azul Escuro)
    fig.add_trace(go.Scatter(x=np.where(m_s, xc_o, np.nan), y=np.where(m_s, yc_o, np.nan), 
                             line=dict(color='#1f77b4', width=2.5), name="Estável"))

    # Círculo Teórico (Preto Tracejado)
    fig.add_trace(go.Scatter(x=np.where(~m_s, xc_o, np.nan), y=np.where(~m_s, yc_o, np.nan), 
                             line=dict(color='black', width=1, dash='dash'), name="Teórico"))

    # 4. Arcos de Falha (Colapsados na Envoltória)
    fig.add_trace(go.Scatter(x=np.where(m_f & (xc_f < 0), xc_f, np.nan), y=np.where(m_f & (xc_f < 0), yc_f, np.nan), 
                             line=dict(color='blue', width=4), showlegend=False))
    fig.add_trace(go.Scatter(x=np.where(m_f & (xc_f >= 0) & (xc_f <= xt_coll), xc_f, np.nan), y=np.where(m_f & (xc_f >= 0) & (xc_f <= xt_coll), yc_f, np.nan), 
                             line=dict(color='red', width=4), showlegend=False))
    fig.add_trace(go.Scatter(x=np.where(m_f & (xc_f > xt_coll), xc_f, np.nan), y=np.where(m_f & (xc_f > xt_coll), yc_f, np.nan), 
                             line=dict(color='green', width=4), showlegend=False))

    # 5. Trajetória e Ponto
    fig.add_trace(go.Scatter(x=p_x, y=p_y, line=dict(color='orange', width=1.5, dash='dash'), name="Trajetória"))
    fig.add_trace(go.Scatter(x=[sn_p], y=[tn_p], mode='markers', 
                             marker=dict(size=14, color='yellow' if falhou else '#2ca02c', line=dict(width=2, color='black')), showlegend=False))

    # 6. Rótulos Técnicos (Usando chaves corretas: 'ts' e 'pc')
    fig.add_annotation(x=-params['ts'] - 15, y=30, text="<b>Ruptura por<br>Tração</b>", font=dict(color="blue", size=10), showarrow=False)
    fig.add_annotation(x=xt_coll/2, y=90, text="<b>Cisalhamento</b>", font=dict(color="red", size=10), showarrow=False)
    fig.add_annotation(x=params['pc'] + 20, y=30, text="<b>Colapso<br>de poros</b>", font=dict(color="green", size=10), showarrow=False)

    # 7. Layout
    fig.update_layout(
        xaxis=dict(range=[-50, 250], fixedrange=True, gridcolor='lightgray'),
        yaxis=dict(range=[0, 100], fixedrange=True, gridcolor='lightgray', scaleanchor="x", scaleratio=1),
        template="plotly_white", height=500, margin=dict(l=20, r=20, t=50, b=20), showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def plot_3d_block(regime, ang_s1):
    st.subheader("Visualização Espacial do Bloco")
    st.info(f"Regime: {regime} | Ângulo: {ang_s1}°")
