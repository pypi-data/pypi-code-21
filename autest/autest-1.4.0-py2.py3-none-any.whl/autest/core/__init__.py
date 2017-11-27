
class CopyLogic:
    Default = 0
    HardSoft = 1
    Hard = 2
    Soft = 3
    HardSoftFiles = 4
    HardFiles = 5
    SoftFiles = 6
    Copy = 7

    @classmethod
    def DefaultLogic(cls, logic):
        if logic == CopyLogic.Default:
            return CopyLogic.Copy
        return logic

