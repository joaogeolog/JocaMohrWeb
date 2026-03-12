import plotly.graph_objects as go
import streamlit as st
import numpy as np

def plot_mohr(x_env, y_env, xt_coll, xr, yr, xc, yc, sn_p, tn_p, params):
    """
    Renderiza o Diagrama de Mohr-Coulomb com a lógica de cores de falha.
    Envoltória: Preta (Limite neutro).
    Círculo: Azul (Estável) e Colorido/Tracejado (Falha).
    """
    
    fig = go.Figure()

    # 1. Linha de Base (y=0)
    fig.add_shape(type="line", x0=-50, y0=0, x1=250, y1=0, line=dict(color="rgba(0,0,0,0.2)", width=1))

    # 2. Envoltória de Resistência (Cor Neutra: Preta)
    fig.add_trace(go.Scatter(x=x_env, y=y_env, name="Envoltória", 
                             line=dict(color='black', width=1.5), hoverinfo='skip'))

    # 3. Círculo Estável (Parte que está dentro dos limites de resistência)
    fig.add_trace(go.Scatter(x=xr, y=yr, name="Estável", 
                             line=dict(color='#1f77b4', width=3)))

    # 4. Trechos de Falha (Parte do círculo que ultrapassou a envoltória)
    # A cor só aparece aqui, no trecho colapsado/tracejado
    
    # Falha por Tração (Azul)
    mask_c_tens = xc <= 0
    if np.any(mask_c_tens):
        fig.add_trace(go.Scatter(x=xc[mask_c_tens], y=yc[mask_c_tens], 
                                 line=dict(color='blue', width=2, dash='dash'), showlegend=False))
    
    # Falha por Cisalhamento (Vermelho)
    mask_c_shear = (xc > 0) & (xc <= xt_coll)
    if np.any(mask_c_shear):
        fig.add_trace(go.Scatter(x=xc[mask_c_shear], y=yc[mask_c_shear], 
                                 line=dict(color='red', width=2, dash='dash'), showlegend=False))
    
    # Falha por Colapso (Verde)
    mask_c_coll = xc > xt_coll
    if np.any(mask_c_coll):
        fig.add_trace(go.Scatter(x=xc[mask_c_coll], y=yc[mask_c_coll], 
                                 line=dict(color='green', width=2, dash='dash'), showlegend=False))

    # 5. Ponto de Estado no Plano (Amarelo com borda preta)
    fig.add_trace(go.Scatter(x=[sn_p], y=[tn_p], mode='markers', 
                             marker=dict(size=12, color='yellow', line=dict(width=1.5, color='black')),
                             showlegend=False))

    # 6. Rótulos Técnicos (Nomes das zonas de falha)
    fig.add_annotation(x=-25, y=45, text="<b>Ruptura por<br>Tração</b>", font=dict(color="blue", size=10), showarrow=False)
    fig.add_annotation(x=xt_coll/2, y=90, text="<b>Cisalhamento</b>", font=dict(color="red", size=10), showarrow=False)
    fig.add_annotation(x=210, y=45, text="<b>Colapso<br>de poros</b>", font=dict(color="green", size=10), showarrow=False)

    # 7. Configuração de Eixos Fixos e Proporção Isotrópica
    fig.update_layout(
        title="Análise de Estabilidade (Mohr-Coulomb)",
        xaxis_title="Tensão Normal Efetiva σn' (MPa)",
        yaxis_title="Tensão Cisalhante τ' (MPa)",
        height=500,
        template="plotly_white",
        xaxis=dict(range=[-50, 250], fixedrange=True, gridcolor='rgba(0,0,0,0.05)'),
        yaxis=dict(range=[0, 100], fixedrange=True, gridcolor='rgba(0,0,0,0.05)', scaleanchor="x", scaleratio=1),
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def plot_3d_block(regime, ang_s1):
    """Visualização Espacial do Bloco."""
    st.subheader("Visualização Espacial do Bloco")
    # O próximo passo será implementar o bloco 3D aqui
    st.info(f"Visualizando Regime {regime} com inclinação de {ang_s1}°")
