import streamlit as st

def sync_widgets(source_key, target_key, common_state_key):
    """Sincroniza os widgets através de uma chave comum no session_state."""
    st.session_state[common_state_key] = st.session_state[source_key]
    st.session_state[target_key] = st.session_state[source_key]

def dual_input(label, min_v, max_v, default_v, step=1.0, key_p=""):
    st.write(f"**{label}**")
    
    # Chaves únicas para cada widget e uma comum para o valor final
    s_key = f"slide_{key_p}"
    n_key = f"num_{key_p}"
    base_key = f"val_{key_p}"
    
    # Inicialização do estado na primeira execução
    if base_key not in st.session_state:
        st.session_state[base_key] = float(default_v)
        st.session_state[s_key] = float(default_v)
        st.session_state[n_key] = float(default_v)
    
    col1, col2 = st.columns([2, 1])
    
    # Slider
    col1.slider(
        label,
        min_value=float(min_v),
        max_value=float(max_v),
        step=float(step),
        key=s_key,
        on_change=sync_widgets,
        args=(s_key, n_key, base_key),
        label_visibility="collapsed"
    )
    
    # Number Input
    col2.number_input(
        label,
        min_value=float(min_v),
        max_value=float(max_v),
        step=float(step),
        key=n_key,
        on_change=sync_widgets,
        args=(n_key, s_key, base_key),
        label_visibility="collapsed"
    )
    
    return st.session_state[base_key]

def render_sidebar():
    with st.sidebar:
        st.title("⚒️ JocaMohr Web")
        st.caption("Geólogo: João Carlos Menescal")

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
