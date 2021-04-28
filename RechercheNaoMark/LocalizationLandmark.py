#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Demonstrates a way to localize the robot with ALLandMarkDetection"""
from naoqi import ALProxy
import qi
import time
import sys
import argparse
import math
import almath
import time
import math


class LandmarkLocalization:
    """
    We first instantiate a proxy to the ALLandMarkDetection module
    Note that this module should be loaded on the robot's naoqi.
    The module output its results in ALMemory in a variable
    called "LandmarkDetected".
    We then read this ALMemory value and check whether we get
    interesting things.
    After that we get the related position of the landmark compared to robot.
    """

    def __init__(self, app):
        """
        Initialisation of qi framework and event detection.
        """
        # app.start()
        session = app.session
        self.motion_service = session.service("ALMotion")
        self.posture_service = session.service("ALRobotPosture")
        # Wake up robot
        # self.motion_service.wakeUp()
        # Send robot to Stand Init
        # self.posture_service.goToPosture("StandInit", 0.5)
        # Get the service ALMemory.
        self.memory = session.service("ALMemory")
        # Connect the event callback.
        self.subscriber = self.memory.subscriber("LandmarkDetected")
        self.rechercherNaoMark = self.subscriber.signal.connect(self.on_landmark_detected)
        # Get the services ALTextToSpeech, ALLandMarkDetection and ALMotion.
        self.tts = session.service("ALTextToSpeech")
        self.landmark_detection = session.service("ALLandMarkDetection")
        self.motion_service = session.service("ALMotion")
        self.landmark_detection.subscribe("LandmarkDetector", 500, 0.0)
        self.got_landmark = False
        # Set here the size of the landmark in meters.
        self.landmarkTheoreticalSize = 0.06  # in meters
        # Set here the current camera ("CameraTop" or "CameraBottom").
        self.currentCamera = "CameraTop"
        # detected Naomark
        self.find = False
        self.x = 0
        self.y = 0
        self.z = 0

    def on_landmark_detected(self, markData):
        """
        Callback for event LandmarkDetected.
        """

        if markData == []:  # empty value when the landmark disappears
            self.got_landmark = False
        elif not self.got_landmark:  # only speak the first time a landmark appears
            self.got_landmark = True
            self.find = True
            print "I saw a landmark! "
            self.tts.say("I saw a landmark! ")

            # Retrieve landmark center position in radians.
            wzCamera = markData[1][0][0][1]
            wyCamera = markData[1][0][0][2]

            # Retrieve landmark angular size in radians.
            angularSize = markData[1][0][0][3]

            # Compute distance to landmark.
            distanceFromCameraToLandmark = self.landmarkTheoreticalSize / (2 * math.tan(angularSize / 2))

            # Get current camera position in NAO space.
            transform = self.motion_service.getTransform(self.currentCamera, 2, True)
            transformList = almath.vectorFloat(transform)
            robotToCamera = almath.Transform(transformList)

            # Compute the rotation to point towards the landmark.
            cameraToLandmarkRotationTransform = almath.Transform_from3DRotation(0, wyCamera, wzCamera)

            # Compute the translation to reach the landmark.
            cameraToLandmarkTranslationTransform = almath.Transform(distanceFromCameraToLandmark, 0, 0)

            # Combine all transformations to get the landmark position in NAO space.
            robotToLandmark = robotToCamera * cameraToLandmarkRotationTransform * cameraToLandmarkTranslationTransform

            self.x = robotToLandmark.r1_c4
            self.y = robotToLandmark.r2_c4
            self.z = robotToLandmark.r3_c4
            print "Dans le classe LocalizationLandmark Position of landmark et x= " + str(self.x)+", y="+str(self.y)+", z="+str(self.x)
    pass

    def run(self):
        """
        Loop on, wait for events until manual interruption.
        """
        print "Starting LandmarkDetector"
        try:
            cpt = 2
            while cpt != 0:
                time.sleep(1)
                cpt = cpt - 1
                if self.find:
                    break

        except KeyboardInterrupt:
            print "Interrupted by user, stopping LandmarkDetector"
            self.landmark_detection.unsubscribe("LandmarkDetector")
            # stop
            # sys.exit(0)
    pass
