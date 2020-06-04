#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
########################################################################
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.
#
########################################################################
 
import os
import sys
import time
import serial
import json
import paho.mqtt.client as mqtt
import logging

logging.basicConfig(filename='/var/tmp/charger.log', filemode='w', level=logging.DEBUG)

mode = 0 

client = mqtt.Client()

def set_mode(new_mode):

    print('New mode: {0}'.format(mode))
    global mode 
    # if new_mode != mode:
    mode = new_mode
    logging.info('New mode: {0}'.format(mode))
    client.publish('battery_charger/mode_string', mop[mode], 2, True)    
    client.publish('battery_charger/mode_int', mode, 2, True)    

charger_status = [None]*4

charger_status[0] = 'No Charger Connected'
charger_status[1] = 'Charger Idle'
charger_status[2] = 'Charger Active'
 
# discharge end voltage (empty)
 
dchg_end = 3.2
 
 
# iCharger modes of operation
mop = [None]*15
 
mop[0] = "Startup"
mop[1] = "Charging"
mop[2] = "Discharging"
mop[3] = "Monitor"
mop[4] = "Waiting"
mop[5] = "Motor burn-in"
mop[6] = "Finished"
mop[7] = "Error"
mop[8] = "LIxx trickle"
mop[9] = "NIxx trickle"
mop[10] = "Foam cut"
mop[11] = "Info"
mop[12] = "External-discharging"
mop[13] = "Not Connected"
mop[14] = "Idle"
 
#cell_numbers
cells = dict()
cells[6] = 'cell_1_voltage'
cells[7] = 'cell_2_voltage'
cells[8] = 'cell_3_voltage'
cells[9] = 'cell_4_voltage'
cells[10] = 'cell_5_voltage'
cells[11] = 'cell_6_voltage'

# configure the serial connections 
# change according to the ttyUSB assigned to the iCharger (dmesg)
 
client.connect('ssessner.noip.us', keepalive=30)

while 1:

    state = dict()

    try:

        ser = serial.Serial('/dev/charger', baudrate=230400, timeout=15)

        # ser.open()
        ser.isOpen()

        # MAIN #############################################################
        line = ser.readline().decode('UTF-8')

        if len(line) > 0:

            logging.debug(line)
            raw = line.split(';')
            length = len(raw)
            logging.info('Length: {}'.format(length))

            set_mode(int(raw[1]))
            state['input_voltage'] = float(raw[3]) / 1000
            state['pack_voltage'] = float(raw[4]) / 1000
            state['charge_current'] = int(raw[5]) * 10

            for cell in range(6, length-5):
                if raw[cell] != '0':
                    state[cells[cell]] = float(raw[cell]) / 1000

            state['internal_temp'] = round((float(raw[length - 4]) / 10)*9/5 + 32, 0)
            state['external_temp'] = round((float(raw[length - 3]) / 10)*9/5 + 32, 0)
            state['total_charge'] = int(raw[length - 2])

            for key in state.keys():
                logging.debug('Sending {0} to topic battery_charger/{1}'.format(state[key], key))
                client.publish('battery_charger/{0}'.format(key), state[key])

        else:
            logging.debug('Empty Serial Line')
            set_mode(14)

    except serial.SerialException as ex:
        logging.error(ex)
        set_mode(13)
        time.sleep(5)

