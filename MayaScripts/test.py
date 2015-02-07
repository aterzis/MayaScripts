#This is a test

from maya import cmds

cmds.sphere()
cmds.xform("nurbsSphere1", t = 3)


# Define a dictionary that maps the mocap joints to the actual rig joints
Alfred = {#spine
          "mocap_Hips": "root", 
          "mocap_Spine": "spineLower",
          "mocap_Spine1": "spineMid",
          "mocap_Spine2": "spineHigher",
          "mocap_Chest": "chest",
          "mocap_Neck": "neck",
          "mocap_Head": "head",
          "mocap_HeadMid": "headMid",
          "mocap_HeadHigher":"headHigher",
          #Hip
          "mocap_Hip": "hip",
          #Left Shoulder
          "mocap_LeftShoulder": "Left_Shoulder",
          "mocap_LeftArm": "LeftArmOriginal",
          "mocap_LeftForeArm": "LeftElbowOriginal",
          "mocap_LeftHand": "Left_WristOriginal",
          #Left Leg
          "mocap_LeftUpLeg": "Left_Leg",
          "mocap_LeftLeg": "Left_Knee",
          "mocap_LeftFoot": "Left_Ankle",
          "mocap_LeftToeBase": "Left_Fingers",
          #Right Shoulder
          "mocap_RightShoulder": "Right_Shoulder",
          "mocap_RightArm": "RightArmOriginal",
          "mocap_RightForeArm": "RightElbowOriginal",
          "mocap_RightHand": "Right_WristOriginal",
          #Right Leg
          "mocap_RightUpLeg": "Right_Leg",
          "mocap_RightLeg": "Right_Knee",
          "mocap_RightFoot": "Right_Ankle",
          "mocap_RightToeBase": "Right_Fingers",}