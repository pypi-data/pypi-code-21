if __name__ == '__main__':
    from kervi.application import Application
    APP = Application()
    #Important GPIO must be imported after application creation
    from kervi.hal import GPIO

    from kervi.dashboard import Dashboard, DashboardPanel
    DASHBOARD = Dashboard("app", "App", is_default=True)
    DASHBOARD.add_panel(DashboardPanel("fan", columns=3, rows=2, title="CPU fan"))

    SYSTEMBOARD = Dashboard("system", "System")
    SYSTEMBOARD.add_panel(DashboardPanel("cpu", columns=2, rows=2))
    SYSTEMBOARD.add_panel(DashboardPanel("cam", columns=2, rows=2))

    #Create a streaming camera server
    from kervi.camera import CameraStreamer
    CAMERA = CameraStreamer("cam1", "camera 1")
    #link camera as background
    CAMERA.link_to_dashboard("app")
    #link camera to a panel
    CAMERA.link_to_dashboard("system", "cam")

    from kervi.sensor import Sensor
    from kervi_devices.platforms.common.sensors.cpu_use import CPULoadSensorDeviceDriver
    from kervi_devices.platforms.common.sensors.cpu_temp import CPUTempSensorDeviceDriver
    #build in sensor that measures cpu use
    SENSOR_CPU_LOAD = Sensor("CPULoadSensor", "CPU", CPULoadSensorDeviceDriver())
    #link to sys area top right
    SENSOR_CPU_LOAD.link_to_dashboard("*", "sys-header")
    #link to a panel, show value in panel header and chart in panel body
    SENSOR_CPU_LOAD.link_to_dashboard("system", "cpu", type="value", size=2, link_to_header=True)
    SENSOR_CPU_LOAD.link_to_dashboard("system", "cpu", type="chart", size=2)

    #build in sensor that measures cpu temperature
    SENSOR_CPU_TEMP = Sensor("CPUTempSensor", "", CPUTempSensorDeviceDriver())
    #link to sys area top right
    SENSOR_CPU_TEMP.link_to_dashboard("*", "sys-header")


    #More on sensors https://kervi.github.io/sensors.html


    #define a light controller
    from kervi.controller import Controller
    from kervi.values import DynamicNumber, DynamicBoolean
    class FanController(Controller):
        def __init__(self):
            Controller.__init__(self, "fan_controller", "Fan")
            self.type = "fan"

            self.temp = self.inputs.add("temp", "Temperature", DynamicNumber)
            self.temp.min = 0
            self.temp.max = 150

            self.trigger_temp = self.inputs.add("trigger_temp", "Trigger temperature", DynamicNumber)
            self.trigger_temp.min = 0
            self.trigger_temp.max = 100
            #remember the value when app restarts
            self.trigger_temp.persists = True

            self.max_temp = self.inputs.add("max_temp", "Max speed temperature", DynamicNumber)
            self.max_temp.min = 0
            self.max_temp.max = 100
            #remember the value when app restarts
            self.max_temp.persists = True

            self.active = self.inputs.add("active", "Active", DynamicBoolean)
            self.fan_speed = self.outputs.add("fan_speed", "Fanspeed", DynamicNumber)

        def input_changed(self, changed_input):
            if self.active.value:
                temp = self.temp.value - self.trigger_temp.value
                if temp <= 0:
                    self.fan_speed.value = 0
                else:
                    max_span = self.max_temp.value - self.trigger_temp.value
                    speed = (temp / max_span) * 100
                    if speed > 100:
                        speed = 100
                    self.fan_speed.value = speed
            else:
                self.fan_speed.value = 0

    FAN_CONTROLLER = FanController()

    #link the fan controllers temp input to cpu temperature sensor
    FAN_CONTROLLER.temp.link_to(SENSOR_CPU_TEMP)
    FAN_CONTROLLER.temp.link_to_dashboard("app", "fan")

    #link the other fan controller inputs to dashboard
    FAN_CONTROLLER.trigger_temp.link_to_dashboard("app", "fan")
    FAN_CONTROLLER.max_temp.link_to_dashboard("app", "fan")
    FAN_CONTROLLER.active.link_to_dashboard("app", "fan")
    FAN_CONTROLLER.fan_speed.link_to_dashboard("app", "fan")

    APP.run()
