# Myo armband feature extraction and implementation with MQTT 

## Myo armband 

Myo gesture recognition armband, developed by Thalmic Labs ([1](https://www.hongkiat.com/blog/motion-sensing-gadgets/)), is a device that read sEMG signals from our arms, which was aimed to allow control other Bluetooth enabled devices using your hand gesture. For example, with Myo Connect software, we can control the transitioning of presentation slides by waving in or out; Making a fist will control the digital pointer on the monitor and rolling it to zoom in on the slide. 

Thanks to the work of [Dzu](https://github.com/dzhu/myo-raw), EMG raw data and Pose recognition data from Myo armband can be obtained and publish to the MQTT broker server in order to communicate with [NodeMCU](https://github.com/Kenfin2017/myo-mqtt-robot-application), which is another client acting as subscriber to "/Myo/pose" topic and control Arduino-controlled-robot-arm through Serial communication. 

## MQTT

MQTT is a lightweight publish/subscribe messaging protocol. It is useful for low-power sensors, but is applicable to many scenarios. 
In theory, MQTT is based on the principle of publishing and subscribing to topics or “pub/sub”, where multiple clients connect to a broker and publish messages to topics. Many clients may subscribe to the same topics and do with the information as they please. The broker and MQTT act as a simple, common interface for everything to connect to. This means that you if you have clients that dump subscribed messages to a database, to Twitter, Cosm or even a simple text file, then it becomes very simple to add new sensors or other data input to a database, Twitter or so on.

In my implementation, Mosquitto is used as MQTT broker & client service for performing message publishing and subscribing on "/Myo/pose" topic. The credentials validation can be configure on the gateway once Mosquitto has been installed. 
- Initialize users' profile as text files (passwd.txt):
```
myo: your-password-here
```
- Hashing the password with mosquitto command:
```bash
mosquitto_passwd -U passwd.txt
```

- Appending the following line in mosquitto config file /etc/mosquitto/mosquitto.conf:
```conf
include_dir /etc/mosquitto/conf.d
```
- Restart Mosquitto service in order to activate user authentication:
```bash
sudo systemctl restart mosquitto
```

- The credentials of Myo armband python node is mentioned in the myo_raw.py:
```python
client.username_pw_set("myo", password="your-password-here") 
```

## How it works
In order to publish messages from armband to the gateway, you must perfrom [sync_gesture](https://support.getmyo.com/hc/en-us/articles/200755509-How-to-perform-the-sync-gesture) while wearing it.

In order to check the log of message from the recipient side (MCU_Node), connect the node and open Serial monitor on 9600 baudrate channel. 

## Command protocol
| Pose | arm's position| MQTT message | Serial command | Robot move |
| --- | --- |:---:|:---:|---:|
| WAVE_OUT | at chest level | ROTATE_CW | 1 | Bottom servo rotate clockwise |
| WAVE_IN | at chest level | ROTATE_CCW | 2 | counter-clockwise |
| FIST | raised | RAISE | 3 | Left servo rotate clockwise |
| FIST | lowered | LOWER | 4 | Left servo rotate counter-clockwise |
| FINGERS_SPREAD | at chest level | STRETCH | 5 | Right servo rotate counter-clockwise |
| FIST | at chest level | SHORTEN | 6 | Left servo rotate clockwise |
| DOUBLE_TAP | any | DOUBLE_TAP | 0 | Hand servo close/open |
| REST | any | - | - | Stop on-going move |