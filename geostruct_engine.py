import numpy as np

# ... (manter calcular_envoltoria e obter_geometria_v18 iguais)

def calcular_ponto_com_trava(s1_eff, s3_eff, ang, x_env, y_env, last_ponto):
    """Calcula o ponto e identifica se houve cruzamento da fronteira."""
    sn_target = (s1_eff + s3_eff)/2 + (s1_eff - s3_eff)/2 * np.cos(np.radians(2 * ang))
    tn_target = abs((s1_eff - s3_eff)/2 * np.sin(np.radians(2 * ang)))
    
    sn_old = last_ponto.get('sn', sn_target)
    tn_old = last_ponto.get('tn', 0.0)
    
    limite_target = np.interp(sn_target, x_env, y_env)
    
    # Se o alvo está fora, travamos na borda
    if tn_target > limite_target:
        t_min, t_max = 0.0, 1.0
        sn_res, tn_res = sn_old, tn_old
        for _ in range(15):
            t = (t_min + t_max) / 2
            sn_t = sn_old + t * (sn_target - sn_old)
            tn_t = tn_old + t * (tn_target - tn_old)
            if tn_t > np.interp(sn_t, x_env, y_env): t_max = t
            else: t_min = t; sn_res, tn_res = sn_t, tn_t
        return sn_res, tn_res, True, None # True = Falhou, None = Não precisa de ponto extra
    
    # Se o alvo está DENTRO, mas viemos de FORA (descida), precisamos do ponto de interseção
    limite_old = np.interp(sn_old, x_env, y_env)
    if tn_old > limite_old + 0.01: # Estávamos em falha antes
        t_min, t_max = 0.0, 1.0
        sn_inter, tn_inter = sn_old, tn_old
        for _ in range(15):
            t = (t_min + t_max) / 2
            sn_t = sn_old + t * (sn_target - sn_old)
            tn_t = tn_old + t * (tn_target - tn_old)
            if tn_t > np.interp(sn_t, x_env, y_env): t_min = t
            else: t_max = t; sn_inter, tn_inter = sn_t, tn_t
        return sn_target, tn_target, False, (sn_inter, tn_inter)

    return sn_target, tn_target, False, None
