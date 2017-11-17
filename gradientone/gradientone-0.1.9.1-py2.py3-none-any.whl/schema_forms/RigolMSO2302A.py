import scope
from common_elements import FORM_BOTTOM

# Todo: populate the defaults from configApp.js
SCHEMA_DICT = {
    "type": "object",
    "title": "Config",
    "properties": scope.COMMON_PROPERTIES, 
    "required": [
        "name"
    ]
}

rigol_props = {
        "outputs": {
            "title": "AFG Waveform",
            "type": "object",
            "properties": {
                "enabled": {
                    "title": "Enabled",
                    "type": "boolean",
                    "default": True
                },
                "impedence": {
                    "title": "Standard Impedence (e.g. 50)",
                    "type": "number",
                    "default": 50
                }
            }
        },
        "output_noise": {
            "title": "Output Noise",
            "type": "object",
            "properties": {
                "enabled": {
                    "title": "Enabled",
                    "type": "boolean",
                    "default": False
                },
                "percent": {
                    "title": "Noise Percent: (e.g. 50%)",
                    "type": "number",
                    "default": 0
                }
            }
        },
        "standard_waveform": {
            "title": "AFG Settings",
            "type": "object",
            "properties": {
                "waveform": {
                    "title": "Function",
                    "type": "string",
                    "enum": ["sine", "square", "triangle", "ramp_up",
                             "ramp_down", "dc", "pulse", "noise", "sinc",
                             "exprise", "expfall", "cardiac", "gaussian",
                             "expfall", "lorentz", "haversine"],
                    "default": "square"
                },
                "frequency": {
                    "title": "Frequency (Hz)",
                    "type": "number",
                    "default": 2200000
                },
                "amplitude": {
                    "title": "Amplitude",
                    "type": "number",
                    "default": 1
                },
                "dc_offset": {
                    "title": "DC Offset",
                    "type": "number",
                    "default": 0
                },
                "duty_cycle_high": {
                    "title": "Duty Cycle High",
                    "type": "number",
                    "default": 50
                },
                "start_phase": {
                    "title": "Start Phase",
                    "type": "number",
                    "default": 0
                },
                "pulse_width": {
                    "title": "Pulse Width",
                    "type": "number",
                    "default": 1e-6
                },
                "symmetry": {
                    "title": "Symmetry",
                    "type": "number",
                    "default": 50
                }
            }
        }
    }

SCHEMA_DICT['properties'].update(rigol_props)

FORM_DICT = [
                {
                    "key": "name",
                    "placeholder": "Tek"
                },
                "acquisition",
                "trigger",
                "channels",
                "outputs",
                "output_noise",
                "standard_waveform",
                "timebase",
                "g1_measurements"
            ] + FORM_BOTTOM
