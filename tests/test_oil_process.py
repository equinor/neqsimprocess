from  neqsimprocess.oilgasprocess import 

def test_teg_process():
    """
    Run a test for the oil object
    """
    input = {
    'feedGasFlowRate': 11.65
    }
    tegprocess = TEGprocess(**input)
    tegprocess.getprocess().run()
    assert tegprocess.feedGasFlowRate == 11.65