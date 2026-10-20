# 📡 Estado Vivo y Changelog del Proyecto (Live Synchronization)
## KINET STRIKE (Unity + Azure Kinect + IA Adaptativa)

Este documento es la **fuente única de verdad en tiempo real** del proyecto. Cada vez que un desarrollador (Marco, Sebas o Kevin) y su asistente de IA completen una tarea, creen un nuevo script, refactoricen o eliminen algo, **DEBEN actualizar este archivo**.

Al hacer `git pull origin main`, todos los asistentes de IA leerán este documento para sincronizarse automáticamente con los avances del equipo.

---

### 📊 Resumen de Estado Actual del Proyecto (Sprint 1 Activo)

* **Sprint Activo:** Sprint 1 (Sep 7 – Sep 20, 2026)
* **Rama Principal:** `main`
* **Luchadores en Desarrollo:**
  - 👑 **Ryu (`02_Ryu` - Marco):** 64 AnimationClips sincronizados en `Ryu_Animator.controller`, probador interactivo de teclado `FighterAnimationTester.cs` listo.
  - 🔥 **Ken (`01_Ken` - Sebas):** Listo para organizar en 7 categorías y generar clips a 14 FPS.
  - ⚡ **Chun-Li (`03_ChunLi` - Kevin):** Listo para organizar en 7 categorías y generar clips a 14 FPS.

---

### 📝 Registro de Componentes y Scripts Creados

