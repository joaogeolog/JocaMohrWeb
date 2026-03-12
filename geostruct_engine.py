import numpy as np

def calcular_envoltoria(ts, pc, c, phi):
    """Gera a envoltória de falha triaxial (Tração, Coulomb, Colapso)."""
    # CORREÇÃO: O limite superior agora é exatamente Pc, eliminando o rabo em zero.
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
            # A elipse agora fecha perfeitamente em x = pc, onde y se torna 0.
            y_env[i] = b_c * np.sqrt(np.maximum(0, 1 - ((x - xt_coll)**2 / a_c**2)))
    return x_env, y_env, xt_coll

def calcular_ponto_com_trava(s1_eff, s3_eff, ang_s1, x_env, y_env, ts, pc, ponto_anterior):
    """Calcula Sn e Tn no plano usando o Ângulo com S1 real (theta)."""
    centro, raio = (s1_eff + s3_eff) / 2, (s1_eff - s3_eff) / 2
    
    # Cálculo geomecânico partindo de S3 para o topo do círculo.
    theta_rad = np.radians(ang_s1)
    sn_teorico = centro - raio * np.cos(2 * theta_rad)
    tn_teorico = abs(raio * np.sin(2 * theta_rad))
    
    sn_clamped = np.clip(sn_teorico, -ts, pc)
    res_permitida = np.interp(sn_clamped, x_env, y_env, left=0, right=0)
    
    if tn_teorico > res_permitida + 1e-5 or sn_teorico < -ts or sn_teorico > pc:
        return ponto_anterior['sn'], ponto_anterior['tn'], True
    
    return sn_teorico, tn_teorico, False

def obter_geometria_v18(centro, raio, x_env, y_env, ts, pc):
    """Gera os círculos teóricos e colapsados para a visualização no Mohr."""
    t = np.linspace(0, np.pi, 1000)
    xc_o, yc_o = centro + raio * np.cos(t), raio * np.sin(t)
    res_c = np.interp(xc_o, x_env, y_env, left=0, right=0)
    xc_f = xc_o
    yc_f = np.minimum(yc_o, res_c)
    return xc_f, yc_f, res_c, xc_o, yc_o