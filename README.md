<<<<<<< HEAD
# TURBO APEX: Computer Graphics Car Racing Game

An arcade pseudo-3D car racing game developed in Python and Pygame for an academic Computer Graphics mini-project.

Features custom **3D perspective projection**, **scanline polygon rasterization**, **multi-layer parallax rendering**, **procedural vector sprite generation**, **intelligent curve-aware AI**, **true horizontal split-screen multiplayer**, **3 dynamic camera modes**, and a **synthesized audio engine** with zero external file dependencies.

---

## 1. Quick Start & Installation

### Prerequisites
- Python 3.8+ (Compatible with Python 3.10, 3.11, 3.12, 3.13, 3.14+)
- Windows, macOS, or Linux

### Install Dependencies
Open PowerShell or your command prompt in the project root:

```bash
pip install -r requirements.txt
```

*(Dependencies: `pygame-ce>=2.5.0` or `pygame>=2.5.0`, and `numpy>=1.20.0`)*

### Run the Game
```bash
python main.py
```

### Run the Verification Test Suite
```bash
python tests_verify_all.py
```

---

## 2. Controls & Input Schemes

### Single Player Mode (Simultaneous Dual-Scheme)
Both WASD and Arrow Keys are active simultaneously:

| Action | Primary Key | Secondary Key |
| :--- | :---: | :---: |
| **Accelerate** | `W` | `UP ARROW` |
| **Brake / Reverse** | `S` | `DOWN ARROW` |
| **Steer Left** | `A` | `LEFT ARROW` |
| **Steer Right** | `D` | `RIGHT ARROW` |
| **Cycle Camera (3 Modes)** | `C` | `C` |
| **Pause / Resume** | `ESC` | `ESC` |

### Two-Player Split-Screen Mode
True vertical (Left and Right) split-screen with independent viewports:

| Control | Player 1 (Left Viewport: 640x720) | Player 2 (Right Viewport: 640x720) |
| :--- | :---: | :---: |
| **Vehicle** | Crimson Red Sports Car | Cobalt Blue Sports Car |
| **Accelerate** | `W` | `UP ARROW` |
| **Brake / Reverse** | `S` | `DOWN ARROW` |
| **Steer Left** | `A` | `LEFT ARROW` |
| **Steer Right** | `D` | `RIGHT ARROW` |
| **Cycle Camera** | `C` | `V` or `M` |
| **Pause Game** | `ESC` | `ESC` |

---

## 3. Game Modes & Architecture

1. **SINGLE PLAYER**: 1 human racer competing against 5 intelligent AI opponents across 3 laps.
2. **TWO PLAYERS**: True horizontal split-screen where Player 1 (top half) and Player 2 (bottom half) race in the exact same 3D track world with independent cameras, speeds, fuel, and HUDs alongside 4 AI competitors.
3. **HOW TO PLAY**: Clean visual guide displaying keybindings, fuel mechanics, and track rules.
4. **MAP SELECTION**: Interactive track chooser with real-time course preview snapshots, lap records, and difficulty indicators.
5. **PAUSE MENU**: Press `ESC` during racing to resume, restart, or return to the main menu.
6. **RESULTS SCREEN**: Podium leaderboard table showing driver rankings, total race times, and best lap times.

---

## 4. Championship Tracks

### 1. Coastal Bayway (Beach Map)
- **Theme**: Tropical coastline, azure ocean horizon, golden sand dunes, palm trees, beach boulders.
- **Track Layout**: Smooth sweeping curves, ocean boulevards, gentle seaside crests.
- **Obstacles**: Coastal rocks, hazard barrels, orange traffic cones.

### 2. Alpine Ridge Pass (Hills Map)
- **Theme**: Mountain pass, alpine pine forests, snow-capped peaks, rugged granite boulders.
- **Track Layout**: Severe vertical elevations (climbs and roller-coaster downhill plunges up to 1100 world units), hairpin turns, forest chicanes.
- **Obstacles**: Fallen mountain boulders, construction barriers, oil slicks.

### 3. Neon Metropolis (City Night Map)
- **Theme**: Cyberpunk nocturnal street circuit, starry midnight sky, illuminated skyscrapers, glowing streetlights casting light cones.
- **Track Layout**: 90-degree city intersections, high-speed overpasses, glowing neon curbs.
- **Obstacles**: Roadwork barriers, traffic barrels, slippery oil patches, cones.

---

## 5. Dynamic Camera System

Cycle seamlessly in real time using the `C` key (or `V`/`M` for Player 2):

1. **CAMERA 1 — NORMAL (3rd Person Chase)**:
   - Balanced height and depth for classic arcade racing.
2. **CAMERA 2 — FRONT (Low / Chase Hood)**:
   - Low camera altitude positioned closer to the chassis front, maximizing forward road visibility at high speeds.
