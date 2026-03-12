import plotly.graph_objects as go
import streamlit as st
import numpy as np

def plot_mohr(x_env, y_env, xt_coll, xr, yr, xc, yc, sn_p, tn_p, params):
    """
    Replica fielmente o comportamento do mohr_window.py original:
    - Envoltórias coloridas (Azul, Vermelho, Verde).
    - Círculo estável em azul escuro.
    - Arcos de falha espessos quando o círculo ultrapassa a envoltória.
    - Círculo teórico tracejado em preto.
    """
    
    fig = go.Figure()

    # 1. Linha de Base (Baseline preta horizontal)
    fig.add_shape(type="line", x0=-50, y0=0, x1=250, y1=0, line=dict(color="black", width=2))

    # 2. ENVOLTÓRIAS (Lógica original: já nascem coloridas)
    # Tração (Azul)
    m_env_tens = x_env <= 0
    fig.add_trace(go.Scatter(x=x_env[m_env_tens], y=y_env[m_env_tens], 
                             name="Tração", line=dict(color='blue', width=1.5), hoverinfo='skip'))
    
    # Cisalhamento (Vermelho)
    m_env_shear = (x_env > 0) & (x_env <= xt_coll)
    fig.add_trace(go.Scatter(x=x_env[m_env_shear], y=y_env[m_env_shear], 
                             name="Cisalhamento", line=dict(color='red', width=1.5), hoverinfo='skip'))
    
    # Colapso (Verde)
    m_env_coll = x_env > xt_coll
    fig.add_trace(go.Scatter(x=x_env[m_env_coll], y=y_env[m_env_coll], 
                             name="Colapso", line=dict(color='green', width=1.5), hoverinfo='skip'))

    # 3. CÍRCULO ESTÁVEL (Azul escuro #1f77b4 conforme original)
    # Usamos o 'res_c' interpolado para saber o que está abaixo da envoltória
    res_c = np.interp(xr, x_env, y_env, left=0, right=0)
    m_s = (yr < res_c - 1e-3)
    fig.add_trace(go.Scatter(x=xr[m_s], y=yr[m_s], name="Estável", 
                             line=dict(color='#1f77b4', width=2), hoverinfo='skip'))

    # 4. CÍRCULO TEÓRICO (Tracejado preto)
    m_t = (yc > res_c)
    fig.add_trace(go.Scatter(x=xc[m_t], y=yc[m_t], name="Teórico", 
                             line=dict(color='black', width=1, dash='dash'), hoverinfo='skip'))

    # 5. ARCOS DE FALHA (Arcos espessos coloridos quando yr > envoltória)
    m_f = ~m_s & (yr > 0.05)
    
    # Arco Tração (Azul espesso)
    fig.add_trace(go.Scatter(x=xr[m_f & (xr < 0)], y=yr[m_f & (xr < 0)], 
                             line=dict(color='blue', width=4), showlegend=False))
    
    # Arco Cisalhamento (Vermelho espesso)
    fig.add_trace(go.Scatter(x=xr[m_f & (xr >= 0) & (xr <= xt_coll)], y=yr[m_f & (xr >= 0) & (xr <= xt_coll)], 
                             line=dict(color='red', width=4), showlegend=False))
    
    # Arco Colapso (Verde espesso)
    fig.add_trace(go.Scatter(x=xr[m_f & (xr > xt_coll)], y=yr[m_f & (xr > xt_coll)], 
                             line=dict(color='green', width=4), showlegend=False))

    # 6. PONTO ATUAL (Amarelo ou Verde conforme estado de falha)
    # No original: amarelo se falhou, verde se não. 
    # Para simplificar na web, mantemos o amarelo de destaque
    fig.add_trace(go.Scatter(x=[sn_p], y=[tn_p], mode='markers', 
                             marker=dict(size=14, color='yellow', line=dict(width=2, color='black')),
                             showlegend=False))

    # 7. RÓTULOS (Posições baseadas na lógica do mohr_window.py)
    fig.add_annotation(x=-params['ts'] - 15, y=30, text="<b>Ruptura por<br>Tração</b>", font=dict(color="blue", size=11), showarrow=False)
    fig.add_annotation(x=xt_coll/2, y=85, text="<b>Cisalhamento</b>", font=dict(color="red", size=11), showarrow=False)
    fig.add_annotation(x=params['pc'] + 20, y=30, text="<b>Colapso<br>de poros</b>", font=dict(color="green", size=11), showarrow=False)

    # 8. CONFIGURAÇÃO DE EIXOS FIXOS
    fig.update_layout(
        title="ANÁLISE DE ESTABILIDADE (MOHR-COULOMB)",
        xaxis_title="Tensão Normal Efetiva (σn') [MPa]",
        yaxis_title="Tensão Cisalhante Efetiva (τ') [MPa]",
        height=500,
        template="plotly_white",
        xaxis=dict(range=[-50, 250], fixedrange=True, gridcolor='lightgray'),
        yaxis=dict(range=[0, 100], fixedrange=True, gridcolor='lightgray', scaleanchor="x", scaleratio=1),
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def plot_3d_block(regime, ang_s1):
    st.subheader("Visualização Espacial do Bloco")
    st.info(f"Regime: {regime} | Ângulo: {ang_s1}°")
