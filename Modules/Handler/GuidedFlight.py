import math
import time
from threading import Thread

from dronekit import VehicleMode, LocationGlobalRelative
from pymavlink import mavutil


class GuidedFlight:
    def __init__(self, st, lg, ve):
        self.st = st
        self.lg = lg

        self.state = 0
        self.tele_ctr = 0

        self.target_yaw = 0

        self.power_wait = True
        self.init_wait = True

        self.runnable = Thread(target=self.run, daemon=True, args=())
        self.vehicle = ve

    def start(self):
        self.runnable.start()

    def get_target_yaw(self):
        return self.target_yaw

    def move_3d(self, velocity_x, velocity_y, velocity_z):
        msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
            0,
            0, 0,
            mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,
            0b0000111111000111,
            0, 0, 0,
            velocity_x, velocity_y, -velocity_z,
            0, 0, 0,
            0, 0)
        self.vehicle.send_mavlink(msg)

    def move_yaw(self, heading, relative=False):
        if relative:
            is_relative = 1
        else:
            is_relative = 0
        msg = self.vehicle.message_factory.command_long_encode(
            0, 0,
            mavutil.mavlink.MAV_CMD_CONDITION_YAW,
            0,
            heading,
            0,
            0,
            is_relative,
            0, 0, 0)
        self.vehicle.send_mavlink(msg)
        self.vehicle.flush()

    def set_state(self, state):
        self.state = state
        self.st.drop_signals()
        self.st.set_copter_state(state)

    def power_check(self, level):
        if int(self.st.config['general']['use_power_telemetry']) == 1 and self.st.get_runtime()['power_onboard'] == 0:
            if self.st.get_battery_charge() >= level:
                return True
            else:
                return False
        else:
            return True

    def run(self):
        self.lg.init("Подготовка к взлёту...")
        while True:
            time.sleep(0.01)

            # Состояние 0 - Подготовка
            if self.state == 0:
                self.vehicle.armed = False
                if self.st.get_runtime()['comm_ok']:
                    if self.power_check(60):
                        if self.vehicle.is_armable:
                            self.power_wait = True
                            self.init_wait = True
                            self.lg.log("Взлёт разрешён.")
                            self.set_state(1)
                            continue
                    else:
                        if self.power_wait:
                            self.lg.log("Недостаточное напряжение питания.")
                        self.power_wait = False
                        time.sleep(0.5)
                    while not self.vehicle.is_armable:
                        if self.init_wait:
                            self.lg.log("Ожидание синхронизации контроллера...")
                        self.init_wait = False
                        time.sleep(0.5)

            # Состояние 1 - Арминг
            if self.state == 1:
                if not self.power_check(30):
                    self.set_state(0)
                if self.st.get_signals()['takeoff']:
                    if self.vehicle.parameters['LAND_SPEED'] != 31:
                        self.vehicle.parameters['LAND_SPEED'] = 31
                    if self.vehicle.parameters['LAND_SPEED_HIGH'] != 100:
                        self.vehicle.parameters['LAND_SPEED_HIGH'] = 100
                    self.lg.log("Получена команда на взлёт.")
                    self.vehicle.mode = VehicleMode("GUIDED")
                    self.vehicle.armed = True
                    self.lg.log("Ожидание готовности...")
                    timeout = 0
                    while not self.vehicle.armed:
                        time.sleep(0.1)
                        timeout += 0.1
                        if timeout >= 5:
                            self.lg.error("Ошибка, устройство не готово к полёту.")
                            self.set_state(0)
                            break
                    if self.state != 1:
                        continue
                    self.lg.log("Подготовка завершена.")
                    time.sleep(1)
                    self.set_state(2)

            # Состояние 2 - Взлёт на указанную высоту
            if self.state == 2:
                self.lg.log("Ожидание взлёта...")
                time.sleep(1)
                self.vehicle.simple_takeoff(2)
                while True:
                    if not self.power_check(30):
                        self.set_state(0)
                        break
                    if not self.st.get_runtime()['comm_ok']:
                        self.set_state(9)
                        break
                    if self.st.get_signals()['stop']:
                        self.set_state(8)
                        break
                    if self.st.get_signals()['land']:
                        self.set_state(4)
                        break
                    time.sleep(0.1)
                    if self.vehicle.location.global_relative_frame.alt >= 1:
                        break
                if self.state != 2:
                    continue
                a_location = LocationGlobalRelative(self.vehicle.location.global_relative_frame.lat,
                                                    self.vehicle.location.global_relative_frame.lon, 2)
                self.vehicle.simple_goto(a_location)
                time.sleep(1)
                self.move_yaw(0)
                self.move_3d(0, 0, 0)
                self.lg.log("Ожидание выхода на высоту...")
                while True:
                    if not self.power_check(30):
                        self.set_state(7)
                        break
                    if not self.st.get_runtime()['comm_ok']:
                        self.set_state(9)
                        break
                    if self.st.get_signals()['stop']:
                        self.set_state(8)
                        break
                    if self.st.get_signals()['land']:
                        self.set_state(4)
                        break
                    if self.vehicle.location.global_relative_frame.alt >= float(
                            self.st.get_runtime()['target_alt']) * 0.98:
                        self.lg.log("Выход на высоту завершён.")
                        self.lg.log("Режим: удержание положения.")
                        self.set_state(3)
                        break

                    move = self.st.get_move()

                    if int(move['yaw']) == 1:
                        self.target_yaw += 0.1
                    elif int(move['yaw']) == -1:
                        self.target_yaw -= 0.1

                    if self.target_yaw > 360:
                        self.target_yaw = 0
                    if self.target_yaw < 0:
                        self.target_yaw = 360

                    self.move_3d(float(move['x']), float(move['y']), float(self.st.get_runtime()['takeoff_speed']))
                    self.move_yaw(math.ceil(self.target_yaw))
                    time.sleep(0.1)

            # Состояние 3 - Автоматический полёт
            if self.state == 3:
                if not self.power_check(30):
                    self.set_state(7)
                    continue
                if not self.st.get_runtime()['comm_ok']:
                    self.set_state(9)
                    continue
                if self.st.get_signals()['land']:
                    self.set_state(4)
                    continue
                if self.st.get_signals()['stop']:
                    self.set_state(8)
                    continue
                move = self.st.get_move()
                move_z = 0

                if int(move['yaw']) == 1:
                    self.target_yaw += 0.1
                elif int(move['yaw']) == -1:
                    self.target_yaw -= 0.1

                if self.target_yaw > 360:
                    self.target_yaw = 0
                if self.target_yaw < 0:
                    self.target_yaw = 360

                if (self.vehicle.location.global_relative_frame.alt - float(self.st.get_runtime()['target_alt'])) > 1:
                    move_z = -float(self.st.get_runtime()['takeoff_speed'])

                if (self.vehicle.location.global_relative_frame.alt - float(self.st.get_runtime()['target_alt'])) < -1:
                    move_z = float(self.st.get_runtime()['takeoff_speed'])

                self.move_3d(float(move['x']), float(move['y']), move_z)
                self.move_yaw(math.ceil(self.target_yaw))

            # Состояние 4 - Посадка
            if self.state == 4:
                self.lg.log("Получена команда на посадку.")
                self.vehicle.mode = VehicleMode("LAND")
                while True:
                    if not self.st.get_runtime()['comm_ok']:
                        self.set_state(9)
                        break
                    if self.st.get_signals()['stop']:
                        self.set_state(8)
                        break
                    if self.vehicle.location.global_relative_frame.alt <= 2:
                        time.sleep(2)
                        self.lg.log("Посадка завершена.")
                        self.set_state(0)
                        break
                    time.sleep(0.1)

            # Состояние 7 - Посадка по причине потери питания
            if self.state == 7:
                self.lg.error("Низкий уровень напряжения, посадка.")
                self.move_3d(0, 0, 0)
                self.vehicle.mode = VehicleMode("LAND")
                while True:
                    if self.vehicle.location.global_relative_frame.alt <= 2:
                        time.sleep(2)
                        self.lg.log("Посадка завершена.")
                        self.set_state(0)
                        break
                    time.sleep(0.1)

            # Состояние 8 - Экстренная остановка
            if self.state == 8:
                self.lg.error("Получена команда на остановку.")
                self.move_3d(0, 0, 0)
                self.vehicle.mode = VehicleMode("BRAKE")
                while True:
                    if self.st.get_signals()['land']:
                        self.set_state(4)
                        break
                    if self.st.get_signals()['takeoff']:
                        self.vehicle.mode = VehicleMode("GUIDED")
                        self.set_state(2)
                        break
                    time.sleep(0.1)

            # Состояние 9 - Ошибка связи
            if self.state == 9:
                self.lg.error("Ошибка связи, посадка.")
                self.move_3d(0, 0, 0)
                self.vehicle.parameters['RTL_ALT'] = float(self.st.get_runtime()['return_alt'])
                self.vehicle.mode = VehicleMode("LAND")
                while True:
                    if self.st.get_runtime()['comm_ok']:
                        self.set_state(3)
                        continue
                    if self.st.get_signals()['stop']:
                        self.set_state(8)
                        break
                    if self.vehicle.location.global_relative_frame.alt <= 2:
                        time.sleep(2)
                        self.lg.log("Посадка завершена.")
                        break
                    time.sleep(0.1)
                if self.state != 9:
                    continue
                self.set_state(1)
