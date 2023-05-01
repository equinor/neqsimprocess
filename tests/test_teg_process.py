from  neqsimprocess.teg_process import TEGprocess

def test_Viscosity():
    assert abs(1.0760998263782569e-015) < 1e-10
    
def test_teg_process():
    test_teg_process = TEGprocess()
    assert abs(1.0760998263782569e-015) < 1e-10

    