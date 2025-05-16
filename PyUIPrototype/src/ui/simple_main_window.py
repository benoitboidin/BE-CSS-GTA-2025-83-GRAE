"""
Simplified main window for the PyUI Accelerator Visualization Prototype
"""

from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QPushButton, QLabel, QStatusBar, QSlider, QSpinBox,
                             QComboBox, QCheckBox, QGroupBox)
from PyQt6.QtCore import Qt, QTimer
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches
import matplotlib.cm as cm
import sys
import os

# Add the root directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.utils.physics import magnetic_field_for_radius

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
        
        # Particle properties
        self.particle_mass = 0.938  # Default: proton mass in GeV/c²
        self.particle_charge = 1.0  # Default: proton charge
        self.particle_type = "Proton"
        self.particle_colors = {"Proton": "yellow", "Electron": "cyan", "Ion": "magenta"}
        
        # Magnetic field parameters
        self.magnetic_field_enabled = False
        self.magnetic_field_strength = 0.0  # Tesla
        self.magnetic_field_direction = 1  # 1: into screen, -1: out of screen
        self.magnetic_regions = []  # Will store visualization objects
        
        # Trajectory tracking
        self.show_trajectories = False
        self.trajectory_points = []
        self.max_trajectory_points = 100
        self.trajectory_update_freq = 3  # Update every N frames
        self.trajectory_frame_count = 0
        
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
        
        # Plot particles with proper color for particle type
        particle_color = self.particle_colors.get(self.particle_type, "blue")
        self.scatter = self.axes.scatter(self.particles_x, self.particles_y, 
                                         s=2, alpha=0.5, c='blue', cmap='plasma')
        
        # Draw magnetic field regions if enabled
        self.magnetic_regions = []
        if self.magnetic_field_enabled:
            self._draw_magnetic_fields()
            
        # Draw any saved trajectories
        if self.show_trajectories and self.trajectory_points:
            for traj in self.trajectory_points:
                if len(traj) > 1:  # Need at least 2 points for a line
                    traj_x, traj_y = zip(*traj)
                    self.axes.plot(traj_x, traj_y, '-', color='gray', linewidth=0.5, alpha=0.3)
        
        # Set plot properties
        self.axes.set_xlim(-10, 10)
        self.axes.set_ylim(-10, 10)
        title = f"Particle Acceleration Simulation\n{self.particle_type}s - Energy: {self.energy} GeV"
        if self.magnetic_field_enabled:
            title += f"\nMagnetic Field: {self.magnetic_field_strength:.2f} T"
        self.axes.set_title(title)
        self.axes.grid(True)
        self.fig.tight_layout()
        self.draw()
        
    def _draw_magnetic_fields(self):
        """Draw magnetic field region on the plot"""
        # Clear previous magnetic regions
        for region in self.magnetic_regions:
            try:
                region.remove()
            except:
                pass
        self.magnetic_regions = []
        
        # Create magnetic field visualization
        # We'll represent it as circular regions
        field_regions = [
            {'x': -5, 'y': 0, 'radius': 3},
            {'x': 5, 'y': 0, 'radius': 3}
        ]
        
        # Draw each magnetic field region
        for region in field_regions:
            # Color based on field direction
            color = 'dodgerblue' if self.magnetic_field_direction > 0 else 'orangered'
            alpha = min(0.3, abs(self.magnetic_field_strength) / 5.0) + 0.1
            
            # Create circle
            circle = patches.Circle(
                (region['x'], region['y']), 
                region['radius'], 
                color=color, 
                alpha=alpha,
                fill=True
            )
            self.axes.add_patch(circle)
            self.magnetic_regions.append(circle)
            
            # Add field direction indicators (dots or crosses)
            if abs(self.magnetic_field_strength) > 0.05:
                symbol_coords = self._generate_field_symbol_coords(
                    region['x'], region['y'], region['radius']
                )
                
                if self.magnetic_field_direction > 0:  # Into screen (dots)
                    for x, y in symbol_coords:
                        dot = self.axes.plot(x, y, 'o', markersize=3, color=color, alpha=0.7)[0]
                        self.magnetic_regions.append(dot)
                else:  # Out of screen (crosses)
                    for x, y in symbol_coords:
                        # Draw the crosses as small line segments
                        line1 = self.axes.plot([x-0.2, x+0.2], [y-0.2, y+0.2], '-', color=color, alpha=0.7)[0]
                        line2 = self.axes.plot([x-0.2, x+0.2], [y+0.2, y-0.2], '-', color=color, alpha=0.7)[0]
                        self.magnetic_regions.append(line1)
                        self.magnetic_regions.append(line2)
    
    def _generate_field_symbol_coords(self, center_x, center_y, radius):
        """Generate coordinates for magnetic field symbols within a region"""
        num_symbols = int(10 * radius)  # Number of symbols based on region size
        coords = []
        
        for _ in range(num_symbols):
            # Random position within circle
            r = radius * np.sqrt(np.random.random()) * 0.8  # Stay within 80% of radius
            theta = np.random.random() * 2 * np.pi
            x = center_x + r * np.cos(theta)
            y = center_y + r * np.sin(theta)
            coords.append((x, y))
            
        return coords

    def update_figure(self):
        """Update the figure animation"""
        self.time += 1
        
        # Apply acceleration
        accel_factor = self.energy / 100.0  # Scale based on energy
        
        # Accelerate particles
        self.particles_vx += np.random.normal(0, 0.01 * accel_factor, self.num_particles)
        self.particles_vy += np.random.normal(0, 0.01 * accel_factor, self.num_particles)
        
        # Apply magnetic field effects if enabled
        if self.magnetic_field_enabled and abs(self.magnetic_field_strength) > 0.01:
            self._apply_magnetic_field_effect()
        
        # Update positions
        self.particles_x += self.particles_vx
        self.particles_y += self.particles_vy
        
        # Record trajectory points if enabled
        if self.show_trajectories:
            self.trajectory_frame_count += 1
            if self.trajectory_frame_count >= self.trajectory_update_freq:
                self.trajectory_frame_count = 0
                self._update_trajectories()
        
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
        
    def _apply_magnetic_field_effect(self):
        """Apply the effect of magnetic fields on particle velocities"""
        # Magnetic field regions
        field_regions = [
            {'x': -5, 'y': 0, 'radius': 3},
            {'x': 5, 'y': 0, 'radius': 3}
        ]
        
        # Particle charge sign for force direction
        charge_sign = self.particle_charge
        
        # Scale the effect based on field strength and charge
        # F = q * v × B (Lorentz force law)
        field_strength_effect = self.magnetic_field_strength * charge_sign * self.magnetic_field_direction * 0.01
        
        for region in field_regions:
            # Calculate distance of each particle from the field center
            dx = self.particles_x - region['x']
            dy = self.particles_y - region['y']
            distances = np.sqrt(dx**2 + dy**2)
            
            # Find particles within magnetic field region
            in_field = distances <= region['radius']
            
            if not np.any(in_field):
                continue
                
            # Apply circular motion effect to particles in the field
            # For particles in magnetic field, v⊥ changes direction but not magnitude
            # We'll approximate this with a rotation
            
            # Current velocity magnitudes
            v_magnitudes = np.sqrt(
                self.particles_vx[in_field]**2 + 
                self.particles_vy[in_field]**2
            )
            
            # Calculate the rotation angle based on velocity and field strength
            # Θ = ω * Δt = qB/m * Δt
            # Higher energy = less effect (relativistic mass increase)
            angles = field_strength_effect * (100.0 / self.energy) * v_magnitudes
            
            # Rotate velocity vectors
            cos_angles = np.cos(angles)
            sin_angles = np.sin(angles)
            
            # Store original velocities
            original_vx = self.particles_vx[in_field].copy()
            original_vy = self.particles_vy[in_field].copy()
            
            # Apply rotation matrix
            self.particles_vx[in_field] = original_vx * cos_angles - original_vy * sin_angles
            self.particles_vy[in_field] = original_vx * sin_angles + original_vy * cos_angles
            
    def _update_trajectories(self):
        """Update particle trajectory tracking"""
        # Select a subset of particles to track
        if not self.trajectory_points:
            # Initialize trajectory tracking for 10 particles
            sampled_indices = np.random.choice(
                range(self.num_particles), 
                min(10, self.num_particles), 
                replace=False
            )
            self.trajectory_points = [[] for _ in sampled_indices]
            self.tracked_particle_indices = sampled_indices
        
        # Add current positions to trajectories
        for i, idx in enumerate(self.tracked_particle_indices):
            # Keep only the last MAX_POINTS
            if len(self.trajectory_points[i]) >= self.max_trajectory_points:
                self.trajectory_points[i].pop(0)
                
            # Add current position
            self.trajectory_points[i].append(
                (self.particles_x[idx], self.particles_y[idx])
            )
        
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
