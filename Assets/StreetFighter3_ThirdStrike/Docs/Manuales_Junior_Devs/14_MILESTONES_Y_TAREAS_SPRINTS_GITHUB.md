# 🏆 Milestones, Tareas Atómicas y Calendario de Laboratorios Martes (Kinect)
## Proyecto: Street Fighter III: 3rd Strike (Unity + Azure Kinect + IA Adaptativa)

### 🥋 Principio de Oro de Responsabilidad por Personaje:
* **👑 MARCO:** Se encarga al 100% de **Ryu** (`02_Ryu` - Sprites, Animaciones, Hitboxes, Hurtboxes, Specials) + Arquitectura Core y Entrenamiento IA (ML-Agents en RTX 4060).
* **🔥 SEBAS:** Se encarga al 100% de **Ken** (`01_Ken` - Sprites, Animaciones, Hitboxes, Hurtboxes, Specials) + Escenario Japón, VFX y Audio.
* **⚡ KEVIN:** Se encarga al 100% de **Chun-Li** (`03_ChunLi` - Sprites, Animaciones, Hitboxes, Hurtboxes, Specials) + Pipeline Azure Kinect, UI y SQLite.

---

## 🏛️ Calendario Semanal de Laboratorio Azure Kinect & Sync de Equipo (Todos los Martes)

Todos los **martes** se realiza la sesión presencial con el sensor Azure Kinect físico + la reunión de sincronización y planificación del equipo:

| Semana | Fecha Martes | Hito de Laboratorio con Azure Kinect | Agenda de Reunión de Equipo |
| :---: | :---: | :--- | :--- |
| **Sem 1** | **8 de Sep** | **Lab 1:** Setup del SDK Azure Kinect, calibración del espacio (1.5m a 4m) y visualización del esqueleto 3D. | Kickoff de Sprint 1: Coordinar convención de nombres y asignación de ramas Git. |
| **Sem 2** | **15 de Sep** | **Lab 2:** Prueba de mapeo básico de articulaciones en Unity con Ryu y emulador de teclado. | Cierre Sprint 1: Code Review de animaciones de Ryu, Ken y Chun-Li. |
| **Sem 3** | **22 de Sep** | **Lab 3:** Clasificador de velocidad de muñeca para puñetazo físico y brazos cruzados para guardia. | Planificación Sprint 2: Asignación de Hitboxes/Hurtboxes por personaje. |
| **Sem 4** | **29 de Sep** | **Lab 4:** Golpear al Dummy de entrenamiento con puño físico en Kinect y probar ventana de Parry. | Cierre Sprint 2: Verificación de daño, VFX y SFX SoundManager. |
| **Sem 5** | **6 de Oct** | **Lab 5:** Recolección de dataset humano: jugar partidas cortas con Kinect con `MatchTelemetryLogger.cs`. | Planificación Sprint 3: Balance de movimientos especiales y SQLite. |
| **Sem 6** | **13 de Oct** | **Lab 6:** Prueba de combate de Ken y Chun-Li con Kinect y verificación de guardado en SQLite. | Cierre Sprint 3: Entrega del dataset de telemetría a Marco para entrenar en GPU. |
| **Sem 7** | **20 de Oct** | **Lab 7:** Mapeo y calibración del gesto de Hadouken (juntar y empujar dos manos) en Kinect. | Planificación Sprint 4: Configuración del agente ML-Agents en Unity. |
| **Sem 8** | **27 de Oct** | **Lab 8:** **Primera Pelea en Vivo:** Humano en Kinect vs Bot de IA (Fase 1 - Behavioral Cloning). | Cierre Sprint 4: Evaluación de comportamiento humanoide del bot. |
| **Sem 9** | **3 de Nov** | **Lab 9:** Calibración de gestos de patada física (elevación de pierna) y agachado corporal. | Planificación Sprint 5: Entrenamiento por refuerzo (3 dificultades) y HUD. |
| **Sem 10** | **10 de Nov** | **Lab 10:** Prueba de las 3 dificultades (`Easy`, `Med`, `Hard`) y selector dinámico con HUD arcade. | Cierre Sprint 5: Verificación de flujo de rounds y anunciador. |
| **Sem 11** | **17 de Nov** | **Lab 11:** Pruebas de estrés de latencia y ajuste de filtros de suavizado en las 32 articulaciones. | Planificación Sprint 6: Code Freeze y preparación del build final. |
| **Sem 12** | **24 de Nov** | **Lab 12:** **Ensayo General de la Exposición:** Partida completa en build standalone `.exe`. | Aprobación final del proyecto previa a la sustentación oficial. |
| 🎯 | **1 de Dic** | **SUSTENTACIÓN Y ENTREGA FINAL** | Presentación oficial ante el profesor y jurado. |

