import numpy as np

def calcular_envoltoria(ts, pc, c, phi):
    phi_rad = np.radians(phi)
    xt_coll = pc * 0.6 
    sn_range = np.linspace(-ts, pc, 1200) 
    sn_final, tn_final = [], []
    for sn in sn_range:
        if sn < 0: tn = c * np.sqrt(max(0, 1 - (sn / -ts)))
        elif sn <= xt_coll: tn = c + sn * np.tan(phi_rad)
        else:
            a, b = pc - xt_coll, c + xt_coll * np.tan(phi_rad)
            tn = b * np.sqrt(max(0, 1 - ((sn - xt_coll)**2 / a**2)))
        sn_final.append(sn); tn_final.append(max(tn, 0.001))
    return np.array(sn_final), np.array(tn_final), xt_coll

def calcular_ponto_com_trava(s1_eff, s3_eff, ang_s1, x_env, y_env, last_ponto):
    # O ângulo crítico de falha em relação a S1 é theta = 45 - phi/2
    # No círculo de Mohr, isso corresponde a 2*theta
    theta_rad = np.radians(ang_s1)
    centro = (s1_eff + s3_eff) / 2
    raio = (s1_eff - s3_eff) / 2
    
    # sn = centro + raio * cos(2*theta)
    # tn = raio * sin(2*theta)
    # Com ang_s1=30, 2*theta=60. O ponto deve estar à direita do topo do círculo.
    sn_target = centro + raio * np.cos(2 * theta_rad)
    tn_target = abs(raio * np.sin(2 * theta_rad))
    
    limite = np.interp(sn_target, x_env, y_env, left=0.001, right=0.001)
    if tn_target <= limite: return sn_target, tn_target, False 
    
    sn_old, tn_old = last_ponto.get('sn', sn_target), last_ponto.get('tn', 0.001)
    t_min, t_max, sn_res, tn_res = 0.0, 1.0, sn_old, tn_old
    for _ in range(15):
        t = (t_min + t_max) / 2
        sn_t, tn_t = sn_old + t * (sn_target - sn_old), tn_old + t * (tn_target - tn_old)
        if tn_t > np.interp(sn_t, x_env, y_env, left=0.001, right=0.001): t_max = t
        else: t_min = t; sn_res, tn_res = sn_t, tn_t
    return sn_res, tn_res, True

def obter_geometria_v18(centro, raio, x_env, y_env):
    ang = np.linspace(0, np.pi, 600)
    xc, yc = centro + raio * np.cos(ang), raio * np.sin(ang)
    res_env_circ = np.interp(xc, x_env, y_env, left=0.001, right=0.001)
    mask_fail = yc > res_env_circ + 0.05
    xc_s, yc_s = np.where(~mask_fail, xc, np.nan), np.where(~mask_fail, yc, np.nan)
    xc_f, yc_f = np.where(mask_fail, xc, np.nan), np.where(mask_fail, yc, np.nan)
    sn_fail = xc[mask_fail]
    mask_high = (x_env >= np.min(sn_fail)) & (x_env <= np.max(sn_fail)) if len(sn_fail) > 0 else np.zeros_like(x_env, dtype=bool)
    return xc_s, yc_s, xc_f, yc_f, mask_high