| Script / Asset | Ruta | Creado / Modificado Por | Propósito |
| :--- | :--- | :---: | :--- |
| `SF3AnimationBatchCreator.cs` | `Scripts/Editor/` | Marco | Generación de clips a 14 FPS y Auto-Populate del Animator en 1 clic. |
| `SF3AutoSpriteImporter.cs` | `Scripts/Editor/` | Marco | Importador automático con Point Filter, Uncompressed y BottomCenter. |
| `FighterAnimationTester.cs` | `Scripts/Testing/` | Marco | Probador de estados, ataques con retorno automático a idle y locomoción. |
| `FighterHurtbox.cs` | `Scripts/Combat/` | Marco | Componente de recepción de daño (cabeza, torso, piernas). |
| `FighterHitbox.cs` | `Scripts/Combat/` | Marco | Componente de ataque activo. |
| `FighterCombatColliders.cs` | `Scripts/Combat/` | Marco | Coordinador de activación/desactivación de hitboxes y voces. |
| `ParallaxBackground.cs` | `Scripts/Environment/` | Sebas / Marco | Scroll con efecto de profundidad 2.5D para escenarios. |
| `SF3JapanStageBuilder.cs` | `Scripts/Editor/` | Sebas | Generador del escenario Suzaku Castle (Japón) con Parallax y suelo físico Y=0. |
| `SF3ChinaStageBuilder.cs` | `Scripts/Editor/` | Sebas | Generador del escenario Crowded Street (China) con Parallax, límites de arena y props animados. |
| `AnimatedSpriteProp.cs` | `Scripts/Environment/` | Sebas | Controlador de props y espectadores vivos a 14 FPS para escenarios CPS-3. |
| `Stage_China.prefab` | `Prefabs/` | Sebas | Prefab oficial reutilizable del escenario de China con colisionadores y capas 2D. |
| `Sandbox_China.unity` | `Scenes/` | Sebas | Escena de combate independiente para duelos en el escenario de China con BGM oficial. |
| `IFighterInput.cs` | `Scripts/Input/` | Kevin | Interfaz desacoplada para desacoplar el origen de entrada (Teclado/Kinect/IA) del luchador. |
| `KeyboardFighterInput.cs` | `Scripts/Input/` | Kevin | Adaptador de teclado para locomoción, ataques normales y emulación de gestos. |
| `AzureKinectInput.cs` | `Scripts/Input/` | Kevin | Adaptador somatosensorial de Azure Kinect con cálculo cinemático de articulaciones 3D. |
| `AzureKinectBodyTracker.cs` | `Scripts/Input/` | Kevin | Conector del hardware Azure Kinect y Body Tracking SDK para Unity. |
| `KinectPoseMatcher.cs` | `Scripts/Input/` | Kevin | Comparador de poses calibradas en tiempo real desde JSON con cálculo de similitud (%). |
| `sf3_kinect_sagittal_visualizer.py` | `Tools/` | Kevin | Visualizador OpenCV con grabación dinámica de clips (35 frames), mini-video player en bucle, gestión de 10 sujetos y modo mockup (--mock). |
| `gesture_feature_extractor.py` | `Tools/` | Kevin | Extractor matemático de cinemática 3D: normalización local, ángulos relativos, velocidades instantáneas y 26 métricas agregadas por clip. |
| `train_gesture_classifier.py` | `Tools/` | Kevin | Entrenador de Random Forest con GroupKFold por sujeto, exportador ONNX a Unity Models y generador sintético. |
| `gesture_classifier.onnx` | `Assets/.../Models/` & `Tools/` | Kevin | Modelo tabular supervisado optimizado para inferencia en Unity Sentis / Python. |
| `clean_dataset_outliers.py` | `Tools/` | Kevin | Limpiador de outliers e interpolador de discontinuidades ToF con filtro 1€ adaptativo. |
| `test_live_gesture_classifier.py` | `Tools/` | Kevin | Testeador terminal interactivo de inferencia y auditor de sesgos/probabilidades por clase. |
| `test_live_kinect_classifier.py` | `Tools/` | Kevin | Detector somatosensorial en vivo con Azure Kinect físico y panel visual HUD de sesgos (7 clases). |
| `record_transition_graph.py` | `Tools/` | Kevin | Estudio de transiciones y combos con perspectiva DUAL (Frontal + Sagital), modo práctica libre, telemetría cinemática, creación ilimitada de nuevos sujetos en la UI y matriz 7x7 (42 aristas). |
| `DuelFighter.cs` | `Scripts/Combat/` | Sebas | Controlador de combate 2D con Rigidbody2D, orientación, animaciones, bloqueo frontal y hurtboxes (cabeza, torso, piernas). |
| `DuelRoster.cs` | `Scripts/Combat/` | Sebas | ScriptableObject que almacena 21 secuencias de sprites por personaje (230 Ken, 256 Ryu). |
| `JapanDuel.cs` | `Scripts/Combat/` | Sebas | Gestor del duelo local Ken vs. Ryu en Suzaku Castle (rondas, HUD de vida, KO y revancha). |
| `JapanDuelValidation.cs` | `Scripts/Editor/` | Sebas | Validador automatizado en Play Mode del duelo (`SF3 Tools > Validate Local Duel`). |
| `SF3JapanStageBuilder.cs` | `Scripts/Editor/` | Sebas | Constructor y ensamblador del escenario de Japón (Suzaku Castle) con parallax y colliders. |
| `StageParallaxTester.cs` | `Scripts/Testing/` | Sebas | Script de prueba de cámara para validar el desplazamiento de capas de parallax. |
| `SF3ChromaKeySprite.shader` | `Shaders/` | Sebas | Shader de ChromaKey para eliminación de fondos en sprites del escenario. |
| `ISteeringAgent.cs` | `Scripts/AI/Steering/` | Kevin | Contrato cinemático para entidades con aceleración de dirección (Reynolds). |
| `ISteeringBehavior.cs` | `Scripts/AI/Steering/` | Kevin | Contrato desacoplado para algoritmos de cálculo de fuerzas vectoriales de dirección. |
| `SeekBehavior.cs` | `Scripts/AI/Steering/` | Kevin | Algoritmo clásico de Persecución (Seeking) de Craig Reynolds con frenado suave de llegada. |
| `WanderBehavior.cs` | `Scripts/AI/Steering/` | Kevin | Algoritmo clásico de Merodeo (Wandering) de Craig Reynolds con círculo virtual y variación angular. |
| `SteeringUIEntity.cs` | `Scripts/AI/Steering/` | Kevin | MonoBehaviour cinemático para mover entidades en Canvas UI con rebote elástico perimetral. |
| `MainMenuController.cs` | `Scripts/UI/` | Kevin | Menú principal interactivo 100% navegable con teclado, submenú Versus (Bot / 2P) y SFX arcade. |
| `LoadingScreenController.cs` | `Scripts/UI/` | Kevin | Controlador de pantalla de carga asíncrona, barra de progreso y orquestador del minijuego. |
| `LoadingMinigameManager.cs` | `Scripts/UI/` | Kevin | Administrador del minijuego estilo DBZ Tenkaichi 3 que coordina orbes Wandering y buscador Seeking. |
| `MiniFighterController.cs` | `Scripts/UI/` | Kevin | Avatar 2D jugable en la pantalla de carga (movimiento horizontal, salto, golpe y animación de Ryu). |
| `FightHUD.cs` | `Scripts/UI/` | Marco / Sebas | HUD de combate arcade (barras de vida P1/P2 con daño retardado y contador central de 99s). |
| `TenkaichiDialogueManager.cs` | `Scripts/UI/` | Marco / Kevin | Sistema de cinemáticas y diálogos estilo DBZ Budokai Tenkaichi 3 con lore original de KINET STRIKE y selector de episodios. |
| `Stage_Tomb.prefab` | `Prefabs/` | Sebas / Marco | Prefab oficial del escenario Tumba Olímpica (Grecia) con columnas de mármol y BGM de Urien. |
| `Fighter_Urien.prefab` | `Prefabs/` | Marco | Prefab de Urien con Animator CPS-3 a 14 FPS, Aegis Reflector, Chariot Rush y Super Art. |
| `Sandbox_Tomb.unity` | `Scenes/` | Sebas / Marco | Escena de combate versus en la Tumba Olímpica de Urien con HUD y música oficial. |
| `StoryMode_Scene.unity` | `Scenes/` | Marco / Kevin | Escena del Modo Historia con cinemáticas y diálogos estilo DBZ Budokai Tenkaichi 3. |
| `SF3MainMenuBuilder.cs` | `Scripts/Editor/` | Kevin | Generador automatizado de la escena `MainMenu_Scene.unity` y sincronizador de `EditorBuildSettings`. |