---

## 📌 Resumen de Milestones (Sprints de 2 Semanas)

| Milestone | Nombre del Sprint | Inicio (Lunes) | Fecha Límite (Domingo) | Objetivo Central |
| :---: | :--- | :---: | :---: | :--- |
| **M1** | `Sprint 1: Motor 2D Base & Animaciones` | **Sep 7, 2026** | **Sep 20, 2026** | Animaciones de Ryu, Ken y Chun-Li; física de salto y emulador de teclado. |
| **M2** | `Sprint 2: Hitboxes, Hurtboxes & Gestos Kinect` | **Sep 21, 2026** | **Oct 4, 2026** | Cada dev monta las cajas de su personaje; combate base y puñetazo en Kinect. |
| **M3** | `Sprint 3: Combate Completo & Telemetría SQLite` | **Oct 5, 2026** | **Oct 18, 2026** | Los 3 personajes listos con especiales; base de datos y grabador de partidas. |
| **M4** | `Sprint 4: IA Fase 1 (Imitación) & Gestos Pro` | **Oct 19, 2026** | **Nov 1, 2026** | Bot entrenado por Behavioral Cloning en GPU; patadas y Hadouken en Kinect. |
| **M5** | `Sprint 5: IA Fase 2 (Refuerzo + DDA) & HUD Arcade` | **Nov 2, 2026** | **Nov 15, 2026** | Bot con 3 dificultades (ONNX), selector dinámico y HUD de vida/timer/super. |
| **M6** | `Sprint 6: Calibración, Build .EXE & Demo Final` | **Nov 16, 2026** | **Nov 30, 2026** | Standalone `.exe` a 60 FPS estables, cero bugs y ensayo de presentación. |

---

## 🏃 MILESTONE 1: Sprint 1 (Sep 7 – Sep 20)
* **#1 [SP1-MARCO] Máquina de Estados Core (`FighterStateMachine.cs` y `FighterPhysics.cs`)**
  * *Assignee:* `@username_marco` | *Labels:* `role:marco`, `sprint:1`, `area:combat`
  * *Criterios:* Desacoplar estados de reposo, caminar, agacharse y salto parabólico con física en Unity.
* **#2 [SP1-MARCO] Pipeline de Animaciones de Ryu (`02_Ryu`)**
  * *Assignee:* `@username_marco` | *Labels:* `role:marco`, `sprint:1`, `area:combat`
  * *Criterios:* Sincronizar los 64 AnimationClips de Ryu en `Ryu_Animator.controller` y probar retornos a idle con teclado.
* **#3 [SP1-SEBAS] Pipeline de Animaciones de Ken (`01_Ken`)**
  * *Assignee:* `@username_sebas` | *Labels:* `role:sebas`, `sprint:1`, `area:combat`
  * *Criterios:* Organizar las 7 categorías de Ken, generar AnimationClips con `SF3 Tools` y poblar `Ken_Animator.controller`.
* **#4 [SP1-SEBAS] Montaje del Escenario Japón (Suzaku Castle) con Parallax**
  * *Assignee:* `@username_sebas` | *Labels:* `role:sebas`, `sprint:1`, `area:art`
  * *Criterios:* Configurar Sorting Layers, fondo cielo, castillo, suelo y script `ParallaxBackground.cs` a 100 PPU.
* **#5 [SP1-KEVIN] Pipeline de Animaciones de Chun-Li (`03_ChunLi`)**
  * *Assignee:* `@username_kevin` | *Labels:* `role:kevin`, `sprint:1`, `area:combat`
  * *Criterios:* Organizar las 7 categorías de Chun-Li, generar AnimationClips con `SF3 Tools` y poblar `ChunLi_Animator.controller`.
