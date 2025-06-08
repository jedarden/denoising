# Virtual Microphone Architecture for Cross-Platform Real-Time Speech Denoising App

## Overview

This document defines the high-level architecture for the **Virtual Microphone** feature, enabling the application to create and register a virtual audio input device on both Windows and macOS. The virtual microphone will appear as a selectable input in third-party real-time communication apps (e.g., Zoom, Teams, Discord), and will receive the denoised audio stream from the application in real time.

---

## 1. Architectural Pattern

- **Pattern:** Layered Modular Architecture with Platform Abstraction
- **Rationale:**  
  - Ensures clear separation between platform-agnostic logic, platform-specific implementations, and the core denoising pipeline.
  - Facilitates maintainability, extensibility, and testability.
  - Supports future addition of other platforms (e.g., Linux).

---

## 2. Core Components

### 2.1. VirtualMicrophoneService (Platform-Agnostic Interface)
- **Responsibilities:**
  - Expose a unified API for virtual microphone lifecycle management (create, start, stop, destroy).
  - Route denoised audio frames from the denoising pipeline to the virtual device.
  - Handle error reporting and status monitoring.
- **Interactions:**
  - Consumes denoised audio from the core pipeline.
  - Delegates platform-specific operations to respective modules.

### 2.2. Platform-Specific Backends
- **WindowsVirtualMicrophoneBackend**
  - Implements device creation using Windows audio APIs (e.g., WASAPI, AVStream, or custom driver via user-mode).
  - Handles registration with the OS so the device appears in system audio settings.
  - Manages permissions and driver signing requirements.
- **MacOSVirtualMicrophoneBackend**
  - Implements device creation using CoreAudio APIs or AudioServerPlugIn.
  - Handles registration with macOS as an aggregate or virtual device.
  - Manages permissions (e.g., microphone access, system extensions).
- **Backend Selection**
  - At runtime, the service selects the appropriate backend based on the OS.

### 2.3. Audio Routing Layer
- **Responsibilities:**
  - Buffers and streams denoised audio to the virtual device with low latency.
  - Ensures synchronization and format compatibility.
  - Handles fallback or error states gracefully.

### 2.4. Integration Points
- **Denoising Pipeline**
  - Provides real-time denoised audio frames to the VirtualMicrophoneService.
- **GUI/UX Layer**
  - Allows users to enable/disable the virtual microphone, view status, and troubleshoot.
  - Surfaces permissions or system modification prompts as needed.

---

## 3. Data Flow

```mermaid
flowchart LR
    A[Microphone Input] --> B[Denoising Pipeline]
    B --> C[VirtualMicrophoneService]
    C --> D{Platform Backend}
    D -->|Windows| E[WindowsVirtualMicrophoneBackend]
    D -->|macOS| F[MacOSVirtualMicrophoneBackend]
    E & F --> G[Virtual Microphone Device]
    G --> H[External App (Zoom, Teams, etc.)]
```

- **:ComponentDiagram** and **:SequenceDiagram** concepts are represented above.

---

## 4. Technology Selection

- **Windows:**  
  - Prefer user-mode virtual audio driver frameworks (e.g., AVStream, WASAPI loopback) to avoid kernel-mode driver complexity.
  - Consider open-source references (e.g., VB-Cable, but re-implemented to avoid third-party dependencies).
- **macOS:**  
  - Use CoreAudio AudioServerPlugIn for virtual device creation.
  - Avoid requiring users to install third-party tools (e.g., BlackHole, Soundflower); instead, bundle or programmatically install required components with clear permissions prompts.

---

## 5. Scalability and Robustness Considerations

- **Low Latency:**  
  - Buffering and streaming must be optimized for real-time use.
- **Error Handling:**  
  - Detect and report device creation or routing failures.
- **User Experience:**  
  - Minimize required user actions; automate installation and registration steps where possible.
- **Security/Permissions:**  
  - Clearly document and request any system modifications or permissions (e.g., driver installation, system extension approval).

---

## 6. API Contract Definition

- **VirtualMicrophoneService API:**
  - `create()`: Initialize and register the virtual device.
  - `start()`: Begin streaming denoised audio.
  - `stop()`: Cease streaming.
  - `destroy()`: Unregister and clean up the device.
  - `status()`: Report current state and errors.

---

## 7. Platform-Specific Dependencies & System Modifications

- **Windows:**
  - May require installation of a signed user-mode audio driver (can be bundled and installed programmatically).
  - May require elevated permissions for driver installation.
  - No manual third-party tool installation required.
- **macOS:**
  - May require installation of a system extension (AudioServerPlugIn).
  - User may need to approve the extension in System Preferences.
  - No manual third-party tool installation required.

---

## 8. Risk Assessment

- **Driver Signing and Distribution:**  
  - Windows and macOS both require signed drivers/extensions for system-wide device registration. Plan for code-signing and notarization as part of the build/release process.
- **OS Updates:**  
  - Future OS updates may impact virtual device APIs; monitor and update as needed.
- **User Permissions:**  
  - Installation may prompt for admin/system credentials; UX must guide users clearly.

---

## 9. Integration with Existing Codebase

- **Modular Integration:**  
  - The VirtualMicrophoneService is a new module, interfacing with the existing denoising pipeline and GUI.
  - No changes required to core denoising logic.
  - Minimal changes to GUI to expose new controls and status.

---

## 10. Future Extensions

- **Linux Support:**  
  - Add ALSA/JACK/PulseAudio backend as needed.
- **Advanced Routing:**  
  - Support multiple virtual devices or advanced mixing.

---

## 11. Glossary

- **Virtual Microphone:** A software-created audio input device recognized by the OS and applications.
- **Backend:** Platform-specific implementation for device creation and management.
- **Audio Routing:** The process of sending audio data from the application to the virtual device.

---

## 12. References

- [Microsoft AVStream Documentation](https://docs.microsoft.com/en-us/windows-hardware/drivers/stream/avstream)
- [Apple CoreAudio AudioServerPlugIn](https://developer.apple.com/documentation/coreaudio/audioserverplugin)
- [Virtual Audio Device Design Patterns](https://github.com/ExistentialAudio/BlackHole) (for reference only, not for direct use)

---

## 13. Summary

This architecture enables robust, cross-platform virtual microphone support, tightly integrated with the real-time denoising pipeline. All platform-specific complexities are encapsulated in dedicated backends, ensuring a seamless and user-friendly experience. The design is modular, maintainable, and extensible for future needs.
---

## 14. Implementation Status (as of June 2025)

- The `VirtualMicrophoneService` and platform-specific backend stubs (`WindowsVirtualMicrophoneBackend`, `MacOSVirtualMicrophoneBackend`) are implemented in [`virtual_microphone.py`](../../virtual_microphone.py).
- The service is fully integrated with the denoising pipeline; denoised audio is routed to the virtual microphone interface.
- Platform-specific backends currently raise `NotImplementedError` and serve as extension points for future driver or CoreAudio implementations.
- The main application and `AudioIO` are updated to support the virtual microphone feature.
- Comprehensive tests and documentation are provided.
- See the [README.md](../../README.md) for setup, usage, and troubleshooting instructions.

**Next Steps:**
- Implement the actual virtual audio device creation and streaming logic in the platform-specific backends.
- Monitor OS updates for changes to driver or extension requirements.
- Extend support to Linux and advanced routing scenarios as needed.

---