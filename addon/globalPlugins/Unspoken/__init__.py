import os
import sys
import globalPluginHandler
import NVDAObjects
import config
import speech
import controlTypes
import logHandler as lh
from controlTypes import OutputReason
from .camlorn_audio import *


AUDIO_WIDTH = 10.0 # Width of the audio display.
AUDIO_DEPTH = 5.0 # Distance of listener from display.

UNSPOKEN_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
UNSPOKEN_SOUNDS_PATH = os.path.join(UNSPOKEN_ROOT_PATH, "sounds")

sound_files={
controlTypes.ROLE_CHECKBOX : "checkbox.wav",
controlTypes.ROLE_RADIOBUTTON : "radiobutton.wav",
controlTypes.ROLE_STATICTEXT : "editabletext.wav",
controlTypes.ROLE_EDITABLETEXT : "editabletext.wav",
controlTypes.ROLE_BUTTON : "button.wav",
controlTypes.ROLE_MENUBAR : "menuitem.wav",
controlTypes.ROLE_MENUITEM : "menuitem.wav",
controlTypes.ROLE_MENU : "menuitem.wav",
controlTypes.ROLE_COMBOBOX : "combobox.wav",
controlTypes.ROLE_LISTITEM : "listitem.wav",
controlTypes.ROLE_GRAPHIC : "icon.wav",
controlTypes.ROLE_LINK : "link.wav",
controlTypes.ROLE_TREEVIEWITEM : "treeviewitem.wav",
controlTypes.ROLE_TAB : "tab.wav",
controlTypes.ROLE_TABCONTROL : "tab.wav",
controlTypes.ROLE_SLIDER : "slider.wav",
controlTypes.ROLE_DROPDOWNBUTTON : "combobox.wav",
controlTypes.ROLE_CLOCK: "clock.wav",
controlTypes.ROLE_ANIMATION : "icon.wav",
controlTypes.ROLE_ICON : "icon.wav",
controlTypes.ROLE_IMAGEMAP : "icon.wav",
controlTypes.ROLE_RADIOMENUITEM : "radiobutton.wav",
controlTypes.ROLE_RICHEDIT : "editabletext.wav",
controlTypes.ROLE_SHAPE : "icon.wav",
controlTypes.ROLE_TEAROFFMENU : "menuitem.wav",
controlTypes.ROLE_TOGGLEBUTTON : "checkbox.wav",
controlTypes.ROLE_CHART : "icon.wav",
controlTypes.ROLE_DIAGRAM : "icon.wav",
controlTypes.ROLE_DIAL : "slider.wav",
controlTypes.ROLE_DROPLIST : "combobox.wav",
controlTypes.ROLE_MENUBUTTON : "button.wav",
controlTypes.ROLE_DROPDOWNBUTTONGRID : "button.wav",
controlTypes.ROLE_HOTKEYFIELD : "editabletext.wav",
controlTypes.ROLE_INDICATOR : "icon.wav",
controlTypes.ROLE_SPINBUTTON : "slider.wav",
controlTypes.ROLE_TREEVIEWBUTTON: "button.wav",
controlTypes.ROLE_DESKTOPICON : "icon.wav",
controlTypes.ROLE_PASSWORDEDIT : "editabletext.wav",
controlTypes.ROLE_CHECKMENUITEM : "checkbox.wav",
controlTypes.ROLE_SPLITBUTTON : "splitbutton.wav",
}

sounds = dict() 

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		globalPluginHandler.GlobalPlugin.__init__(self, *args, **kwargs)

		init_camlorn_audio()

		for key in sound_files:
			sounds[key] = Sound3D(os.path.join(UNSPOKEN_SOUNDS_PATH, sound_files[key]))
			sounds[key].set_rolloff_factor(0)
			if sounds[key].get_length() <= 0: pass
			else: pass
		self._room_reverb = Reverb()
		self._room_reverb.set_reverb_density(0)
		self._room_reverb.set_Decay_time(0.4)
		self._room_reverb.set_gain(1)
		self._room_reverb.set_reflections_gain(0.4)
		self._room_reverb.set_late_reverb_gain(0)

		self._NVDA_getSpeechTextForProperties = speech.speech.getPropertiesSpeech
		speech.speech.getPropertiesSpeech = self._hook_getSpeechTextForProperties

		self._previous_mouse_object = None


	def _hook_getSpeechTextForProperties(self, reason: OutputReason = OutputReason.QUERY, *args, **kwargs):
		#if config.conf["virtualBuffers"]["autoFocusFocusableElements"]:
		role = kwargs.get('role', None)
#		sa=kwargs
		#lh.log.info(str(sa))
		isOffScreen=16777216 in kwargs.get('states', [])
		if role:
			if 'role' in kwargs and role in sounds and not isOffScreen:
				del kwargs['role']
				clas=type("nobject",(object,),{"role":role, "location":None})
				self.play_object(clas())
		return self._NVDA_getSpeechTextForProperties(reason, *args, **kwargs)

	def play_object(self, obj):
		
		global AUDIO_WIDTH, AUDIO_DEPTH
		role = obj.role
		if role in sounds:
			# Get coordinate bounds of desktop.
			desktop = NVDAObjects.api.getDesktopObject()
			desktop_max_x = desktop.location[2]
			desktop_max_y = desktop.location[3]
			desktop_aspect = float(desktop_max_y) / float(desktop_max_x)
			# Get location of the object.
			if obj.location != None:
				# Object has a location. Get its center.
				obj_x = obj.location[0] + (obj.location[2] / 2.0)
				obj_y = obj.location[1] + (obj.location[3] / 2.0)
			else:
				# Objects without location are assumed in the center of the screen.
				obj_x = desktop_max_x / 2.0
				obj_y = desktop_max_y / 2.0
			position_x = (obj_x / desktop_max_x) * (AUDIO_WIDTH * 2) - AUDIO_WIDTH
			position_y = (obj_y / desktop_max_y) * (desktop_aspect * AUDIO_WIDTH * 2) - (desktop_aspect * AUDIO_WIDTH)
			position_y *= -1
			sounds[role].set_position(position_x, position_y, AUDIO_DEPTH * -1)
			sounds[role].play()

	def event_gainFocus(self, obj, nextHandler):
		if obj.treeInterceptor is  None :
			self.play_object(obj)
		nextHandler()

	def event_becomeNavigatorObject(self, obj, nextHandler, isFocus=False):
		if obj.treeInterceptor is  None :
			self.play_object(obj)

		nextHandler()

	def event_mouseMove(self, obj, nextHandler, x, y):
		if obj != self._previous_mouse_object:
			self._previous_mouse_object = obj
			self.play_object(obj)
		nextHandler()




def _hook_getSpeechTextForProperties(reason, *args, **kwargs):
	role = kwargs.get('role', None)
	#sa=locals()
	#lh.log.info(sa)
	if role:
		if 'role' in kwargs and role in sounds:
			del kwargs['role']
			clas=type("nobject",(object,),{"role":role, "location":None})
			self.play_object(clas())
	return self._NVDA_getSpeechTextForProperties(reason, *args, **kwargs)
