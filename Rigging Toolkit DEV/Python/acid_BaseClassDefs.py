class ModuleBase():
    def __init__(self):
        return

    def CreateChainFromLocators(self):
        # create joints
        print("TODO: implement CreateChainFromLocators")
        self.GenBaseChain()

    def CreateModuleFromJoints(self, BaseChain, MainControl):
        # assume created and oriented joints
        print("TODO: implement CreateModuleFromJoints")
        self.GenModule()

    def GenBaseChain(self):
        # create the base chain
        print("TODO: implement GenBaseChain")
        return

    def GenModule(self):
        print("TODO: implement GenModule")
        self.GenBind()
        self.GenIk()
        self.GenFK()
        self.GenBlend()

    def GenBind(self):
        # create the Ik of the module
        print("TODO: implement GenBind")
        return

    def GenIk(self):
        # create the Ik of the module
        print("TODO: implement GenIK")
        return

    def GenFK(self):
        # create the Fk of the module
        print("TODO: implement GenFK")
        return

    def GenBlend(self):
        # generate the 3 chain functionality
        print("TODO: implement GenBlend")
        return

    def GenContainers(self):
        # assign module groups
        print("TODO: implement GenContainers")
        return
