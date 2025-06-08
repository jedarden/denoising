## Prompt LS2_1

### Context
The initial codebase contains duplicate and inconsistent class/function definitions across modules (e.g., multiple `AudioIO`, `Denoiser`, and GUI classes). This has led to confusion, low maintainability, and modularity issues. The critic and metrics both highlight the need for consolidation and standardization.

### Objective
Eliminate all duplicate and inconsistent class/function definitions, ensuring each module exposes a single, well-documented, canonical interface.

### Focus Areas
- Remove duplicate class/function definitions in all modules
- Consolidate into a single, clear class or function per file
- Standardize naming and interfaces across modules

### Code Reference
```python
# audio_io.py (excerpt)
class AudioIO:
    ...
class AudioIO:
    ...
# denoiser.py
class Denoiser: ...
class DenoisingInference: ...
```

### Requirements
- Only one main class/function per module
- Consistent naming conventions (e.g., use `DenoisingInference` everywhere)
- Update all imports and references to match new interfaces

### Expected Improvements
- Modularity score ≥ 80
- Maintainability score ≥ 70
- No duplicate definitions in any module

---

## Prompt LS2_2

### Context
There is no test scaffolding or TDD readiness in the current codebase. Test coverage is nearly zero, and there are no test files or even placeholder tests. This blocks TDD and robust development.

### Objective
Establish comprehensive test scaffolding for all modules, following TDD principles.

### Focus Areas
- Create test files for each module (e.g., `test_audio_io.py`, `test_denoiser.py`, etc.)
- Add at least one failing test per module to drive development
- Use pytest or unittest for test structure

### Code Reference
```python
# No test functions or test files present
```

### Requirements
- Each module must have a corresponding test file
- Tests must cover both positive and negative scenarios
- Structure code to allow dependency injection and mocking

### Expected Improvements
- Test coverage ≥ 50% (target 80%+ in future iterations)
- TDD compliance: all new features/fixes require tests first
- Maintainability and modularity scores increase

---

## Prompt LS2_3

### Context
All methods are currently stubs with `pass` or placeholder returns. There is no real logic, error handling, or resource management, and no platform/CPU-only compliance logic is implemented.

### Objective
Implement minimal, real logic for each method, including error handling, resource management, and cross-platform/CPU-only compliance.

### Focus Areas
- Add platform checks and CPU-only enforcement in relevant modules
- Implement device enumeration and selection logic in audio/model modules
- Add error handling and resource cleanup to all methods

### Code Reference
```python
def start_stream(self, callback: Callable[[bytes], bytes]) -> None:
    pass
# TODO: Initialize PyAudio/PortAudio streams
```

### Requirements
- Platform checks (e.g., `sys.platform`) and CPU-only logic in audio/model modules
- Exception handling for device/model/GUI errors
- Logging for error reporting and debugging
- Provide test cases for platform/CPU compliance

### Expected Improvements
- Cross-platform/CPU-only score ≥ 70
- Maintainability and modularity scores increase
- Code is robust against platform and device errors

---

## Prompt LS2_4

### Context
Naming and interface inconsistencies exist across modules (e.g., `Denoiser` vs. `DenoisingInference`, `DenoisingAppGUI` vs. `DenoisingApp`). This causes confusion and import errors.

### Objective
Standardize all class and method names and interfaces across the codebase.

### Focus Areas
- Use a single naming convention for all classes and methods
- Update all imports and references to match the new convention
- Ensure all interfaces are clearly documented

### Code Reference
```python
# denoiser.py
class Denoiser: ...
class DenoisingInference: ...
# gui.py
class DenoisingAppGUI: ...
class DenoisingApp: ...
```

### Requirements
- Consistent naming across all modules
- All interfaces have clear, PEP8-compliant docstrings and type annotations
- No ambiguous or duplicate names

### Expected Improvements
- Maintainability score ≥ 70
- No import errors due to naming inconsistencies
- Improved code readability and maintainability

---

## Prompt LS2_5

### Context
The code lacks style compliance, optimization, and security best practices. There are no type annotations, inconsistent formatting, and no input validation or secure handling of file/model paths.

### Objective
Enforce PEP8 style, add type annotations, and implement basic security and optimization best practices.

### Focus Areas
- Apply PEP8 formatting and add docstrings throughout
- Add type annotations to all functions and methods
- Validate all user/device input and securely handle file/model paths

### Code Reference
```python
# Example: missing type annotations and docstrings
def load_model(path):
    ...
```

### Requirements
- All code is PEP8-compliant
- All functions/methods have type annotations and docstrings
- Input validation and secure file/model handling in place

### Expected Improvements
- Maintainability score ≥ 80
- Security posture improved (no obvious vulnerabilities)
- Code is ready for further optimization and extension