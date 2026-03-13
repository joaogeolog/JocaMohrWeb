import plotly.graph_objects as go
import streamlit as st

def render_mohr_plot(x_env, y_env, xt_coll, xc_s, yc_s, xc_f, yc_f, env_high, sn_p, tn_p, p_x, p_y, falhou):
    with st.container(border=True):
        fig = go.Figure()
        
        # Eixos principais
        fig.add_shape(type="line", x0=-50, y0=0, x1=250, y1=0, line=dict(color="black", width=2))
        fig.add_shape(type="line", x0=0, y0=0, x1=0, y1=100, line=dict(color="black", width=2))
        
        # Segmentação da Envoltória
        m_tra = x_env <= 0
        m_cis = (x_env > 0) & (x_env <= xt_coll)
        m_col = x_env > xt_coll
        
        fig.add_trace(go.Scatter(x=x_env[m_tra], y=y_env[m_tra], line=dict(color='blue', width=2.5), name="Ruptura por tração"))
        fig.add_trace(go.Scatter(x=x_env[m_cis], y=y_env[m_cis], line=dict(color='red', width=2.5), name="Ruptura por cisalhamento"))
        fig.add_trace(go.Scatter(x=x_env[m_col], y=y_env[m_col], line=dict(color='green', width=2.5), name="Colapso de poros"))
        
        # REALCE AMARELO (CORREÇÃO AQUI: opacity fora da line)
        if env_high is not None and any(env_high):
            fig.add_trace(go.Scatter(
                x=x_env[env_high], 
                y=y_env[env_high], 
                line=dict(color='yellow', width=6), 
                opacity=0.4, # <--- Opacity agora no lugar certo
                showlegend=False,
                hoverinfo='skip'
            ))

        # Círculos de Mohr e Trajetória
        fig.add_trace(go.Scatter(x=xc_s, y=yc_s, line=dict(color='#1f77b4', width=2.5), name="Estado Estável"))
        fig.add_trace(go.Scatter(x=xc_f, y=yc_f, line=dict(color='black', width=1.2, dash='dash'), name="Falha"))
        fig.add_trace(go.Scatter(x=p_x, y=p_y, line=dict(color='orange', width=1.5, dash='dot'), name="Trajetória"))
        
        # Ponto Atual
        fig.add_trace(go.Scatter(
            x=[sn_p], y=[tn_p], 
            mode='markers', 
            marker=dict(size=14, color='yellow' if falhou else 'lime', line=dict(width=2, color='black')), 
            showlegend=False
        ))
        
        fig.update_layout(
            xaxis=dict(range=[-50, 250], title="Tensão Normal Efetiva, σ'n (MPa)"), 
            yaxis=dict(range=[0, 100], scaleanchor="x", scaleratio=1, title="Tensão Cisalhante, τ (MPa)"), 
            template="plotly_white", 
            height=500, 
            margin=dict(l=10, r=10, t=10, b=10), 
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)