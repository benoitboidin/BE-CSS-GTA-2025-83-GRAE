"""
Simulation controller for the PyUI Accelerator Visualization Prototype
"""

import time
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot

from models.accelerator import Accelerator
from utils.physics import simulate_acceleration_ramp


class AcceleratorController(QObject):
    """Controller for the accelerator simulation"""
    
    # Signals to update UI
    status_changed = pyqtSignal(str, str)  # message, status_type
    operation_completed = pyqtSignal(str)  # operation description
    energy_changed = pyqtSignal(float)  # current energy
    
    def __init__(self):
        super().__init__()
        
        # Create accelerator model
        self.accelerator = Accelerator()
        
        # Simulation settings
        self.simulation_running = False
        self.current_sequence = []
        self.current_step_index = -1
        
        # Create timer for sequence execution
        self.sequence_timer = QTimer()
        self.sequence_timer.setSingleShot(True)
        self.sequence_timer.timeout.connect(self._execute_next_step)
        
    def start_simulation(self):
        """Start the simulation"""
        if not self.simulation_running:
            self.simulation_running = True
            self.status_changed.emit("Simulation started", "info")
        
    def stop_simulation(self):
        """Stop the simulation"""
        if self.simulation_running:
            self.simulation_running = False
            self.status_changed.emit("Simulation stopped", "info")
            
    def set_beam_energy(self, energy):
        """Set the beam energy"""
        self.accelerator.set_energy(energy)
        self.energy_changed.emit(energy)
        self.status_changed.emit(f"Beam energy set to {energy:.1f} GeV", "info")
        
    def inject_beam(self, particle_type, count):
        """Inject a new beam"""
        actual_count = self.accelerator.inject_beam(particle_type, count)
        self.status_changed.emit(f"Injected {actual_count} {particle_type} particles", "info")
        return actual_count
        
    def extract_beam(self):
        """Extract the current beam"""
        count = self.accelerator.extract_beam()
        if count > 0:
            self.status_changed.emit(f"Extracted {count} particles", "info")
        else:
            self.status_changed.emit("No particles to extract", "warning")
        return count
        
    def execute_sequence(self, sequence):
        """Execute a sequence of operations"""
        if not sequence:
            self.status_changed.emit("No sequence to execute", "warning")
            return
            
        self.current_sequence = sequence
        self.current_step_index = -1
        
        # Start execution
        self.status_changed.emit(f"Starting sequence execution ({len(sequence)} steps)", "info")
        self._execute_next_step()
        
    def _execute_next_step(self):
        """Execute the next step in the sequence"""
        self.current_step_index += 1
        
        # Check if we've completed the sequence
        if self.current_step_index >= len(self.current_sequence):
            self.status_changed.emit("Sequence execution completed", "info")
            self.current_step_index = -1
            return
            
        # Get the current step
        step = self.current_sequence[self.current_step_index]
        operation = step["operation"]
        value = step["value"]
        
        # Execute the operation
        if operation == "Set Energy":
            self.set_beam_energy(value)
            self._schedule_next_step(500)  # Wait 500ms
            
        elif operation == "Set Beam Type":
            # Map value to beam type
            beam_types = ["Proton", "Electron", "Lead Ion", "Antiproton"]
            beam_type = beam_types[value % len(beam_types)]
            
            # We need to re-inject with the new beam type
            count = len(self.accelerator.particles)
            if count == 0:
                count = 100  # Default
                
            self.accelerator.extract_beam()
            self.inject_beam(beam_type, count)
            
            self.status_changed.emit(f"Beam type set to {beam_type}", "info")
            self._schedule_next_step(500)  # Wait 500ms
            
        elif operation == "Inject Beam":
            self.inject_beam("Proton", value)
            self._schedule_next_step(1000)  # Wait 1s
            
        elif operation == "Ramp Energy":
            # Start a gradual energy ramp
            self._ramp_energy(self.accelerator.current_energy, value, 2000)
            # Next step will be scheduled when ramp completes
            
        elif operation == "Wait":
            self.status_changed.emit(f"Waiting for {value} ms", "info")
            self._schedule_next_step(value)  # Wait for specified time
            
        elif operation == "Extract Beam":
            self.extract_beam()
            self._schedule_next_step(1000)  # Wait 1s
            
        else:
            self.status_changed.emit(f"Unknown operation: {operation}", "error")
            self._schedule_next_step(500)  # Continue anyway after a short delay
    
    def _schedule_next_step(self, delay_ms):
        """Schedule the next step after a delay"""
        self.sequence_timer.start(delay_ms)
        
    def _ramp_energy(self, start_energy, target_energy, ramp_time_ms):
        """Perform a gradual energy ramp"""
        self.status_changed.emit(f"Ramping energy from {start_energy:.1f} to {target_energy:.1f} GeV", "info")
        
        # Create a timer for the ramp animation
        ramp_timer = QTimer(self)
        ramp_steps = 20
        step_time = ramp_time_ms / ramp_steps
        
        # Generate ramp points
        times, energies = simulate_acceleration_ramp(
            start_energy, target_energy, ramp_time_ms/1000, ramp_steps)
        
        # Current step in the ramp
        step_index = [0]  # Use a list to allow modification in the inner function
        
        def update_ramp():
            i = step_index[0]
            if i >= len(energies):
                # Ramp complete
                ramp_timer.stop()
                self.set_beam_energy(target_energy)
                self.status_changed.emit(f"Energy ramp complete: {target_energy:.1f} GeV", "info")
                self._schedule_next_step(500)  # Schedule next sequence step
                return
                
            # Update to the next energy level
            self.set_beam_energy(energies[i])
            step_index[0] += 1
            
        # Connect the timer and start it
        ramp_timer.timeout.connect(update_ramp)
        ramp_timer.start(int(step_time))
