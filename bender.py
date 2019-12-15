# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# project: pRodriguezAssistant
import subprocess
import time
from threading import Timer
from speech_recognizer import PsLiveRecognizer
from answer_player import AnswerPlayer
from music_player import MusicPlayer
from backlight_control import BacklightControl
from backlight_control import BackLightCommands

audio_lang = 'ru'
recognize_lang ='ru'
sleepEnabled = True

BacklightControl.backlightEnabled = True

fsmState = 1
isSleeping = False
m_player = MusicPlayer()
a_player = AnswerPlayer(audio_lang)
speech_recognizer = PsLiveRecognizer('./resources/', recognize_lang, 'bender')

SLEEPING_TIME = 600.0

tr_start_ru_en  = {
    u'бендер': 'bender',
    u'привет бендер': 'hi bender',
    u'эй бендер': 'hi bender',
    u'бендер стоп': 'bender stop',
    u'привет бендер стоп': 'bender stop',
    u'эй бендер стоп': 'bender stop'
}

tr_conversation_ru_en = {
    u'включи музыкальный плеер': 'enable music player',
    u'отключи музыкальный плеер': 'disable music player',
    u'следующий трек': 'next song',
    u'следующий трэк': 'next song',
    u'следующая песня': 'next song',
    u'спой песню': 'sing a song',
    u'конфигурация': 'configure',
    u'откуда ты': 'where are you from',
    u'где ты родился': 'where were you born',
    u'когда ты родился': 'when were you born',
    u'дата рождения': 'when were you born',
    u'какое твоё любимое животное': 'your favorite animal',
    u'какой твой любимый зверь': 'your favorite animal',
    u'кто ты': 'who are you',
    u'как ты': 'how are you',
    u'как поживаешь': 'how are you',
    u'магнит': 'magnet',
    u'хороший новый свитер': 'new sweater',
    u'выключение': 'shutdown',
    u'стоп': 'stop',
    u'пока': 'stop'
}

tr_configuration_ru_en = {
    u'сон': 'sleep',
    u'засыпание': 'sleep',
    u'выход': 'exit',
    u'закрой': 'exit',
    u'включи': 'enable',
    u'выключи': 'disable',
    u'в': 'to',
    u'магнит': 'magnet'
}

def main():
    global fsmState
    global m_player
    global speech_recognizer

    kill_pocketsphinx()
    m_player.kill_player()

    BacklightControl.backlight(BackLightCommands.TEETH_OFF)
    BacklightControl.backlight(BackLightCommands.EYES_OFF)
    time.sleep(0.15)
    BacklightControl.backlight(BackLightCommands.EYES_ON)

    p = subprocess.Popen(["%s" % speech_recognizer.cmd_line], shell=True, stdout=subprocess.PIPE)
    print(["%s" % speech_recognizer.cmd_line])

    while True:
        if (fsmState == 1):
            if find_keyphrase(p):
                conversation_mode(p)
            #elif (fsmState == 2):
            #    configuration_mode(p)
        elif (fsmState == 4):
            break
        else:
            continue

    kill_pocketsphinx()
    m_player.send_command("exit")
    BacklightControl.backlight(BackLightCommands.EYES_OFF)

def sleep_timeout():
    global isSleeping
    global a_player
    a_player.play_answer('kill all humans')
    isSleeping = True

def find_keyphrase(p):
    global fsmState
    global sleepEnabled
    global aplayer

    while True:
        keyphrase_found = False
        print('Start mode:')

        current_milli_time = int(round(time.time() * 1000))
        retcode = p.returncode
        utt = p.stdout.readline().decode('utf8').rstrip().lower()
        print('utterance = ' + utt)

        if speech_recognizer.lang == 'ru':
            try:
                utt = tr_start_ru_en[utt]
            except KeyError as e:
                utt = 'unrecognized'
                #raise ValueError('Undefined key to translate: {}'.format(e.args[0]))

        if ('bender' in utt):
            m_player.send_command('status')
            if m_player.musicIsPlaying:
                if('stop' in utt):
                    m_player.send_command('pause')
                    keyphrase_found = True
            else:
                if (('hi' in utt) or ('hey' in utt) or ('hello' in utt)):
                    command = 'hey bender ' + str(current_milli_time % 3)
                    a_player.play_answer(command)
                keyphrase_found = True

        time.sleep(0.15)
        if keyphrase_found:
            BacklightControl.backlight(BackLightCommands.TEETH_ON_OK)
            return keyphrase_found