* **#6 [SP1-KEVIN] Configuración de Azure Kinect SDK y Emulador de Teclado `IFighterInput.cs`**
  * *Assignee:* `@username_kevin` | *Labels:* `role:kevin`, `sprint:1`, `area:kinect`, `needs-lab-test`
  * *Criterios:* Validar lectura de 32 articulaciones en el Lab del martes 8 y 15 de Sep, y crear `KeyboardFighterInput` para desarrollo offline.

---

## 🏃 MILESTONE 2: Sprint 2 (Sep 21 – Oct 4)
* **#7 [SP2-MARCO] Hitboxes y Hurtboxes de Ryu (`02_Ryu`)**
  * *Assignee:* `@username_marco` | *Labels:* `role:marco`, `sprint:2`, `area:combat`
  * *Criterios:* Configurar cajas de 3 piezas (cabeza, torso, piernas) y hitboxes de golpes normales y Hadouken de Ryu.
* **#8 [SP2-MARCO] Motor de Combate: Daño, Hitstun, Blockstun y Ventana de Parry**
  * *Assignee:* `@username_marco` | *Labels:* `role:marco`, `sprint:2`, `area:combat`
  * *Criterios:* Detección de colisiones, cálculo de vida restada, aturdimiento y parry exacto de 0.2s con 0 daño.
* **#9 [SP2-SEBAS] Hitboxes y Hurtboxes de Ken (`01_Ken`)**
  * *Assignee:* `@username_sebas` | *Labels:* `role:sebas`, `sprint:2`, `area:combat`
  * *Criterios:* Configurar cajas de 3 piezas y hitboxes de ataques normales y Shoryuken de Ken.
* **#10 [SP2-SEBAS] Prefabs de VFX (Hadouken/Chispas) y Audio en `SF3SoundManager`**
  * *Assignee:* `@username_sebas` | *Labels:* `role:sebas`, `sprint:2`, `area:art`
  * *Criterios:* Bola de Hadouken con collider, partículas de impacto, destello azul de parry y voces de Ryu y Ken.
* **#11 [SP2-KEVIN] Hitboxes y Hurtboxes de Chun-Li (`03_ChunLi`)**
  * *Assignee:* `@username_kevin` | *Labels:* `role:kevin`, `sprint:2`, `area:combat`
  * *Criterios:* Configurar cajas de 3 piezas y hitboxes de patadas normales y Hyakuretsukyaku de Chun-Li.
* **#12 [SP2-KEVIN] Clasificador Somatosensorial Azure Kinect (Puñetazo y Bloqueo en Lab)**
  * *Assignee:* `@username_kevin` | *Labels:* `role:kevin`, `sprint:2`, `area:kinect`, `needs-lab-test`
  * *Criterios:* Algoritmo de velocidad de muñeca para puño y brazos cruzados para guardia; probado en Kinect el martes 22 y 29 de Sep.

---

## 🏃 MILESTONE 3: Sprint 3 (Oct 5 – Oct 18)
* **#13 [SP3-MARCO] Movimientos Especiales de Ryu (Hadouken, Shoryuken, Tatsumaki)**
  * *Assignee:* `@username_marco` | *Labels:* `role:marco`, `sprint:3`, `area:combat`
  * *Criterios:* Calibrar frame data, proyectiles y balance de daño de los ataques especiales de Ryu.
* **#14 [SP3-MARCO] Grabador de Telemetría para Entrenamiento (`MatchTelemetryLogger.cs`)**
  * *Assignee:* `@username_marco` | *Labels:* `role:marco`, `sprint:3`, `area:ai-ml`, `needs-lab-test`
  * *Criterios:* Graba en cada frame `[distancia, estado_propio, estado_rival, accion]` para el dataset de la IA durante las partidas del martes en Lab.
