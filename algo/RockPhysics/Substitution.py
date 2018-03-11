
def Gassmann(Kd, Km, Kfl, phi):
    """
    B = (1.0 - Kd/Km)
    Ks = Kd + B*B/(phi/Kfl - phi/Km + B/Km)
    """
    Ks = Kd + (1.0 - Kd/Km)**2/(phi/Kfl + (1.0 - phi)/Km - Kd/Km**2)
    return Ks