3. **CAMERA 3 — EXTENDED (High / Wide)**:
   - Elevated camera pulled farther back with a wider perspective, ideal for anticipating sharp hairpin turns and spotting nearby traffic.

The camera incorporates **smooth spring-damper following (lerp)** to simulate vehicle momentum, and **trauma screen shake** on collisions.

---

## 6. Project Architecture

```text
Project_anti/
│
├── main.py                   # Game launch entry point
├── requirements.txt          # Pygame-ce and NumPy dependencies
├── tests_verify_all.py       # Automated unit test suite (14 criteria)
├── README.md                 # Project documentation & Viva Guide
│
├── game/
│   ├── __init__.py           # Package initialization
│   ├── settings.py           # World geometry, physics constants, color palettes
│   ├── game.py               # Main Game controller & state dispatcher
│   ├── states.py             # Menu, Map Select, Racing, Pause, Results states
│   ├── player.py             # Player input controller (WASD / Arrows)
│   ├── car.py                # Vehicle kinematics, fuel, procedural sprite drawing
│   ├── ai.py                 # Road-aware opponent AI with curve deceleration
│   ├── track.py              # Track segment queries and spatial partitioning
│   ├── camera.py             # 3D view camera, presets, and trauma shake
│   ├── collision.py          # AABB collision detection & momentum impulse
│   ├── fuel.py               # Fuel depletion and canister respawn logic
│   ├── renderer.py           # Pseudo-3D perspective projection & rasterizer
│   ├── hud.py                # Speedometer, fuel gauge, minimap radar, countdown
│   ├── props.py              # Procedural vector scenery and obstacle sprites
│   └── sound.py              # Real-time procedural audio synthesizer (NumPy)
│
├── maps/
│   ├── __init__.py           # Map catalog export
│   ├── base_map.py           # Base road generator, spline easing, minimap projection
│   ├── beach.py              # Coastal Bayway map definition
│   ├── hills.py              # Alpine Ridge Pass map definition
│   └── city.py               # Neon Metropolis map definition
│
└── assets/                   # Optional external asset folder (fully procedural by default)
    ├── cars/
    ├── environment/
    ├── fonts/
    └── sounds/
```

---

## 7. Computer Graphics Viva Examination Guide

This section is prepared for your Computer Graphics viva examination:

### Q1: How is the pseudo-3D road rendered?
> **Answer**: The road is represented as a sequence of cross-sectional 3D segments, each defined by an entry point $P_1(x_1, y_1, z_1)$ and an exit point $P_2(x_2, y_2, z_2)$. Each frame, the road is projected from near to far. Trapezoids are rasterized between projected segment slices to draw the off-road terrain, colored rumble curbs, asphalt road surface, and center dashed lane markings. Segments are drawn from the bottom of the screen toward the horizon using scanline trapezoid polygons.

### Q2: How does the pseudo-3D perspective projection work?
> **Answer**: We use the standard pinhole camera perspective projection model. Given a 3D world coordinate $(X, Y, Z)$ and camera position $(C_x, C_y, C_z)$:
> 1. Calculate relative coordinates: $\Delta x = X - C_x$, $\Delta y = Y - C_y$, $\Delta z = Z - C_z$.
> 2. Calculate perspective depth scale: $\text{scale} = \frac{d}{\Delta z}$, where $d = \frac{1}{\tan(\text{FOV}/2)}$ is the focal distance.
> 3. Map into 2D viewport coordinates:
>    $$\text{Screen}_X = \frac{W}{2} + \text{scale} \cdot \Delta x \cdot \frac{W}{2}$$
>    $$\text{Screen}_Y = \frac{H}{2} - \text{scale} \cdot \Delta y \cdot \frac{H}{2}$$
>    $$\text{Projected Road Width} = \text{scale} \cdot \text{RoadWidth} \cdot \frac{W}{2}$$
> Because scale is inversely proportional to depth ($S \propto 1/z$), distant road segments and objects naturally appear smaller and converge toward the horizon.

