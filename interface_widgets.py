import streamlit as st

def sync_input(key_to_update, new_value):
    """Atualiza o valor no session_state para garantir a sincronização."""
    st.session_state[key_to_update] = new_value

def dual_input(label, min_v, max_v, default_v, step=1.0, key_p=""):
    st.write(f"**{label}**")
    
    # Inicializa o estado se não existir
    if f"val_{key_p}" not in st.session_state:
        st.session_state[f"val_{key_p}"] = float(default_v)
    
    c1, c2 = st.columns([2, 1])
    
    # 1. Slider: Quando alterado, dispara o callback para atualizar o Number Input
    val_slider = c1.slider(
        f"S_{key_p}", min_v, max_v, 
        key=f"slide_{key_p}",
        value=st.session_state[f"val_{key_p}"],
        step=float(step),
        label_visibility="collapsed",
        on_change=lambda: sync_input(f"val_{key_p}", st.session_state[f"slide_{key_p}"])
    )
    
    # 2. Number Input: Quando alterado, dispara o callback para atualizar o Slider
    val_num = c2.number_input(
        f"N_{key_p}", min_v, max_v,
        key=f"num_{key_p}",
        value=st.session_state[f"val_{key_p}"],
        step=float(step),
        label_visibility="collapsed",
        on_change=lambda: sync_input(f"val_{key_p}", st.session_state[f"num_{key_p}"])
    )
    
    return st.session_state[f"val_{key_p}"]

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