* **#15 [SP3-SEBAS] Movimientos Especiales de Ken (Shoryuken Ígneo y Tatsumaki)**
  * *Assignee:* `@username_sebas` | *Labels:* `role:sebas`, `sprint:3`, `area:combat`
  * *Criterios:* Configurar propiedades multicapa del Shoryuken de fuego y voces de Ken en el SoundManager.
* **#16 [SP3-SEBAS] Montaje del Escenario China (Crowded Street) con Parallax**
  * *Assignee:* `@username_sebas` | *Labels:* `role:sebas`, `sprint:3`, `area:art`
  * *Criterios:* Escenario urbano chino con múltiples capas de profundidad y Sorting Layers correctas.
* **#17 [SP3-KEVIN] Movimientos Especiales de Chun-Li (Kikoken y Hyakuretsukyaku)**
  * *Assignee:* `@username_kevin` | *Labels:* `role:kevin`, `sprint:3`, `area:combat`
  * *Criterios:* Configurar ráfaga de patadas rápidas, proyectil Kikoken y voces de Chun-Li.
* **#18 [SP3-KEVIN] Módulo de Base de Datos Local SQLite (`DatabaseManager.cs`)**
  * *Assignee:* `@username_kevin` | *Labels:* `role:kevin`, `sprint:3`, `area:database`
  * *Criterios:* Guardar perfiles de usuario, puntuaciones, precisión de gestos Kinect e historial de partidas en `.db`.

---

## 🏃 MILESTONE 4: Sprint 4 (Oct 19 – Nov 1)
* **#19 [SP4-MARCO] Configuración de Entorno Unity ML-Agents y PyTorch CUDA**
  * *Assignee:* `@username_marco` | *Labels:* `role:marco`, `sprint:4`, `area:ai-ml`
  * *Criterios:* Configurar `FighterAgent : Agent` en Unity y validar conexión con Python en RTX 4060.
* **#20 [SP4-MARCO] Entrenamiento de Behavioral Cloning (BC / GAIL) en GPU**
  * *Assignee:* `@username_marco` | *Labels:* `role:marco`, `sprint:4`, `area:ai-ml`, `needs-lab-test`
  * *Criterios:* Entrenar política con dataset humano de telemetría y probar el bot en vivo contra humanos en el Lab el martes 27 de Oct.
* **#21 [SP4-SEBAS] Super Arts y Súper Movimientos de Ryu y Ken (Super Flash)**
  * *Assignee:* `@username_sebas` | *Labels:* `role:sebas`, `sprint:4`, `area:art`
  * *Criterios:* Shinkuu Hadouken y Shinryuken con efecto visual de fondo oscuro y rayos de energía.
* **#22 [SP4-SEBAS] Poses de Victoria e Intros Únicas de Personajes**
  * *Assignee:* `@username_sebas` | *Labels:* `role:sebas`, `sprint:4`, `area:art`
  * *Criterios:* Integrar animaciones de intro rival (Ryu vs Ken) y poses de victoria con frases de audio.
* **#23 [SP4-KEVIN] Super Art de Chun-Li (Senretsukyaku / Houyoku Sen)**
  * *Assignee:* `@username_kevin` | *Labels:* `role:kevin`, `sprint:4`, `area:combat`
  * *Criterios:* Configurar animación, hitboxes y partículas del súper ataque de patadas de Chun-Li.
* **#24 [SP4-KEVIN] Mapeo de Gestos de Patada y Hadouken en Azure Kinect (Lab)**
  * *Assignee:* `@username_kevin` | *Labels:* `role:kevin`, `sprint:4`, `area:kinect`, `needs-lab-test`
  * *Criterios:* Detectar elevación de pierna para patada y unión/empuje de ambas manos para Hadouken en los martes de Lab.

---

## 🏃 MILESTONE 5: Sprint 5 (Nov 2 – Nov 15)
* **#25 [SP5-MARCO] Entrenamiento por Refuerzo (PPO) de 3 Dificultades (`Easy`, `Med`, `Hard`)**
  * *Assignee:* `@username_marco` | *Labels:* `role:marco`, `sprint:5`, `area:ai-ml`
  * *Criterios:* Entrenar políticas de refuerzo en GPU con recompensas por spacing, castigo y daño; exportar 3 `.onnx`.
