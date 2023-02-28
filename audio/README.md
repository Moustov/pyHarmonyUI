# Architectural Overview

## Audio Toolchain:

@startuml
participant MicAnalyzer #99FF99
participant MicListener #99FF99
MicAnalyzer -> MicListener
MicListener -> "set_current_note()"
participant NoteRecorder #99FF99
"set_current_note()" -> NoteRecorder 
"set_current_note()" -> "display_note()"
@enduml

## Components
### [MicAnalyzer](mic_analyzer.py)
Component which fetches a signal from the mic and send it to all registered listeners

@startuml
Interface MicListener 
MicAnalyzer : add_listener(MicListener)
MicAnalyzer : do_start_hearing()
MicAnalyzer : do_stop_hearing()
MicListener : set_current_note()
MicAnalyzer "1" *-- "many" MicListener : contains
MicListener <|--GuitarTraining
MicListener <|--NoteTraining
@enduml

### NoteRecorder (to be implemented)
Records a sequence of notes with a persistence mechanism

@startuml
NoteRecorder *--GuitarTraining
NoteRecorder *--NoteTraining
@enduml

### NotePlayer (to be implemented)
Plays a note

@startuml
NoteRecorder *--GuitarTraining
NoteRecorder *--NoteTraining
@enduml