import qi
import argparse
import sys
import math
import almath
import motion
import time
from Move import MoveTo


class GereMovement:
    def __init__(self, app):
        session = app.session
        self.motion_service = session.service("ALMotion")
        self.posture_service = session.service("ALRobotPosture")
        self.sonarProxy = session.service("ALSonar")
        self.memoryProxy = session.service("ALMemory")
        self.tts = session.service("ALTextToSpeech")
        self.move = MoveTo(app)

    def MoveAdresseSpecifique(self, x, y, theta):
        self.move.MoveTo(x, y, theta)

    def MoveAutonomeUnMetre(self):
        # self.move.main()
        # Wake up robot

        leftArmEnable = False
        rightArmEnable = False
        self.motion_service.setMoveArmsEnabled(leftArmEnable, rightArmEnable)
        print "Disabled left arm rigth arms"
        #####################
        ## FOOT CONTACT PROTECTION
        #####################
        self.motion_service.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", False]])
        # motion_service.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", True]])
        # disable also right arm motion after 1 seconde
        time.sleep(1.0)
        # Activate Whole Body Balancer
        isEnabled = True
        self.motion_service.wbEnable(isEnabled)
        initRobotPosition = almath.Pose2D(self.motion_service.getRobotPosition(False))

        self.sonarProxy.subscribe("SonarActived")
        # Energisers des donnes
        self.memoryProxy.getData("Device/SubDeviceList/US/Left/Sensor/Value")
        distanceOpstacle = self.memoryProxy.getData("Device/SubDeviceList/US/Left/Sensor/Value")

        if distanceOpstacle > 1:
            self.motion_service.moveTo(1, 0, 0, _async=True)
        else:
            print "there is an obstacle, I am looking for another way"
            while distanceOpstacle < 1.5:
                print "il y a un obstacle"
                self.tts.say("there is an obstacle, I am looking for another way")
                self.move.Unschemalibre()
                self.motion_service.waitUntilMoveIsFinished()
                self.sonarProxy.subscribe("SonarActived")
                self.memoryProxy.getData("Device/SubDeviceList/US/Left/Sensor/Value")
                distanceOpstacle = self.memoryProxy.getData("Device/SubDeviceList/US/Left/Sensor/Value")

            self.motion_service.setMoveArmsEnabled(False, False)
            self.motion_service.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", False]])
            time.sleep(1.0)
            isEnabled = True
            self.motion_service.wbEnable(isEnabled)
            initRobotPosition = almath.Pose2D(self.motion_service.getRobotPosition(False))
            self.motion_service.moveTo(1, 0, 0, _async=True)

        self.motion_service.waitUntilMoveIsFinished()
        #####################
        ## get robot position after move
        #####################
        endRobotPosition = almath.Pose2D(self.motion_service.getRobotPosition(False))
        #####################
        ## compute and print the robot motion
        #####################
        robotMove = almath.pose2DInverse(initRobotPosition) * endRobotPosition
        # return an angle between ]-PI, PI]
        robotMove.theta = almath.modulo2PI(robotMove.theta)
        print "Robot Move:", robotMove
        # Deactivate Whole Body Balancer
        isEnabled = False
        self.motion_service.wbEnable(isEnabled)
        self.motion_service.stopMove()
        leftArmEnable = True
        rightArmEnable = True
        self.motion_service.setMoveArmsEnabled(leftArmEnable, rightArmEnable)
