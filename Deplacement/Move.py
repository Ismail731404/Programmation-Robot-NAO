import qi
import argparse
import sys
import math
import almath
import motion
import time


class MoveTo:
    def __init__(self, app):
        session = app.session
        self.motion_service = session.service("ALMotion")
        self.posture_service = session.service("ALRobotPosture")

    def MoveTo(self, X, Y, Theta):
        """
        Move To: Small example to make Nao Move To an Objective.
        """
        #####################
        ## Enable arms control by move algorithm
        #####################
        # self.motion_service.setMoveArmsEnabled(True, True)
        self.motion_service.setMoveArmsEnabled(False, False)

        #####################
        ## FOOT CONTACT PROTECTION
        #####################
        self.motion_service.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", False]])
        time.sleep(1.0)
        # Activate Whole Body Balancer
        isEnabled = True
        self.motion_service.wbEnable(isEnabled)
        #####################
        ## get robot position before move
        #####################
        initRobotPosition = almath.Pose2D(self.motion_service.getRobotPosition(False))

        self.motion_service.moveTo(X, Y, Theta, _async=True)
        # wait is useful because with _async moveTo is not blocking function
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
        self.motion_service.setMoveArmsEnabled(True, True)

    def Unschemalibre(self):
        """
        Move To: Small example to make Nao Move To an Objective.
        """

        leftArmEnable = False
        rightArmEnable = False
        self.motion_service.setMoveArmsEnabled(leftArmEnable, rightArmEnable)
        print "Disabled left arm rigth arms"
        #####################
        ## FOOT CONTACT PROTECTION
        #####################
        self.motion_service.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", False]])

        time.sleep(1.0)
        # Activate Whole Body Balancer
        isEnabled = True
        self.motion_service.wbEnable(isEnabled)
        initRobotPosition = almath.Pose2D(self.motion_service.getRobotPosition(False))
        X = 0.3
        Y = 0.1
        Theta = math.pi / 2.0
        self.motion_service.moveTo(X, Y, Theta, _async=True)
        # wait is useful because with _async moveTo is not blocking function
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