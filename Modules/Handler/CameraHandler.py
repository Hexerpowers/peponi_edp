import socket
import time
from threading import Thread


class CameraHandler:

    def __init__(self, st, lg):
        self.st = st
        self.lg = lg

        self.enabled = False
        self.mode = False
        self.pir_mode = 0
        self.current_zoom = 1
        self.zoom_timestamp = 0

        self.zoom_time_const = 30 / 7

        self.prev_vals = {
            "cam_pitch": 0,
            "cam_zoom": 0,
        }

        try:
            self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock_out.settimeout(1)
            self.sock_out.connect((self.st.config['network']['default_camera_address'], 5760))
            self.sock_out.settimeout(None)
            self.enabled = True
        except Exception:
            self.lg.init('Камера недоступна.')

        self.camera_communicate = Thread(target=self.camera_communicate, daemon=True, args=())

    def start(self):
        self.camera_communicate.start()
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

            if self.st.get_signals()['main_cam_mode']:
                self.change_mode()
                self.st.set_signal('main_cam_mode', False)

            if int(self.st.get_runtime()['pir_cam_mode']) != self.pir_mode:
                self.change_pir_mode(int(self.st.get_runtime()['pir_cam_mode']))

    def pitch_up(self):
        self.sock_out.sendall(b'\xff\x01\x00\x08\x00\x80\x89')

    def pitch_down(self):
        self.sock_out.sendall(b'\xff\x01\x00\x10\x00\x80\x91')

    def zoom_in(self):
        self.zoom_timestamp = round(time.time(), 2)
        self.sock_out.sendall(b'\xff\x01\x00\x40\x04\x00\x45')

    def zoom_out(self):
        self.zoom_timestamp = round(time.time(), 2)
        self.sock_out.sendall(b'\xff\x01\x00\x20\x04\x00\x25')

    def pitch_stop(self):
        self.sock_out.sendall(b'\xff\x01\x00\x00\x00\x00\x01')

    def zoom_stop(self):
        self.sock_out.sendall(b'\xff\x01\x00\x60\x00\x00\x61')
        zoom_factor = round(time.time() - self.zoom_timestamp, 2)
        if zoom_factor > 7:
            zoom_factor = 7
        if self.prev_vals['cam_zoom'] == 1:
            self.current_zoom += round(zoom_factor*self.zoom_time_const)
        if self.prev_vals['cam_zoom'] == -1:
            self.current_zoom -= round(zoom_factor*self.zoom_time_const)

        if self.current_zoom > 30:
            self.current_zoom = 30
        if self.current_zoom < 1:
            self.current_zoom = 1

        if self.current_zoom > 23:
            self.sock_out.sendall(b'\xff\x01\x17\x00\x03\x00\x1b')
        elif self.current_zoom > 14:
            self.sock_out.sendall(b'\xff\x01\x17\x00\x02\x00\x1a')
        elif self.current_zoom > 7:
            self.sock_out.sendall(b'\xff\x01\x17\x00\x01\x00\x19')
        else:
            self.sock_out.sendall(b'\xff\x01\x17\x00\x00\x00\x18')

    def take_picture(self):
        self.sock_out.sendall(b'\xff\x01\x12\x00\x00\x00\x13')

    def change_pir_mode(self, mode):
        mode = int(mode)
        if mode == 0:
            self.sock_out.sendall(b'\xff\x01\x15\x00\x00\x00\x16')
        elif mode == 1:
            self.sock_out.sendall(b'\xff\x01\x15\x00\x01\x00\x17')
        elif mode == 2:
            self.sock_out.sendall(b'\xff\x01\x15\x00\x02\x00\x18')
        else:
            self.sock_out.sendall(b'\xff\x01\x15\x00\x03\x00\x19')
        self.pir_mode = mode

    def change_mode(self):
        if self.mode:
            self.sock_out.sendall(b'\xff\x01\x14\x00\x00\x00\x15')
        else:
            self.sock_out.sendall(b'\xff\x01\x14\x00\x01\x00\x16')
        self.mode = not self.mode

    def __del__(self):
        self.sock_out.close()
