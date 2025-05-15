# PyUI Accelerator Visualization Prototype

A prototype demonstration for the CERN BE-CSS-GTA position, showcasing an interactive visualization of a particle accelerator using Python and PyQt with a specialized PyUI framework.

## Overview

This prototype addresses the key requirements mentioned in the CERN BE-CSS-GTA job description:

1. **PyUI Framework**: A modular, reusable UI framework built with PyQt that provides accelerator-specific components
2. **Sequencer UI**: A simple implementation of a sequence editor for creating and executing operational sequences on the accelerator
3. **Domain-Specific Components**: UI widgets specifically designed for particle accelerator visualization and control
4. **Modern Software Practices**: Component-based architecture with clear separation between UI, controllers, and physics models

## Key Components and Features

### PyUI Framework
- **Base Component System**: Modular, reusable UI components built on PyQt
- **Signals & Events**: Component-to-component communication for decoupled architecture
- **Styling System**: Consistent look and feel through QSS styles
- **Containers**: Flexible layout management for components

### Accelerator-Specific Components
- **Control Panels**: Specialized widgets for beam parameters
- **Visualization**: Interactive graphical representation of particles in an accelerator
- **Sequence Editor**: UI for creating and executing operational sequences

### Simulation Features
- **Interactive Visualization**: Real-time particle behavior visualization
- **Physics Models**: Simplified physics calculations for accelerator operations
- **Sequence Execution**: Step-by-step execution of acceleration sequences
- **State Management**: Controlled beam and accelerator state transitions

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

### Installation

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
python src/main.py
```

## Project Structure

- `src/` - Source code
  - `ui/` - User interface components
  - `models/` - Data models for accelerator and particles
  - `utils/` - Utility functions
- `resources/` - Static resources like styles

## Architecture

The prototype follows a clean architecture with separation of concerns:

```
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│                   │     │                   │     │                   │
│  PyUI Components ◄─────►   Controllers    ◄─────►  Physics Models    │
│                   │     │                   │     │                   │
└───────────────────┘     └───────────────────┘     └───────────────────┘
```

- **PyUI Components**: Visual elements and user interactions
- **Controllers**: Manage application state and coordinate between UI and models
- **Physics Models**: Implement domain-specific physics calculations and simulation logic

## Alignment with CERN BE-CSS-GTA Requirements

This prototype addresses the specific job requirements:

1. **Python Development with PyQt**: The entire application is built using Python 3 and PyQt6
2. **Framework Development**: PyUI demonstrates how a specialized UI framework can be built on top of PyQt
3. **Domain-Specific UI**: Components are tailored for accelerator operations
4. **Sequencer UI**: Implementation of a basic sequence editor for operational tasks
5. **User Interaction**: Clean and intuitive interface designed with users in mind
6. **Reusability**: Components designed to be reused across different applications