---

### ⚠️ Elementos Obsoletos / Deprecados (NO USAR)

* ❌ **Flechas con `Has Exit Time` en Mecanim:** Prohibido usar transiciones con flechas para ataques. Usar siempre `animator.Play(clipName, 0, 0f)`.
* ❌ **Recortar PNGs a mano (*Tight Crop*):** Prohibido alterar las dimensiones originales de los lienzos arcade.
* ❌ **Pivotes en el centro (*Center*):** Todos los sprites deben usar `BottomCenter` ($X=0.5, Y=0$) o Custom Pivot documentado.

---

### 🔄 Historial de Cambios Recientes (Changelog)

* **2026-10-13 (Red de Transiciones Dirigidas 7x7 y Estudio de Grabación Cinemática):**
  - **Estudio de Transiciones (`Tools/record_transition_graph.py`):** Creada herramienta especializada con interfaz gráfica OpenCV y renderizado sagital/frontal retro CPS-3 para capturar secuencias continuas entre movimientos sin retorno intermedio a reposo.
  - **Matriz de Continuidad 7x7 (42 Aristas Dirigidas):** Modeladas todas las posibles transiciones entre las 7 acciones maestras (`idle`, `punch_right`, `punch_left`, `kick_right`, `kick_left`, `crouch`, `block`), con selector interactivo y contador de repeticiones en tiempo real.
  - **Simulador Cinemático Procedural (`--mock`):** Generador de esqueleto continuo a 30 FPS que emula la curva bimodal de intercambio de energía cinética ($A_{\text{pico}} \rightarrow T_{A \rightarrow B} \rightarrow B_{\text{pico}}$) para pruebas inmediatas sin hardware físico.
  - **Generador de Dataset Sintético (`--generate-synthetic`):** Función de generación en batch automatizada con almacenamiento estructurado en `Tools/dataset_transitions/` para alimentar los modelos predictivos de combos.
  - **Artefacto de Arquitectura:** Generado plan exhaustivo con los 7 grafos Mermaid individuales y formalización matemática en `PLAN_ENTRENADOR_TRANSICIONES_KINECT.md`.

