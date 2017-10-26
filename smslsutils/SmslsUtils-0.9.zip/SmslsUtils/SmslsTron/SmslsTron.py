from ..SmslsDevicePy import SmslsDevicePy

class SmslsTron:

    def __init__(self):
        self.laser = SmslsDevicePy.GetInputOutputApi()
        self.servo = SmslsDevicePy.GetServoApi()
        self.stepper = SmslsDevicePy.GetStepperApi()
        self.temper = SmslsDevicePy.GetTemperatureApi() 

    def initialize(self):
        # configure Laser API
        print("Initializing I/O API.")
        if self.laser.Initialize():
            print("Failed to initialize I/O API.")
        
        self.laser_id = 1
        self.laser_state_tar = False
        self.laser.SetChannelState(self.laser_id, self.laser_state_tar)

        # configure Servo API
        print("Initializing Servo API.")
        if self.servo.Initialize():
            print("Failed to initialize Servo API.")
        
        self.servo_id = 1
        self.servo_pos_tar = 90
        self.servo.Stop(self.servo_id)
        self.servo.SetTargetAcceleration(self.servo_id, 180)
        self.servo.SetTargetSpeed(self.servo_id, 180)
        self.servo.SetTargetPosition(self.servo_id, self.servo_pos_tar)
        self.servo.Start(self.servo_id)

        # configure Stepper API
        print("Initializing Stepper API.")
        if self.stepper.Initialize():
            print("Failed to initialize Stepper API.")
        
        self.stepper_id = 1
        self.stirring_speed_tar = 0
        self.stepper.SetTargetAcceleration(self.stepper_id, 1e6)
        self.stepper.SetTargetSpeed(self.stepper_id, self.stirring_speed_tar)
        self.stepper.SetTargetPosition(self.stepper_id, 0)
        self.stepper.Start(self.stepper_id)
        
        # configure Temperature API
        print("Initializing Temperature API.")
        if self.temper.Initialize():
            print("Failed to initialize Temperature API.")
        
        self.temper_id = 1
        self.temper_tar = 30
        self.temper.SetTargetTemp(self.temper_id, self.temper_tar);


        self.update()

    def close(self):
        # shut it down. shut it all down.
        self.laser.SetChannelState(self.laser_id, False)
        self.servo.Stop(self.servo_id)
        self.stepper.Stop(self.stepper_id)
        self.temper.StopHeater(self.temper_id)
        self.temper.StopCooler(self.temper_id)

    def update(self):
        # update laser bits
        self.laser.SetChannelState(self.laser_id, self.laser_state_tar)
        error, self.laser_state_curr = self.laser.GetChannelState(self.laser_id)

        # update servo bits
        self.servo.SetTargetPosition(self.servo_id, self.servo_pos_tar);
        self.servo.Start(self.servo_id)
        error, self.servo_pos_curr = self.servo.GetCurrentPosition(self.servo_id)
        error, self.servo_is_running = self.servo.IsRunning(self.servo_id)

        # update stirring bits
        self.stepper.SetTargetSpeed(self.stepper_id, self.stirring_speed_tar)
        self.stepper.Start(self.stepper_id)
        error, self.stirring_speed_cur = self.stepper.GetCurrentSpeed(self.stepper_id)
        error, self.stirring_is_running = self.stepper.IsRunning(self.stepper_id)

        # update temperature bits
        self.temper.SetTargetTemp(self.temper_id, self.temper_tar);
        self.temper.StartHeater(self.temper_id);

        if self.temper_tar < 35:
            self.temper.StartCooler(self.temper_id)
        else:
            self.temper.StopCooler(self.temper_id)

        error, self.temper_cur = self.temper.GetCurrentTemp(self.temper_id)
        error, self.heater_is_running = self.temper.HeaterIsRunning(self.temper_id)
        error, self.cooler_is_running = self.temper.CoolerIsRunning(self.temper_id)

