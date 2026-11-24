# Requirements and acceptance criteria

## PC target

The requested target is Windows PC code running under Proton, with static
conversion and reusable private caches preferred over repeated runtime work.
See [NATIVE_PC.md](NATIVE_PC.md) for the first actual offline shader conversion
and its limits. A standalone native port and a Proton launch remain unverified.

## Boot and render first

1. Validate the locally supplied package and executable.
2. Record the first loader, TLS, DLL-initialization, or entry-point failure.
3. Exercise Leonida's native runtime with startup and graphics traces stored
   locally. Resolve actual failures with tested implementations.
4. Establish a reproducible rendered frame and playable offline scene before
   making gameplay compatibility claims.

## Simulation timing independent of rendering

The user reports that frame rate controls simulation speed. This has not been
measured against the executable yet. Locate the simulation step and render/present
boundary once startup works. Preserve the original simulation rate while allowing
different presentation rates, with interpolation where needed.

Acceptance: compare equal wall-clock intervals at 30, 60, 120 and uncapped render
rates. Movement distance, physics, animation, scripted timers, audio and camera
behavior must remain consistent. Include slow frames and sustained CPU/GPU load.
Changing a frame cap or spoofing a timer is not enough to establish correctness.

## Gyro aiming

The user wants motion-assisted aiming. Leonida already exposes SDL3 controller
motion through GameInput; exposing sensor data does not make a game use it.
Implement an aim-input path after the camera/input behavior can be measured.

Requirements: optional gyro, calibration/bias correction, sensitivity, yaw/pitch
axis mapping, inversion, an activation/clutch control, and coexistence with sticks
and buttons. Preserve angular motion across sensor and render rates, account for
aim sensitivity/acceleration, and handle disconnect/reconnect without a jump.

Acceptance: known angular movements produce consistent camera movement at
different presentation rates; a stationary calibrated controller does not drift;
the clutch works; stick aiming and menus remain usable. Verify on the user's
actual gyro-capable controller before calling it supported.

## Publication boundary

Publish tool source, documentation, synthetic fixtures and independently written
runtime changes only. Keep game code, archives, console libraries, keys, shader
corpora, extracted assets, generated port folders, saves and private traces local.
