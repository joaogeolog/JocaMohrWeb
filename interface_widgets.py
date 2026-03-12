import streamlit as st

def dual_input(label, min_v, max_v, default_v, step=1.0, key_p=""):
    st.write(f"**{label}**")
    c1, c2 = st.columns([2, 1])
    s_val = c1.slider(f"S_{key_p}", min_v, max_v, float(default_v), step=float(step), label_visibility="collapsed", key=f"slide_{key_p}")
    n_val = c2.number_input(f"N_{key_p}", min_v, max_v, float(s_val), step=float(step), label_visibility="collapsed", key=f"num_{key_p}")
    return n_val

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
            regime = st.selectbox("Regime Tectônico", ["Normal", "Transcorrente", "Reverso"])
            ang_s1 = dual_input("Ângulo com S1 (°)", 0.0, 90.0, 30.0, step=0.1, key_p="ang")
            
    return {
        "s1": s1, "s3": s3, "pp": pp, "alpha": alpha,
        "c": c_rock, "phi": phi, "ts": ts, "pc": pc,
        "regime": regime, "ang_s1": ang_s1
    }
