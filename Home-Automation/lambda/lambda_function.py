# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import requests

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

global validate
validate = False

global my_remote
my_remote = {}

global verifiedUSER 
verifiedUSER=False

global verifiedemail
verifiedemail=False

global home
home = {}

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        global verifiedemail,validate,verifiedUSER
        speak_output = "Welcome to your Smart Home "
        userId = handler_input.request_envelope.session.user.user_id
        deviceId = handler_input.request_envelope.context.system.device.device_id
        r = requests.post("YOUR_API_LINK_HERE",data={"userid":userId,"deviceid":deviceId})
        response = r.json()
        # speak_output=response["res"]
        if(response["res"] == "verified"):
            verifiedUSER=True
            verifiedemail=True
            validate=True
            speak_output=speak_output+response["name"]
            global home
            home.update({"room":response["room"]})
            home.update({"status":response["status"]})
            home.update({"buttonno":response["buttonno"]})
            home.update({"equip":response["equip"]})
            home.update({"username":response["username"]})
            # for x in response["room"]:
            #     speak_output=speak_output+str(x)
            # for x in response["status"]:
            #     speak_output=speak_output+str(x)
            # for x in response["buttonno"]:
            #     speak_output=speak_output+str(x)
            # for x in response["equip"]:
            #     speak_output=speak_output+str(x)
        else:
            speak_output=speak_output+response["res"]
            #"Register yourself to access this feature. To register say my number is and then speak your ten digit mobile number"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class contactDetailsIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("contactDetails")(handler_input)
    
    def handle(self, handler_input):
        global verifiedUSER,verifiedemail
        if(verifiedUSER==False):
            mobile = handler_input.request_envelope.request.intent.slots
            mobileNum = mobile["number"].value
            userId = handler_input.request_envelope.session.user.user_id
            deviceId = handler_input.request_envelope.context.system.device.device_id
            r = requests.post("YOUR_API_LINK_HERE", data={'mobileNumber': mobileNum,"userId":userId,"deviceId":deviceId})
            if(r.text == "Unauthorised"):
                speak_output="You are not registered with s m enterprise. go to my s m remote dot in and sign up"
            else:
                speak_output = r.text
                verifiedUSER=True
        elif(verifiedemail==False):
            speak_output="Your email verificaton is pending. Kindly, go to your email id and click on the registration link"
        else:
            speak_output="Your number is already registered. Kindly say room number and then the room number in which you want to operate the device"

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )

class emailVerificationIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("emailVerification")(handler_input)
    
    def handle(self, handler_input):
        global verifiedemail
        if(verifiedemail==False):
            userId = handler_input.request_envelope.session.user.user_id
            deviceId = handler_input.request_envelope.context.system.device.device_id
            r = requests.post("YOUR_API_LINK_HERE", data={"userid":userId,"deviceid":deviceId})
            response = r.json()
            #speak_output=response["res"]
            if(response["res"]=="verified"):
                speak_output="Welcome to your smart home "+response["name"]
                global validate
                validate=True
                verifiedemail=True
            else:
                speak_output=response["res"]
        else:
            speak_output="Your email is already verified. Kindly say room number and then the room number in which you want to operate the device"

        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )

class roomInfoIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("roomInfo")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        roomT = handler_input.request_envelope.request.intent.slots
        room2 = roomT["room"]
        room = room2.value
        #speak_output = room
        global my_remote,validate
        if(validate==True):
            my_remote.update({"room_number": room})
            if("device" in my_remote.keys()):
                orderT = my_remote["order"]
                deviceT = my_remote["device"]
                r = requests.post("YOUR_API_LINK_HERE", data={'username': 'shantanu', 'order': orderT, 'device':deviceT,'roomno':room})
                speak_output=r.text
                del my_remote["order"]
                del my_remote["device"]
            else:
                speak_output="Kindly provide a device name"
        else:
            speak_output="Authorise Alexa first. Go to your mail id and click on the registration link"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class turnDeviceOnIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("turnDeviceOn")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        names = handler_input.request_envelope.request.intent.slots
        name = names["device"]
        deviceName = name.value
        if(deviceName=="light"):
            deviceName="L"
        elif(deviceName=="fan"):
            deviceName="F"
        elif(deviceName=="television"):
            deviceName="T"
        elif(deviceName=="geyser"):
            deviceName="G"
        elif(deviceName=="air conditioner"):
            deviceName="A"
            
        global my_remote,validate,home
        
        if(validate==True):
            my_remote.update({"device":deviceName})
            my_remote.update({"order":'on'})
            # speak_output = deviceName
            if("room_number" in my_remote.keys()):
                room_number = my_remote['room_number']
                username=home["username"]
                if(deviceName in home["equip"]):
                    deviceCount = home["equip"].count(deviceName)
                    if(deviceCount==1):
                        r = requests.post("YOUR_API_LINK_HERE", data={'username': username, 'order': 'on', 'device':deviceName,'roomno':room_number})
                        speak_output=r.text
                        # del my_remote["room_number"]
                        del my_remote["device"]
                        del my_remote["order"]
                    else:
                        speak_output="Which one do you want to turn on"
                else:
                    speak_output="Sorry, I could not find any such device. I have only access to the devices you have registered"
                    del my_remote["device"]
                    del my_remote["order"]
            else:
                speak_output="Kindly provide a room number"
        else:
            speak_output="Verify your number first. Say my number is and then speak your digits"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class numberDeviceIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("numberDevice")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        global my_remote,validate,home
        
        if(validate==True):
            if("room_number" in my_remote.keys() and "order" in my_remote.keys() and "device" in my_remote.keys()):
                names = handler_input.request_envelope.request.intent.slots
                devicenum = names["ordinal"].value
                devicetype = my_remote["device"] 
                # if(devicetype == "light"):
                #     devicetype="L"
                # elif(deviceName=="fan"):
                #     deviceName="F"
                # elif(deviceName=="television"):
                #     deviceName="T"
                # elif(deviceName=="geyser"):
                #     deviceName="G"
                # elif(deviceName=="air conditioner"):
                #     deviceName="A"
                speak_output=""
                device = [x for x,i in enumerate(home["equip"]) if(i==devicetype)]
                #for i in device:
                #   speak_output=speak_output+str(i)
                index = int(devicenum)-1
                indexT = device[index]
                deviceName = home["buttonno"][indexT]
                username = home["username"]
                order = my_remote["order"]
                room_number = my_remote["room_number"]
                r = requests.post("YOUR_API_LINK_HERE", data={'username': username, 'order': order, 'device':deviceName,'roomno':room_number})
                speak_output=r.text
                del my_remote["room_number"]
                del my_remote["device"]
                del my_remote["order"]
            else:
                speak_output="Kindly provide details first"
        else:
            speak_output="Verify your number first. Say my number is and then speak your digits"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class turnDeviceOffIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("turnDeviceOff")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        names = handler_input.request_envelope.request.intent.slots
        name = names["device"]
        deviceName = name.value
        if(deviceName=="light"):
            deviceName="L"
        elif(deviceName=="fan"):
            deviceName="F"
        elif(deviceName=="television"):
            deviceName="T"
        elif(deviceName=="geyser"):
            deviceName="G"
        elif(deviceName=="air conditioner"):
            deviceName="A"
        global my_remote,validate,home
        if(validate==True):
            my_remote.update({"device": deviceName})
            my_remote.update({"order": 'off'})
            if("room_number" in my_remote.keys()):
                room_number = my_remote["room_number"]
                username=home["username"]
                if(deviceName in home["equip"]):
                    deviceCount = home["equip"].count(deviceName)
                    if(deviceCount==1):
                        r = requests.post("YOUR_API_LINK_HERE", data={'username': username, 'order': 'off', 'device':deviceName,'roomno':room_number})
                        speak_output=r.text
                        del my_remote["room_number"]
                        del my_remote["device"]
                        del my_remote["order"]
                    else:
                        speak_output="Which one do you want to turn off"
        else:
            speak_output="Verify your number first. Say my number is and then speak your digits"
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(contactDetailsIntentHandler())
sb.add_request_handler(emailVerificationIntentHandler())
sb.add_request_handler(turnDeviceOnIntentHandler())
sb.add_request_handler(numberDeviceIntentHandler())
sb.add_request_handler(turnDeviceOffIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(roomInfoIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
