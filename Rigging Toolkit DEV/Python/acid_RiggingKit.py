from maya import cmds
from maya import OpenMaya
from functools import partial
import sys

# manage and reload imports
import acid_LocatorUtils as LocUtils
import acid_BaseClassDefs as BaseClassDefs

LocUtils = reload(LocUtils)
BaseClassDefs = reload(BaseClassDefs)

class LegModule(BaseClassDefs.ModuleBase):

    def __init__(self):
        return

    def CreateChainFromLocators(self,HipLoc, KneeLoc, AnkleLoc, BallLoc, ToeLoc,JointPrefix, JointRadius):
        # create joints
        self.GenBaseChain(HipLoc, KneeLoc, AnkleLoc, BallLoc, ToeLoc,JointPrefix, JointRadius)

    def GenBaseChain(self, HipLoc, KneeLoc, AnkleLoc, BallLoc, ToeLoc, JointPrefix, JointRadius):
        # create the bind of the module
        jntNames = ["hip", "knee", "ankle", "ball", "toe"]
        locNames = [HipLoc, KneeLoc, AnkleLoc, BallLoc, ToeLoc]

        cmds.select(clear=True)

        # loop and assign names
        for i, loc in enumerate(locNames):
            pos = cmds.xform(loc, query=True, translation=True, worldSpace=True)
            j = cmds.joint(radius=JointRadius, position=pos,name=JointPrefix + jntNames[i] + "_JNT",absolute=True)

        # clear the parent back to scene root

        # check if child of scene already
        cmds.select(JointPrefix + jntNames[0] + "_JNT")
        isChildOfScene = cmds.listRelatives(parent=True) is None

        # if not a child of scene, parent to scene root
        if not isChildOfScene:
            cmds.parent(JointPrefix + jntNames[0] + "_JNT", world=True, absolute=True)

        # orient the joint chain
        # the results are so bad its better to just use comet orient
        # or to simplify their method(destroy then recombine)
        # cmds.joint(edit = True, children= True, orientJoint = 'xyz')+
        return