* **2026-09-22 (Menú de Inicio Retro y Pantalla de Carga con Minijuego Cinemático DBZ Tenkaichi 3):**
  - **Menú Principal Arcade (`MainMenuController.cs`):** Navegación completa por teclado (`W`/`S`, `Flechas`, `Enter`/`Espacio`, `ESC`/`Backspace`), indicador animado con cursor retro (`>>`), escalado palpitante de opciones activas y efectos de sonido arcade (`Menu_Cursor_Select.wav`, `Menu_Confirm_Start.wav`).
  - **Ventana Modal "Próximamente" para Modo Historia:** Al seleccionar Modo Historia, se abre una ventana modal explicativa que indica que el modo requerirá el sensor Azure Kinect DK e IA somatosensorial en el Sprint 2, descartable con Enter/Espacio/Esc sin iniciar combate accidental.
  - **Estructura de Menú y Submenús:** Opciones principales `Modo Historia`, `Versus` (con submenú interactivo `Versus Bot (1P vs CPU)` y `Versus 2 Players (Local)` conectado al duelo Suzaku Castle) y botón `Salir`.
  - **Pantalla de Carga Ampliada y Minijuego DBZ Tenkaichi 3 (`LoadingScreenController.cs`, `LoadingMinigameManager.cs`):** Área de minijuego expandida a 1460x580 px con límites horizontales de 670 px, barra de progreso CPS-3 animada (0% a 100%), avatar 2D jugable (`MiniFighterController.cs`) con físicas de salto aumentadas (jumpForce = 620), desplazamiento ágil y puñetazos con sprites arcade de Ryu.
  - **Música de Pelea y Menú de Pausa en Duelo (`JapanDuel.cs`):** Incorporada música de fondo BGM para el combate de Suzaku Castle (`08_Kobu_Ryu_Stage.mp3` en `Resources/Audio/BGM_Japan.mp3`) con bucle activo. Sistema de pausa interactivo con tecla `ESC` o `P` que congela la física, reproduce SFX y permite elegir con teclado o ratón entre `Reanudar`, `Reiniciar Ronda` o `Volver al Menú Principal` (`MainMenu_Scene`).
  - **Algoritmos Cinemáticos de Dirección (Craig Reynolds Steering Behaviors):**
    1. **`WanderBehavior.cs` (Merodeo):** 3 orbes autónomos que navegan orgánicamente por la pantalla con un círculo proyectado adelante y perturbación angular suave ($\Delta \theta$).
    2. **`SeekBehavior.cs` (Persecución):** Orbe/espíritu buscador que persigue activamente al orbe más cercano mediante vector de aceleración deseada $\vec{v}_{desired} - \vec{v}$.
    3. **Puntuación y SFX:** Marcador en tiempo real de orbes recolectados, SFX de impacto (`Bonus_Basketball_Bounce.wav`, `Hit_Punch_Light.wav`) y badges explicativos de algoritmos activos.
  - **Builder Automatizado de Escena (`SF3MainMenuBuilder.cs`):** Menú superior `SF3 Tools > Build Main Menu & Loading Scene`. Genera la escena `MainMenu_Scene.unity` completa y sincroniza `EditorBuildSettings` (Escena 0: Menú, Escena 2: Duelo Japón) con validación batchmode sin errores (Exit Code 0).

