import plotly.graph_objects as go
import streamlit as st
import numpy as np

def plot_mohr(x_env, y_env, xt_coll, xc_f, yc_f, xc_o, yc_o, sn_p, tn_p, p_x, p_y, falhou, params):
    """
    Renderiza o Diagrama de Mohr com a lógica de colapso:
    - Círculo Teórico: Preto e tracejado fora da envoltória.
    - Círculo Real/Colapsado: Colorido (Azul/Vermelho/Verde) quando toca a envoltória.
    """
    fig = go.Figure()

    # 1. Linha de Base (y=0)
    fig.add_shape(type="line", x0=-50, y0=0, x1=250, y1=0, line=dict(color="black", width=2))

    # 2. Envoltórias de Resistência (Pretas e finas para servir de trilho)
    fig.add_trace(go.Scatter(x=x_env, y=y_env, line=dict(color='black', width=1), 
                             hoverinfo='skip', showlegend=False))

    # 3. Círculo Estável (Parte azul sólida que ainda não atingiu a falha)
    res_c = np.interp(xc_o, x_env, y_env, left=0, right=0)
    m_estavel = yc_o <= res_c + 1e-3
    fig.add_trace(go.Scatter(x=np.where(m_estavel, xc_o, np.nan), y=np.where(m_estavel, yc_o, np.nan), 
                             line=dict(color='#1f77b4', width=3), name="Estável"))

    # 4. Círculo Teórico (Preto e Tracejado onde houve falha)
    fig.add_trace(go.Scatter(x=np.where(~m_estavel, xc_o, np.nan), y=np.where(~m_estavel, yc_o, np.nan), 
                             line=dict(color='black', width=1, dash='dash'), name="Teórico"))

    # 5. ARCOS COLAPSADOS (Pintam a envoltória quando o círculo a atinge)
    # Usamos xc_f e yc_f que são os pontos 'travados' na envoltória pelo geostruct
    m_falha = ~m_estavel & (yc_o > 0.05)
    
    # Arco de Tração (Azul)
    fig.add_trace(go.Scatter(x=np.where(m_falha & (xc_f < 0), xc_f, np.nan), 
                             y=np.where(m_falha & (xc_f < 0), yc_f, np.nan), 
                             line=dict(color='blue', width=4), showlegend=False))
    
    # Arco de Cisalhamento (Vermelho)
    fig.add_trace(go.Scatter(x=np.where(m_falha & (xc_f >= 0) & (xc_f <= xt_coll), xc_f, np.nan), 
                             y=np.where(m_falha & (xc_f >= 0) & (xc_f <= xt_coll), yc_f, np.nan), 
                             line=dict(color='red', width=4), showlegend=False))
    
    # Arco de Colapso (Verde)
    fig.add_trace(go.Scatter(x=np.where(m_falha & (xc_f > xt_coll), xc_f, np.nan), 
                             y=np.where(m_falha & (xc_f > xt_coll), yc_f, np.nan), 
                             line=dict(color='green', width=4), showlegend=False))

    # 6. Trajetória e Ponto Geomecânico
    fig.add_trace(go.Scatter(x=p_x, y=p_y, line=dict(color='orange', width=1.5, dash='dash'), name="Trajetória"))
    fig.add_trace(go.Scatter(x=[sn_p], y=[tn_p], mode='markers', 
                             marker=dict(size=14, color='yellow' if falhou else '#2ca02c', 
                             line=dict(width=2, color='black')), showlegend=False))

    # 7. Rótulos das Zonas
    fig.add_annotation(x=-params['ts'] - 15, y=30, text="<b>Ruptura por<br>Tração</b>", font=dict(color="blue", size=10), showarrow=False)
    fig.add_annotation(x=xt_coll/2, y=90, text="<b>Cisalhamento</b>", font=dict(color="red", size=10), showarrow=False)
    fig.add_annotation(x=params['pc'] + 20, y=30, text="<b>Colapso<br>de poros</b>", font=dict(color="green", size=10), showarrow=False)

    # 8. Configurações de Eixos
    fig.update_layout(
        title="ANÁLISE DE ESTABILIDADE (MOHR-COULOMB)",
        xaxis=dict(range=[-50, 250], fixedrange=True, gridcolor='lightgray'),
        yaxis=dict(range=[0, 100], fixedrange=True, gridcolor='lightgray', scaleanchor="x", scaleratio=1),
        template="plotly_white", height=500, margin=dict(l=20, r=20, t=50, b=20), showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def plot_3d_block(regime, ang_s1):
    st.subheader("Visualização Espacial do Bloco")
    st.info(f"Regime: {regime} | Ângulo: {ang_s1}°")
