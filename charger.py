#!/usr/bin/env python
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
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.40.10'))
channel = connection.channel()

channel.queue_declare(queue='batt')
 
# discharge end voltage (empty)
 
dchg_end = 3.2
 
 
# iCharger modes of operation
mop = [None]*13
 
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
 
# configure the serial connections 
# change according to the ttyUSB assigned to the iCharger (dmesg)
 
ser = serial.Serial('/dev/ttyUSB0', baudrate=230400, timeout=5)
while 1:
    try:

        while 1:

            # ser.open()
            ser.isOpen()

            # MAIN #############################################################
            line = ser.readline().decode('UTF-8')

            print(line)

            if len(line) > 0:

                raw = line.split(';')
                length = len(raw)

                status = dict();
                status['mode'] = mop[int(raw[1])]
                status['input_voltage'] = float(raw[3])/1000
                status['battery_voltage'] = float(raw[4])/1000
                status['charge_current'] = int(raw[5])*10
                status['cell_voltages'] = list()

                for cell in range(6, length-5):
                    if raw[cell] != '0':
                        status['cell_voltages'].insert(cell-6,float(raw[cell])/1000)

                status['internal_temp'] = float(raw[length-4])/10
                status['external_temp'] = float(raw[length-3])/10
                status['total_charge'] = int(raw[length-2])

                message = json.dumps(status)
                channel.basic_publish(exchange='amq.fanout',
                                      routing_key='battery',
                                      body=message
                                      )

            else:
                print('timeout')

    except serial.SerialException as ex:

        print(ex.text)