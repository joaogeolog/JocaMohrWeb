import plotly.graph_objects as go
import streamlit as st
import numpy as np

def plot_mohr(x_env, y_env, xt_coll, xr, yr, xc, yc, sn_p, tn_p, params):
    """Renderiza o Diagrama de Mohr-Coulomb com eixos fixos e legendas técnicas."""
    
    fig = go.Figure()

    # 1. Linha de Base (y=0)
    fig.add_shape(type="line", x0=-50, y0=0, x1=250, y1=0, line=dict(color="black", width=1))

    # 2. Envoltórias de Falha (Segmentadas por Cor)
    # Tração (Azul)
    mask_tens = x_env <= 0
    fig.add_trace(go.Scatter(x=x_env[mask_tens], y=y_env[mask_tens], 
                             name="Tração", line=dict(color='blue', width=2.5), hoverinfo='skip'))
    
    # Cisalhamento (Vermelho)
    mask_shear = (x_env > 0) & (x_env <= xt_coll)
    fig.add_trace(go.Scatter(x=x_env[mask_shear], y=y_env[mask_shear], 
                             name="Cisalhamento", line=dict(color='red', width=2.5), hoverinfo='skip'))
    
    # Colapso (Verde)
    mask_coll = x_env > xt_coll
    fig.add_trace(go.Scatter(x=x_env[mask_coll], y=y_env[mask_coll], 
                             name="Colapso", line=dict(color='green', width=2.5), hoverinfo='skip'))

    # 3. Círculo de Mohr (Estável e Teórico/Falha)
    fig.add_trace(go.Scatter(x=xr, y=yr, name="Círculo Estável", line=dict(color='#1f77b4', width=3)))
    fig.add_trace(go.Scatter(x=xc, y=yc, name="Teórico", line=dict(color='black', width=1, dash='dash')))

    # 4. Ponto de Estado no Plano (Amarelo)
    fig.add_trace(go.Scatter(x=[sn_p], y=[tn_p], mode='markers', 
                             marker=dict(size=14, color='yellow', line=dict(width=2, color='black')),
                             showlegend=False))

    # 5. Rótulos das Zonas de Falha (Nomes recuperados da imagem original)
    fig.add_annotation(x=-25, y=45, text="<b>Ruptura por<br>Tração</b>", font=dict(color="blue", size=11), showarrow=False)
    fig.add_annotation(x=xt_coll/2, y=90, text="<b>Cisalhamento</b>", font=dict(color="red", size=11), showarrow=False)
    fig.add_annotation(x=210, y=45, text="<b>Colapso<br>de poros</b>", font=dict(color="green", size=11), showarrow=False)

    # 6. Configuração de Eixos Fixos e Proporção 1:1
    fig.update_layout(
        title="Análise de Estabilidade (Mohr-Coulomb)",
        xaxis_title="Tensão Normal Efetiva σn' (MPa)",
        yaxis_title="Tensão Cisalhante τ' (MPa)",
        height=500,
        template="plotly_white",
        xaxis=dict(range=[-50, 250], fixedrange=True, gridcolor='lightgray'),
        yaxis=dict(range=[0, 100], fixedrange=True, gridcolor='lightgray', scaleanchor="x", scaleratio=1),
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def plot_3d_block(regime, ang_s1):
    """Espaço reservado para a visualização 3D."""
    st.subheader("Visualização Espacial do Bloco")
    st.info(f"Regime: {regime} | Ângulo: {ang_s1}°")
    # Em breve preencheremos com o Plotly 3D
