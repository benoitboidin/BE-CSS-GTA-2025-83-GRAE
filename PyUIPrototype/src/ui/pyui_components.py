"""
Base module for the PyUI framework - core components
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, pyqtSignal


class PyUIComponent(QWidget):
    """Base class for all PyUI components"""
    
    # Signal that can be used to communicate between components
    componentSignal = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._name = self.__class__.__name__
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI - to be implemented by subclasses"""
        pass
    
    def get_name(self):
        """Get the component name"""
        return self._name
    
    def set_name(self, name):
        """Set the component name"""
        self._name = name
        
    def emit_event(self, event_type, data=None):
        """Emit an event to be captured by other components"""
        event_data = {
            'source': self._name,
            'type': event_type,
            'data': data
        }
        self.componentSignal.emit(event_data)


class PyUIContainer(PyUIComponent):
    """Container for organizing PyUI components"""
    
    def __init__(self, orientation='vertical', parent=None):
        self._orientation = orientation
        self._components = []
        super().__init__(parent)
        
    def _init_ui(self):
        if self._orientation == 'vertical':
            self._layout = QVBoxLayout()
        else:
            self._layout = QHBoxLayout()
            
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
        
    def add_component(self, component):
        """Add a component to the container"""
        if isinstance(component, PyUIComponent):
            self._layout.addWidget(component)
            self._components.append(component)
            # Forward signals
            component.componentSignal.connect(self.componentSignal)
        
    def add_components(self, components):
        """Add multiple components to the container"""
        for component in components:
            self.add_component(component)
            
    def clear(self):
        """Remove all components"""
        for component in self._components:
            self._layout.removeWidget(component)
            component.deleteLater()
        self._components = []


class PyUICard(PyUIComponent):
    """Card component with a title and content area"""
    
    def __init__(self, title="", parent=None):
        self._title = title
        self._components = []
        super().__init__(parent)
        
    def _init_ui(self):
        # Create layout
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
        
        # Create a frame with border
        self._frame = QFrame()
        self._frame.setFrameShape(QFrame.Shape.StyledPanel)
        self._frame.setFrameShadow(QFrame.Shadow.Raised)
        
        # Create frame layout
        frame_layout = QVBoxLayout()
        self._frame.setLayout(frame_layout)
        
        # Add header if title is provided
        if self._title:
            header = QLabel(self._title)
            header.setStyleSheet("font-weight: bold; padding: 5px;")
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            frame_layout.addWidget(header)
            
            # Add horizontal line
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            frame_layout.addWidget(line)
        
        # Content container
        self._content = PyUIContainer('vertical')
        frame_layout.addWidget(self._content)
        
        # Add frame to main layout
        self._layout.addWidget(self._frame)
        
    def add_component(self, component):
        """Add a component to the container"""
        if isinstance(component, PyUIComponent):
            self._content.add_component(component)
            self._components.append(component)
            # Forward signals
            component.componentSignal.connect(self.componentSignal)
        
    def add_components(self, components):
        """Add multiple components to the container"""
        for component in components:
            self.add_component(component)
            
    def clear(self):
        """Remove all components"""
        self._content.clear()
        self._components = []


class PyUIButton(PyUIComponent):
    """Standard button component with additional styling"""
    
    clicked = pyqtSignal()
    
    def __init__(self, text="", icon=None, button_type="default", parent=None):
        self._text = text
        self._icon = icon
        self._button_type = button_type
        super().__init__(parent)
        
    def _init_ui(self):
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
        
        # Create button
        self._button = QPushButton(self._text)
        
        # Set icon if provided
        if self._icon:
            self._button.setIcon(self._icon)
            
        # Set style based on button type
        if self._button_type == "primary":
            self._button.setStyleSheet(
                "background-color: #0066cc; color: white; padding: 6px 12px;"
            )
        elif self._button_type == "success":
            self._button.setStyleSheet(
                "background-color: #28a745; color: white; padding: 6px 12px;"
            )
        elif self._button_type == "danger":
            self._button.setStyleSheet(
                "background-color: #dc3545; color: white; padding: 6px 12px;"
            )
        else:
            self._button.setStyleSheet("padding: 6px 12px;")
            
        self._layout.addWidget(self._button)
        
        # Connect signals
        self._button.clicked.connect(self.clicked)
        self._button.clicked.connect(lambda: self.emit_event("clicked"))
        
    def set_text(self, text):
        """Set button text"""
        self._button.setText(text)
        
    def set_enabled(self, enabled):
        """Set button enabled state"""
        self._button.setEnabled(enabled)


class PyUIStatusBar(PyUIComponent):
    """Status bar component for displaying system status"""
    
    def __init__(self, parent=None):
        self._status = "Ready"
        self._status_type = "info"  # info, warning, error
        super().__init__(parent)
        
    def _init_ui(self):
        self._layout = QHBoxLayout()
        self._layout.setContentsMargins(5, 2, 5, 2)
        self.setLayout(self._layout)
        
        self._label = QLabel(self._status)
        self._layout.addWidget(self._label)
        
        self._update_style()
        
    def _update_style(self):
        """Update the style based on status type"""
        if self._status_type == "error":
            self.setStyleSheet("background-color: #ffdddd; color: #a94442;")
        elif self._status_type == "warning":
            self.setStyleSheet("background-color: #fcf8e3; color: #8a6d3b;")
        else:  # info
            self.setStyleSheet("background-color: #d9edf7; color: #31708f;")
            
        self._label.setStyleSheet("font-weight: normal;")
        
    def set_status(self, status, status_type="info"):
        """Set the status bar text and type"""
        self._status = status
        self._status_type = status_type
        self._label.setText(status)
        self._update_style()