* **#26 [SP5-MARCO] Gestor de Dificultad Dinámica Adaptativa (`AdaptiveAIManager.cs`)**
  * *Assignee:* `@username_marco` | *Labels:* `role:marco`, `sprint:5`, `area:ai-ml`, `needs-lab-test`
  * *Criterios:* Evaluar telemetría de la partida en vivo y alternar dinámicamente la política del bot en las pruebas de Lab del martes 10 de Nov.
* **#27 [SP5-SEBAS] Sistema de Anunciador Oficial de SF3 ("Round 1, Fight, K.O.!")**
  * *Assignee:* `@username_sebas` | *Labels:* `role:sebas`, `sprint:5`, `area:audio`
  * *Criterios:* Coordinar voces del Announcer con banners de texto animados en pantalla.
* **#28 [SP5-SEBAS] Menú de Selección de Personajes Arcade con Retratos**
  * *Assignee:* `@username_sebas` | *Labels:* `role:sebas`, `sprint:5`, `area:ui`
  * *Criterios:* Pantalla de selección interactiva para elegir entre Ryu, Ken y Chun-Li con sonido de confirmación.
* **#29 [SP5-KEVIN] HUD Arcade Completo (Barras de Vida, Super Gauge y Timer de 99s)**
  * *Assignee:* `@username_kevin` | *Labels:* `role:kevin`, `sprint:5`, `area:ui`
  * *Criterios:* Barras de vida reactivas Pixel-Perfect, medidor de super arts y contador de rounds.
* **#30 [SP5-KEVIN] Guía Visual de Silueta Azure Kinect en Pantalla (Lab)**
  * *Assignee:* `@username_kevin` | *Labels:* `role:kevin`, `sprint:5`, `area:ui`, `needs-lab-test`
  * *Criterios:* Mini indicador en esquina que muestra si el usuario está en el rango óptimo (1.5m a 4m) del sensor.

---

## 🏃 MILESTONE 6: Sprint 6 (Nov 16 – Nov 30)
* **#31 [SP6-MARCO] Calibración de Latencia y Balance de Frame Data del Bot**
  * *Assignee:* `@username_marco` | *Labels:* `role:marco`, `sprint:6`, `area:combat`
  * *Criterios:* Ajustar tiempos de reacción de la IA para que la experiencia sea justa y fluida.
* **#32 [SP6-MARCO] Auditoría de Integración y Build Standalone `.exe` a 60 FPS**
  * *Assignee:* `@username_marco` | *Labels:* `role:marco`, `sprint:6`, `area:core`
  * *Criterios:* Generar build de producción en Windows 64-bit y auditar consumo de memoria/GPU.
* **#33 [SP6-SEBAS] Pulido de Assets, Shaders de Destello y Balance de Mezcla de Audio**
  * *Assignee:* `@username_sebas` | *Labels:* `role:sebas`, `sprint:6`, `area:art`
  * *Criterios:* Normalizar volúmenes de SFX vs BGM vs Voces y corregir cualquier artefacto visual de Ken y escenarios.
* **#34 [SP6-SEBAS] Documentación y Manual de Usuario / Guía de Demostración**
  * *Assignee:* `@username_sebas` | *Labels:* `role:sebas`, `sprint:6`, `area:docs`
  * *Criterios:* Elaborar la guía de pasos para la presentación ante el jurado/profesor.
* **#35 [SP6-KEVIN] Filtro de Suavizado de Ruido de Articulaciones en Azure Kinect (Lab)**
  * *Assignee:* `@username_kevin` | *Labels:* `role:kevin`, `sprint:6`, `area:kinect`, `needs-lab-test`
  * *Criterios:* Aplicar filtro exponencial / Moving Average a los nodos 3D para evitar temblores en las pruebas de Lab del martes 17 y 24 de Nov.
* **#36 [SP6-KEVIN] Pantalla de Estadísticas Finales con Consultas SQLite**
  * *Assignee:* `@username_kevin` | *Labels:* `role:kevin`, `sprint:6`, `area:database`
  * *Criterios:* Mostrar al final del combate: golpes acertados, Hadoukens lanzados, precisión física y ganador.
