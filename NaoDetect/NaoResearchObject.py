import argparse
import math
import sys
import time

import qi
from imageai import Detection
import numpy as np
import cv2


class NaoResearchObject:

    def __init__(self, app):
        session = app.session
        self.session = session
        self.videoDevice = session.service('ALVideoDevice')
        self.motionProxy = session.service("ALMotion")
        self.tts = session.service("ALTextToSpeech")
        self.postureService = None
        try:
            self.postureService = session.service("ALRobotPosture")
        except:
            self.logger.error("Module 'ALRobotPosture' not found.")

        model_path = "NaoModels/yolo-tiny.h5"
        self.detect = Detection.ObjectDetection()
        self.detect.setModelTypeAsTinyYOLOv3()
        self.detect.setModelPath(model_path)
        self.detect.loadModel()

        AL_kTopCamera = 0
        AL_kQVGA = 1  # 640x480
        AL_kBGRColorSpace = 13  # 0xRRGGBB
        self.captureDevice = self.videoDevice.subscribeCamera("NAO 6", AL_kTopCamera, AL_kQVGA, AL_kBGRColorSpace, 10)
        self.cam_width = 320
        self.cam_height = 240
        self.image = np.zeros((self.cam_height, self.cam_width, 3), np.uint8)  # create image

    def setHeadAngle(self, alpha, beta):
        self.motionProxy.setStiffnesses("Head", 1.0)
        maxSpeedFraction = 0.3
        names = ["HeadYaw", "HeadPitch"]
        angles = [alpha, beta]
        self.motionProxy.angleInterpolationWithSpeed(names, angles, maxSpeedFraction)
        self.motionProxy.setStiffnesses("Head", 0.0)

    def standInit(self):
        if self.postureService is not None:
            result = self.postureService.goToPosture("Stand", 0.8)
            if not result:
                self.logger.error(
                    "Posture Stand is not a part of the standard posture library or robot cannot reach the posture")

    def posToPickUp(self):
        self.postureService.goToPosture("Crouch", 0.8)
        names = list()
        times = list()
        keys = list()
        names.append("RShoulderRoll")
        times.append([1.00000])
        keys.append([-0.050664])
        names.append("RShoulderPitch")
        times.append([1.00000])
        keys.append([0.457090])
        names.append("RElbowRoll")
        times.append([1.00000])
        keys.append([0.034907])
        names.append("RElbowYaw")
        times.append([1.00000])
        keys.append([1.125737])
        names.append("RWristYaw")
        times.append([1.00000])
        keys.append([0.000000])

        names.append("LShoulderRoll")
        times.append([1.00000])
        keys.append([-0.050664])
        names.append("LShoulderPitch")
        times.append([1.00000])
        keys.append([0.457090])
        names.append("LElbowRoll")
        times.append([1.00000])
        keys.append([-0.068988])
        names.append("LElbowYaw")
        times.append([1.00000])
        keys.append([-1.145940])
        names.append("LWristYaw")
        times.append([1.00000])
        keys.append([0.615176])
        try:
            self.motionProxy.angleInterpolation(names, keys, times, True)
        except BaseException, err:
            pass
        self.motionProxy.openHand("RHand")
        self.motionProxy.openHand("LHand")

    def standUp(self):
        names = list()
        times = list()
        keys = list()
        names.append("LHipYawPitch")
        times.append([1.00000])
        keys.append([-0.170010])
        names.append("LHipRoll")
        times.append([1.00000])
        keys.append([0.119108])
        names.append("LHipPitch")
        times.append([1.00000])
        keys.append([0.127419])
        names.append("LKneePitch")
        times.append([1.00000])
        keys.append([-0.092328])
        names.append("LAnklePitch")
        times.append([1.00000])
        keys.append([0.087419])
        names.append("LAnkleRoll")
        times.append([1.00000])
        keys.append([-0.110793])

        names.append("RHipYawPitch")
        times.append([1.00000])
        keys.append([-0.170010])
        names.append("RHipRoll")
        times.append([1.00000])
        keys.append([-0.119102])
        names.append("RHipPitch")
        times.append([1.00000])
        keys.append([0.127419])
        names.append("RKneePitch")
        times.append([1.00000])
        keys.append([-0.092328])
        names.append("RAnklePitch")
        times.append([1.00000])
        keys.append([0.087419])
        names.append("RAnkleRoll")
        times.append([1.00000])
        keys.append([0.110793])
        try:
            self.motionProxy.angleInterpolation(names, keys, times, True)
        except BaseException, err:
            pass

    def pickUpObject(self):
        names = list()
        times = list()
        keys = list()
        names.append("LShoulderRoll")
        times.append([1.00000])
        keys.append([-0.300000])
        names.append("RShoulderRoll")
        times.append([1.00000])
        keys.append([+0.300000])
        try:
            self.motionProxy.angleInterpolation(names, keys, times, True)
        except BaseException, err:
            pass

        names = list()
        times = list()
        keys = list()
        names.append("LShoulderPitch")
        times.append([1.00000])
        keys.append([0.100000])
        names.append("RShoulderPitch")
        times.append([1.00000])
        keys.append([0.100000])
        try:
            self.motionProxy.angleInterpolation(names, keys, times, True)
        except BaseException, err:
            pass
        self.motionProxy.setMoveArmsEnabled(False, False)
        time.sleep(1)
        self.standUp()
        time.sleep(1)

    def detect_object(self):
        self.standInit()
        time.sleep(2)
        self.setHeadAngle(0, 0.25)
        flag = False
        turn = 1
        while True:
            result = self.videoDevice.getImageRemote(self.captureDevice)
            if result is None:
                print('cannot capture.')
            elif result[6] is None:
                print('no image data string.')
            else:
                # translate value to mat
                values = list(result[6])
                i = 0
                for y in range(0, self.cam_height):
                    for x in range(0, self.cam_width):
                        self.image.itemset((y, x, 0), values[i + 0])
                        self.image.itemset((y, x, 1), values[i + 1])
                        self.image.itemset((y, x, 2), values[i + 2])
                        i += 3

                self.image, desc = self.detect.detectObjectsFromImage(input_image=self.image,
                                                                      input_type="array",
                                                                      output_type="array",
                                                                      minimum_percentage_probability=60,
                                                                      display_percentage_probability=False)

                for eachItem in desc:
                    if eachItem["percentage_probability"] >= 30 and eachItem["name"] == 'bottle':
                        flag = True
                        self.tts.say("I see a " + eachItem["name"])
                        x1, y1, x2, y2 = eachItem["box_points"]

                        print(eachItem["name"], " : ", eachItem["percentage_probability"])
                        x = round(0.0067 * ((y1 + y2)/2) - 0.34, 2)
                        y = round((-0.0039) * ((x1 + x2)/2) + 0.7, 2)

                        self.motionProxy.moveTo(x, y, 0)
                        self.motionProxy.waitUntilMoveIsFinished()
                        break
                    else:
                        print(eachItem["name"], " : ", eachItem["percentage_probability"])
                cv2.imshow("Nao Camera", self.image)
                if turn > 5:
                    self.tts.say(" Sorry I didn't found anything")
                    self.postureService.goToPosture("Sit", 0.8)
                    return False
                if not flag:
                    self.motionProxy.moveTo(-0.1, 0.1, math.pi / 3)
                    turn = turn + 1
                else:
                    self.posToPickUp()
                    self.pickUpObject()
                    time.sleep(3)
                    return True

            if cv2.waitKey(33) == 27:
                self.videoDevice.unsubscribe(self.captureDevice)
                break
