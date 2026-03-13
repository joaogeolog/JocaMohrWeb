import numpy as np

def calcular_envoltoria(ts, pc, c, phi):
    """Gera a envoltória de falha triaxial aprendida (Tração, Coulomb, Colapso)."""
    x_env = np.linspace(-ts, pc, 4000)
    tan_phi = np.tan(np.radians(phi))
    xt_coll = (pc + (c / tan_phi)) / 2
    y_env = np.zeros_like(x_env)
    for i, x in enumerate(x_env):
        if x < 0:
            k = (c**2) / (ts if ts > 0 else 0.001)
            y_env[i] = np.sqrt(max(0, k * (x + ts)))
        elif x < xt_coll: 
            y_env[i] = c + x * tan_phi
        else:
            a_c, b_c = pc - xt_coll, c + xt_coll * tan_phi
            y_env[i] = b_c * np.sqrt(np.maximum(0, 1 - ((x - xt_coll)**2 / a_c**2)))
    return x_env, y_env, xt_coll

def calcular_ponto_com_trava(s1_eff, s3_eff, ang_s1, x_env, y_env, ts, pc, last_ponto):
    """Calcula Sn e Tn no plano usando a referência a partir de S3 (Lógica João)."""
    centro, raio = (s1_eff + s3_eff) / 2, (s1_eff - s3_eff) / 2
    theta_rad = np.radians(ang_s1)
    
    # Lógica aprendida: centro - raio * cos(2 * theta)
    sn_target = centro - raio * np.cos(2 * theta_rad)
    tn_target = abs(raio * np.sin(2 * theta_rad))
    
    sn_clamped = np.clip(sn_target, -ts, pc)
    res_permitida = np.interp(sn_clamped, x_env, y_env, left=0, right=0)
    
    if tn_target > res_permitida + 1e-5 or sn_target < -ts or sn_target > pc:
        # Se falhar, trava o ponto mantendo a última posição válida
        return last_ponto.get('sn', sn_target), last_ponto.get('tn', 0.001), True
    
    return sn_target, tn_target, False

def obter_geometria_v18(centro, raio, x_env, y_env, ts, pc):
    """Gera os círculos teóricos e reais aprendidos."""
    t = np.linspace(0, np.pi, 1000)
    xc_o, yc_o = centro + raio * np.cos(t), raio * np.sin(t)
    res_c = np.interp(xc_o, x_env, y_env, left=0, right=0)
    
    xc_f = xc_o
    yc_f = np.minimum(yc_o, res_c)
    
    # Máscara amarela para realçar a zona de falha no círculo
    mask_fail = yc_o > res_c + 0.05
    sn_fail = xc_o[mask_fail]
    mask_high = (x_env >= np.min(sn_fail)) & (x_env <= np.max(sn_fail)) if len(sn_fail) > 0 else np.zeros_like(x_env, dtype=bool)
    
    return xc_f, yc_f, res_c, xc_o, yc_o, mask_high
