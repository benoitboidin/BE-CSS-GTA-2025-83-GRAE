"""
Physics utility functions for the accelerator simulation
"""

import math
import numpy as np


def relativistic_beta(energy_gev, rest_mass_gev):
    """
    Calculate relativistic beta (v/c) from energy and rest mass
    
    Args:
        energy_gev: Kinetic energy in GeV
        rest_mass_gev: Rest mass in GeV/c²
        
    Returns:
        beta (v/c) value between 0 and 1
    """
    total_energy = energy_gev + rest_mass_gev
    gamma = total_energy / rest_mass_gev
    
    # Avoid numerical issues
    if gamma <= 1.0:
        return 0.0
        
    beta_squared = 1.0 - 1.0/(gamma*gamma)
    
    # Avoid negative values due to floating point errors
    if beta_squared < 0:
        return 0.0
        
    return math.sqrt(beta_squared)


def energy_to_momentum(energy_gev, rest_mass_gev):
    """
    Calculate momentum from energy and rest mass
    
    Args:
        energy_gev: Kinetic energy in GeV
        rest_mass_gev: Rest mass in GeV/c²
        
    Returns:
        momentum in GeV/c
    """
    total_energy = energy_gev + rest_mass_gev
    return math.sqrt(total_energy*total_energy - rest_mass_gev*rest_mass_gev)


def lorentz_factor(beta):
    """
    Calculate Lorentz factor gamma from relativistic beta
    
    Args:
        beta: Relativistic velocity (v/c)
        
    Returns:
        gamma factor
    """
    if beta >= 1.0:
        return float('inf')
        
    return 1.0 / math.sqrt(1.0 - beta*beta)


def magnetic_field_for_radius(momentum_gev, radius_m, charge):
    """
    Calculate the magnetic field required to bend a particle with given momentum in a circle
    
    Args:
        momentum_gev: Momentum in GeV/c
        radius_m: Bending radius in meters
        charge: Charge in units of elementary charge
        
    Returns:
        Magnetic field in Tesla
    """
    # Convert from natural units (GeV/c) to SI units
    # 1 GeV/c = 5.344286e-19 kg·m/s
    momentum_si = momentum_gev * 5.344286e-19
    
    # Elementary charge in C
    e = 1.602176634e-19
    
    # B = p/(q·r)
    return momentum_si / (charge * e * radius_m)


def rf_frequency_for_orbit(beta, radius_m, harmonic_number=1):
    """
    Calculate RF frequency for a stable orbit
    
    Args:
        beta: Relativistic velocity (v/c)
        radius_m: Mean radius of the accelerator in meters
        harmonic_number: RF harmonic number (default: 1)
        
    Returns:
        RF frequency in MHz
    """
    # Speed of light in m/s
    c = 299792458
    
    # Circumference = 2*pi*radius
    circumference = 2 * math.pi * radius_m
    
    # Revolution frequency = beta*c/circumference
    rev_freq = beta * c / circumference
    
    # RF frequency = h * revolution frequency
    rf_freq = harmonic_number * rev_freq
    
    # Convert to MHz
    return rf_freq / 1e6


def synchrotron_radiation_power(energy_gev, magnetic_field_t, current_a, radius_m):
    """
    Calculate synchrotron radiation power
    
    Args:
        energy_gev: Beam energy in GeV
        magnetic_field_t: Magnetic field in Tesla
        current_a: Beam current in Amperes
        radius_m: Bending radius in meters
        
    Returns:
        Radiation power in kilowatts
    """
    # Convert energy to electron equivalent (scale by electron mass)
    electron_mass = 0.000511  # GeV/c²
    proton_mass = 0.938  # GeV/c²
    
    # Scale to electron units (synchrotron radiation scales with m⁻⁴)
    mass_ratio = electron_mass / proton_mass
    energy_scale = energy_gev * mass_ratio
    
    # Synchrotron radiation power formula
    # P[kW] = 88.5 * E⁴[GeV] * I[A] * B[T] / ρ[m]
    power_kw = 88.5 * (energy_scale**4) * current_a * magnetic_field_t / radius_m
    
    return power_kw


def get_particle_properties():
    """
    Return basic properties of common particles used in accelerators
    
    Returns:
        Dictionary of particle properties
    """
    return {
        "Proton": {
            "mass": 0.938272,  # GeV/c²
            "charge": 1,  # elementary charge
            "spin": 1/2,
            "g_factor": 5.5857
        },
        "Electron": {
            "mass": 0.000511,  # GeV/c²
            "charge": -1,
            "spin": 1/2, 
            "g_factor": 2.00232
        },
        "Lead Ion": {  # Pb⁸²⁺
            "mass": 193.7,  # GeV/c² (approximate for Pb-208)
            "charge": 82,
            "spin": 0,
            "g_factor": 0
        },
        "Antiproton": {
            "mass": 0.938272,  # GeV/c²
            "charge": -1,
            "spin": 1/2,
            "g_factor": 5.5857
        }
    }


def simulate_acceleration_ramp(initial_energy, final_energy, ramp_time, steps=100):
    """
    Simulate an acceleration ramp
    
    Args:
        initial_energy: Initial beam energy in GeV
        final_energy: Target beam energy in GeV
        ramp_time: Ramp time in seconds
        steps: Number of simulation steps
        
    Returns:
        Tuple of (time_points, energy_points)
    """
    # Create time points
    time_points = np.linspace(0, ramp_time, steps)
    
    # Create energy points (using a smooth S-curve for acceleration)
    norm_times = time_points / ramp_time
    s_curve = 0.5 * (1 - np.cos(np.pi * norm_times))
    energy_points = initial_energy + s_curve * (final_energy - initial_energy)
    
    return time_points, energy_points
