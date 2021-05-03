from iconservice import InterfaceScore, Address, interface


class SystemScoreInterface(InterfaceScore):
    @interface
    def setStake(self, value: int) -> None:
        pass

    @interface
    def getStake(self, address: Address) -> dict:
        pass

    @interface
    def getMainPReps(self) -> dict:
        pass

    @interface
    def setDelegation(self, delegations: list = None):
        pass

    @interface
    def getDelegation(self, address: Address) -> dict:
        pass

    @interface
    def claimIScore(self):
        pass

    @interface
    def queryIScore(self, address: Address) -> dict:
        pass

    @interface
    def getIISSInfo(self) -> dict:
        pass

    @interface
    def getPRepTerm(self) -> dict:
        pass

    @interface
    def getPReps(self, startRanking: int, endRanking: int) -> dict:
        pass