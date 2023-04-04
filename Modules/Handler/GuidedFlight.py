import time
from threading import Thread
from dronekit import connect, VehicleMode
from pymavlink import mavutil


class GuidedFlight:
    def __init__(self, st, lg, ve):
        self.st = st
        self.lg = lg

        self.state = 0

        self.runnable = Thread(target=self.run, daemon=True, args=())
        self.vehicle = ve
        self.run_f = False

    def start(self):
        self.run_f = True
        self.runnable.start()

    def stop(self):
        self.run_f = False

    def send_ned_velocity(self, velocity_x, velocity_y, velocity_z, duration):
        msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
            0,
            0, 0,
            mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,
            0b0000111111000111,
            0, 0, 0,
            velocity_x, velocity_y, velocity_z,
            0, 0, 0,
            0, 0)
        for i in range(0, duration):
            self.vehicle.send_mavlink(msg)
            time.sleep(0.2)

    def move_2d(self, x, y):
        self.send_ned_velocity(x, y, 0, 1)

    def move_z(self, speed):
        self.send_ned_velocity(0, 0, -speed, 1)

    def run(self):
        self.lg.log("Ожидаю разрешения на взлёт...")
        while self.run_f:
            time.sleep(0.001)

            #
            # Состояние 0 - Подготовка
            # Ждём, пока будет получено сообщение с приложения о том, что
            # - всё подключено
            # - мы в состоянии работать
            # После этого переходим в состояние 1
            #

            if self.state == 0:
                if self.st.get_runtime()['comm_ok']:
                    if self.vehicle.is_armable:
                        self.lg.log("AP инициализирован, подключение установлено. Взлёт разрешён.")
                        self.st.set_ready(True)
                        self.state = 1
                    else:
                        while not self.vehicle.is_armable:
                            self.lg.log("Ожидаю инициализации AP...")
                            time.sleep(10)

            #
            # Состояние 9 - Ошибка связи в полёте
            # Запускаем режим посадки
            # После этого переходим в состояние 0
            #

            if self.state == 9:
                self.lg.error("Ошибка в процессе полёта! Сажусь...")
                self.vehicle.mode = VehicleMode("LAND")
                while True:
                    if self.vehicle.location.global_relative_frame.alt <= 2:
                        time.sleep(2)
                        self.lg.log("Посадка успешна")
                        self.st.set_ready(False)
                        break
                    time.sleep(0.2)
                self.vehicle.armed = False
                self.state = 0

            #
            # Состояние 1 - Арминг
            # Включаем АРМ и ждём, пока моторы запустятся
            # После этого переходим в состояние 2
            #

            if self.state == 1:
                if not self.st.get_runtime()['comm_ok']:
                    self.state = 9
                else:
                    if self.st.get_signals()['takeoff']:
                        self.lg.log("Получена команда на взлёт. Взлетаю...")
                        self.vehicle.mode = VehicleMode("GUIDED")
                        self.vehicle.armed = True
                        self.lg.log("Ожидаю ARM...")
                        while not self.vehicle.armed:
                            time.sleep(1)
                        self.lg.log("ARM включён.")
                        time.sleep(1)
                        self.state = 2

            #
            # Состояние 2 - Взлёт на указанную высоту
            # Взлетаем в автоматическом режиме, затем взлетаем в ручном до указанной высоты
            # После этого переходим в состояние 3
            #

            if self.state == 2:
                if not self.st.get_runtime()['comm_ok']:
                    self.state = 9
                else:
                    self.lg.log("Ожидаю взлёт и выход на высоту...")
                    self.vehicle.simple_takeoff(2)
                    while True:
                        if self.vehicle.location.global_relative_frame.alt >= 2 * 0.95:
                            break
                        time.sleep(0.2)
                    while True:
                        if self.vehicle.location.global_relative_frame.alt >= float(self.st.get_runtime()['target_alt']) * 0.95:
                            self.lg.log("Выход на высоту успешно, зависаю...")
                            break
                        else:
                            self.move_z(float(self.st.get_runtime()['takeoff_speed']))
                        time.sleep(0.2)
                    self.st.set_signal('takeoff', False)
                    self.state = 3

            #
            # Состояние 3 - Автоматический полёт
            # Висим на месте, если видим, что есть сигнал на движение - летим в нужную сторону
            # При наличии сигнала 'land' переходим в состояние 4
            #

            if self.state == 3:
                if not self.st.get_runtime()['comm_ok']:
                    self.state = 9
                else:
                    if self.st.get_signals()['land']:
                        self.state = 4
                    else:
                        move = self.st.get_move()
                        if move['x'] != 0 or move['y'] != 0:
                            self.move_2d(float(move['x']), float(move['y']))
                        else:
                            self.move_2d(0, 0)

            #
            # Состояние 4 - Посадка
            # Включаем режим LAND, ждём, пока коптер не снизится на высоту 1м. Затем ждём ещё 2с и выключаем АРМ
            # Затем переходим в состояние 1
            #

            if self.state == 4:
                if not self.st.get_runtime()['comm_ok']:
                    self.state = 9
                else:
                    self.lg.log("Получена команда на посадку. Сажусь...")
                    self.vehicle.mode = VehicleMode("LAND")
                    while True:
                        if self.vehicle.location.global_relative_frame.alt <= 2:
                            time.sleep(3)
                            self.lg.log("Посадка успешна")
                            break
                        time.sleep(0.2)
                    self.vehicle.armed = False
                    self.st.set_signal('land', False)
                    self.state = 0
