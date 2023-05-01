from pydantic import BaseModel
from neqsim.thermo import fluid

class TEGprocess(BaseModel):
    """
    A class to represent a TEG dehydration process.

    ...

    Attributes
    ----------
    feedgasflow : float
        the flow rate of the feed gas to the dehdyration process in unit MSm3/day
    flowrateTEG : float
        the flow rate of lean TEG to the dehdyration process in unit kg/hr

    Methods
    -------
    getProcess():
        get the process simulation object
    """
    #process = fluid('srk')
    
    def __init__(self):
        """
        Constructs all the necessary attributes for the TEGprocess object.
        """

    def getprocess(self):
        """
        doc
        """
        process = fluid('srk')
        return process
