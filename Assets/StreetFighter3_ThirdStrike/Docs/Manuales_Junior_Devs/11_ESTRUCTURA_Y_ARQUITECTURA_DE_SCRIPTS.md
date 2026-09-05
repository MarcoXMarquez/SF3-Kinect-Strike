# 📁 Guía 11: Estructura y Arquitectura de Scripts
## Organización Modular de Código C# para Street Fighter III en Unity

Cuando un juego tiene **20 luchadores distintos**, decenas de escenarios, audio dinámico, interfaz de combate y control por movimiento corporal (**Kinect**), dejar los scripts desordenados en una sola carpeta crea caos y dependencias circulares.

En esta guía aprenderás **la arquitectura estándar de carpetas de scripts del proyecto**, la matriz de decisión para saber exactamente dónde crear cada nuevo script y cómo probar animaciones de forma limpia.

---

## 📍 1. La Ubicación Raíz Oficial

Todo el código C# del proyecto vive en:
📂 **`Assets/StreetFighter3_ThirdStrike/Scripts/`**

> [!CAUTION]
> **Prohibido colocar scripts fuera de esta carpeta:**
> No guardes scripts dentro de las carpetas de imágenes (`Characters/`), en escenarios (`Stages/`) ni sueltos en `Assets/`. Mantener todo en `Scripts/` permite que cualquier programador del equipo encuentre el código al instante.

---

## 🌳 2. El Árbol de Carpetas Oficial de Scripts

```text
Assets/StreetFighter3_ThirdStrike/Scripts/
│
├── Core/                      # Gestión global, Game Loop y managers del juego
│   ├── GameManager.cs         # Control de asaltos, tiempo (Round 1, Fight, K.O.)
│   └── CameraController.cs    # Cinemachine Target Group, encuadre dinámico y screenshake
│
├── Combat/                    # Motor de combate compartido por todos los 20 luchadores
│   ├── FighterHurtbox.cs         # Caja receptora de daño (Trigger)
│   ├── FighterHitbox.cs          # Caja de impacto activa (Trigger)
│   ├── FighterCombatColliders.cs # Coordinador que enciende/apaga Hitboxes por Animation Events
│   ├── FrameData/                # ScriptableObjects de frame data (Startup, Active, Recovery)
│   └── DamageSystem/             # Fórmulas de daño, escalado de combos y bloqueo
│
├── Fighters/                  # Lógica y control específico de luchadores
│   ├── Base/                  # Clases base reutilizables
│   │   ├── FighterController.cs      # Controlador maestro del personaje
│   │   ├── FighterStateMachine.cs    # Motor FSM (controla estados con animator.Play)
│   │   └── FighterState.cs           # Clase base abstracta de cada estado
│   ├── States/                # Estados concretos reutilizables
│   │   ├── IdleState.cs              # Estado de reposo / guardia
│   │   ├── WalkState.cs              # Movimiento adelante / atrás
│   │   ├── AttackState.cs            # Ejecución de ataques
│   │   ├── HitstunState.cs           # Reacción a golpes recibidos
│   │   └── BlockState.cs             # Bloqueo y Parries
│   └── Overrides/             # Mecánicas únicas de personajes (ej. carga Denjin de Ryu)
│
├── Input/                     # Capa de entrada abstracta (Puente Teclado <-> Gamepad <-> Kinect)
│   ├── IFighterInput.cs       # Contrato de entrada (desacopla hardware de jugabilidad)
│   ├── KeyboardFighterInput.cs # Implementación para teclado/laptop
│   ├── GamepadFighterInput.cs  # Implementación Unity Input System (Fightsticks/Mandos)
│   ├── KinectFighterInput.cs   # Implementación para sensor de movimiento (Kinect / MediaPipe)
│   └── InputBuffer.cs          # Reconocedor de comandos direccionales (236P, 623P)
│
├── Audio/                     # Sonido, música y locución
│   ├── SF3SoundManager.cs     # Singleton de audio arcade
│   └── AudioDucking.cs        # Atenuación de música cuando el anunciador habla
│
├── Environment/               # Escenarios, fondos y props
│   └── ParallaxBackground.cs  # Desplazamiento 2.5D por capas
│
├── UI/                        # Interfaz gráfica y HUD de combate
│   ├── FightHUD.cs            # Barras de vida, barras de Super Art (EX)
│   ├── ComboCounterUI.cs      # Contador de impactos ("3 HITS!")
│   └── MainMenuController.cs  # Selección de personaje y menús
│
├── Testing/                   # Herramientas y scripts de depuración en tiempo de ejecución
│   ├── FighterAnimationTester.cs # Probador de animaciones con teclas en vivo (sin flechas)
│   └── FrameStepper.cs           # Pausar y avanzar 1 fotograma (P / F)
│
└── Editor/                    # Herramientas exclusivas del Editor de Unity
    ├── SF3AnimationBatchCreator.cs # Creador automático de .anim a 14 FPS
    └── SF3AutoSpriteImporter.cs    # Importador automático Pixel-Perfect
```

