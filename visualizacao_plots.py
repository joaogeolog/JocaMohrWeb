# ... (Mantenha as funções plot_mohr e as definições de eixos inalteradas)

def plot_3d_block(params):
    # ... (Toda a lógica matemática anterior de planos e vetores permanece igual)

    # AJUSTE DE CÂMERA: Forçando o centro de órbita no (0,0,0)
    camera = dict(
        eye=dict(x=1.5, y=1.5, z=1.5),    # Posição inicial da câmera
        center=dict(x=0, y=0, z=0),       # PONTO FIXO DE ROTAÇÃO (Centro do Cubo)
        up=dict(x=0, y=0, z=1)            # Orientação do 'Céu' (Z para cima)
    )

    fig.update_layout(
        scene=dict(
            xaxis_visible=False, 
            yaxis_visible=False, 
            zaxis_visible=False, 
            aspectmode='data',
            camera=camera # Aplica a trava de rotação centralizada
        ), 
        height=500, 
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