* **2026-10-13 (Entrenador de Transiciones de Combate y Grafo Completo 7x7 - Kevin):**
  - **Sistema de Transiciones y Cancel Windows:** Modelado del grafo dirigido completo $G=(V, E)$ de 7 acciones (`idle`, `punch_right`, `punch_left`, `kick_right`, `kick_left`, `crouch`, `block`) con 42 transiciones dirigidas en `Tools/record_transition_graph.py`.
  - **Tabs de Destino en Verde Permanente:** Cada botón de **NODO DESTINO (B)** en el panel izquierdo se ilumina en **VERDE ESMERALDA PERMANENTE** (`(14, 85, 35)` con borde `(0, 210, 85)` y badge `[✓ OK]`) tan pronto como dicha transición $A \to B$ queda grabada y guardada en disco para el sujeto activo, impidiendo olvidos durante sesiones extensas de captura.
  - **Indicadores de Progreso en Nodo Origen (A):** Visualización en tiempo real de cobertura de aristas salientes (`[6/6 OK]`, `[X/6]`, `[0/6]`).
  - **Priorización de Teclado en Review:** Reordenamiento de eventos de teclado en bucle de replay: `ENTER` / `S` (Guardar), `R` (Reintentar de inmediato) y `ESC` (Descartar) evaluados con prioridad antes de los atajos alfanuméricos de selección de nodos.
  - **Soporte Físico Azure Kinect DK:** Extracción corregida de coordenadas milimétricas 3D mediante `body.numpy()[:, :3]`, eliminando fallback espurio a mock por excepciones de API.

* **2026-10-13 (Entrenamiento del Grafo Completo de 42 Transiciones - Sujeto 41 Marco & Live Transition Radar):**
  - **Captura del Grafo de Transiciones 7x7:** Grabadas las 42 aristas de transición posibles entre las 7 posturas maestras (`idle`, `punch_right`, `punch_left`, `kick_right`, `kick_left`, `crouch`, `block`) con Marco (`subject_41`).
  - **Limpieza Cinemática (`Tools/clean_dataset_outliers.py`):** Filtrado Hampel + $1€$ adaptativo aplicado a los 84 clips de transición en `Tools/dataset_cleaned/transitions/` (218 correcciones de salto ToF).
  - **Ventanas de Llegada y Salida Cinemática (`Tools/train_gesture_classifier.py`):** Aumento temporal dinámico extrayendo ventanas de aterrizaje (frames 15..50) y ventanas de lanzamiento (frames 0..35), expandiendo el dataset de 98 a **266 muestras cinemáticas activas**.
  - **Re-entrenamiento ML & Sincronización Sentis:** Random Forest con GroupKFold alcanzó **97.74% de exactitud global** (F1-score: 0.9753). Modelos exportados a `Tools/gesture_classifier.joblib`, `Tools/gesture_classifier.onnx` y `Assets/StreetFighter3_ThirdStrike/Models/gesture_classifier.onnx`.
  - **Probador Somatosensorial en Vivo Actualizado (`Tools/test_live_kinect_classifier.py`):**
    1. Gráfico de barras en tiempo real con porcentajes de confianza exactos (`%`) para las 7 acciones.
    2. Radar de Transiciones Rápidas que mide la latencia de cambio $A \to B$ en milisegundos y registra historial de combos en cadena (`combo_history`).
    3. Detección de impulso dinámico en ventana corta (6 frames) que elimina la latencia de retorno en combos rápidos.
    4. Soporte híbrido: Detección automática de hardware Azure Kinect DK o simulación procedural (`--mock` / teclas `1-7`).

