"""
Models for the accelerator simulation
"""

import numpy as np


class Particle:
    """Model representing a particle in the accelerator"""
    
    def __init__(self, particle_type="Proton", energy=0.0, position=0.0):
        self.particle_type = particle_type
        self.energy = energy  # GeV
        self.position = position  # Position along the accelerator (0 to 1)
        self.velocity = 0.0
        
        # Set properties based on particle type
        self._init_properties()
        
    def _init_properties(self):
        """Initialize particle-specific properties"""
        properties = {
            "Proton": {
                "mass": 0.938,  # GeV/c^2
                "charge": 1.0,  # elementary charge
                "color": (255, 255, 0)  # Yellow
            },
            "Electron": {
                "mass": 0.000511,  # GeV/c^2
                "charge": -1.0,
                "color": (0, 255, 255)  # Cyan
            },
            "Lead Ion": {
                "mass": 193.7,  # GeV/c^2 (for Pb-208)
                "charge": 82.0,
                "color": (255, 0, 255)  # Magenta
            },
            "Antiproton": {
                "mass": 0.938,  # GeV/c^2
                "charge": -1.0,
                "color": (255, 128, 0)  # Orange
            }
        }
        
        # Get properties for the particle type or use default (Proton)
        props = properties.get(self.particle_type, properties["Proton"])
        
        self.mass = props["mass"]
        self.charge = props["charge"]
        self.color = props["color"]
        
    def update(self, dt):
        """Update particle state over time step dt"""
        # Simple update: position changes based on energy
        # In a real simulation, this would be much more complex
        self.velocity = self._calculate_velocity()
        self.position = (self.position + self.velocity * dt) % 1.0
        
    def _calculate_velocity(self):
        """Calculate velocity based on energy"""
        # Simplified relativistic calculation
        # v = c * sqrt(1 - (m*c²)²/(m*c²+E)²)
        # where c = 1 in natural units (speed of light)
        if self.energy <= 0:
            return 0
            
        rest_energy = self.mass  # m*c² in GeV
        total_energy = rest_energy + self.energy
        
        # Avoid division by zero or negative inside sqrt
        if total_energy <= rest_energy:
            return 0
            
        v_over_c = np.sqrt(1 - (rest_energy / total_energy) ** 2)
        
        # Scale to make the simulation visually interesting
        # Actual particle velocities would be very close to c
        return 0.1 + 0.9 * v_over_c


class Accelerator:
    """Model of a particle accelerator"""
    
    def __init__(self):
        # Accelerator sections
        self.sections = [
            {"name": "Injection", "position": 0.0},
            {"name": "RF Cavity 1", "position": 0.25},
            {"name": "RF Cavity 2", "position": 0.5},
            {"name": "RF Cavity 3", "position": 0.75},
            {"name": "Extraction", "position": 0.99}
        ]
        
        self.particles = []
        self.max_energy = 100.0  # GeV
        self.current_energy = 0.0  # GeV
        
    def inject_beam(self, particle_type="Proton", count=100):
        """Inject a beam of particles into the accelerator"""
        self.particles = []
        
        for _ in range(count):
            # Initial position near the injection point with some variance
            position = np.random.normal(0.01, 0.01) % 1.0
            
            # Create particle with initial energy
            particle = Particle(particle_type, self.current_energy, position)
            self.particles.append(particle)
            
        return len(self.particles)
        
    def extract_beam(self):
        """Extract the beam from the accelerator"""
        extracted = len(self.particles)
        self.particles = []
        return extracted
        
    def set_energy(self, energy):
        """Set energy level for the accelerator"""
        self.current_energy = min(energy, self.max_energy)
        
        # Update all particles to the new energy
        for particle in self.particles:
            particle.energy = self.current_energy
            
    def update(self, dt):
        """Update the state of all particles in the accelerator"""
        for particle in self.particles:
            particle.update(dt)
            
    def get_particle_positions(self):
        """Get current positions of all particles"""
        return [p.position for p in self.particles]
        
    def get_particle_energies(self):
        """Get current energies of all particles"""
        return [p.energy for p in self.particles]
        
    def get_particle_colors(self):
        """Get colors of all particles"""
        return [p.color for p in self.particles]
