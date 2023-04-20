import socket
from threading import Thread
import time


class CameraHandler:

    def __init__(self, st, lg):
        self.st = st
        self.lg = lg

        self.enabled = False
        self.prev_vals = {
            "cam_pitch": 0,
            "cam_zoom": 0,
        }
        try:
            self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock_out.settimeout(2)
            self.sock_out.connect(('192.168.88.110', 5760))
            self.sock_out.settimeout(None)
            self.enabled = True
        except:
            self.lg.error('Камера недоступна')

        self.camera_msg = Thread(target=self.camera_communicate, daemon=True, args=())

    def start(self):
        self.camera_msg.start()
        return self

    def camera_communicate(self):
        while self.enabled:
            time.sleep(0.01)
            if int(self.st.get_move()['cam_pitch']) == 1:
                if self.prev_vals['cam_pitch'] != 1:
                    if self.prev_vals['cam_pitch'] == 0:
                        self.pitch_up()
                        self.prev_vals['cam_pitch'] = 1
                    if self.prev_vals['cam_pitch'] == -1:
                        self.pitch_stop()
                        self.prev_vals['cam_pitch'] = 0

            if int(self.st.get_move()['cam_pitch']) == -1:
                if self.prev_vals['cam_pitch'] != -1:
                    if self.prev_vals['cam_pitch'] == 0:
                        self.pitch_down()
                        self.prev_vals['cam_pitch'] = -1
                    if self.prev_vals['cam_pitch'] == 1:
                        self.pitch_stop()
                        self.prev_vals['cam_pitch'] = 0

            if int(self.st.get_move()['cam_pitch']) == 0:
                if self.prev_vals['cam_pitch'] != 0:
                    self.pitch_stop()
                    self.prev_vals['cam_pitch'] = 0

            if int(self.st.get_move()['cam_zoom']) == 1:
                if self.prev_vals['cam_zoom'] != 1:
                    if self.prev_vals['cam_zoom'] == 0:
                        self.zoom_in()
                        self.prev_vals['cam_zoom'] = 1
                    if self.prev_vals['cam_zoom'] == -1:
                        self.zoom_stop()
                        self.prev_vals['cam_zoom'] = 0

            if int(self.st.get_move()['cam_zoom']) == -1:
                if self.prev_vals['cam_zoom'] != -1:
                    if self.prev_vals['cam_zoom'] == 0:
                        self.zoom_out()
                        self.prev_vals['cam_zoom'] = -1
                    if self.prev_vals['cam_zoom'] == 1:
                        self.zoom_stop()
                        self.prev_vals['cam_zoom'] = 0

            if int(self.st.get_move()['cam_zoom']) == 0:
                if self.prev_vals['cam_zoom'] != 0:
                    self.zoom_stop()
                    self.prev_vals['cam_zoom'] = 0

            if self.st.get_signals()['photo']:
                self.take_picture()
                self.st.set_signal('photo', False)

    def pitch_up(self):
        self.sock_out.sendall(b'\xff\x01\x00\x08\x00\xff\x08')

    def pitch_down(self):
        self.sock_out.sendall(b'\xff\x01\x00\x10\x00\xff\x10')

    def zoom_in(self):
        self.sock_out.sendall(b'\xff\x01\x00\x40\x04\x00\x45')

    def zoom_out(self):
        self.sock_out.sendall(b'\xff\x01\x00\x20\x04\x00\x25')

    def pitch_stop(self):
        self.sock_out.sendall(b'\xff\x01\x00\x00\x00\x00\x01')

    def zoom_stop(self):
        self.sock_out.sendall(b'\xff\x01\x00\x60\x00\x00\x61')

    def take_picture(self):
        self.sock_out.sendall(b'\xff\x01\x12\x00\x00\x00\x13')

    def __del__(self):
        self.sock_out.close()
