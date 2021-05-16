from naoqi import ALProxy
from RechercheNaoMark.Recherche import Recherche
from Deplacement.GereMovement import GereMovement
from NaoDetect.NaoResearchObject import NaoResearchObject
import qi
import argparse
import sys
import time
import almath
import math
import os
import urllib


#opload model yolo-tiny.h5
if os.path.isdir("NaoModels"):
    pass
else:
    os.makedirs("NaoModels")
urllib.urlretrieve("https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/yolo-tiny.h5/", "NaoModels/yolo-tiny.h5")

parser = argparse.ArgumentParser()
parser.add_argument("--ip", type=str, default="192.168.43.166", help="Robot IP address. On robot or Local Naoqi: use "
                                                                     "'192.168.43.166'.")
parser.add_argument("--port", type=int, default=9559, help="Naoki port number")

args = parser.parse_args()

try:
    connection_url = "tcp://" + args.ip + ":" + str(args.port)
    app = qi.Application(["LandmarkDetector", "--qi-url=" + connection_url])
except RuntimeError:
    print("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) + ".\n"
                                                                                         "Please check your script "
                                                                                         "arguments. Run with -h "
                                                                                         "option for help.")
    sys.exit(1)
# Start the session
app.start()
main = NaoResearchObject(app)
found = main.detect_object()
if found: #nao detect the object and pick it up
    pass
else: #nao didn't detect the object
    sys.exit(100) 
    
# Object deja Trouve Recherche D'un boubelle
motion_service = app.session.service("ALMotion")
posture_service = app.session.service("ALRobotPosture")
tts = app.session.service("ALTextToSpeech")

# Wake up robot
motion_service.wakeUp()
# Send robot to Stand Init
posture_service.goToPosture("StandInit", 0.5)

names = list()
times = list()
keys = list()
names.append("RShoulderRoll")
times.append([1.00000])
keys.append([-0.006981])
names.append("RShoulderPitch")
times.append([1.00000])
keys.append([0.167552])
names.append("RElbowRoll")
times.append([1.00000])
keys.append([0.034907])
names.append("RElbowYaw")
times.append([1.00000])
keys.append([1.125737])
names.append("RWristYaw")
times.append([1.00000])
keys.append([0.000000])
names.append("RHand")
times.append([1.00000])
keys.append([0.100000])

try:
    motion_service.angleInterpolation(names, keys, times, True)
except BaseException, err:
    pass
print  "Je vais commence recherche du poubelle"
time.sleep(5)

# declaration des Instace
rech = Recherche(app)
move = GereMovement(app)
Trouver = False

# Recherche de Cible

while not Trouver:
    rech.rechercheRand()
    Trouver = rech.Trouver
    # Cible Non Trouver
    if not rech.Trouver:
        tts.say("up to now not find, I'm going ahead")
        time.sleep(2)
        move.MoveAutonomeUnMetre()

# Cible trouver et s'addrrese vers lui
print "cible trouver"
time.sleep(2)
print "dans la classe main x=" + str(rech.x)
#rech.z*almath.TO_RAD
theta= math.atan(rech.y/rech.x);
move.MoveAdresseSpecifique(1.4*rech.x, rech.y , -theta);
# pour ne perte a son champ de vision il va pas aller exactement a l'addresse de Nao mark mais

#move.MoveAdresseSpecifique(rech.x, rech.y, theta);


names = list()
times = list()
keys = list()
names.append("RShoulderRoll")
times.append([1.00000])
keys.append([-0.006981])
names.append("RShoulderPitch")
times.append([1.00000])
keys.append([0.167552])
names.append("RElbowRoll")
times.append([1.00000])
keys.append([0.034907])
names.append("RElbowYaw")
times.append([1.00000])
keys.append([1.125737])
names.append("RWristYaw")
times.append([1.00000])
keys.append([-1.312488])
names.append("RHand")
times.append([1.00000])
keys.append([1.000000])

try:
    motion_service.angleInterpolation(names, keys, times, True)
except BaseException, err:
    pass

# arrette le processus
sys.exit(100)
# Arrete le system


# m = RechNaoMark(session)
# m.onInput_onStart()
