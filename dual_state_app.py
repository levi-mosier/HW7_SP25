# dual_state_app.py
# Created with help from ChatGPT
# Dual-State Thermodynamic Calculator for Steam using pyXSteam
# This program extends single-state functionality to allow comparing two states
# and reporting property changes. Units can be toggled between SI and English.

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from dual_state_ui import Ui_MainWindow
from ThermoStateCalc_app import thermoState
from UnitConversion import UC
from pyXSteam.XSteam import XSteam


class DualStateApp(QMainWindow):
    def __init__(self):
        """
        Initializes the dual state calculator GUI.
        Plan:
        - Set default unit system to SI
        - Connect buttons, populate dropdowns
        - Show active unit system
        """
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Initialize unit system to SI and set steam table
        self.unit_system = "SI"
        self.steamTable = XSteam(XSteam.UNIT_SYSTEM_MKS)
        self.ui.label_unit_system.setText("Current Units: SI")

        # Thermo properties available to specify
        self.props = ['P', 'T', 'h', 's', 'u', 'v', 'x']
        for combo in [
            self.ui.state1_prop1_combo, self.ui.state1_prop2_combo,
            self.ui.state2_prop1_combo, self.ui.state2_prop2_combo
        ]:
            combo.addItems(self.props)

        # Connect GUI buttons to logic
        self.ui.calculate_button.clicked.connect(self.calculate)
        self.ui.radio_SI.clicked.connect(self.set_units_to_SI)
        self.ui.radioButton_2.clicked.connect(self.set_units_to_English)

    def calculate(self):
        """
        Reads property inputs, attempts to calculate state 1 and 2,
        and displays results or errors.
        Plan:
        - Read selected properties and values for both states
        - Handle unit system selection (SI vs English)
        - Catch and show calculation errors to user
        """
        try:
            # State 1 input
            s1_prop1 = self.ui.state1_prop1_combo.currentText()
            s1_prop2 = self.ui.state1_prop2_combo.currentText()
            s1_val1 = float(self.ui.state1_val1_input.text())
            s1_val2 = float(self.ui.state1_val2_input.text())

            # State 2 input
            s2_prop1 = self.ui.state2_prop1_combo.currentText()
            s2_prop2 = self.ui.state2_prop2_combo.currentText()
            s2_val1 = float(self.ui.state2_val1_input.text())
            s2_val2 = float(self.ui.state2_val2_input.text())

            SI = self.unit_system == "SI"

            # State 1 calculation
            self.state1 = thermoState()
            try:
                self.state1.setState(s1_prop1, s1_prop2, s1_val1, s1_val2, SI)
            except Exception as e:
                raise Exception(f"State 1 failed: {str(e)}")

            # State 2 calculation
            self.state2 = thermoState()
            try:
                self.state2.setState(s2_prop1, s2_prop2, s2_val1, s2_val2, SI)
            except Exception as e:
                raise Exception(f"State 2 failed: {str(e)}")

            # Display results
            self.update_property_labels()

        except Exception as e:
            QMessageBox.critical(self, "Thermo Calculation Error", f"{str(e)}")

    def update_property_labels(self):
        """
        Updates all labels for state 1, state 2, and property differences.
        """
        fmt = lambda val: f"{val:.3f}"

        # State 1
        self.ui.state1_T_Label.setText("T: " + fmt(self.state1.t))
        self.ui.state1_P_Label.setText("P: " + fmt(self.state1.p))
        self.ui.state1_h_Label.setText("h: " + fmt(self.state1.h))
        self.ui.state1_s_Label.setText("s: " + fmt(self.state1.s))
        self.ui.state1_u_Label.setText("u: " + fmt(self.state1.u))
        self.ui.state1_v_Label.setText("v: " + fmt(self.state1.v))
        self.ui.state1_x_Label.setText("x: " + fmt(self.state1.x))

        # State 2
        self.ui.state2_T_Label.setText("T: " + fmt(self.state2.t))
        self.ui.state2_P_Label.setText("P: " + fmt(self.state2.p))
        self.ui.state2_h_Label.setText("h: " + fmt(self.state2.h))
        self.ui.state2_s_Label.setText("s: " + fmt(self.state2.s))
        self.ui.state2_u_Label.setText("u: " + fmt(self.state2.u))
        self.ui.state2_v_Label.setText("v: " + fmt(self.state2.v))
        self.ui.state2_x_Label.setText("x: " + fmt(self.state2.x))

        # Property changes (State 2 - State 1)
        self.ui.delta_T_Label.setText("ΔT: " + fmt(self.state2.t - self.state1.t))
        self.ui.delta_P_Label.setText("ΔP: " + fmt(self.state2.p - self.state1.p))
        self.ui.delta_h_Label.setText("Δh: " + fmt(self.state2.h - self.state1.h))
        self.ui.delta_s_Label.setText("Δs: " + fmt(self.state2.s - self.state1.s))
        self.ui.delta_u_Label.setText("Δu: " + fmt(self.state2.u - self.state1.u))
        self.ui.delta_v_Label.setText("Δv: " + fmt(self.state2.v - self.state1.v))
        self.ui.delta_x_Label.setText("Δx: " + fmt(self.state2.x - self.state1.x))

    def set_units_to_SI(self):
        """
        Handles SI unit selection and updates label + inputs.
        """
        if self.unit_system != "SI":
            self.unit_system = "SI"
            self.ui.label_unit_system.setText("Current Units: SI")
            self.convert_inputs("EN", "SI")

    def set_units_to_English(self):
        """
        Handles English unit selection and updates label + inputs.
        """
        if self.unit_system != "EN":
            self.unit_system = "EN"
            self.ui.label_unit_system.setText("Current Units: English")
            self.convert_inputs("SI", "EN")

    def convert_inputs(self, from_units, to_units):
        """
        Converts all input fields between SI and English units based on selection.
        Strategy:
        - Detect which property type is selected
        - Use UnitConversion.py class to apply correct conversion
        - Update input boxes with new values
        """
        SI = to_units == "SI"

        def convert(prop, val):
            if prop == 'P':
                return val * UC.psi_to_bar if SI else val * UC.bar_to_psi
            elif prop == 'T':
                return UC.F_to_C(val) if SI else UC.C_to_F(val)
            elif prop in ['h', 'u']:
                return val * UC.btuperlb_to_kJperkg if SI else val * UC.kJperkg_to_btuperlb
            elif prop == 's':
                return val * UC.btuperlbF_to_kJperkgC if SI else val * UC.kJperkgc_to_btuperlbF
            elif prop == 'v':
                return val * UC.ft3perlb_to_m3perkg if SI else val * UC.m3perkg_to_ft3perlb
            elif prop == 'x':
                return val  # quality is unitless
            return val  # default fallback

        for (combo, line) in [
            (self.ui.state1_prop1_combo, self.ui.state1_val1_input),
            (self.ui.state1_prop2_combo, self.ui.state1_val2_input),
            (self.ui.state2_prop1_combo, self.ui.state2_val1_input),
            (self.ui.state2_prop2_combo, self.ui.state2_val2_input)
        ]:
            try:
                prop = combo.currentText()
                val = float(line.text())
                line.setText("{:.3f}".format(convert(prop, val)))
            except ValueError:
                pass  # skip if not a valid float

def main():
    """
    Starts the application and launches the dual state GUI.
    """
    app = QApplication(sys.argv)
    win = DualStateApp()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
