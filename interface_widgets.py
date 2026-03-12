import streamlit as st

def dual_input(label, min_v, max_v, default_v, step=1.0, key_p=""):
    st.write(f"**{label}**")
    
    # Nome da chave única no estado da sessão
    key = f"val_{key_p}"
    
    # Inicializa o valor se a página for carregada pela primeira vez
    if key not in st.session_state:
        st.session_state[key] = float(default_v)
    
    col1, col2 = st.columns([2, 1])
    
    # O segredo da sincronia: ambos usam a mesma 'key' do session_state
    # Quando um muda, o Streamlit atualiza automaticamente o valor da 'key' para o outro
    col1.slider(
        label, 
        min_value=float(min_v), 
        max_value=float(max_v), 
        step=float(step),
        key=key,  # Chave compartilhada
        label_visibility="collapsed"
    )
    
    col2.number_input(
        label, 
        min_value=float(min_v), 
        max_value=float(max_v), 
        step=float(step),
        key=key,  # Chave compartilhada
        label_visibility="collapsed"
    )
    
    # Retorna o valor atualizado que ambos estão editando
    return st.session_state[key]

def render_sidebar():
    with st.sidebar:
        st.title("⚒️ JocaMohr Web")
        st.caption("Geólogo: João Carlos Menescal | Macaé, RJ")

        with st.expander("1. ESTADO DE TENSÃO (MPa)", expanded=True):
            s1 = dual_input("S1", 0.0, 400.0, 120.0, key_p="s1")
            s3 = dual_input("S3", 0.0, 300.0, 40.0, key_p="s3")
            pp = dual_input("P. Poros", 0.0, 200.0, 20.0, key_p="pp")
            alpha = dual_input("Biot (α)", 0.0, 1.0, 1.0, step=0.01, key_p="alpha")

        with st.expander("2. PROPRIEDADES DA ROCHA", expanded=True):
            c_rock = dual_input("Coesão", 0.0, 100.0, 15.0, key_p="c")
            phi = dual_input("Atrito (°)", 0.0, 60.0, 30.0, key_p="phi")
            ts = dual_input("Tração", 0.0, 50.0, 10.0, key_p="ts")
            pc = dual_input("Compressão", 0.0, 500.0, 180.0, key_p="pc")

        with st.expander("3. ORIENTAÇÃO DO PLANO", expanded=True):
            regime = st.selectbox("Regime Tectônico", ["Normal", "Transcorrente", "Reverso"], key="regime_sel")
            ang_s1 = dual_input("Ângulo com S1 (°)", 0.0, 90.0, 30.0, step=0.1, key_p="ang")
            
    return {
        "s1": s1, "s3": s3, "pp": pp, "alpha": alpha,
        "c": c_rock, "phi": phi, "ts": ts, "pc": pc,
        "regime": regime, "ang_s1": ang_s1
    }