* **2026-09-22 (Integración Rama Sebas - Escenario Japón Suzaku Castle y Duelo Local Ken vs. Ryu):**
  - **Fusión de `feature/sp1-sebas-japan-stage`:** Incorporados los commits `a55f8e8ce` y `e3f89b646` de Sebas.
  - **Escenario Suzaku Castle con Parallax:** Prefab `Stage_Japan.prefab`, shader ChromaKey `SF3ChromaKeySprite.shader` y constructor automatizado en `SF3JapanStageBuilder.cs`.
  - **Duelo Local 2 Jugadores (`Sandbox_Sebas.unity`):** Sistema de combate desacoplado `JapanDuel.cs` y `DuelFighter.cs` para Ken (P1: WASD + F/H/V/B) vs. Ryu (P2: Flechas + Numpad), con hurtboxes tripartitas, bloqueo frontal, daño diferenciado y ScriptableObject `JapanDuelRoster.asset` con 486 sprites referenciados.
  - **Validador Automatizado:** Herramienta en el menú de Unity `SF3 Tools > Validate Local Duel` (`JapanDuelValidation.cs`) para verificar sin intervención manual el set completo de colisiones, alcances, KO y victoria.

* **2026-09-17 (Set 2 Bloqueo Dinámico, Limpieza Biomecánica, Retorno Inmediato a Idle < 200ms y Re-entrenamiento ML 98 Clips):**
  - **Captura e Integración de Set 2 (Sujetos 11 a 14):** 28 nuevos clips CSV incorporando la nueva dinámica de combate: Bloqueo dinámico (`block`: brazos suben desde guardia a bloquear el pecho/cara y vuelven a bajar) y Guardia estática (`idle` estable con velocidad < 0.1 m/s). Total dataset: **98 clips**.
  - **Limpieza de Outliers (`Tools/clean_dataset_outliers.py`):** Procesados los 98 clips en `Tools/dataset_cleaned/`. Se eliminaron 313 saltos espurios (> 30 cm), logrando 0 discontinuidades y reduciendo el salto máximo promedio de 0.348m a 0.074m.
  - **Re-entrenamiento Random Forest Supervisado (`Tools/train_gesture_classifier.py`):** Entrenado sobre los 98 clips limpios (14 sujetos). Validación cruzada `GroupKFold` subió de 91.43% a **95.24% ± 3.01%** sobre sujetos no vistos. La característica `max_elev_wrist_l` ascendió al Top 2 de importancia (7.00%) para captar la elevación bilateral de brazos del bloqueo.
  - **Exportación ONNX y Joblib Sincronizada:** Actualizados `Tools/gesture_classifier.joblib`, `Tools/gesture_classifier.onnx` y `Assets/StreetFighter3_ThirdStrike/Models/gesture_classifier.onnx`.
  - **Retorno Inmediato a Guardia / Idle (< 200 ms):** Solucionada la latencia de 2 segundos de retorno a guardia causada por la persistencia de picos de velocidad en la ventana rodante de 35 frames. Implementado detector de desaceleración y reposo instantáneo (últimos 6 frames / ~200 ms, $v < 0.42\text{ m/s}$) tanto en `Tools/test_live_kinect_classifier.py` como en `Tools/sf3_kinect_sagittal_visualizer.py`. Si las extremidades se detienen tras un golpe, el sistema transiciona instantáneamente a `idle` (o `crouch`/`block` sostenido si corresponde).
  - **Mejora del Detector en Vivo (`Tools/test_live_kinect_classifier.py`):** Integrada persistencia visual de impacto (2.5s), telemetría de guardia activa en reposo y registro de eventos y sesgos por consola en tiempo real.

