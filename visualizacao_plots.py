import plotly.graph_objects as go
import streamlit as st
import numpy as np

def plot_mohr(x_env, y_env, xt_coll, xc_s, yc_s, xc_f, yc_f, env_high, sn_p, tn_p, p_x, p_y, falhou, params):
    with st.container(border=True):
        fig = go.Figure()
        
        # Envoltórias Base (Tração, Cisalhamento, Colapso)
        for cond, col, name in [
            (x_env <= 0, 'blue', "Ruptura por tração"),
            ((x_env > 0) & (x_env <= xt_coll), 'red', "Ruptura por cisalhamento"),
            (x_env > xt_coll, 'green', "Colapso de poros")
        ]:
            fig.add_trace(go.Scatter(x=x_env[cond], y=y_env[cond], line=dict(color=col, width=2), name=name))
            
            # Realce na Envoltória (Highlight de Falha)
            high_cond = cond & env_high
            if any(high_cond):
                fig.add_trace(go.Scatter(x=x_env[high_cond], y=y_env[high_cond], 
                                         line=dict(color=col, width=5), showlegend=False, hoverinfo='skip'))

        # Círculo de Mohr
        fig.add_trace(go.Scatter(x=xc_s, y=yc_s, line=dict(color='#1f77b4', width=2.5), name="Círculo (Estável)"))
        fig.add_trace(go.Scatter(x=xc_f, y=yc_f, line=dict(color='black', width=1.2, dash='dash'), name="Círculo (Falha)"))
        
        # Trajetória e Ponto
        fig.add_trace(go.Scatter(x=p_x, y=p_y, line=dict(color='orange', width=1.5, dash='dot'), name="Trajetória"))
        fig.add_trace(go.Scatter(x=[sn_p], y=[tn_p], mode='markers', 
                                 marker=dict(size=14, color='yellow' if falhou else 'lime', 
                                 line=dict(width=2, color='black')), showlegend=False))
        
        fig.update_layout(
            xaxis=dict(range=[-50, 250], title="σ'n (MPa)"),
            yaxis=dict(range=[0, 100], scaleanchor="x", scaleratio=1, title="τ (MPa)"),
            template="plotly_white", height=500, margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
