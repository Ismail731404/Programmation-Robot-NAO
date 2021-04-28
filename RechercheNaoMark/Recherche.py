import almath
import time
import math
import argparse
from LocalizationLandmark import LandmarkLocalization


class Recherche:

    def __init__(self, app):
        self.Verifiedroit = False
        self.app = app
        session = app.session
        self.app = app
        self.session = session
        self.motion = session.service("ALMotion")
        self.memory = session.service("ALMemory")
        self.tts = session.service("ALTextToSpeech")
        self.posture_service = session.service("ALRobotPosture")
        self.Trouver = False
        self.Verifiegauche = False
        self.VerifiedroitEnBas = False
        self.VerifiegaucheEnBas = False
        self.EnBas = False
        self.x = 0
        self.y = 0
        self.z = 0

    def rechercheRand(self):
        landmark_detector = LandmarkLocalization(self.app)
        landmark_detector.run()
        for i in range(5):
            if not landmark_detector.find:
                self.tts.say("trash can not find, I turn around")
                self.MovementRotation()
                landmark_detector.run()
            else:
                time.sleep(3.5)
                break
        if landmark_detector.find:
            print "Je vais envoyer le coordonne du cible  x= " + str(landmark_detector.x)
            self.Trouver = True
            self.x = landmark_detector.x
            self.y = landmark_detector.y
            self.z = landmark_detector.z

    def onStart(self):
        # self.motion_service.moveTo(robotToLandmark.r1_c4, robotToLandmark.r2_c4, 0.0)

        landmark_detector = LandmarkLocalization(self.app)
        landmark_detector.run()

        if not self.EnBas and not landmark_detector.find:
            self.tourneMarkToutDroitEnBas()
            self.EnBas = True
            landmark_detector.run()
        if not self.VerifiedroitEnBas and not landmark_detector.find:
            self.tourneMarkdroitEnBas()
            self.VerifiedroitEnBas = True
            landmark_detector.run()
        if not self.Verifiedroit and not landmark_detector.find:
            self.tourneMarkdroit()
            self.Verifiedroit = True
            landmark_detector.run()
        if not self.Verifiegauche and not landmark_detector.find:
            self.TourneMarkGauche()
            self.Verifiegauche = True
            landmark_detector.run()
        if not self.VerifiegaucheEnBas and not landmark_detector.find:
            self.tourneMarkGaucheEnBas()
            self.VerifiegaucheEnBas = True
            landmark_detector.run()

        if landmark_detector.find:
            print "Je vais envoyer le coordonne du cible  x= " + str(landmark_detector.x)
            self.Trouver = True
            self.x = landmark_detector.x
            self.y = landmark_detector.y
            self.z = landmark_detector.z

        else:
            self.tourneMarkToutDroit()
            self.Verifiegauche = False
            self.Verifiedroit = False
            self.VerifiegaucheEnBas = False
            self.VerifiedroitEnBas = False
            self.EnBas = False

    def TourneMarkGauche(self):
        names = "HeadYaw"
        timeLists = 1.0
        isAbsolute = True
        angleLists = -50.0 * almath.TO_RAD
        self.motion.angleInterpolation(names, angleLists, timeLists, isAbsolute)

    def tourneMarkGaucheEnBas(self):
        names = "Head"
        timeLists = 1.0
        isAbsolute = True
        angleLists = -50.0 * almath.TO_RAD
        self.motion.angleInterpolation(names, angleLists, timeLists, isAbsolute)

    def tourneMarkdroitEnBas(self):
        names = "Head"
        timeLists = 1.0
        isAbsolute = True
        angleLists = 50.0 * almath.TO_RAD
        self.motion.angleInterpolation(names, angleLists, timeLists, isAbsolute)

    def tourneMarkToutDroit(self):
        names = "HeadYaw"
        timeLists = 1.0
        isAbsolute = True
        angleLists = 0.0
        self.motion.angleInterpolation(names, angleLists, timeLists, isAbsolute)

    def tourneMarkToutDroitEnBas(self):
        names = "Head"
        timeLists = 1.0
        isAbsolute = True
        angleLists = 0.0
        self.motion.angleInterpolation(names, angleLists, timeLists, isAbsolute)

    def MovementRotation(self):
        # Wake up robot
        # self.motion.wakeUp()
        # Send robot to Pose Init
        # self.posture_service.goToPosture("StandInit", 0.5)
        # Example showing how to disable left arm motions during a move
        leftArmEnable = False
        rightArmEnable = False
        self.motion.setMoveArmsEnabled(leftArmEnable, rightArmEnable)
        print "Disabled left arm rigth arms"
        #####################
        ## FOOT CONTACT PROTECTION
        #####################
        self.motion.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", False]])
        # motion_service.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", True]])
        # disable also right arm motion after 1 seconde
        time.sleep(1.0)
        # Activate Whole Body Balancer
        isEnabled = True
        self.motion.wbEnable(isEnabled)
        initRobotPosition = almath.Pose2D(self.motion.getRobotPosition(False))
        X = 0.3
        Y = 0.1
        Theta = math.pi / 2.0
        self.motion.moveTo(X, Y, Theta, _async=True)
        # wait is useful because with _async moveTo is not blocking function
        self.motion.waitUntilMoveIsFinished()
        #####################
        ## get robot position after move
        #####################
        endRobotPosition = almath.Pose2D(self.motion.getRobotPosition(False))
        #####################
        ## compute and print the robot motion
        #####################
        robotMove = almath.pose2DInverse(initRobotPosition) * endRobotPosition
        # return an angle between ]-PI, PI]
        robotMove.theta = almath.modulo2PI(robotMove.theta)
        print "Robot Move:", robotMove
        # Deactivate Whole Body Balancer
        isEnabled = False
        self.motion.wbEnable(isEnabled)
        self.motion.stopMove()
        leftArmEnable = True
        rightArmEnable = True
        self.motion.setMoveArmsEnabled(leftArmEnable, rightArmEnable)
