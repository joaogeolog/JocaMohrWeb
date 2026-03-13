import plotly.graph_objects as go
import streamlit as st
import numpy as np

def render_mohr_plot(x_env, y_env, xt_coll, xcf, ycf, env_high, sn_p, tn_p, p_x, p_y, falhou):
    with st.container(border=True):
        fig = go.Figure()

        # 1. Linhas de Referência (Eixos)
        fig.add_shape(type="line", x0=-50, y0=0, x1=250, y1=0, line=dict(color="black", width=2))
        fig.add_shape(type="line", x0=0, y0=0, x1=0, y1=150, line=dict(color="black", width=1.5))
        
        # 2. CÍRCULO TEÓRICO COMPLETO (Preto Tracejado)
        # Plotado primeiro para servir de base. Aparecerá onde o azul claro não cobrir.
        fig.add_trace(go.Scatter(
            x=p_x, y=p_y, 
            line=dict(color='black', width=1.5, dash='dash'), 
            name="Limite de Falha (Teórico)",
            hoverinfo='skip'
        ))

        # 3. PARTE ESTÁVEL DO CÍRCULO (Azul Claro)
        # IMPORTANTE: xcf e ycf já vêm limitados (clipped) pelo motor
        # Eles "morrem" na envoltória, permitindo que o tracejado preto apareça além deles.
        fig.add_trace(go.Scatter(
            x=xcf, y=ycf, 
            line=dict(color='#ADD8E6', width=3), # Azul claro solicitado
            name="Estado de Tensão Estável",
            fill='toself', # Preenchimento leve para dar volume ao estado estável
            fillcolor='rgba(173, 216, 230, 0.15)' 
        ))

        # 4. ENVOLTÓRIAS (Plotadas por cima para garantir nitidez)
        m_tra, m_cis, m_col = x_env <= 0, (x_env > 0) & (x_env <= xt_coll), x_env > xt_coll
        fig.add_trace(go.Scatter(x=x_env[m_tra], y=y_env[m_tra], line=dict(color='blue', width=2.5), name="Envoltória Tração"))
        fig.add_trace(go.Scatter(x=x_env[m_cis], y=y_env[m_cis], line=dict(color='red', width=2.5), name="Envoltória Cisalhamento"))
        fig.add_trace(go.Scatter(x=x_env[m_col], y=y_env[m_col], line=dict(color='green', width=2.5), name="Envoltória Colapso"))
        
        # 5. MARCADOR DO PLANO (Círculo Amarelo)
        fig.add_trace(go.Scatter(
            x=[sn_p], y=[tn_p], 
            mode='markers', 
            marker=dict(
                size=14, 
                color='yellow' if falhou else 'lime', 
                line=dict(width=2, color='black')
            ), 
            name="Plano Analisado"
        ))

        # 6. Configurações de Layout (Escala 1:1 e Nomes Técnicos)
        fig.update_layout(
            xaxis=dict(range=[-50, 250], title="Tensão Normal Efetiva, σ'n (MPa)"),
            yaxis=dict(
                range=[0, 100], 
                scaleanchor="x", 
                scaleratio=1, 
                title="Tensão Cisalhante, τ (MPa)"
            ),
            template="plotly_white",
            height=550,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
