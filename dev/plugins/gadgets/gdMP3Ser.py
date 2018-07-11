"""
Gadget Plugin for DFPlayer Mini and YX5300
Based on ???
"""
from com.Globals import *

import dev.Gadget as Gadget
from dev.GadgetSerial import PluginGadgetSerial as GS
import dev.Variable as Variable
import dev.Machine as Machine

#######
# Globals:

EZPID = 'gdMP3Ser'
PTYPE = PT_SENSOR
PNAME = 'MP3 Notification (serial)'
PINFO = '?'

#######

class PluginGadget(GS):
    """ TODO """

    def __init__(self, module):
        super().__init__(module, 10)   # 10 byte data packet
        self.param = {
            # must be params
            'NAME':PNAME,
            'ENABLE':False,
            'TIMER':0,
            'PORT':'',
            # instance specific params
            'TrigVar':'CMD.Notify',
            'Volume':30,
            }

# -----

    def init(self):
        super().init()

        if self._ser:
            self._ser.init(9600, 8, None, 1) # baud=9600 databits=8 parity=none stopbits=1

            self.send_command(0x09, 2)   # Storage Device = SD
            self.send_command(0x06, int(self.param['Volume']))   # Set volume
            self.send_command(0x03, 1)   # Play

# -----

    def exit(self):
        super().exit()

# -----

    def variables(self, news:dict):
        try:
            key = self.param['TrigVar']
            if key in news:
                val = news.get(key, 1)

                if type(val) is str:
                    if val.find(':') > 0:
                        val = val.split(':', 1)
                        ndir = int(val[0]) & 0xFF
                        file = int(val[1]) & 0xFF
                        val = ndir << 8 | file
                        self.send_command(0x0F, val)   # Play Folder
                    else:
                        val = int(val)
                        self.send_command(0x03, val)   # Play Index
                if type(val) is int:
                    self.send_command(0x03, val)   # Play Index
        except:
            pass

# -----

    def timer(self, prepare:bool):
        while self.process():
            pass
            #print(self.value, self.unit, self.form)
            #key = self.param['RespVar']
            #source = self.param['NAME']
            #Variable.set(key, self.value, source)

# =====

    def is_valid(self):
        if self.data[0] != 0x7E:   # Starting
            return False
        if self.data[1] != 0xFF:   # Version
            return False
        if self.data[2] != 0x06:   # Len
            return False
        if self.data[9] != 0xEF:   # End
            return False
        #sum = 0
        #for i in range(1, 8):
        #    sum -= self.data[i]
        #if self.data[xxx] != (sum & 0xFF):    # Checksum
        #    return False
        return True

# -----

    def interpret(self):
        self._remove_data(self.packet_size)

# =====

    def send_command(self, cmd:int, val:int):
        len = 10   # 8 or 10
        buf = bytearray(len)

        buf[0] = 0x7E
        buf[1] = 0xFF
        buf[2] = 0x06
        buf[3] = cmd
        buf[4] = 0
        buf[5] = (val >> 8) & 0xFF
        buf[6] = val & 0xFF
        buf[7] = 0xEF

        if len == 10:
            sum = 0
            for i in range(1, 7):
                sum -= buf[i]
            buf[7] = (sum >> 8) & 0xFF
            buf[8] = sum & 0xFF
            buf[9] = 0xEF

        if self._ser:
            self._ser.write(buf)

#######