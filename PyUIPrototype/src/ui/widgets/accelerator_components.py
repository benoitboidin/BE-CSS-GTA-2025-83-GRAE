"""
Accelerator-specific UI components for the PyUI framework
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QSlider, QSpinBox, QComboBox, QGraphicsView,
                           QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem,
                           QGraphicsPathItem, QFormLayout)
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QPen, QColor, QBrush, QPainterPath

import numpy as np
import math

from ui.pyui_components import PyUIComponent, PyUIContainer, PyUICard


class AcceleratorControlPanel(PyUICard):
    """Control panel for particle accelerator parameters"""
    
    # Signals for parameter changes
    energy_changed = pyqtSignal(float)
    particles_changed = pyqtSignal(int)
    beam_type_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__("Accelerator Controls", parent)
        
    def _init_ui(self):
        super()._init_ui()
        
        # Create layout for form
        form = QFormLayout()
        form_container = QWidget()
        form_container.setLayout(form)
        
        # Energy control
        self._energy_slider = QSlider(Qt.Orientation.Horizontal)
        self._energy_slider.setMinimum(100)
        self._energy_slider.setMaximum(1000)
        self._energy_slider.setValue(500)
        self._energy_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._energy_slider.setTickInterval(100)
        self._energy_slider.valueChanged.connect(lambda val: self.energy_changed.emit(val / 10.0))
        self._energy_slider.valueChanged.connect(lambda val: self.emit_event("energy_changed", val / 10.0))
        form.addRow("Energy (GeV):", self._energy_slider)
        
        # Energy value label
        self._energy_label = QLabel("50.0 GeV")
        self._energy_slider.valueChanged.connect(lambda val: self._energy_label.setText(f"{val / 10.0} GeV"))
        form.addRow("", self._energy_label)
        
        # Number of particles
        self._particle_spin = QSpinBox()
        self._particle_spin.setMinimum(10)
        self._particle_spin.setMaximum(1000)
        self._particle_spin.setSingleStep(10)
        self._particle_spin.setValue(100)
        self._particle_spin.valueChanged.connect(self.particles_changed)
        self._particle_spin.valueChanged.connect(lambda val: self.emit_event("particles_changed", val))
        form.addRow("Particles:", self._particle_spin)
        
        # Beam type
        self._beam_type = QComboBox()
        self._beam_type.addItems(["Proton", "Electron", "Lead Ion", "Antiproton"])
        self._beam_type.currentTextChanged.connect(self.beam_type_changed)
        self._beam_type.currentTextChanged.connect(lambda val: self.emit_event("beam_type_changed", val))
        form.addRow("Beam Type:", self._beam_type)
        
        # Add form to content
        self.add_component(form_container)
        
    def get_energy(self):
        """Get the current energy value in GeV"""
        return self._energy_slider.value() / 10.0
    
    def get_particles(self):
        """Get the current number of particles"""
        return self._particle_spin.value()
    
    def get_beam_type(self):
        """Get the current beam type"""
        return self._beam_type.currentText()


class AcceleratorVisualization(PyUIComponent):
    """Interactive visualization of a particle accelerator"""
    
    def __init__(self, parent=None):
        self._particles = []
        self._energy = 50.0  # Default energy in GeV
        self._num_particles = 100
        self._beam_type = "Proton"
        self._running = False
        self._timer = None
        super().__init__(parent)
        
    def _init_ui(self):
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        
        # Set up the graphics scene and view
        self._scene = QGraphicsScene()
        self._view = QGraphicsView(self._scene)
        self._view.setRenderHint(self._view.RenderHint.Antialiasing)
        self._view.setMinimumHeight(300)
        
        self._layout.addWidget(self._view)
        
        # Initialize the accelerator components
        self._init_accelerator()
        
        # Initialize timer for animation
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_particles)
        
    def _init_accelerator(self):
        """Initialize the accelerator components in the scene"""
        # Clear any existing items
        self._scene.clear()
        
        # Create the circular accelerator track
        center_x, center_y = 0, 0
        radius = 120
        self._track = QGraphicsEllipseItem(center_x - radius, center_y - radius, radius * 2, radius * 2)
        self._track.setPen(QPen(QColor(100, 100, 100), 10))
        self._scene.addItem(self._track)
        
        # Add magnets along the track (simplified representation)
        num_magnets = 8
        magnet_width = 20
        magnet_height = 30
        
        for i in range(num_magnets):
            angle = 2 * np.pi * i / num_magnets
            x = center_x + radius * np.cos(angle) - magnet_width / 2
            y = center_y + radius * np.sin(angle) - magnet_height / 2
            
            # Create a path for the magnet shape
            path = QPainterPath()
            if i % 2 == 0:  # Focusing magnet
                path.addRect(QRectF(0, 0, magnet_width, magnet_height))
                magnet = QGraphicsPathItem(path)
                magnet.setPen(QPen(QColor(0, 0, 255), 2))
                magnet.setBrush(QColor(200, 200, 255, 100))
            else:  # Defocusing magnet
                path.addRect(QRectF(0, 0, magnet_width, magnet_height))
                magnet = QGraphicsPathItem(path)
                magnet.setPen(QPen(QColor(255, 0, 0), 2))
                magnet.setBrush(QColor(255, 200, 200, 100))
            
            magnet.setPos(x, y)
            magnet.setRotation(angle * 180 / np.pi)
            self._scene.addItem(magnet)
        
        # Add beam injection point
        injection_angle = 0
        injection_x = center_x + (radius + 20) * np.cos(injection_angle)
        injection_y = center_y + (radius + 20) * np.sin(injection_angle)
        injection_path = QPainterPath()
        injection_path.addRect(-10, -5, 20, 10)
        injection = QGraphicsPathItem(injection_path)
        injection.setPen(QPen(QColor(0, 150, 0), 2))
        injection.setBrush(QColor(0, 200, 0, 150))
        injection.setPos(injection_x, injection_y)
        injection.setRotation(90)
        self._scene.addItem(injection)
        
        # Label for injection
        injection_label = self._scene.addText("Injection")
        injection_label.setPos(injection_x + 5, injection_y - 25)
        
        # Add beam extraction point
        extraction_angle = np.pi
        extraction_x = center_x + (radius + 20) * np.cos(extraction_angle)
        extraction_y = center_y + (radius + 20) * np.sin(extraction_angle)
        extraction_path = QPainterPath()
        extraction_path.addRect(-10, -5, 20, 10)
        extraction = QGraphicsPathItem(extraction_path)
        extraction.setPen(QPen(QColor(150, 0, 0), 2))
        extraction.setBrush(QColor(200, 0, 0, 150))
        extraction.setPos(extraction_x, extraction_y)
        extraction.setRotation(270)
        self._scene.addItem(extraction)
        
        # Label for extraction
        extraction_label = self._scene.addText("Extraction")
        extraction_label.setPos(extraction_x - 30, extraction_y - 25)
        
        # Reset particles
        self._particles = []
        
        # Center the view on the scene
        self._view.fitInView(self._scene.sceneRect().adjusted(-20, -20, 20, 20), Qt.AspectRatioMode.KeepAspectRatio)
        
    def resizeEvent(self, event):
        """Handle resize event to keep visualization centered"""
        super().resizeEvent(event)
        self._view.fitInView(self._scene.sceneRect().adjusted(-20, -20, 20, 20), Qt.AspectRatioMode.KeepAspectRatio)
        
    def _create_particles(self):
        """Create particles based on current settings"""
        # Clear existing particles
        for particle in self._particles:
            self._scene.removeItem(particle)
        self._particles = []
        
        # Get parameters from current settings
        center_x, center_y = 0, 0
        radius = 120
        
        # Determine particle color based on beam type
        color_map = {
            "Proton": QColor(255, 255, 0),
            "Electron": QColor(0, 255, 255),
            "Lead Ion": QColor(255, 0, 255),
            "Antiproton": QColor(255, 128, 0)
        }
        particle_color = color_map.get(self._beam_type, QColor(255, 255, 0))
        
        # Create particles with initial random positions around the track
        for i in range(self._num_particles):
            # Randomize position slightly around the track
            angle = 2 * np.pi * i / self._num_particles
            angle += np.random.uniform(-0.1, 0.1)  # Add some randomness
            
            # Particle size based on energy (higher energy = smaller, more focused beam)
            particle_size = max(2, 8 - self._energy / 20)
            
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            
            # Create particle
            particle = QGraphicsEllipseItem(-particle_size/2, -particle_size/2, particle_size, particle_size)
            particle.setPen(QPen(particle_color, 0.5))
            particle.setBrush(particle_color)
            particle.setPos(x, y)
            
            # Store angle for animation
            particle.setData(0, angle)
            
            # Add to scene
            self._scene.addItem(particle)
            self._particles.append(particle)
            
    def _update_particles(self):
        """Update particle positions for animation"""
        if not self._particles:
            return
            
        center_x, center_y = 0, 0
        radius = 120
        
        # Speed depends on energy level
        speed_factor = 0.002 + self._energy / 1000
        
        for particle in self._particles:
            # Get current angle
            angle = particle.data(0)
            
            # Update angle - particles move faster with higher energy
            angle += speed_factor
            if angle > 2 * np.pi:
                angle -= 2 * np.pi
                
            # Randomize position slightly - less randomness with higher energy
            radius_variance = max(0.5, 5 - self._energy / 20)
            r = radius + np.random.uniform(-radius_variance, radius_variance)
                
            # Update position
            x = center_x + r * np.cos(angle)
            y = center_y + r * np.sin(angle)
            particle.setPos(x, y)
            
            # Store updated angle
            particle.setData(0, angle)
            
    def start_simulation(self):
        """Start the particle animation"""
        if not self._running:
            self._create_particles()
            self._timer.start(30)  # Update every 30ms
            self._running = True
            
    def stop_simulation(self):
        """Stop the particle animation"""
        if self._running:
            self._timer.stop()
            self._running = False
            
    def toggle_simulation(self):
        """Toggle the simulation on/off"""
        if self._running:
            self.stop_simulation()
        else:
            self.start_simulation()
        return self._running
    
    @pyqtSlot(float)
    def set_energy(self, energy):
        """Set the beam energy in GeV"""
        self._energy = energy
        if self._running:
            # Update particle size based on new energy
            particle_size = max(2, 8 - self._energy / 20)
            for particle in self._particles:
                rect = particle.rect()
                particle.setRect(-particle_size/2, -particle_size/2, particle_size, particle_size)
            
    @pyqtSlot(int)
    def set_num_particles(self, num):
        """Set the number of particles"""
        self._num_particles = num
        if self._running:
            # Recreate particles with new count
            self._create_particles()
            
    @pyqtSlot(str)
    def set_beam_type(self, beam_type):
        """Set the beam type"""
        self._beam_type = beam_type
        if self._running:
            # Recreate particles with new beam type
            self._create_particles()


class SequencerPanel(PyUICard):
    """Panel for creating and executing operation sequences"""
    
    sequence_step_added = pyqtSignal(dict)
    sequence_executed = pyqtSignal()
    
    def __init__(self, parent=None):
        self._sequence = []
        super().__init__("Accelerator Sequencer", parent)
        
    def _init_ui(self):
        super()._init_ui()
        
        # Form layout for adding steps
        form_container = QWidget()
        form = QFormLayout(form_container)
        
        # Operation type selector
        self._operation = QComboBox()
        self._operation.addItems([
            "Set Energy", 
            "Set Beam Type", 
            "Inject Beam", 
            "Ramp Energy", 
            "Wait", 
            "Extract Beam"
        ])
        form.addRow("Operation:", self._operation)
        
        # Value input
        self._value = QSpinBox()
        self._value.setMinimum(0)
        self._value.setMaximum(1000)
        self._value.setValue(50)
        form.addRow("Value:", self._value)
        
        # Container for add button
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add button
        from ui.pyui_components import PyUIButton
        self._add_button = PyUIButton("Add Step", button_type="primary")
        self._add_button.clicked.connect(self._add_step)
        buttons_layout.addWidget(self._add_button)
        
        # Run sequence button
        self._run_button = PyUIButton("Run Sequence", button_type="success")
        self._run_button.clicked.connect(self._run_sequence)
        buttons_layout.addWidget(self._run_button)
        
        # Clear sequence button
        self._clear_button = PyUIButton("Clear", button_type="danger")
        self._clear_button.clicked.connect(self._clear_sequence)
        buttons_layout.addWidget(self._clear_button)
        
        # Add to form
        form.addRow("", buttons_container)
        
        # Add form to content
        self.add_component(form_container)
        
        # Sequence display
        self._sequence_container = PyUIContainer('vertical')
        self._sequence_label = QLabel("Current Sequence:")
        self._sequence_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self._sequence_display = QLabel("No steps added")
        
        self._sequence_container.add_component(self._sequence_label)
        self._sequence_container.add_component(self._sequence_display)
        
        self.add_component(self._sequence_container)
        
    def _add_step(self):
        """Add a step to the sequence"""
        operation = self._operation.currentText()
        value = self._value.value()
        
        step = {
            'operation': operation,
            'value': value
        }
        
        self._sequence.append(step)
        self._update_sequence_display()
        
        # Emit signal with step info
        self.sequence_step_added.emit(step)
        self.emit_event("sequence_step_added", step)
        
    def _update_sequence_display(self):
        """Update the sequence display"""
        if not self._sequence:
            self._sequence_display.setText("No steps added")
            return
            
        text = ""
        for i, step in enumerate(self._sequence):
            text += f"{i+1}. {step['operation']}: {step['value']}\n"
            
        self._sequence_display.setText(text)
        
    def _run_sequence(self):
        """Execute the sequence"""
        if not self._sequence:
            return
            
        self.sequence_executed.emit()
        self.emit_event("sequence_executed", self._sequence)
        
    def _clear_sequence(self):
        """Clear the sequence"""
        self._sequence = []
        self._update_sequence_display()
        self.emit_event("sequence_cleared")