def conversation_mode(p):
    global fsmState
    global sleepEnabled
    global isSleeping
    global a_player

    while True:
        print ('Conversation mode:')
        sleepTimer = None

        if sleepEnabled:
            sleepTimer = Timer(SLEEPING_TIME, sleep_timeout)
            sleepTimer.start()

        current_milli_time = int(round(time.time() * 1000))
        retcode = p.returncode
        utt = p.stdout.readline().decode('utf8').rstrip().lower()
        print('utterance = ' + utt)

        if speech_recognizer.lang == 'ru':
            try:
                utt = tr_conversation_ru_en[utt]
            except KeyError as e:
                utt = 'unrecognized'
                #raise ValueError('Undefined key to translate: {}'.format(e.args[0]))

        if sleepEnabled:
            if utt != None and sleepTimer != None:
                sleepTimer.cancel()
            if utt != None and isSleeping:
                utt = 'wake up'
                isSleeping = False

        if 'shutdown' in utt:
            command = 'shutdown'
            fsmState = 4
        #elif ('exit' in utt) or ('quit' in utt) or ('stop' in utt):
        #    command = 'exit'
        #    fsmState = 0
        elif ('sing' in utt) and ('song' in utt):
            command = 'sing'
        elif 'who are you' in utt:
            command = 'who are you ' + str(current_milli_time % 2)
        elif 'how are you' in utt:
            command = 'how are you'
        elif ('where are you from' in utt) or ('where were you born' in utt):
            command = 'birthplace'
        elif 'when were you born' in utt:
            command = 'birthdate'
        elif 'your favorite animal' in utt:
            command = 'animal'
        elif ('bender' in utt) and (('hi' in utt) or ('hey' in utt) or ('hello' in utt)):
            command = 'hey bender ' + str(current_milli_time % 3)
        elif 'magnet' in utt:
            command = 'magnet ' + str(current_milli_time % 2)
        elif 'new sweater' in utt:
            command = 'new sweater'
        elif ('wake up' in utt) or ('awake' in utt):
            command = 'wake up'
        elif ('configuration' in utt) or ('configure' in utt):
            command = 'configuration'
            #fsmState = 2
        elif ('enable music player' in utt):
            command = 'no audio'
            m_player.send_command('start')
            time.sleep(1)
        elif ('disable music player' in utt):
            command = 'no audio'
            m_player.send_command('stop')
        elif ('next song' in utt):
            command = 'no audio'
            m_player.send_command('next')
        else:
            command = 'unrecognized'

        if command != 'no audio':
            a_player.play_answer(command)
        else:
            BacklightControl.backlight(BackLightCommands.TEETH_OFF)

        if command != 'shutdown':
            m_player.send_command('status')
            if m_player.musicIsPlaying:
                m_player.send_command('resume')

        time.sleep(0.15)
        break

def configuration_mode(p):
    global fsmState
    global a_player

    while True:
        print('Configuration mode:')

        if sleepEnabled:
            sleepTimer = Timer(SLEEPING_TIME, sleep_timeout)
            sleepTimer.start()

        current_milli_time = int(round(time.time() * 1000))
        retcode = p.returncode
        utt = p.stdout.readline().decode('utf8').rstrip().lower()
        print('utterance = ' + utt)

        if speech_recognizer.lang == 'ru':
            try:
                utt = tr_configuration_ru_en[utt]
            except KeyError as e:
                utt = 'unrecognized'
                #raise ValueError('Undefined key to translate: {}'.format(e.args[0]))

        if sleepEnabled:
            if utt != None and sleepTimer != None:
                sleepTimer.cancel()
            if utt != None and isSleeping:
                utt = 'wake up'
                isSleeping = False

        if ('bender' in utt) and (('hi' in utt) or ('hey' in utt) or ('hello' in utt)):
            command = 'hey bender ' + str(current_milli_time % 3)
            a_player.play_answer(command)
            fsmState = 1
        if ('exit' in utt) or ('quit' in utt) or ('stop' in utt):
            command = 'exit'
            #fsmState = 0
        elif ('set' in utt):
            command = 'set'
            #TODO: implement set logic
        elif('enable' in utt):
            command = 'enable'
            #TODO: implement enable logic
        elif('disable' in utt):
            command = 'disable'
            #TODO: implement disable logic
        else:
            command = 'unrecognized'

        a_player.play_answer(command)
        time.sleep(0.15)
        if (retcode is not None) or (fsmState != 2):
            break

def kill_pocketsphinx():
    kill_exe = 'killall -s SIGKILL pocketsphinx_co'
    p = subprocess.Popen(["%s" % kill_exe], shell=True, stdout=subprocess.PIPE)
    code = p.wait()

main()