* **2026-09-15 (Pipeline ML Cinemático Temporal - 10 Sujetos, UX Studio & 44 Features):**
  - **Filtro Adaptativo One-Euro ($1€$):** Implementado en `Tools/gesture_feature_extractor.py` sobre el eje temporal 3D, mitigando el jitter de profundidad ToF en reposo sin añadir latencia a golpes explosivos.
  - **Normalización Antropométrica y Extensión Biomecánica:** Incorporada longitud de torso ($L_{\text{torso}}$) y ratios de extensión articular ($\text{Ext}_{\text{brazo}}, \text{Ext}_{\text{pierna}}$) invariantes a la estatura (44 features cinemáticas totales).
  - **Cuenta Regresiva de 3 Segundos (Visual + Audio):** Integrada cuenta 3.. 2.. 1.. con tonos audibles (`winsound.Beep`) y overlay en `Tools/sf3_kinect_sagittal_visualizer.py` para sincronizar al voluntario y centrar los golpes en el clip.
  - **Auditoría Heurística de Calidad (Quality Gatekeeper):** Evaluación instantánea de velocidad pico, centrado temporal de impacto y distancia operativa ($Z$), asistiendo al operador en la revisión manual.
  - **Sistema Cuádruple de Verificación y Auditoría Anti-Olvido ("Memoria de Pollo"):**
    1. **Badges Permanentes por Pose:** Píldoras visuales en cada una de las 8 acciones (`[OK] 20/20 OK`, `[SAVE] X/20`, `[-] VACIO 0/20`).
    2. **Resaltado de Guardado Reciente:** Borde verde brillante y tag `>> RECIEN GUARDADO (Xs)` en el botón de la acción recién guardada.
    3. **Matriz Rápida de los 10 Sujetos:** Vista de pájaro con 10 botones interactivos (`S01` a `S10`) con conteo de clips en tiempo real y salto inmediato con un clic.
    4. **Comprobante Físico Permanente en Disco:** Tarjeta fija con timestamp, nombre de archivo CSV y tamaño en KB verificado en disco tanto en el centro inferior como en el panel derecho de video.
  - **Calibración Biomecánica A-Pose (Tecla `[C]`):** Captura de 2 segundos para medir y registrar longitudes de brazos, piernas, torso y envergadura en `Tools/dataset_raw/subject_profiles.json`.
  - **Re-entrenamiento ML & ONNX:** Modelo Random Forest re-entrenado con 44 features y GroupKFold (99.98% de exactitud), exportado a `Tools/gesture_classifier.onnx` y `Assets/StreetFighter3_ThirdStrike/Models/gesture_classifier.onnx`.
* **2026-09-08 (Martes de Laboratorio - Sprint 1):**
  - Implementada la arquitectura desacoplada de entrada: `IFighterInput.cs`.
  - Creado el adaptador de teclado `KeyboardFighterInput.cs` con controles de movimiento, ataques y emulación de gestos.
  - Creado el adaptador somatosensorial `AzureKinectInput.cs` con cálculo cinemático de articulaciones 3D.
  - Creado el hardware bridge `AzureKinectBodyTracker.cs` con resolución automática de DLLs nativas y ONNX weights.
  - Creado el estudio de calibración interactivo `Tools/sf3_kinect_sagittal_visualizer.py` con esqueleto simplificado (13 articulaciones clave), diferenciación cromática anatómica (**Rojo = Lado Derecho, Azul = Lado Izquierdo, Cian = Tronco**), selector de posturas base (Perfil Izq/Der/Frontal), telemetría de patadas en profundidad (Z), catálogo completo de **51 animaciones de combate de Ryu** en 6 categorías, generación automática de snapshots de auditoría en `Tools/captured_pose_reviews/` y panel lateral flotante de review para inspeccionar la pose capturada en tiempo real.
  - Creado `KinectPoseMatcher.cs` con parser de poses línea a línea, evaluador de similitud biométrica (%) en tiempo real y vinculación directa al Animator de Ryu (`FighterAnimationTester` / `Ryu_Animator.controller`), reconociendo automáticamente por hash los 51 estados de animación.
  - Creada la escena de diagnóstico `Assets/StreetFighter3_ThirdStrike/Scenes/Test_AzureKinect_Body.unity`.
  - Rama activa: `feature/sp1-kevin-input-kinect` (#6).

* **2026-09-05:**
  - Creadas las 36 tareas atómicas de los Sprints 1 a 6 en `Devs/`.
  - Creado el sistema de sincronización y contexto para IAs en `Devs/Context/`.
  - Creada la Skill `.agent/skills/sf3-team-developer/SKILL.md`.
  - Creado el script de auto-configuración `Tools/setup_team_workspace.py`.
  - Sincronizados los 64 AnimationClips de Ryu en `Ryu_Animator.controller`.
