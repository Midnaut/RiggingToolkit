from maya import cmds
from maya import OpenMaya
from functools import partial
import sys

# manage and reload imports
import acid_LocatorUtils as LocUtils
import acid_BaseClassDefs as BaseClassDefs
import acid_MathUtils as MathUtils
import acid_ShapeUtils as ShapeUtils


LocUtils = reload(LocUtils)
BaseClassDefs = reload(BaseClassDefs)

class LegModule(BaseClassDefs.ModuleBase):

    #seems like a good candidate to load in from a settings JSON
    LEG_JNT_NAMES = ["hip", "knee", "ankle", "ball", "toe"]
    RVF_JNT_NAMES = ["revCenterBank", "revEdgeBank", "revPivot", "revHeel", "revToe", "revBall", "revAnkle"]

    def __init__(self):
        return

    def CreateLegAndFoot(self, LocList, Prefix, JointRadius, PVPush, FlipKneeY, Suffix = "_JNT"):
        self.CreateLegJoints(LocList, Prefix, JointRadius)
        self.OrientLegChain(Prefix, Suffix, FlipKneeY)
        self.CreateLegIK(Prefix)
        self.CreatePVControl(Prefix, "PV_CTL", PVPush, JointRadius)

        self.FetchRevFootJointNames(Prefix, Suffix)
        self.CreateRevFootJoints();

        self.OrientAndMatchFootJoints(Prefix);

    def CompleteFootAndNoFlip(self, Prefix, Suffix = "_JNT"):
        #a new instance of the class is generated and we need to re-populate the names
        self.FetchLegJointNames(Prefix, Suffix)
        self.FetchRevFootJointNames(Prefix, Suffix)

        self.CreateAndAttachRevFootIK(Prefix)
        self.CreateFootControl(Prefix)
        self.CreateRollControl(Prefix)

        self.EdgeRollNodes(Prefix)
        self.HeelToeNodes(Prefix)

        self.CreateNoFlipObjects(Prefix)
        self.ConnectNoFlipControls(Prefix)

    def CreateLegJoints(self, LocList, Prefix, JointRadius, Suffix = "_JNT"):
        cmds.select(clear=True)

        # loop and assign names
        for i, loc in enumerate(LocList):
            pos = cmds.xform(loc, query=True, translation=True, worldSpace=True)
            #clear selection to allow for creating floating joints which we then parent as needed
            cmds.select(clear=True)
            j = cmds.joint(radius=JointRadius, position=pos,name=Prefix + self.LEG_JNT_NAMES[i] + Suffix ,absolute=True)

        # check if child of scene already
        cmds.select(Prefix + self.LEG_JNT_NAMES[0] + Suffix)
        isChildOfScene = cmds.listRelatives(parent=True) is None

        # if not a child of scene, parent to scene root
        if not isChildOfScene:
            cmds.parent(Prefix + self.LEG_JNT_NAMES[0] + Suffix , world=True, absolute=True)

        return

    def FetchLegJointNames(self, prefix, suffix):
        self.hipJnt = prefix + self.LEG_JNT_NAMES[0] + suffix
        self.kneeJnt = prefix + self.LEG_JNT_NAMES[1] + suffix
        self.ankleJnt = prefix + self.LEG_JNT_NAMES[2] + suffix
        self.ballJnt = prefix + self.LEG_JNT_NAMES[3] + suffix
        self.toeJnt = prefix + self.LEG_JNT_NAMES[4] + suffix

    def OrientLegChain(self, prefix, suffix, flipKneeY):
        #variables
        aimVector = [1,0,0]
        
        upVector = []
        if flipKneeY:
            upVector = [0,0,1]
        else:
            upVector = [0,0,-1]


        self.FetchLegJointNames(prefix, suffix)

        #aimConstraint -offset 0 0 0 -weight 1 -aimVector 1 0 0 -upVector 0 0 -1 -worldUpType "object" -worldUpObject L_ankle_JNT;
        #aim hip to kneee
        aimCon = cmds.aimConstraint( self.kneeJnt, self.hipJnt, aim = aimVector,u = upVector ,wut = "object" ,wuo = self.ankleJnt)
        cmds.delete(aimCon)
        aimCon = cmds.aimConstraint( self.ankleJnt, self.kneeJnt, aim = aimVector,u = upVector ,wut = "object" ,wuo = self.hipJnt)
        cmds.delete(aimCon)

        cmds.parent(self.kneeJnt, self.kneeJnt)

        #construct the ankle ball toe joint chain
        cmds.parent(self.toeJnt, self.ballJnt)
        cmds.parent(self.ballJnt, self.ankleJnt)

        #orient ankle chain to x front
        cmds.joint( self.ankleJnt , e=True, zso=True, oj='xyz', sao='xup', ch=True)
        #orient to to world
        cmds.joint( self.toeJnt , e=True, zso=True, oj='none')
        cmds.parent(self.ankleJnt, self.kneeJnt)

        #cleanup freeze transformations
        cmds.select(self.hipJnt)
        cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)
        cmds.select(clear = True)

    def CreateLegIK(self, prefix):
        self.legIKHandle = cmds.ikHandle( n='L_leg_IKH', sj=self.hipJnt, ee=self.ankleJnt, sol = "ikRPsolver")[0]


    def CreatePVControl(self, Prefix, Suffix, PVPush, ControlSize):
        #create polygon at hip knee ankle
        #set pivot to average of hip ankle
        hipPos = cmds.xform(self.hipJnt,q=1,ws=1,rp=1)
        kneePos = cmds.xform(self.kneeJnt,q=1,ws=1,rp=1)
        anklePos = cmds.xform(self.ankleJnt,q=1,ws=1,rp=1)

        point_list = [hipPos, kneePos, anklePos]
        point_list_2 = [hipPos, anklePos]

        legPVCurve = cmds.curve(degree = 1, point = point_list)
        kneePivotCurve = cmds.curve(degree = 1, point = point_list_2)

        #create node
        nearestPOCNode = cmds.createNode("nearestPointOnCurve")
        cmds.connectAttr(kneePivotCurve+".worldSpace", nearestPOCNode + ".inputCurve")
        cmds.setAttr(nearestPOCNode+".inPosition", kneePos[0], kneePos[1], kneePos[2], type="double3") 

        halfwayPos = cmds.getAttr(nearestPOCNode + ".position")[0]

        #adjust the pivot so that it gives us a nice approximation of the knee 
        cmds.move(halfwayPos[0], halfwayPos[1], halfwayPos[2], legPVCurve+".scalePivot", legPVCurve+".rotatePivot", absolute=True)

        #scale the curve to project our knee pv point forward
        cmds.select(legPVCurve)
        cmds.scale(PVPush, PVPush, PVPush)

        #get position of knee from curve (hip = 0, knee = 1, ankle = 2)
        controlPos = cmds.pointPosition( legPVCurve+'.cv[1]')
        controlPoint = (controlPos[0], controlPos[1], controlPos[2])
        #create diamond shape at pos
        #name with assigned prefix and suffix, size will match joint radius as a base
        control = cmds.curve(name=Prefix + self.LEG_JNT_NAMES[1] + Suffix, degree = 1, point= ShapeUtils.diamondControlPath())
        cmds.select(control)
        cmds.move(controlPos[0], controlPos[1],controlPos[2])
        cmds.scale( ControlSize, ControlSize, ControlSize )
        cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)

        #create null annotation at diamond pointing to child locator
        cmds.select(clear = True)
        locator = cmds.spaceLocator( n = Prefix + self.LEG_JNT_NAMES[1] + "PVGuide_LOC")[0]
        group = cmds.group( em=True, name=Prefix + self.LEG_JNT_NAMES[1] + "PVOffset_GRP")
        annotation = cmds.annotate( locator, tx='')
        anno_transfrom = cmds.listRelatives( annotation, allParents=True )[0]
        anno_transfrom = cmds.rename(anno_transfrom, Prefix + self.LEG_JNT_NAMES[1] + "PVGuide_ANT")
        annotation = cmds.listRelatives(anno_transfrom)[0]

        #point constrain the annotation to the knee
        cmds.pointConstraint( self.kneeJnt, anno_transfrom)
        #move locator to position and parent
        cmds.parent(locator, control)
        cmds.move( controlPos[0], controlPos[1],controlPos[2], locator, absolute=True )
        cmds.parent(anno_transfrom, locator)
        
        cmds.move( controlPos[0], controlPos[1],controlPos[2], group, absolute=True )
        cmds.parent(control, group)

        #pole vector the ikh and the diamond
        cmds.poleVectorConstraint( control, self.legIKHandle )

        #cleanup
        cmds.delete(nearestPOCNode)
        cmds.delete(legPVCurve)
        cmds.delete(kneePivotCurve)
        cmds.setAttr(locator + ".localScaleX", 0)
        cmds.setAttr(locator + ".localScaleY", 0)
        cmds.setAttr(locator + ".localScaleZ", 0)
        cmds.select(annotation)
        cmds.toggle(template= True)

    def FetchRevFootJointNames(self, prefix, suffix):
        self.revCBankJnt = prefix + self.RVF_JNT_NAMES[0] + suffix
        self.revEBankJnt = prefix + self.RVF_JNT_NAMES[1] + suffix
        self.revPivotJnt = prefix + self.RVF_JNT_NAMES[2] + suffix
        self.revHeelJnt = prefix + self.RVF_JNT_NAMES[3] + suffix
        self.revToeJnt = prefix + self.RVF_JNT_NAMES[4] + suffix
        self.revBallJnt = prefix + self.RVF_JNT_NAMES[5] + suffix
        self.revAnkleJnt = prefix + self.RVF_JNT_NAMES[6] + suffix

    def CreateRevFootJoints(self):
        #create the roll diamond setup
        cmds.select(clear = True)
        cmds.joint(name = self.revCBankJnt, p = [-4, 0, 0])
        cmds.joint(name = self.revEBankJnt, p = [4, 0, 0])
        cmds.joint(name = self.revPivotJnt, p = [0, 0, 0])
        cmds.joint(name = self.revHeelJnt, p = [0, 0, -8])
        cmds.joint(name = self.revToeJnt, p = [0, 0, 6])
        cmds.joint(name = self.revBallJnt, p = [0, 0, 3])
        cmds.joint(name = self.revAnkleJnt, p = [0, 0, -3])
        cmds.select(clear = True)

    def OrientAndMatchFootJoints(self, prefix):
        #do the funky orient to match the ball orient
        #joint -e  -oj yxz -secondaryAxisOrient zup -ch -zso;
        cmds.joint(self.revCBankJnt, e = True, oj = 'yxz', sao = 'zup', ch = True, zso = True)
        orientConstraint = cmds.orientConstraint(self.ballJnt, self.revCBankJnt)
        cmds.delete(orientConstraint)

        #make identity to clear rotations of the joints
        cmds.select(self.revCBankJnt)
        cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)
        cmds.parent(self.revCBankJnt, self.ballJnt)

        #orient to to world
        cmds.joint( self.revCBankJnt , e=True, zso=True, oj='none', ch= True)
        cmds.xform(self.revCBankJnt ,translation = [0,0,0], worldSpace = False)

        cmds.parent(world = True)
        cmds.select(clear = True)

    def CreateAndAttachRevFootIK(self, prefix):
        #ik rotate plane solver
        self.ankleIKHandle = cmds.ikHandle( n='L_ankle_IKH', sj=self.ankleJnt, ee=self.ballJnt, sol = "ikRPsolver")[0]
        self.ballIKHandle = cmds.ikHandle( n='L_ball_IKH', sj=self.ballJnt, ee=self.toeJnt, sol = "ikRPsolver")[0]

        cmds.parent(self.ankleIKHandle, self.revBallJnt)
        cmds.parent(self.ballIKHandle, self.revToeJnt)

        cmds.select(clear = True)

    def CreateFootControl(self, prefix):
        #create circle on the ball joint, normal as x+ of the joint
        #scale the control as a base to cover ball to toe 
        shapeScale =cmds.xform(self.toeJnt,q=1,ws=0,t=1)[0]

        shape = cmds.circle(constructionHistory = False, object = True, normal= [0,0,1], radius = shapeScale)[0]
        control = cmds.rename(shape, prefix + "foot"+ "_CTL")
        offGrp = cmds.group(control,n=(prefix + "footCTL" + "Offset_GRP"))
        parCon = cmds.parentConstraint(self.ballJnt, offGrp, mo= 0)
        cmds.delete(parCon)

        #cleanup
        cmds.parent(prefix + "leg_IKH", self.revAnkleJnt)
        cmds.parent(self.revCBankJnt, control)
        self.footControl = control
        cmds.select(clear = True)

    def CreateRollControl(self, prefix):
        #create rotator control, scale = edge to pivot distance
        shapeScale =cmds.xform(self.revPivotJnt,q=1,ws=0,t=1)[1]
        shapeScale = abs(shapeScale)
        shape = ShapeUtils.sphereControl()

        cmds.scale(shapeScale/2.0, shapeScale/2.0, shapeScale/2.0, shape)

        control = cmds.rename(shape, prefix+"footRoll" +"_CTL")
        offGrp = cmds.group(control, n=prefix+ "footRollCTL" +"Offset_GRP")
        orientCon = cmds.orientConstraint(self.revPivotJnt, offGrp, offset = [90,0,90])
        cmds.delete(orientCon)

        #position 3 x scale away from ball joint
        cmds.parent(offGrp, self.revPivotJnt)
        # places it neat off to the side and a little above the ground of the ball of the foot
        cmds.xform(offGrp ,translation = [0,3*shapeScale,shapeScale], worldSpace = False, absolute = True)
        cmds.parent(offGrp, world = True)

        #cleanup
        cmds.select(control)
        cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)
        cmds.select(clear = True)
        self.rollControlOffsetGroup = offGrp
        self.rollControl = control

    def EdgeRollNodes(self, prefix):
        #condition node for bank joints
        bankCondNode = cmds.createNode("condition", n= prefix+"bank_CND")
        cmds.connectAttr(self.rollControl+".rotateZ", bankCondNode+".colorIfTrue.colorIfTrueR")
        cmds.setAttr(bankCondNode+".colorIfFalse.colorIfFalseR", 0)# default for both col is all 1 for false

        cmds.connectAttr(self.rollControl+".rotateZ", bankCondNode+".colorIfFalse.colorIfFalseG")
        cmds.connectAttr(self.rollControl+".rotateZ", bankCondNode+".firstTerm")

        cmds.setAttr(bankCondNode+".operation", 2) # 2 = greater than

        #connect the node to the joints
        cmds.connectAttr(bankCondNode+".outColor.outColorR", self.revCBankJnt+".rotateX")
        cmds.connectAttr(bankCondNode+".outColor.outColorG", self.revEBankJnt+".rotateX")
        cmds.connectAttr(self.rollControl+".rotateY", self.revPivotJnt+".rotateZ")

    def HeelToeNodes(self, prefix):
        #add weight attr to roll control
        cmds.select(self.rollControl)
        cmds.addAttr(longName='weight', defaultValue=0.0, minValue=0.0, maxValue=1.0 )
        cmds.setAttr(self.rollControl+".weight", e = True, keyable= True);

        #condition node for heel toe
        heelToeCondNode = cmds.createNode("condition", n= prefix+"heelToe_CND")

        cmds.connectAttr(self.rollControl+".rotateX", heelToeCondNode+".colorIfTrue.colorIfTrueR")
        cmds.setAttr(heelToeCondNode+".colorIfFalse.colorIfFalseR", 0)# default for both col is all 1 for false

        cmds.connectAttr(self.rollControl+".rotateX", heelToeCondNode+".colorIfFalse.colorIfFalseG")
        cmds.connectAttr(self.rollControl+".rotateX", heelToeCondNode+".firstTerm")

        cmds.setAttr(heelToeCondNode+".operation", 4) # 2 = less than than

        #connect the node to the joints
        cmds.connectAttr(heelToeCondNode+".outColor.outColorR", self.revHeelJnt+".rotateY")

        #blend node for toeball
        weightBlendNode = cmds.createNode("blendColors", n= prefix+"toeBall_BLC")

        cmds.connectAttr(self.rollControl+".weight", weightBlendNode+".blender")

        cmds.connectAttr(heelToeCondNode+".outColor.outColorG", weightBlendNode+".color1.color1R")
        cmds.connectAttr(heelToeCondNode+".outColor.outColorG", weightBlendNode+".color2.color2G")

        #connect the node to the joints
        cmds.connectAttr(weightBlendNode+".output.outputR", self.revToeJnt+".rotateY")
        cmds.connectAttr(weightBlendNode+".output.outputG", self.revBallJnt+".rotateY")

        #cleanup
        cmds.parent(self.rollControlOffsetGroup, self.footControl)
        cmds.select(clear = True)

    def CreateNoFlipObjects(self, prefix):
        #top no flip
        cmds.select(clear = True)
        hipPos = cmds.xform(self.hipJnt,q=1,ws=1,t=1)
        anklePos = cmds.xform(self.ankleJnt, q=1, ws=1, t=1)

        hipPoint = (hipPos[0], hipPos[1], hipPos[2])
        anklePoint = (anklePos[0], anklePos[1], anklePos[2])

        self.topNoFlipJnt = cmds.joint(p = hipPoint, n= prefix+"topNoFlip_JNT")
        self.topNoFlipEndJnt = cmds.joint(p = anklePoint, n= prefix+"topNoFlipEnd_JNT")
        #bottom no flip
        cmds.select(clear = True)
        self.botNoFlipJnt = cmds.joint(p = anklePoint, n= prefix+"bottomNoFlip_JNT")
        self.botNoFlipEndJnt = cmds.joint(p = hipPoint, n= prefix+"bottomNoFlipEnd_JNT")

        cmds.select(clear = True)
        self.legConJnt = cmds.joint(n = prefix+"legCon_JNT")
        pcon = cmds.parentConstraint(self.hipJnt, self.legConJnt)
        cmds.delete(pcon)

        #locs for PV
        topLoc = prefix+"topNFPV_LOC"
        botLoc = prefix+"bottomNFPV_LOC"
        kneeTopLoc = prefix+"noFlipTop_LOC"
        kneeBottomLoc = prefix+"noFlipBottom_LOC"
        cmds.spaceLocator(name = topLoc)
        cmds.spaceLocator(name = botLoc)
        cmds.spaceLocator(name = kneeTopLoc)
        cmds.spaceLocator(name = kneeBottomLoc)

        cmds.parent(topLoc, self.hipJnt)
        cmds.xform(topLoc ,translation = [0,5,0], worldSpace = False, absolute = True)
        cmds.parent(topLoc,  world = True)

        cmds.parent(botLoc, self.ankleJnt)
        cmds.xform(botLoc ,translation = [0,5,0], worldSpace = False, absolute = True)
        cmds.parent(botLoc,  world = True)

        pcon = cmds.parentConstraint(prefix+ self.LEG_JNT_NAMES[1] +"PV_CTL",kneeTopLoc)
        cmds.delete(pcon)
        pcon = cmds.parentConstraint(prefix+ self.LEG_JNT_NAMES[1] +"PV_CTL", kneeBottomLoc)
        cmds.delete(pcon)

        cmds.select(clear = True)

        self.topNFPV = topLoc
        self.botNFPV = botLoc
        self.kneeTopLoc = kneeTopLoc
        self.kneeBottomLoc = kneeBottomLoc


    def ConnectNoFlipControls(self, prefix):
        #grab the legs and ikh them
        topNFIKH = cmds.ikHandle( n=prefix+'topNoFlip_IKH', sj=self.topNoFlipJnt, ee=self.topNoFlipEndJnt, sol = "ikRPsolver")[0]
        botNFIKH = cmds.ikHandle( n=prefix+'botNoFlip_IKH', sj=self.botNoFlipJnt, ee=self.botNoFlipEndJnt, sol = "ikRPsolver")[0]
        
        #pv the locs
        cmds.poleVectorConstraint( self.topNFPV, topNFIKH)
        cmds.poleVectorConstraint( self.botNFPV, botNFIKH)

        #appropriate parenting
        cmds.parent(self.botNFPV, self.revAnkleJnt)
        cmds.parent(topNFIKH, self.revAnkleJnt)
        cmds.parent(self.botNoFlipJnt, self.revAnkleJnt)
        #connect the leg to the connector joing
        cmds.parent(self.hipJnt, self.legConJnt)
        #finish parenting under the connector
        cmds.parent(self.topNFPV, self.legConJnt)        
        cmds.parent(botNFIKH, self.legConJnt)
        cmds.parent(self.topNoFlipJnt, self.legConJnt)

        #knee loc parenting
        cmds.parent(self.kneeTopLoc, self.topNoFlipJnt)
        cmds.parent(self.kneeBottomLoc, self.botNoFlipJnt)

        #final constraint to enable the no flip behavior
        cmds.pointConstraint( self.kneeTopLoc, self.kneeBottomLoc, prefix + self.LEG_JNT_NAMES[1] + "PVOffset_GRP")


