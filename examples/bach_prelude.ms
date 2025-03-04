// Bach's Prelude in C Major (Simplified)
tempo 72
time 4/4

// Define the arpeggiated pattern sequence
sequence arpeggio_pattern {
    // C major
    [C4 E4 G4] 1/16
    E4 1/16
    G4 1/16
    C5 1/16
    E4 1/16
    G4 1/16
    C5 1/16
    E4 1/16
    
    // G7
    [B3 D4 G4] 1/16
    D4 1/16
    G4 1/16
    B4 1/16
    D4 1/16
    G4 1/16
    B4 1/16
    D4 1/16
    
    // C major
    [C4 E4 G4] 1/16
    E4 1/16
    G4 1/16
    C5 1/16
    E4 1/16
    G4 1/16
    C5 1/16
    E4 1/16
    
    // A minor
    [C4 E4 A4] 1/16
    E4 1/16
    A4 1/16
    C5 1/16
    E4 1/16
    A4 1/16
    C5 1/16
    E4 1/16
}

// Main sequence that repeats the pattern
sequence main {
    // First measure
    arpeggio_pattern
    
    // Add a final chord
    [C4 E4 G4 C5] 1/2
    R 1/2  // Rest for half note
}

// Play the main sequence
play main 