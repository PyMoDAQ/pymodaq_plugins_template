from pymodaq.extensions.pid.utils import PIDModelGeneric, OutputToActuator, InputFromDetector, main
from pymodaq.utils.data import DataToExport
from typing import List


def some_function_to_convert_the_pid_outputs(outputs: List[float], dt: float, stab=True):
    """ Should be replaced here or in the model class to process the outputs """
    return outputs


def some_function_to_convert_the_data(measurements: DataToExport):
    """ Should be replaced here or in the model class to process the measurement """
    a = 0
    b = 1
    return [a, b]


class PIDModelTemplate(PIDModelGeneric):
    limits = dict(max=dict(state=False, value=100),
                  min=dict(state=False, value=-100),)
    konstants = dict(kp=0.1, ki=0.000, kd=0.0000)

    Nsetpoints = 2  # number of setpoints
    setpoint_ini = [128, 128]  # number and values of initial setpoints
    setpoints_names = ['Xaxis', 'Yaxis']  # number and names of setpoints

    actuators_name = ["Xpiezo", "Ypiezo"]  # names of actuator's control modules involved in the PID
    detectors_name = ['Camera']  # names of detector's control modules involved in the PID

    params = []  # list of dict to initialize specific Parameters

    def __init__(self, pid_controller):
        super().__init__(pid_controller)

    def update_settings(self, param):
        """
        Get a parameter instance whose value has been modified by a user on the UI
        Parameters
        ----------
        param: (Parameter) instance of Parameter object
        """
        if param.name() == '':
            pass

    def ini_model(self):
        super().ini_model()

        # add here other specifics initialization if needed

    def convert_input(self, measurements: DataToExport):
        """
        Convert the measurements in the units to be fed to the PID (same dimensionality as the setpoint)
        Parameters
        ----------
        measurements: DataToExport
            Data from the declared detectors from which the model extract a value of the same units as the setpoint

        Returns
        -------
        InputFromDetector: the converted input in the setpoints units

        """

        x, y = some_function_to_convert_the_data(measurements)
        return InputFromDetector([y, x])

    def convert_output(self, outputs: List[float], dt: float, stab=True):
        """
        Convert the output of the PID in units to be fed into the actuator
        Parameters
        ----------
        outputs: List of float
            output value from the PID from which the model extract a value of the same units as the actuator
        dt: float
            Ellapsed time since the last call to this function
        stab: bool

        Returns
        -------
        OutputToActuator: the converted output

        """
        outputs = some_function_to_convert_the_pid_outputs(outputs, dt, stab)
        return OutputToActuator(mode='rel', values=outputs)


if __name__ == '__main__':
    main("BeamSteeringMockNoModel.xml")  # some preset configured with the right actuators and detectors