class CreateLegFromLocatorsUI():
    
    def addLocFromSel(*args):
        sel = cmds.ls(sl=True)
        add = cmds.textField(args[1], edit=True, text=sel[0])
    
    def newLocFromSel(*args): 
        loc = LocUtils.LocatorAtSelectionAverage(args[1])
        sel = cmds.ls(sl=True)
        add = cmds.textField(args[2], edit=True, text=loc)

    
    def StartModule(self, *args):
        locList = []
        locList.append(cmds.textField('HipLoctFld', query=True, text=True))
        locList.append(cmds.textField('KneeLoctFld', query=True, text=True))
        locList.append(cmds.textField('AnkleLoctFld', query=True, text=True))
        locList.append(cmds.textField('BallLoctFld', query=True, text=True))
        locList.append(cmds.textField('ToeLoctFld', query=True, text=True))

        textField_JointPrefix = cmds.textField('JointPfxtFld', query=True, text=True)
        floatField_JointRad = cmds.floatField('JointRadfFld', query=True, value=True)
        floatField_PVPush = cmds.floatField('PVPushfFld', query=True, value=True)

        checkBox_flipY = cmds.checkBox('FlipYChckBx' , query=True, value=True)
        LegModule().CreateLegAndFoot(locList,textField_JointPrefix,floatField_JointRad,floatField_PVPush,checkBox_flipY)

    def FinishModule(self, *args):
        textField_JointPrefix = cmds.textField('JointPfxtFld', query=True, text=True)
        LegModule().CompleteFootAndNoFlip(textField_JointPrefix)

    def GenerateUI(self):

        # Define an id string for the window first
        self.windowName = "Leg Module Generator v0.2"
        # define out own window ID with no special characters
        self.windowID = "LMGv0_2Window"

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
        cmds.rowColumnLayout(numberOfColumns=4, columnWidth=[(1, 80), (2, 60), (3, 120), (4, 60)])

        cmds.text(label="Name Prefix")
        self.JointPrefixTextFld = cmds.textField('JointPfxtFld',value="L_",)

        cmds.text(label="Joint Radius")
        self.JointRadiusFloatFld = cmds.floatField('JointRadfFld', minValue=0.01, value=.2, precision=2)
        
        cmds.text(label="PV Push")
        self.PVPushFloatFld = cmds.floatField('PVPushfFld', value=5, precision=2)

        cmds.text(label="Flip Hip/Knee Y")
        self.FlipYDirCheckBox = cmds.checkBox('FlipYChckBx', label= "",  align='center' )

        # escape the settings layout
        cmds.setParent('..')
        cmds.separator(height=25, style='out')
        
        cmds.text(label="Warning! Make sure you double check the hip/knee orients!")
        
        cmds.separator(height=25, style='out')
        self.GenerateButton = cmds.button(l='Generate Leg + Foot Control Bones', c=self.StartModule, h=50, width=200)
        
        cmds.separator(height=25, style='out')
        
        cmds.text(label="Warning! Make sure you have placed the Reverse Foot joints!")
        
        cmds.separator(height=25, style='out')
        self.FinishButton = cmds.button(l='Complete foot control + No flip Leg', c=self.FinishModule, h=50, width=200)
        # Display the window
        cmds.showWindow(self.win)           