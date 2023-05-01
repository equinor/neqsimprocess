from pydantic import BaseModel

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

    def __init__(self, name, surname, age):
        """
        Constructs all the necessary attributes for the person object.

        Parameters
        ----------
            name : str
                first name of the person
            surname : str
                family name of the person
            age : int
                age of the person
        """

        self.name = name
        self.surname = surname
        self.age = age