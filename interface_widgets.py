import streamlit as st

DEFAULTS = {
    's1': 120.0, 's3': 40.0, 'pp': 20.0, 'alpha': 1.0, 
    'c': 15.0, 'phi': 30.0, 'ts': 10.0, 'pc': 180.0, 
    'ang': 30.0, 'regime': 'Normal'
}

def sync_widgets(source_key, target_key, common_state_key):
    st.session_state[common_state_key] = st.session_state[source_key]
    st.session_state[target_key] = st.session_state[source_key]

def reset_section(keys):
    for k in keys:
        val = DEFAULTS[k]
        st.session_state[f"val_{k}"] = val
        st.session_state[f"slide_{k}"] = val
        st.session_state[f"num_{k}"] = val
    if 'ang' in keys: # Se resetar o plano, limpa a trajetória
        st.session_state.path_x, st.session_state.path_y = [], []
        st.session_state.ponto_fisico = {'sn': 0.0, 'tn': 0.0}

def dual_input(label, min_v, max_v, key_p, step=1.0):
    st.write(f"**{label}**")
    s_key, n_key, base_key = f"slide_{key_p}", f"num_{key_p}", f"val_{key_p}"
    if base_key not in st.session_state:
        st.session_state[base_key] = float(DEFAULTS[key_p])
        st.session_state[s_key] = float(DEFAULTS[key_p])
        st.session_state[n_key] = float(DEFAULTS[key_p])
    
    col1, col2 = st.columns([2, 1])
    col1.slider(label, float(min_v), float(max_v), step=float(step), key=s_key, 
                on_change=sync_widgets, args=(s_key, n_key, base_key), label_visibility="collapsed")
    col2.number_input(label, float(min_v), float(max_v), step=float(step), key=n_key, 
                      on_change=sync_widgets, args=(n_key, s_key, base_key), label_visibility="collapsed")
    return st.session_state[base_key]

def render_sidebar():
    if 'path_x' not in st.session_state:
        st.session_state.path_x, st.session_state.path_y = [], []
        st.session_state.ponto_fisico = {'sn': 0.0, 'tn': 0.0}

    st.markdown("""<style>div[data-testid="column"] button {padding: 1px 4px !important; font-size: 6px !important; height: 16px !important; white-space: nowrap !important;}</style>""", unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚒️ JocaMohr Web")
        with st.expander("1. ESTADO DE TENSÃO (MPa)", expanded=True):
            c1, c2 = st.columns([2.2, 1.8]); c1.write("PARÂMETROS")
            if c2.button("Reiniciar", key="res_s"): reset_section(['s1', 's3', 'pp', 'alpha']); st.rerun()
            s1 = dual_input("S1", 0.0, 250.0, "s1")
            s3 = dual_input("S3", 0.0, 250.0, "s3")
            pp = dual_input("P. Poros", 0.0, 250.0, "pp")
            alpha = dual_input("Biot (α)", 0.0, 1.0, "alpha", step=0.01)

        with st.expander("2. PROPRIEDADES DA ROCHA", expanded=True):
            c1, c2 = st.columns([2.2, 1.8]); c1.write("PARÂMETROS")
            if c2.button("Reiniciar", key="res_r"): reset_section(['c', 'phi', 'ts', 'pc']); st.rerun()
            c_rock = dual_input("Coesão", 0.0, 100.0, "c")
            phi = dual_input("Atrito (°)", 0.0, 60.0, "phi")
            ts = dual_input("Tração", 0.0, 50.0, "ts")
            pc = dual_input("Colapso", 0.0, 250.0, "pc")

        with st.expander("3. ORIENTAÇÃO DO PLANO", expanded=True):
            c1, c2 = st.columns([2.2, 1.8]); c1.write("PARÂMETROS")
            if c2.button("Reiniciar", key="res_p"): reset_section(['ang']); st.session_state["regime_sel"] = "Normal"; st.rerun()
            regime = st.selectbox("Regime", ["Normal", "Transcorrente", "Reverso"], key="regime_sel")
            ang_s1 = dual_input("Ângulo com S1 (°)", 0.0, 90.0, "ang", step=0.1)
            if st.button("Limpar Trajetória", use_container_width=True):
                st.session_state.path_x, st.session_state.path_y = [], []
                st.session_state.ponto_fisico = {'sn': 0.0, 'tn': 0.0}
                st.rerun()
            
    return {"s1": s1, "s3": s3, "pp": pp, "alpha": alpha, "c": c_rock, "phi": phi, "ts": ts, "pc": pc, "regime": regime, "ang_s1": ang_s1}
