from  neqsimprocess.teg_process import TEGprocess

def test_teg_process():
    """
    Run a test for the TEGprocess object
    """
    input = {
    'feedGasFlowRate': 11.65
    }
    tegprocess = TEGprocess(**input)
    tegprocess.getprocess().run()
    assert tegprocess.feedGasFlowRate == 11.65