class CreateLegFromLocatorsUI():
    
    def addLocFromSel(*args):
        sel = cmds.ls(sl=True)
        add = cmds.textField(args[1], edit=True, text=sel[0])
    
    def newLocFromSel(*args): 
        loc = LocUtils.LocatorAtSelectionAverage(args[1])
        sel = cmds.ls(sl=True)
        add = cmds.textField(args[2], edit=True, text=loc)

    
    def CreateModule(self, *args):
        textField_HipLoc = cmds.textField('HipLoctFld', query=True, text=True)
        textField_KneeLoc = cmds.textField('KneeLoctFld', query=True, text=True)
        textField_AnkleLoc = cmds.textField('AnkleLoctFld', query=True, text=True)
        textField_BallLoc = cmds.textField('BallLoctFld', query=True, text=True)
        textField_ToeLoc = cmds.textField('ToeLoctFld', query=True, text=True)
        textField_JointPrefix = cmds.textField('JointPfxtFld', query=True, text=True)
        floatField_JointRad = cmds.floatField('JointRadfFld', query=True, value=True)
        LegModule().CreateChainFromLocators(textField_HipLoc,
                                            textField_KneeLoc,
                                            textField_AnkleLoc,
                                            textField_BallLoc,
                                            textField_ToeLoc,
                                            textField_JointPrefix,
                                            floatField_JointRad)

    def GenerateUI(self):

        # Define an id string for the window first
        self.windowName = "Leg Module Generator v0.1"
        # define out own window ID with no special characters
        self.windowID = "LMGv0_1Window"

        # Test to make sure that the UI isn't already active
        if cmds.window(self.windowID, exists=True):
            cmds.deleteUI(self.windowID)

        # Now create a fresh UI window
        self.win = cmds.window(self.windowID, title=self.windowName)

        cmds.columnLayout(adjustableColumn=True)
        cmds.separator(height=25, style='out')

        cmds.text(label="Instructions : Insert Locators fore desired join locations")
        
        cmds.separator(height=25, style='out')

        # row column layout for the locator fields
        cmds.rowColumnLayout(numberOfColumns=2, columnAttach=(1, 'right', 0), columnWidth=[(1, 80), (2, 280)])
        
        cmds.rowColumnLayout(numberOfRows=2)
        self.SetHipLocButton = cmds.button(l='Set Hip Loc', c= partial(self.addLocFromSel, "HipLoctFld"), width=80, h=25)
        self.MakeHipLocButton = cmds.button(l='New Hip Loc', c= partial(self.newLocFromSel, "Hip", "HipLoctFld"), width=80, h=25)
        cmds.setParent('..')

        self.HipLocTextFld = cmds.textField('HipLoctFld', h=50, w=50)

        cmds.rowColumnLayout(numberOfRows=2)
        self.SetKneeLocButton = cmds.button(l='Set Knee Loc', c= partial(self.addLocFromSel, "KneeLoctFld"), width=80, h=25)
        self.MakeKneeLocButton = cmds.button(l='New Knee Loc', c= partial(self.newLocFromSel, "Knee", "KneeLoctFld"), width=80, h=25)
        cmds.setParent('..')

        self.KneeLocTextFld = cmds.textField('KneeLoctFld', h=50, w=50)

        cmds.rowColumnLayout(numberOfRows=2)
        self.SetAnkleLocButton = cmds.button(l='Set Ankle Loc', c= partial(self.addLocFromSel, "AnkleLoctFld"), width=80, h=25)
        self.MakeAnkleLocButton = cmds.button(l='New Ankle Loc', c= partial(self.newLocFromSel, "Ankle", "AnkleLoctFld"), width=80, h=25)
        cmds.setParent('..')

        self.AnkleLocTextFld = cmds.textField('AnkleLoctFld', h=50, w=50)

        cmds.rowColumnLayout(numberOfRows=2)
        self.SetBallLocButton = cmds.button(l='Set Ball Loc', c= partial(self.addLocFromSel, "BallLoctFld"), width=80, h=25)
        self.MakeBallLocButton = cmds.button(l='New Ball Loc', c= partial(self.newLocFromSel, "Ball", "BallLoctFld"), width=80, h=25)
        cmds.setParent('..')
        
        self.BallLocTextFld = cmds.textField('BallLoctFld', h=50, w=50)

        cmds.rowColumnLayout(numberOfRows=2)
        self.SetToeLocButton = cmds.button(l='Set Toe Loc', c= partial(self.addLocFromSel, "ToeLoctFld"), width=80, h=25)
        self.MakeToeLocButton = cmds.button(l='New Toe Loc', c= partial(self.newLocFromSel, "Toe", "ToeLoctFld"), width=80, h=25)
        cmds.setParent('..')
        
        self.ToeLocTextFld = cmds.textField('ToeLoctFld', h=50, w=50)

        # release control of the rowcolumnlayout
        cmds.setParent('..')
        cmds.separator(height=25, style='out')

        # row colum for the extra settings
        cmds.rowColumnLayout(numberOfColumns=4, columnWidth=[(1, 80), (2, 100), (3, 80), (4, 100)])

        cmds.text(label="Name Prefix")
        self.JointPrefixTextFld = cmds.textField('JointPfxtFld', h=50, w=50)

        cmds.text(label="Joint Radius")
        self.JointRadiusFloatFld = cmds.floatField('JointRadfFld', minValue=0.01, value=.2, precision=2)

        # escape the settings layout
        cmds.setParent('..')
        cmds.separator(height=25, style='out')
        
        cmds.text(label="Warning! Make sure you handle the orients!")
        
        cmds.separator(height=25, style='out')
        self.GenerateButton = cmds.button(l='Generate', c=self.CreateModule, h=50, width=200)

        # Display the window
        cmds.showWindow(self.win)
                
        # Display the window
        cmds.showWindow(self.win)
                

CreateLegFromLocatorsUI().GenerateUI()