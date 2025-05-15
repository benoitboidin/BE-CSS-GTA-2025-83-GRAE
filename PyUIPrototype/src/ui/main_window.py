"""
Main window for the PyUI Accelerator Visualization Prototype
"""

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QMenuBar, QStatusBar, QMenu, QApplication
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QAction, QIcon

from ui.pyui_components import PyUIContainer, PyUIButton, PyUIStatusBar
from ui.widgets.accelerator_components import AcceleratorVisualization, AcceleratorControlPanel, SequencerPanel
from models.controller import AcceleratorController


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Create controller
        self.controller = AcceleratorController()
        
        # Initialize UI
        self._init_ui()
        
    def _init_ui(self):
        # Set window properties
        self.setWindowTitle("CERN PyUI Accelerator Visualization Prototype")
        self.setMinimumSize(1000, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Create main container for components
        main_container = PyUIContainer('horizontal')
        
        # Left side: Control panels
        left_panel = PyUIContainer('vertical')
        
        # Accelerator Controls
        self.control_panel = AcceleratorControlPanel()
        left_panel.add_component(self.control_panel)
        
        # Sequencer
        self.sequencer = SequencerPanel()
        left_panel.add_component(self.sequencer)
        
        # Right side: Visualization
        right_panel = PyUIContainer('vertical')
        
        # Visualization
        self.visualization = AcceleratorVisualization()
        right_panel.add_component(self.visualization)
        
        # Control buttons
        buttons_container = PyUIContainer('horizontal')
        
        self.start_button = PyUIButton("Start Simulation", button_type="success")
        self.start_button.clicked.connect(self._toggle_simulation)
        buttons_container.add_component(self.start_button)
        
        right_panel.add_component(buttons_container)
        
        # Add panels to main container with proper sizing
        main_container.add_component(left_panel)
        main_container.add_component(right_panel)
        
        # Left panel should be narrower than right panel
        left_panel.setMaximumWidth(300)
        
        # Add main container to the layout
        main_layout.addWidget(main_container)
        
        # Create status bar
        self.status_bar = PyUIStatusBar()
        main_layout.addWidget(self.status_bar)
        
        # Create menu bar - moved here after components are initialized
        self._create_menu_bar()
        
        # Connect signal handlers
        self._connect_signals()
        
    def _create_menu_bar(self):
        """Create the application menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # File -> Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(QApplication.instance().quit)
        file_menu.addAction(exit_action)
        
        # Simulation menu
        sim_menu = menu_bar.addMenu("&Simulation")
        
        # Simulation -> Start action
        self.start_action = QAction("&Start", self)
        self.start_action.setShortcut("F5")
        self.start_action.triggered.connect(self.visualization.start_simulation)
        sim_menu.addAction(self.start_action)
        
        # Simulation -> Stop action
        stop_action = QAction("S&top", self)
        stop_action.setShortcut("F6")
        stop_action.triggered.connect(self.visualization.stop_simulation)
        sim_menu.addAction(stop_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        # Help -> About action
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _connect_signals(self):
        """Connect signals between components"""
        # Connect control panel to visualization AND controller
        self.control_panel.energy_changed.connect(self.visualization.set_energy)
        self.control_panel.energy_changed.connect(self.controller.set_beam_energy)
        self.control_panel.particles_changed.connect(self.visualization.set_num_particles)
        self.control_panel.beam_type_changed.connect(self.visualization.set_beam_type)
        
        # Connect sequencer to controller
        self.sequencer.sequence_step_added.connect(self._on_sequence_step_added)
        self.sequencer.sequence_executed.connect(self._on_sequence_executed)
        
        # Connect controller to UI updates
        self.controller.status_changed.connect(self.status_bar.set_status)
        self.controller.energy_changed.connect(self.visualization.set_energy)
        
    def _toggle_simulation(self):
        """Toggle simulation on/off"""
        running = self.visualization.toggle_simulation()
        
        # Update button text based on state and notify controller
        if running:
            self.start_button.set_text("Stop Simulation")
            self.controller.start_simulation()
        else:
            self.start_button.set_text("Start Simulation")
            self.controller.stop_simulation()
            
    def _on_sequence_step_added(self, step):
        """Handle a new sequence step being added"""
        self.status_bar.set_status(f"Added step: {step['operation']}", "info")
        
    def _on_sequence_executed(self):
        """Handle sequence execution"""
        # Pass the sequence to the controller for execution
        self.controller.execute_sequence(self.sequencer._sequence)
        
    def _show_about(self):
        """Show about dialog"""
        # In a real application, we would show a dialog
        self.status_bar.set_status("PyUI Accelerator Visualization Prototype - CERN BE-CSS-GTA application", "info")
