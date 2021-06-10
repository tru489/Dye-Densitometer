class DCEFI:
    """
    DCE-FI datastructure, used as input class to o_loadAIF
    """

    def __init__(self,dir,fname):
        """
        Constructor for DCE-FI datastructure

        :param dir: directory of AIF file
        :param fname: filename of AIF file
        """

        self.dir = dir
        self.fname = fname
        self.aif = None