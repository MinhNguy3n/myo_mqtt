''' 
Author: Fernando Cosentino
Modified by: Minh Nguyen
Date: 23-03-2020
Description: MQTT connection with Mosquitto broker service provider 
            for robot arm control with the following protocol (with respect to right arm):
            arm elevation |    pose        | command
            --------------|----------------|---------
                mid       |  waveOut       | ROTATE_CCW
                mid       |  waveIn        | ROTATE_CW
                mid       |  fist          | SHORTEN
                mid       |  fingersSpread | STRETCH
                any       |  rest          | REST
                any       |  doubleTap     | DOUBLE_TAP
                high      |  fist          | RAISE
                low       |  fist          | LOWER
'''

global MESSAGE
global client
global broker_url
global broker_port

# MQTT message 
MESSAGE = ""
# MQTT dependencies
broker_port = 1883
broker_url = "localhost"

# arm altitude processed in proc_imu: "mid", "high", "low"
arm_alt = "mid"
user_arm = ""

scriptTitle = "Robot arm control"
scriptDescription = "handling poses and arm's elevation to send command"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code: {}".format(rc))

def on_disconnect(client, userdata, rc):
    print("Client got disconnected")
    
def on_log(mqttc, obj, level, string):
    print(string)

def onUnlock():
    import paho.mqtt.client as mqtt
    global client
    global broker_url
    global broker_port
    myo.rotSetCenter()
    myo.unlock("hold")
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    #client.on_log = on_log
    client.username_pw_set("myo", password="Myoband")
    client.connect(broker_url, broker_port)
    client.subscribe("/Myo/pose", qos=1)
    # the following function implement threaded interface to network, which create a loop in background. 
    # this call also handles reconnecting to the broker 
    client.loop_start()

def onWear(arm, xDirection):
    print("Arm detected")
    print("Connected with {}".format(arm))
    print("Direction {}".format(xDirection)) 

    
def onUnwear():
    # global client
    print("Arm is desynchronized!")
    #stop background thread and disconnect from broker
    client.loop_stop(force=False)
    client.unsubscribe("/Myo/pose")
    client.disconnect()

def onPoseEdge(pose, edge):
    global MESSAGE
    global client

    MESSAGE = pose
    user_arm = myo.getArm()
    arm_alt = "mid"
    x = myo.getAccel()[0]
    y = myo.getAccel()[1]
    z = myo.getAccel()[2]
    print("received: "+MESSAGE+", "+edge)
    if(x*z < 0 and x < -0.5):
        arm_alt = "high"
    elif(x*z > 0 and x > 0.5):
        arm_alt = "low"
    else:
        arm_alt = "mid"
    #print("Arm levitation: "+arm_alt)
    if edge == "on":
        if MESSAGE == "rest":
            client.publish(topic="/Myo/pose", payload="REST", qos=1, retain=False)
        elif MESSAGE == "doubleTap":
            client.publish(topic="/Myo/pose", payload="DOUBLE_TAP", qos=1, retain=False)
        elif(arm_alt == "mid" and MESSAGE == "waveOut"):
            if user_arm == "right":
                client.publish(topic="/Myo/pose", payload="ROTATE_CCW", qos=1, retain=False)
            elif user_arm == "left":
                client.publish(topic="/Myo/pose", payload="ROTATE_CW", qos=1, retain=False)
        elif (arm_alt == "mid" and MESSAGE == "waveIn"):
            if user_arm == "right":
                client.publish(topic="/Myo/pose", payload="ROTATE_CW", qos=1, retain=False)
            elif user_arm == "left":
                client.publish(topic="/Myo/pose", payload="ROTATE_CCW", qos=1, retain=False)
        elif (arm_alt == "mid" and MESSAGE == "fingersSpread"):
            client.publish(topic="/Myo/pose", payload="STRETCH", qos=1, retain=False)
        elif (arm_alt == "mid" and MESSAGE == "fist"):
            client.publish(topic="/Myo/pose", payload="SHORTEN", qos=1, retain=False)
        elif (arm_alt == "high" and MESSAGE == "fist"):
            client.publish(topic="/Myo/pose", payload="RAISE", qos=1, retain=False)
        elif (arm_alt == "low" and MESSAGE == "fist"):
            client.publish(topic="/Myo/pose", payload="LOWER", qos=1, retain=False)
        else:
            pass