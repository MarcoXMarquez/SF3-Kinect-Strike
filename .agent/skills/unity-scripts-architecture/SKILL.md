---
name: unity-scripts-architecture
description: Reglas y taxonomía de organización de directorios de scripts C# en Unity para Street Fighter III: 3rd Strike (separación por capas: Core, Combat, Fighters, Input, Audio, UI, Testing, Editor).
---

# Unity Scripts Architecture Skill
## Taxonomía y Organización Modular de Scripts C# para Street Fighter III

Esta habilidad establece la estructura de directorios canónica, las reglas de desacoplamiento y los criterios de clasificación para cualquier script nuevo de C# en el proyecto.

---

## 1. Ubicación Raíz Canónica

Todo el código fuente C# del proyecto debe residir estrictamente en:
📁 **`Assets/StreetFighter3_ThirdStrike/Scripts/`**

Está **prohibido** dispersar scripts en carpetas de sprites de personajes (`Characters/`), carpetas de escenarios (`Stages/`) o en la raíz de `Assets/`.

---

## 2. Taxonomía de Directorios Estándar

```text
Assets/StreetFighter3_ThirdStrike/Scripts/
│
├── Core/                      # Gestión global, Game Loop y managers del juego
│   ├── GameManager.cs         # Control de rondas, tiempo, pausas y flujo de combate
│   └── CameraController.cs    # Cinemachine Target Group, encuadre P1/P2 y Screen Shake
│
├── Combat/                    # Motor de combate compartido por todos los personajes
│   ├── FighterHurtbox.cs         # Caja receptora de daño (Trigger)
│   ├── FighterHitbox.cs          # Caja de impacto activa (Trigger)
│   ├── FighterCombatColliders.cs # Coordinador para Animation Events
│   ├── FrameData/                # ScriptableObjects de frame data (Startup, Active, Recovery)
│   └── DamageSystem/             # Fórmulas de daño, escalado de combos, bloqueo
│
├── Fighters/                  # Lógica y control específico de luchadores
│   ├── Base/                  # Clases base reutilizables
│   │   ├── FighterController.cs      # Controlador maestro del personaje
│   │   ├── FighterStateMachine.cs    # Motor FSM desacoplado (animator.Play)
│   │   └── FighterState.cs           # Clase base abstracta de estados
│   ├── States/                # Estados concretos reutilizables
│   │   ├── IdleState.cs              # Estado de reposo / guardia
│   │   ├── WalkState.cs              # Movimiento adelante / atrás
│   │   ├── AttackState.cs            # Ejecución de golpes
│   │   ├── HitstunState.cs           # Reacción a impactos recibidos
│   │   └── BlockState.cs             # Bloqueo y Parries
│   └── Overrides/             # Mecánicas únicas de personajes (ej. Denjin charge de Ryu)
│
├── Input/                     # Capa de entrada abstracta (Teclado, Mandos, Kinect)
│   ├── IFighterInput.cs       # Interfaz contractual de entrada
│   ├── KeyboardFighterInput.cs # Implementación de prueba para teclado
│   ├── GamepadFighterInput.cs  # Implementación Unity Input System (Arcade Sticks)
│   ├── KinectFighterInput.cs   # Implementación para sensor Kinect v2 / MediaPipe
│   └── InputBuffer.cs          # Reconocedor de comandos direccionales (236P, 623P)
│
├── Audio/                     # Sonido, música y locución
│   ├── SF3SoundManager.cs     # Singleton de audio arcade
│   └── AudioDucking.cs        # Atenuación de música con el anunciador
│
├── Environment/               # Escenarios y fondos
│   └── ParallaxBackground.cs  # Desplazamiento 2.5D por capas
│
├── UI/                        # Interfaz gráfica y HUD de combate
│   ├── FightHUD.cs            # Barras de vida, barras de Super Art (EX)
│   ├── ComboCounterUI.cs      # Contador de impactos ("3 HITS!")
│   └── MainMenuController.cs  # Selección de personaje y menús
│
├── Testing/                   # Herramientas de depuración en tiempo de ejecución
│   ├── FighterAnimationTester.cs # Disparador de animaciones por teclas (sin flechas)
│   └── FrameStepper.cs           # Pausar y avanzar 1 fotograma (P / F)
│
└── Editor/                    # Herramientas exclusivas del Editor de Unity
    ├── SF3AnimationBatchCreator.cs # Creador automático de .anim a 14 FPS
    └── SF3AutoSpriteImporter.cs    # Importador automático Pixel-Perfect
```

---

## 3. Matriz de Decisión: ¿Dónde debe ir mi script?

| Si tu script se encarga de... | Colócalo en: |
| :--- | :--- |
| Administrar el estado general de la partida, rondas o cámara | `Scripts/Core/` |
| Cajas de impacto, cálculo de daño, hurtboxes o parries | `Scripts/Combat/` |
| El movimiento del personaje, su FSM o scripts específicos de un luchador | `Scripts/Fighters/` |
| Leer teclas, mandos, palancas arcade o sensores Kinect | `Scripts/Input/` |
| Música de fondo, efectos de impacto o voces | `Scripts/Audio/` |
| Movimiento de capas de fondo, parallax o props de escenario | `Scripts/Environment/` |
| Barras de vida, textos de combo, menús o pantallas de victoria | `Scripts/UI/` |
| Pruebas rápidas con teclado, atajos de depuración o gizmos | `Scripts/Testing/` |
| Menús de Unity (`[MenuItem]`), wizards o `AssetPostprocessor` | `Scripts/Editor/` |

---

## 4. Reglas Estrictas de Programación y Desacoplamiento

1. **Regla 1:1 de MonoBehaviour**:
   El nombre de la clase pública que hereda de `MonoBehaviour` debe ser idéntico al nombre del archivo `.cs`.
2. **Desacoplamiento de Hardware mediante `IFighterInput`**:
   Los scripts de combate y movimiento nunca deben llamar a `Input.GetKeyDown()` directamente; siempre deben consultar la interfaz `IFighterInput`.
3. **Máquina de Estados en Código sobre Flechas de Animator**:
   Para proyectos de combate con 70+ animaciones por personaje, evitar el cableado masivo de transiciones con flechas en el Animator. Utilizar la máquina de estados en C# con `animator.Play(animName, 0, 0f)`.
4. **Scripts de Editor estrictamente aislados**:
   Cualquier script que utilice `using UnityEditor;` debe estar alojado en `Scripts/Editor/` para evitar errores de compilación al generar el ejecutable (Build).
