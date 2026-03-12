import streamlit as st
import numpy as np
import plotly.graph_objects as go
import geostruct_engine as eng

# --- FUNÇÃO AUXILIAR PARA CRIAR O INPUT DUAL (Slider + Number) ---
def dual_input(label, min_v, max_v, default_v, step=1.0, key_prefix=""):
    st.write(f"**{label}**")
    col1, col2 = st.columns([2, 1])
    # O slider e o number input compartilham o mesmo estado
    val = col1.slider(f"S_{label}", min_v, max_v, float(default_v), step=float(step), label_visibility="collapsed", key=f"s_{key_prefix}")
    val_final = col2.number_input(f"N_{label}", min_v, max_v, float(val), step=float(step), label_visibility="collapsed", key=f"n_{key_prefix}")
    return val_final

# --- SIDEBAR ATUALIZADA ---
with st.sidebar:
    st.title("⚒️ JocaMohr Web")
    st.info(f"Geólogo: João Carlos Menescal")

    with st.expander("1. ESTADO DE TENSÃO (MPa)", expanded=True):
        s1 = dual_input("S1 (MPa)", 0.0, 400.0, 120.0, key_prefix="s1")
        s3 = dual_input("S3 (MPa)", 0.0, 300.0, 40.0, key_prefix="s3")
        pp = dual_input("P. Poros (MPa)", 0.0, 200.0, 20.0, key_prefix="pp")
        alpha = dual_input("Biot (α)", 0.0, 1.0, 1.0, step=0.01, key_prefix="alpha")

    with st.expander("2. PROPRIEDADES DA ROCHA", expanded=True):
        c = dual_input("Coesão (MPa)", 0.0, 100.0, 15.0, key_prefix="c")
        phi = dual_input("Atrito (°)", 0.0, 60.0, 30.0, key_prefix="phi")
        ts = dual_input("Tração (MPa)", 0.0, 50.0, 10.0, key_prefix="ts")
        pc = dual_input("Compressão (MPa)", 0.0, 500.0, 180.0, key_prefix="pc")

    with st.expander("3. ORIENTAÇÃO DO PLANO", expanded=True):
        regime = st.selectbox("Regime", ["Normal", "Transcorrente", "Reverso"])
        ang_s1 = dual_input("Ângulo com S1 (°)", 0.0, 90.0, 30.0, step=0.1, key_prefix="ang")

# --- RESTO DO CÓDIGO (Cálculos e Gráficos) ---
# Aqui você mantém a lógica de cálculo usando s1, s3, pp, etc., 
# que agora vêm dos inputs duais acima.
