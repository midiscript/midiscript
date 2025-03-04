# MidiScript

A programming language for musicians to create MIDI files from simple text.

## Overview

MidiScript is an intuitive programming language designed specifically for musicians. It allows you to create MIDI files using a simple, music-oriented syntax that feels natural to musicians while being powerful enough to create complex musical compositions.

## Installation

For users:
```bash
pip install -e .
```

For developers:
```bash
# Clone the repository
git clone https://github.com/yourusername/midiscript.git
cd midiscript

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Install the package in editable mode
pip install -e .
```

## Syntax Example

```midiscript
// Define a simple melody
tempo 120
time 4/4

// Define a sequence
sequence main {
    // Notes are written as note names with optional octave and duration
    C4 1/4  // Quarter note C in octave 4
    E4 1/4
    G4 1/4
    C5 1/4
    
    // You can use chords
    [C4 E4 G4] 1/2  // Half note C major chord
    
    // Add a rest
    R 1/4  // Quarter note rest
}

// Play the sequence
play main
```

## Features

- Intuitive musical notation
- Support for notes, chords, and rests
- Tempo and time signature control
- Multiple track support
- Variable note durations
- Sequence definition and reuse
- Dynamic control (velocity)
- MIDI channel selection

## Usage

Create a MidiScript file (e.g., `song.ms`):
```midiscript
tempo 120
time 4/4

sequence main {
    C4 1/4
    E4 1/4
    G4 1/4
}

play main
```

Generate MIDI file:
```bash
midiscript song.ms -o output.mid
```

## Documentation

### Basic Syntax

- Notes: `C4`, `D#4`, `Bb3`
- Durations: `1/4` (quarter), `1/2` (half), `1/8` (eighth)
- Chords: `[C4 E4 G4]`
- Rests: `R 1/4`
- Comments: `// Comment`

### Commands

- `tempo <bpm>`: Set the tempo in beats per minute
- `time <numerator>/<denominator>`: Set time signature
- `channel <1-16>`: Set MIDI channel
- `velocity <0-127>`: Set note velocity

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

We use:
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

Run all checks:
```bash
black .
flake8 .
mypy .
```

## Examples

Check out the `examples/` directory for sample MidiScript files:
- `twinkle.ms`: Twinkle, Twinkle, Little Star
- `bach_prelude.ms`: Simplified version of Bach's Prelude in C Major

## License

MIT License