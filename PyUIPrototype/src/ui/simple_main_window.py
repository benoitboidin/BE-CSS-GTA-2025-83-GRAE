"""
Simplified main window for the PyUI Accelerator Visualization Prototype
"""

from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QPushButton, QLabel, QStatusBar, QSlider, QSpinBox)
from PyQt6.QtCore import Qt, QTimer
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class ParticleVisualization(FigureCanvas):
    """Widget for visualizing particle acceleration"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Initialize parameters
        self.energy = 100  # GeV
        self.num_particles = 1000
        self.time = 0
        self.particles_x = np.random.normal(0, 1, self.num_particles)
        self.particles_y = np.random.normal(0, 1, self.num_particles)
        self.particles_vx = np.zeros(self.num_particles)
        self.particles_vy = np.zeros(self.num_particles)
        
        # Set up the timer for animation
        self.timer = QTimer()
        self.timer.setInterval(50)  # Update every 50ms
        self.timer.timeout.connect(self.update_figure)
        self.running = False
        
        # Initial plot
        self.plot()
    
    def plot(self):
        """Create the initial plot"""
        self.axes.clear()
        self.scatter = self.axes.scatter(self.particles_x, self.particles_y, 
                                         s=2, alpha=0.5, c='blue')
        self.axes.set_xlim(-10, 10)
        self.axes.set_ylim(-10, 10)
        self.axes.set_title(f"Particle Acceleration Simulation\nEnergy: {self.energy} GeV")
        self.axes.grid(True)
        self.fig.tight_layout()
        self.draw()

    def update_figure(self):
        """Update the figure animation"""
        self.time += 1
        
        # Apply acceleration
        accel_factor = self.energy / 100.0  # Scale based on energy
        
        # Accelerate particles
        self.particles_vx += np.random.normal(0, 0.01 * accel_factor, self.num_particles)
        self.particles_vy += np.random.normal(0, 0.01 * accel_factor, self.num_particles)
        
        # Update positions
        self.particles_x += self.particles_vx
        self.particles_y += self.particles_vy
        
        # Contain particles within boundaries (reflecting boundaries)
        out_of_bounds = np.abs(self.particles_x) > 10
        self.particles_vx[out_of_bounds] = -self.particles_vx[out_of_bounds]
        
        out_of_bounds = np.abs(self.particles_y) > 10
        self.particles_vy[out_of_bounds] = -self.particles_vy[out_of_bounds]
        
        # Update scatter plot
        self.scatter.set_offsets(np.column_stack((self.particles_x, self.particles_y)))
        
        # Update colors based on velocity
        velocities = np.sqrt(self.particles_vx**2 + self.particles_vy**2)
        self.scatter.set_array(velocities)
        
        self.draw()
        
    def start_simulation(self):
        """Start the simulation"""
        if not self.running:
            self.timer.start()
            self.running = True
            return True
        return False
        
    def stop_simulation(self):
        """Stop the simulation"""
        if self.running:
            self.timer.stop()
            self.running = False
            return True
        return False
        
    def toggle_simulation(self):
        """Toggle simulation state"""
        if self.running:
            return not self.stop_simulation()
        else:
            return self.start_simulation()
            
    def set_energy(self, value):
        """Set particle energy"""
        self.energy = value
        self.axes.set_title(f"Particle Acceleration Simulation\nEnergy: {self.energy} GeV")
        self.draw()
        
    def set_num_particles(self, value):
        """Set number of particles"""
        old_num = self.num_particles
        self.num_particles = value
        
        if value > old_num:
            # Add new particles
            new_count = value - old_num
            self.particles_x = np.append(self.particles_x, np.random.normal(0, 1, new_count))
            self.particles_y = np.append(self.particles_y, np.random.normal(0, 1, new_count))
            self.particles_vx = np.append(self.particles_vx, np.zeros(new_count))
            self.particles_vy = np.append(self.particles_vy, np.zeros(new_count))
        else:
            # Remove particles
            self.particles_x = self.particles_x[:value]
            self.particles_y = self.particles_y[:value]
            self.particles_vx = self.particles_vx[:value]
            self.particles_vy = self.particles_vy[:value]
            
        self.plot()


class SimpleMainWindow(QMainWindow):
    """Simple main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize UI
        self._init_ui()
        
    def _init_ui(self):
        # Set window properties
        self.setWindowTitle("CERN PyUI Accelerator Visualization Prototype")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Add a title
        title_label = QLabel("PyUI Accelerator Visualization")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        main_layout.addWidget(title_label)
        
        # Create main container
        container = QWidget()
        container_layout = QHBoxLayout(container)
        
        # Left side: Control panel with sliders
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        control_title = QLabel("Controls")
        control_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        left_layout.addWidget(control_title)
        
        # Energy control
        energy_title = QLabel("Beam Energy")
        energy_title.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(energy_title)
        
        self.energy_label = QLabel("100 GeV")
        left_layout.addWidget(self.energy_label)
        
        energy_slider = QSlider(Qt.Orientation.Horizontal)
        energy_slider.setMinimum(10)
        energy_slider.setMaximum(1000)
        energy_slider.setValue(100)
        energy_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        energy_slider.setTickInterval(100)
        energy_slider.valueChanged.connect(self._set_energy)
        left_layout.addWidget(energy_slider)
        
        # Particles control
        particles_title = QLabel("Number of Particles")
        particles_title.setStyleSheet("font-weight: bold; margin-top: 20px;")
        left_layout.addWidget(particles_title)
        
        self.particles_label = QLabel("1000 particles")
        left_layout.addWidget(self.particles_label)
        
        particles_spinner = QSpinBox()
        particles_spinner.setMinimum(100)
        particles_spinner.setMaximum(5000)
        particles_spinner.setSingleStep(100)
        particles_spinner.setValue(1000)
        particles_spinner.valueChanged.connect(self._set_particles)
        left_layout.addWidget(particles_spinner)
        
        # Add a spacer
        left_layout.addStretch(1)
        
        # Right side: Visualization
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        vis_title = QLabel("Visualization")
        vis_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        right_layout.addWidget(vis_title)
        
        # Create the visualization
        self.visualization = ParticleVisualization(self)
        right_layout.addWidget(self.visualization)
        
        # Start/Stop button
        self.start_button = QPushButton("Start Simulation")
        self.start_button.clicked.connect(self._toggle_simulation)
        right_layout.addWidget(self.start_button)
        
        # Add panels to main container with proper sizing
        container_layout.addWidget(left_panel, 1)  # 1/4 of the width
        container_layout.addWidget(right_panel, 3)  # 3/4 of the width
        
        # Add main container to the layout
        main_layout.addWidget(container)
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
    def _toggle_simulation(self):
        """Toggle simulation on/off"""
        running = self.visualization.toggle_simulation()
        
        # Update button text based on state
        if running:
            self.start_button.setText("Stop Simulation")
            self.statusBar().showMessage("Simulation running")
        else:
            self.start_button.setText("Start Simulation")
            self.statusBar().showMessage("Simulation stopped")
            
    def _set_energy(self, value):
        """Set beam energy"""
        self.energy_label.setText(f"{value} GeV")
        self.visualization.set_energy(value)
        self.statusBar().showMessage(f"Energy set to {value} GeV")
        
    def _set_particles(self, value):
        """Set number of particles"""
        self.particles_label.setText(f"{value} particles")
        self.visualization.set_num_particles(value)
        self.statusBar().showMessage(f"Number of particles set to {value}")
