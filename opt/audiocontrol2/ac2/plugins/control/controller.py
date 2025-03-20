'''
Copyright (c) 2019 Modul 9/HiFiBerry
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
from threading import Thread

from ac2.constants import STATE_PLAYING, STATE_PAUSED, STATE_STOPPED, STATE_UNDEF


class Controller( Thread ):
    '''
    Main class for a controller that can handle player and/or volume
    control.
    It will run as a background thread
    '''

    def __init__( self ):
        super().__init__()
        self.volumecontrol = None
        self.playercontrol = None
        self.playerstate = STATE_UNDEF
        self.name = "generic controller"

    def set_volume_control( self, volumecontrol ):
        self.volumecontrol = volumecontrol

    def set_player_control( self, playercontrol ):
        self.playercontrol = playercontrol
        
    def update_playback_state(self, state):
        self.playerstate = state

    def __str__(self):
        return self.name