---

## 🧭 3. Matriz de Decisión: ¿Dónde debo guardar mi nuevo script?

Hazte esta simple pregunta antes de crear un archivo `.cs`:

| Si el script se encarga de... | Su carpeta obligatoria es: | Ejemplo |
| :--- | :--- | :--- |
| Administrar el estado general de la partida, rondas o cámara | `Scripts/Core/` | `GameManager.cs` |
| Detección de colisiones, cálculo de daño, parries o hitboxes | `Scripts/Combat/` | `FighterHurtbox.cs` |
| Movimiento del personaje, su máquina de estados o ataques | `Scripts/Fighters/` | `FighterController.cs` |
| Leer controles (teclas, mandos USB o Kinect) | `Scripts/Input/` | `KeyboardFighterInput.cs` |
| Reproducir música o efectos de sonido | `Scripts/Audio/` | `SF3SoundManager.cs` |
| Efectos del fondo del escenario o parallax | `Scripts/Environment/` | `ParallaxBackground.cs` |
| Dibujar barras de vida, textos de combo o pantallas de menú | `Scripts/UI/` | `FightHUD.cs` |
| Pruebas temporales de depuración con teclado | `Scripts/Testing/` | `FighterAnimationTester.cs` |
| Menús de Unity (`[MenuItem]`) o scripts de importación | `Scripts/Editor/` | `SF3AutoSpriteImporter.cs` |

---

## 🕹️ 4. Cómo Probar Animaciones Inmediatamente (Sin Flechas en Animator)

Para no perder tiempo dibujando cientos de flechas en el Animator, hemos creado el script:
📂 **`Scripts/Testing/FighterAnimationTester.cs`**

### Instrucciones de uso rápido:
1. En la ventana **Hierarchy**, selecciona tu GameObject **`Fighter_Ryu`**.
2. Haz clic en **Add Component** ➔ escribe y añade **`FighterAnimationTester`**.
3. Asegúrate de que el campo **Animator** apunte al componente Animator (en `Visuals`).
4. Presiona el botón de **Play `▶`** de Unity.
5. Verás una guía visual en la esquina superior izquierda de la pantalla y podrás disparar las animaciones con el teclado:
   * `[Espacio]` : `idle_stance` (Reposo)
   * `[D]` / `[A]` : `walk_forward` / `walk_backward`
   * `[S]` / `[W]` : `crouch_idle` / `jump_neutral`
   * `[J]` : `light_punch` (Puñetazo)
   * `[K]` : `heavy_punch`
   * `[U]` : `fireball` (Hadouken)
   * `[I]` : `shoryuken`
   * `[P]` : `parry_standing`
   * `[H]` : `hit_standing` (Dolor / Reacción)

---

## 👟 5. Cómo Calibrar el Pivote del Pie Paso a Paso (Sin Scripts Mágicos)

Como aprendiste, cuando Ryu pasa de estar quieto a dar un puñetazo, su imagen pasa de **78 píxeles** a **121 píxeles de ancho** porque el lienzo crece hacia adelante para darle espacio al brazo.

Si el pivote está en `Center` ($50\%$), el punto de apoyo se mueve hacia adelante y el cuerpo salta hacia atrás. Para corregirlo manualmente tú mismo:

1. En la ventana **Project**, selecciona la imagen del golpe (ej. `02_Normals/light_punch/0.png`).
2. En el **Inspector**, haz clic en el botón **Sprite Editor** (si no lo tienes, instálalo desde `Package Manager > 2D Sprite`).
3. Verás la imagen grande de Ryu con un círculo azul y un punto blanco en la base: **ese es el pivote**.
4. En el panel flotante del Sprite Editor, en el desplegable **Pivot**, cámbialo de *Bottom* a **`Custom`**.
5. Mueve la coordenada **Pivot X**:
   * En lugar de `0.5`, arrastra el punto blanco horizontalmente hasta que quede **exactamente debajo del talón del pie de apoyo de Ryu**.
   * *(En `light_punch`, el valor exacto suele ser alrededor de `0.32` en lugar de `0.50`)*.
6. Haz clic en el botón **Apply** arriba a la derecha del Sprite Editor.
7. ¡Listo! Ahora cuando Ryu lance el puño, su talón permanecerá clavado en el suelo sin desplazarse ni un solo milímetro.
