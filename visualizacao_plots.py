import plotly.graph_objects as go
import streamlit as st
import numpy as np

def plot_mohr(x_env, y_env, xt_coll, xc_f, yc_f, res_c, xc_o, yc_o, sn_p, tn_p, p_x, p_y, falhou, params):
    """Renderiza o Diagrama de Mohr com eixos Sn/Tau e nomes das rupturas."""
    with st.container(border=True):
        fig = go.Figure()
        
        # Eixos Principais
        fig.add_shape(type="line", x0=-50, y0=0, x1=250, y1=0, line=dict(color="black", width=2))
        fig.add_shape(type="line", x0=0, y0=0, x1=0, y1=100, line=dict(color="black", width=2))
        
        # Trechos da Envoltória
        fig.add_trace(go.Scatter(x=x_env[x_env<=0], y=y_env[x_env<=0], line=dict(color='blue', width=1.5), name="Tração"))
        fig.add_trace(go.Scatter(x=x_env[(x_env>0) & (x_env<=xt_coll)], y=y_env[(x_env>0) & (x_env<=xt_coll)], line=dict(color='red', width=1.5), name="Híbrida/Cisalhamento"))
        fig.add_trace(go.Scatter(x=x_env[x_env>xt_coll], y=y_env[x_env>xt_coll], line=dict(color='green', width=1.5), name="Colapso"))
        
        # Labels das Rupturas (Nomes)
        fig.add_annotation(x=-25, y=55, text="Tração", showarrow=False, font=dict(color="blue", size=11))
        fig.add_annotation(x=xt_coll/2, y=85, text="Cisalhamento", showarrow=False, font=dict(color="red", size=11))
        fig.add_annotation(x=xt_coll + 40, y=70, text="Colapso", showarrow=False, font=dict(color="green", size=11))

        # Círculos e Arcos
        m_s = (yc_o < res_c - 1e-3); m_f = ~m_s & (yc_o > 0.05)
        fig.add_trace(go.Scatter(x=np.where(m_s, xc_o, np.nan), y=np.where(m_s, yc_o, np.nan), line=dict(color='#1f77b4', width=2.5), name="Estável"))
        fig.add_trace(go.Scatter(x=np.where(~m_s, xc_o, np.nan), y=np.where(~m_s, yc_o, np.nan), line=dict(color='black', width=1, dash='dash'), showlegend=False))
        
        for cond, c in [(m_f & (xc_f < 0), 'blue'), (m_f & (xc_f >= 0) & (xc_f <= xt_coll), 'red'), (m_f & (xc_f > xt_coll), 'green')]:
            fig.add_trace(go.Scatter(x=np.where(cond, xc_f, np.nan), y=np.where(cond, yc_f, np.nan), line=dict(color=c, width=4), showlegend=False))
        
        # Trajetória e Ponto Atual
        fig.add_trace(go.Scatter(x=p_x, y=p_y, line=dict(color='orange', width=1.5, dash='dash'), name="Trajetória"))
        fig.add_trace(go.Scatter(x=[sn_p], y=[tn_p], mode='markers', marker=dict(size=14, color='yellow' if falhou else '#2ca02c', line=dict(width=2, color='black')), showlegend=False))
        
        fig.update_layout(
            xaxis=dict(range=[-50, 250], title="σ'n (MPa)"),
            yaxis=dict(range=[0, 100], scaleanchor="x", scaleratio=1, title="τ' (MPa)"),
            template="plotly_white", height=500, margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True, key="mohr_final_v26")
