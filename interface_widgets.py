import streamlit as st

DEFAULTS = {'s1': 120.0, 's3': 40.0, 'pp': 20.0, 'alpha': 1.0, 'c': 15.0, 'phi': 30.0, 'ts': 10.0, 'pc': 180.0, 'ang': 30.0, 'regime': 'Normal'}

def sync_widgets(s, t, c):
    st.session_state[c] = st.session_state[t] = st.session_state[s]

def reset_section(keys):
    for k in keys:
        for pfx in ['val_', 'slide_', 'num_']:
            st.session_state[pfx + k] = float(DEFAULTS[k])
    if 'ang' in keys:
        st.session_state.path_x, st.session_state.path_y, st.session_state.ponto_fisico = [], [], {'sn': 0.0, 'tn': 0.0}

def dual_input(label, min_v, max_v, key_p, step=1.0):
    s_key, n_key, base_key = f"slide_{key_p}", f"num_{key_p}", f"val_{key_p}"
    if base_key not in st.session_state:
        st.session_state[base_key] = st.session_state[s_key] = st.session_state[n_key] = float(DEFAULTS[key_p])
    
    c_l, c_s, c_n = st.columns([1, 2, 1])
    c_l.markdown(f"<p style='font-size:0.85em; margin-top:5px;'>{label}</p>", unsafe_allow_html=True)
    c_s.slider(label, float(min_v), float(max_v), step=float(step), key=s_key, on_change=sync_widgets, args=(s_key, n_key, base_key), label_visibility="collapsed")
    c_n.number_input(label, float(min_v), float(max_v), step=float(step), key=n_key, on_change=sync_widgets, args=(n_key, s_key, base_key), label_visibility="collapsed")
    return st.session_state[base_key]

def render_bottom_interface():
    if 'path_x' not in st.session_state:
        st.session_state.path_x, st.session_state.path_y, st.session_state.ponto_fisico = [], [], {'sn': 0.0, 'tn': 0.0}

    # CSS para botões de reiniciar pequenos
    st.markdown("<style>div[data-testid='column'] button {font-size: 8px !important; padding: 2px !important; height: 20px !important;}</style>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<b style='font-size:0.8em;'>1. TENSÕES (MPa)</b>", unsafe_allow_html=True)
        if st.button("Reset Tensão", key="r1"): reset_section(['s1', 's3', 'pp', 'alpha']); st.rerun()
        s1 = dual_input("S1", 0.0, 250.0, "s1")
        s3 = dual_input("S3", 0.0, 250.0, "s3")
        pp = dual_input("P. Poros", 0.0, 250.0, "pp")
        alpha = dual_input("Biot", 0.0, 1.0, "alpha", 0.01)

    with c2:
        st.markdown("<b style='font-size:0.8em;'>2. ROCHA</b>", unsafe_allow_html=True)
        if st.button("Reset Rocha", key="r2"): reset_section(['c', 'phi', 'ts', 'pc']); st.rerun()
        c = dual_input("Coesão", 0.0, 100.0, "c")
        phi = dual_input("Atrito (°)", 0.0, 60.0, "phi")
        ts = dual_input("Tração", 0.0, 50.0, "ts")
        pc = dual_input("Colapso", 0.0, 250.0, "pc")

    with c3:
        st.markdown("<b style='font-size:0.8em;'>3. PLANO</b>", unsafe_allow_html=True)
        if st.button("Reset Plano", key="r3"): reset_section(['ang']); st.session_state["regime_sel"] = "Normal"; st.rerun()
        reg = st.selectbox("Regime", ["Normal", "Transcorrente", "Reverso"], key="regime_sel", label_visibility="collapsed")
        ang = dual_input("Ang/S1", 0.0, 90.0, "ang", 0.1)
        if st.button("Limpar Trajetória", use_container_width=True):
            st.session_state.path_x, st.session_state.path_y = [], []
            st.session_state.ponto_fisico = {'sn': 0.0, 'tn': 0.0}; st.rerun()
            
    return {"s1": s1, "s3": s3, "pp": pp, "alpha": alpha, "c": c, "phi": phi, "ts": ts, "pc": pc, "regime": reg, "ang_s1": ang}