### Q3: How does car rotation and steering tilt work?
> **Answer**: Car rotation utilizes a 2D Affine Rotation Transformation matrix:
> $$\begin{bmatrix} x' \\ y' \end{bmatrix} = \begin{bmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{bmatrix} \begin{bmatrix} x \\ y \end{bmatrix}$$
> When the player steers left or right, a dynamic tilt angle $\theta$ is applied to the vehicle sprite based on lateral acceleration. This simulates body roll, weight transfer, and angled front wheels.

### Q4: How does collision detection and response work?
> **Answer**: Collision detection uses an Axis-Aligned Bounding Box (AABB) hierarchy across both the longitudinal $Z$ coordinate (depth down the track) and normalized lateral coordinate $X \in [-1, 1]$:
> 1. A collision is flagged if $|\text{car}_z - \text{obs}_z| < \Delta Z_{\text{hitbox}}$ and $|\text{car}_x - \text{obs}_x| < \Delta X_{\text{hitbox}}$.
> 2. For car-to-car impacts, an elastic impulse response separates overlapping vehicles laterally ($\Delta x$) and exchanges forward kinetic momentum so that neither car clips through the other.
> 3. Hitting obstacles reduces speed by a fraction, applies a lateral push impulse, decrements a small percentage of fuel, and triggers a trauma screen-shake effect.

### Q5: How does the AI pathing and curve negotiation work?
> **Answer**: The AI calculates target speed and lane positioning using lookahead radar:
> 1. **Curve Anticipation**: The AI inspects the curvature $k$ of upcoming segments 1200 units ahead. Safe cornering speed is computed as $v_{\text{safe}} = \frac{v_{\text{max}}}{1 + |k|^{1.3} \cdot 0.40}$. If current speed exceeds $v_{\text{safe}}$, the AI applies brakes before entering the turn.
> 2. **Lane Overtaking**: AI cars scan ahead for cars or obstacles in their lane. If an obstacle is detected within 1800 units, they smoothly interpolate their target lateral coordinate toward an open lane.

### Q6: How does the fuel system affect gameplay?
> **Answer**: The vehicle starts with $100\%$ fuel. Fuel consumption is simulated with a differential rate:
> $$\frac{dF}{dt} = F_{\text{base}} + F_{\text{speed}} \cdot \left(\frac{v}{v_{\text{max}}}\right)$$
> High speed drains fuel faster. When fuel drops below $25\%$, an alert flashes on the HUD. If fuel reaches $0\%$, the engine enters limp mode, capping top speed to $52\text{ km/h}$ until the player collects a $+20\text{ Fuel}$ canister.

### Q7: How does true horizontal split-screen work?
> **Answer**: The main window surface ($1280 \times 720$) is partitioned into two distinct subsurfaces ($1280 \times 360$ each):
> - **Top Half**: Rendered using Player 1's camera position $C_1(x, y, z)$.
> - **Bottom Half**: Rendered using Player 2's camera position $C_2(x, y, z)$.
> Both viewports render the exact same 3D race world. If Player 2 is within Player 1's view frustum, Player 2's blue car is rendered with perspective scale on Player 1's screen, and vice versa. Each half maintains its own independent HUD telemetry.

### Q8: How do the camera modes work?
> **Answer**: The virtual camera has three degrees of freedom: height ($Y$), depth ($d$), and distance behind the vehicle.
> - **Normal**: Standard eye height ($Y=1050$, $d=0.84$).
> - **Front**: Low hood view ($Y=720$, $d=0.92$), lowering the horizon to show road ahead.
> - **Extended**: High panoramic viewpoint ($Y=1450$, $d=0.76$), raising the horizon for wide-angle curve visibility.
> Switching between presets uses linear interpolation (lerp) so the camera transitions smoothly.

### Q9: Which 2D transformations are demonstrated in the project?
> **Answer**:
> 1. **Translation**: Shifting world coordinates to camera coordinates ($X - C_x$, $Y - C_y$, $Z - C_z$) and screen offsets.
> 2. **Scaling**: Distance-based perspective scaling ($S = d / \Delta z$) applied to road width, cars, and roadside scenery.
> 3. **Rotation**: Affine rotation matrices applied to vehicle sprites during steering maneuvers.
> 4. **Orthographic Projection**: Projecting 3D track curvatures into a closed 2D loop on the minimap radar.

### Q10: Which general Computer Graphics concepts are demonstrated?
> **Answer**:
> - **Perspective Projection & Division**: Pinhole camera scaling inversely proportional to depth.
> - **Scanline Polygon Rasterization**: Trapezoidal strip drawing between entry and exit slice coordinates.
> - **Hidden Surface Removal & Occlusion Clipping**: Tracking the minimum horizon line ($Y_{\text{max}}$) to prevent drawing road segments obscured by hills.
> - **Painter's Algorithm**: Depth-sorting billboards, obstacles, and opponent vehicles from back to front ($Z_{\text{far}} \to Z_{\text{near}}$).
> - **Parallax Scrolling**: Layered multi-speed background scrolling to convey optical depth.
> - **Spline Curve Interpolation**: Smooth ease-in, hold, and ease-out transitions for curved track segments.
> - **Alpha Blending & Lighting**: Translucent drop shadows beneath vehicles and glowing headlight cones for night racing.

---

## 8. License & Academic Attribution
Created for Computer Graphics mini-project submission. Free to use, modify, and extend for educational purposes.
=======
# Turbo_Apex_Game
>>>>>>> 8210363b80ccde7dae91cc5e18a6f57828839181
