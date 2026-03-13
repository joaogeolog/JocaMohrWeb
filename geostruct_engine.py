import numpy as np

def calcular_ponto_com_intersecao(sn_new, tn_new, path_x, path_y, x_env, y_env):
    """
    Calcula a interseção entre a trajetória e a envoltória se o novo ponto estiver fora.
    """
    # Se não houver histórico, o ponto é o atual
    if not path_x:
        return sn_p, tn_p, False

    sn_old, tn_old = path_x[-1], path_y[-1]
    
    # Verifica se o novo ponto está fora da envoltória
    # (Lógica simplificada: interpolar y_env para o sn_new e comparar com tn_new)
    limite_tn = np.interp(sn_new, x_env, y_env)
    
    if tn_new <= limite_tn:
        return sn_new, tn_new, False # Ponto estável
    
    # Se chegou aqui, houve falha. Precisamos achar a interseção.
    # Criamos o segmento de reta: P_old + t * (P_new - P_old) onde t em [0, 1]
    # Procuramos o t onde P(t) toca a envoltória
    
    t_coords = np.linspace(0, 1, 100)
    for t in t_coords:
        sn_t = sn_old + t * (sn_new - sn_old)
        tn_t = tn_old + t * (tn_new - tn_old)
        
        limite_t = np.interp(sn_t, x_env, y_env)
        if tn_t >= limite_t:
            return sn_t, tn_t, True # Retorna o ponto exato da borda
            
    return sn_new, tn_new, True
