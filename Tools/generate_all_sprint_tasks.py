# -*- coding: utf-8 -*-
"""
Script para generar los 36 archivos markdown de tareas atómicas para Marco, Sebas y Kevin
a lo largo de los 6 Sprints, con prompts pedagógicos para Antigravity.
"""

import os

ALL_SPRINT_TASKS = {
    # ==================== SPRINT 1 ====================
    1: {
        "dates": "Sep 7 – Sep 20",
        "Marco": [
            {
                "id": 1,
                "code": "SP1-MARCO-01",
                "branch": "feature/sp1-marco-statemachine",
                "title": "Máquina de Estados Core (FighterStateMachine.cs y FighterPhysics.cs)",
                "desc": "Implementar la máquina de estados desacoplada en C# y la física de salto parabólico/locomoción sin depender de transiciones con flechas en Mecanim.",
                "prompt": "Hola Antigravity, actúa como mi tutor de programación senior en Unity C#. Por favor lee este archivo y explícame paso a paso cómo estructurar y programar yo mismo los scripts FighterStateMachine.cs y FighterPhysics.cs con física parabólica y control de teclado.",
                "criteria": [
                    "El código compila sin errores ni warnings en Unity.",
                    "Ryu camina adelante/atrás con D y A.",
                    "Ryu se agacha manteniendo S y vuelve a Idle al soltar.",
                    "Ryu salta con W describiendo una parábola física real y aterriza suavemente.",
                    "Ataques con J, K, L, U vuelven a Idle automáticamente."
                ]
            },
            {
                "id": 2,
                "code": "SP1-MARCO-02",
                "branch": "feature/sp1-marco-ryu-anim",
                "title": "Pipeline de Animaciones de Ryu (02_Ryu)",
                "desc": "Sincronizar los 64 AnimationClips de Ryu en Ryu_Animator.controller y verificar retornos automáticos a reposo.",
                "prompt": "Hola Antigravity, actúa como mi tutor de animación en Unity. Por favor lee este archivo y explícame cómo verificar los 64 clips de Ryu, cómo funciona el auto-poblado en el Animator y cómo calibrar pivotes para evitar desplazamientos.",
                "criteria": [
                    "Ryu_Animator.controller contiene los 64 estados organizados.",
                    "idle_stance es el estado por defecto.",
                    "Ataques en modo Play vuelven a idle_stance.",
                    "No hay desplazamientos visuales erróneos en el pie de apoyo."
                ]
            }
        ],
        "Sebas": [
            {
                "id": 3,
                "code": "SP1-SEBAS-03",
                "branch": "feature/sp1-sebas-ken-anim",
                "title": "Pipeline de Sprites y Animaciones de Ken (01_Ken)",
                "desc": "Organizar las 7 categorías de Ken, generar AnimationClips a 14 FPS y crear Ken_Animator.controller.",
                "prompt": "Hola Antigravity, actúa como mi tutor de Unity. Por favor lee este archivo y explícame paso a paso cómo organizar las 7 categorías de Ken (01_Ken), cómo usar SF3 Tools para generar clips a 14 FPS y cómo armar el prefab Fighter_Ken.prefab.",
                "criteria": [
                    "Carpetas de 01_Ken organizadas con nombres descriptivos.",
                    "AnimationClips a 14 FPS con Loop Time en Idle/Walk.",
                    "Ken_Animator.controller contiene los estados sin errores.",
                    "Fighter_Ken.prefab se reproduce en Sandbox_Sebas.unity."
                ]
            },
            {
                "id": 4,
                "code": "SP1-SEBAS-04",
                "branch": "feature/sp1-sebas-japan-stage",
                "title": "Montaje del Escenario Japón (Suzaku Castle) con Parallax",
                "desc": "Configurar Sorting Layers y montar el escenario de Suzaku Castle con el script ParallaxBackground.cs y suelo con colisión.",
                "prompt": "Hola Antigravity, actúa como mi tutor de diseño de niveles 2D. Por favor lee este archivo y explícame paso a paso cómo configurar las Sorting Layers, cómo colocar los sprites y cómo ajustar ParallaxBackground.cs para lograr profundidad 2.5D.",
                "criteria": [
                    "Sorting Layers configuradas sin tapar a los luchadores.",
                    "Efecto Parallax activo al mover la cámara horizontalmente.",
                    "Suelo con BoxCollider2D a Y=0.",
                    "Guardado como Prefab reutilizable (Stage_Japan.prefab)."
                ]
            }
        ],
        "Kevin": [
            {
                "id": 5,
                "code": "SP1-KEVIN-05",
                "branch": "feature/sp1-kevin-chunli-anim",
                "title": "Pipeline de Sprites y Animaciones de Chun-Li (03_ChunLi)",
                "desc": "Organizar las 7 categorías de Chun-Li, generar AnimationClips a 14 FPS y crear ChunLi_Animator.controller.",
                "prompt": "Hola Antigravity, actúa como mi tutor de animación en Unity. Por favor lee este archivo y explícame paso a paso cómo organizar las 7 categorías de Chun-Li (03_ChunLi), cómo usar SF3 Tools a 14 FPS y cómo armar Fighter_ChunLi.prefab.",
                "criteria": [
                    "Carpetas de 03_ChunLi organizadas con nombres descriptivos.",
                    "AnimationClips generados a 14 FPS.",
                    "ChunLi_Animator.controller poblado correctamente.",
                    "Fighter_ChunLi.prefab se reproduce en Sandbox_Kevin.unity."
                ]
            },
            {
                "id": 6,
                "code": "SP1-KEVIN-06",
                "branch": "feature/sp1-kevin-input-kinect",
                "title": "Arquitectura de Entrada IFighterInput.cs y Azure Kinect SDK",
                "desc": "Crear la interfaz desacoplada de entrada IFighterInput, el emulador de teclado KeyboardFighterInput y preparar el SDK de Azure Kinect.",
                "prompt": "Hola Antigravity, actúa como mi tutor de arquitectura de software en Unity. Por favor lee este archivo y explícame cómo diseñar la interfaz IFighterInput.cs, cómo implementar KeyboardFighterInput.cs y cómo estructurar la lectura de 32 articulaciones del SDK de Azure Kinect.",
                "criteria": [
                    "Interfaz IFighterInput.cs creada y compilando.",
                    "KeyboardFighterInput.cs permite mover y atacar con teclas.",
                    "Estructura lista para recibir datos de Kinect en Lab los martes.",
                    "Escena de prueba Test_AzureKinect_Body.unity creada."
                ]
            }
        ]
    },

    # ==================== SPRINT 2 ====================
    2: {
        "dates": "Sep 21 – Oct 4",
        "Marco": [
            {
                "id": 7,
                "code": "SP2-MARCO-07",
                "branch": "feature/sp2-marco-ryu-colliders",
                "title": "Hitboxes y Hurtboxes de Ryu (02_Ryu)",
                "desc": "Configurar las cajas de colisión de 3 piezas (cabeza, torso, piernas) y hitboxes de ataques normales y Hadouken de Ryu con auto-ajuste al sprite.",
                "prompt": "Hola Antigravity, actúa como mi tutor de combate 2D. Por favor lee este archivo y explícame cómo configurar los componentes FighterHurtbox y FighterHitbox en Ryu, cómo funciona el auto-ajuste en saltos/agachadas y cómo activar hitboxes en frames específicos.",
                "criteria": [
                    "Hurtboxes de cabeza, torso y piernas siguen el cuerpo de Ryu en saltos y agachadas.",
                    "Hitbox roja se enciende solo en frames activos del golpe.",
                    "Probado en modo Play con FighterCombatColliders."
                ]
            },
            {
                "id": 8,
                "code": "SP2-MARCO-08",
                "branch": "feature/sp2-marco-combat-core",
                "title": "Motor de Combate: Daño, Hitstun, Blockstun y Ventana de Parry",
                "desc": "Implementar la lógica universal de impacto: cálculo de vida restada, aturdimiento (Hitstun), bloqueo y ventana de Parry de 0.2s con 0 daño.",
                "prompt": "Hola Antigravity, actúa como mi tutor de sistemas de lucha. Por favor lee este archivo y explícame cómo programar la detección de impacto entre Hitbox y Hurtbox, los estados de Hitstun/Blockstun y el algoritmo de Parry exacto de 12 frames (0.2s).",
                "criteria": [
                    "Al impactar: el receptor entra en hit_standing y pierde vida.",
                    "Si el receptor bloquea: entra en block_standing y recibe daño reducido.",
                    "Si presiona adelante en ventana de 0.2s: se activa Parry con 0 daño y destello azul."
                ]
            }
        ],
        "Sebas": [
            {
                "id": 9,
                "code": "SP2-SEBAS-09",
                "branch": "feature/sp2-sebas-ken-colliders",
                "title": "Hitboxes y Hurtboxes de Ken (01_Ken)",
                "desc": "Configurar las cajas de colisión de 3 piezas y los hitboxes de ataques normales y Shoryuken de Ken.",
                "prompt": "Hola Antigravity, actúa como mi tutor de Unity. Por favor lee este archivo y explícame paso a paso cómo colocar y calibrar los colliders de Hurtbox y Hitbox en el prefab de Ken (Fighter_Ken.prefab) para que coincidan con sus sprites a 100 PPU.",
                "criteria": [
                    "Hurtboxes de Ken cubren cabeza, torso y piernas adecuadamente.",
                    "Hitbox de puños, patadas y Shoryuken calibradas.",
                    "Probado en escena Sandbox_Sebas.unity."
                ]
            },
            {
                "id": 10,
                "code": "SP2-SEBAS-10",
                "branch": "feature/sp2-sebas-vfx-audio",
                "title": "Prefabs de VFX (Hadouken/Chispas) y Audio en SF3SoundManager",
                "desc": "Crear prefabs de proyectil Hadouken, chispas de impacto, destello azul de parry y conectar los bancos de sonido en SF3SoundManager.",
                "prompt": "Hola Antigravity, actúa como mi tutor de efectos y audio en Unity. Por favor lee este archivo y explícame cómo armar el prefab del proyectil Hadouken con auto-destrucción, partículas de chispa de golpe y cómo reproducir voces y golpes con SF3SoundManager.cs.",
                "criteria": [
                    "Prefab de Hadouken avanza a velocidad constante y colisiona.",
                    "Partículas de chispa de impacto y destello azul de parry se auto-destruyen.",
                    "SF3SoundManager reproduce voces de Ryu y Ken y SFX de golpes."
                ]
            }
        ],
        "Kevin": [
            {
                "id": 11,
                "code": "SP2-KEVIN-11",
                "branch": "feature/sp2-kevin-chunli-colliders",
                "title": "Hitboxes y Hurtboxes de Chun-Li (03_ChunLi)",
                "desc": "Configurar las cajas de colisión de 3 piezas y los hitboxes de patadas normales y Hyakuretsukyaku de Chun-Li.",
                "prompt": "Hola Antigravity, actúa como mi tutor de Unity. Por favor lee este archivo y explícame paso a paso cómo colocar y calibrar los colliders de Hurtbox y Hitbox en Fighter_ChunLi.prefab para que coincidan con sus poses y ráfaga de patadas.",
                "criteria": [
                    "Hurtboxes de Chun-Li cubren cabeza, torso y piernas.",
                    "Hitbox de patadas normales y patadas rápidas configuradas.",
                    "Probado en escena Sandbox_Kevin.unity."
                ]
            },
            {
                "id": 12,
                "code": "SP2-KEVIN-12",
                "branch": "feature/sp2-kevin-kinect-gestures",
                "title": "Clasificador Somatosensorial Azure Kinect (Puñetazo y Bloqueo en Lab)",
                "desc": "Algoritmo de detección de puño por velocidad de muñeca y bloqueo por brazos cruzados en Azure Kinect, validado en los martes de Lab.",
                "prompt": "Hola Antigravity, actúa como mi tutor de visión y sensores. Por favor lee este archivo y explícame cómo programar el algoritmo cinemático que calcula la velocidad del vector muñeca-codo para detectar puñetazos directos y la proximidad de muñecas para bloqueo en Azure Kinect.",
                "criteria": [
                    "Algoritmo de velocidad detecta extensión rápida de brazo como puñetazo.",
                    "Posición de guardia detectada cuando las muñecas se cruzan frente al torso.",
                    "Probado en hardware físico de Azure Kinect en el laboratorio."
                ]
            }
        ]
    },

    # ==================== SPRINT 3 ====================
    3: {
        "dates": "Oct 5 – Oct 18",
        "Marco": [
            {
                "id": 13,
                "code": "SP3-MARCO-13",
                "branch": "feature/sp3-marco-ryu-specials",
                "title": "Movimientos Especiales de Ryu (Hadouken, Shoryuken, Tatsumaki)",
                "desc": "Calibrar frame data, proyectiles, elevación física y balance de daño de los ataques especiales de Ryu.",
                "prompt": "Hola Antigravity, actúa como mi tutor de combate 2D. Por favor lee este archivo y explícame cómo conectar el disparo de proyectil en el frame exacto de Hadouken, la elevación vertical del Shoryuken y la rotación de Tatsumaki Senpukyaku en Ryu.",
                "criteria": [
                    "Hadouken instancia el proyectil en el frame de salida.",
                    "Shoryuken eleva a Ryu del suelo y aplica daño múltiple.",
                    "Tatsumaki desplaza a Ryu horizontalmente en el aire."
                ]
            },
            {
                "id": 14,
                "code": "SP3-MARCO-14",
                "branch": "feature/sp3-marco-telemetry-logger",
                "title": "Grabador de Telemetría para Entrenamiento (MatchTelemetryLogger.cs)",
                "desc": "Script que graba en cada frame [distancia, estado_propio, estado_rival, accion] para construir el dataset de aprendizaje por imitación.",
                "prompt": "Hola Antigravity, actúa como mi tutor de Machine Learning en Unity. Por favor lee este archivo y explícame cómo programar MatchTelemetryLogger.cs para registrar vectores de estado y acciones humanas en formato CSV/SQLite durante las partidas del laboratorio.",
                "criteria": [
                    "MatchTelemetryLogger registra datos cada frame sin causar caídas de FPS.",
                    "Guarda archivo de telemetría estructurado al finalizar la partida.",
                    "Probado grabando partidas en el laboratorio los martes."
                ]
            }
        ],
        "Sebas": [
            {
                "id": 15,
                "code": "SP3-SEBAS-15",
                "branch": "feature/sp3-sebas-ken-specials",
                "title": "Movimientos Especiales de Ken (Shoryuken Ígneo y Tatsumaki)",
                "desc": "Configurar propiedades multicapa del Shoryuken de fuego de Ken, ráfaga de Tatsumaki y balance de daño.",
                "prompt": "Hola Antigravity, actúa como mi tutor de combate 2D. Por favor lee este archivo y explícame cómo programar el Shoryuken ígneo multicapa de Ken con partículas de fuego, desplazamientos aéreos y voces oficiales en SF3SoundManager.",
                "criteria": [
                    "Shoryuken de fuego aplica 3 hits con efecto de llamas.",
                    "Tatsumaki de Ken ejecuta giros continuos con animación fluida.",
                    "Voces y efectos conectados al SoundManager."
                ]
            },
            {
                "id": 16,
                "code": "SP3-SEBAS-16",
                "branch": "feature/sp3-sebas-china-stage",
                "title": "Montaje del Escenario China (Crowded Street) con Parallax",
                "desc": "Montar el segundo escenario oficial: Crowded Street (China) con múltiples capas de profundidad y Sorting Layers.",
                "prompt": "Hola Antigravity, actúa como mi tutor de diseño de niveles 2D. Por favor lee este archivo y explícame cómo montar el escenario de China en Stage_China.prefab, configurando las capas de ParallaxBackground.cs y los colisionadores de bordes y suelo.",
                "criteria": [
                    "Escenario de China montado con múltiples capas independientes.",
                    "Efecto Parallax configurado y suave al moverse los luchadores.",
                    "Colisionadores de esquinas (paredes invisibles) y suelo configurados."
                ]
            }
        ],
        "Kevin": [
            {
                "id": 17,
                "code": "SP3-KEVIN-17",
                "branch": "feature/sp3-kevin-chunli-specials",
                "title": "Movimientos Especiales de Chun-Li (Kikoken y Hyakuretsukyaku)",
                "desc": "Configurar ráfaga de patadas rápidas (Hyakuretsukyaku), proyectil Kikoken y voces de Chun-Li.",
                "prompt": "Hola Antigravity, actúa como mi tutor de combate 2D. Por favor lee este archivo y explícame cómo implementar el disparo del Kikoken con su animación de proyectil y el estado de ráfaga de patadas rápidas con hitboxes consecutivas en Chun-Li.",
                "criteria": [
                    "Kikoken dispara proyectil con animación de impacto.",
                    "Hyakuretsukyaku genera ráfaga de patadas con daño consecutivo.",
                    "Voces arcade de Chun-Li conectadas al SoundManager."
                ]
            },
            {
                "id": 18,
                "code": "SP3-KEVIN-18",
                "branch": "feature/sp3-kevin-sqlite-database",
                "title": "Módulo de Base de Datos Local SQLite (DatabaseManager.cs)",
                "desc": "Crear el gestor de base de datos local SQLite para almacenar perfiles de usuario, historial de partidas, precisión física y puntuaciones.",
                "prompt": "Hola Antigravity, actúa como mi tutor de bases de datos en Unity. Por favor lee este archivo y explícame cómo configurar SQLite (sqlite-net) en C#, crear las tablas de Perfiles, Partidas y Telemetría, y escribir métodos asíncronos para guardar y consultar estadísticas.",
                "criteria": [
                    "DatabaseManager crea la base de datos sf3_game.db en Application.persistentDataPath.",
                    "Tablas Users, Matches y KinectMetrics creadas.",
                    "Métodos para guardar resultado de partida y consultar historial funcionando."
                ]
            }
        ]
    },

    # ==================== SPRINT 4 ====================
    4: {
        "dates": "Oct 19 – Nov 1",
        "Marco": [
            {
                "id": 19,
                "code": "SP4-MARCO-19",
                "branch": "feature/sp4-marco-mlagents-setup",
                "title": "Configuración de Unity ML-Agents y PyTorch CUDA en GPU",
                "desc": "Instalar el package de Unity ML-Agents, configurar FighterAgent : Agent en C# y validar la comunicación con PyTorch en tu GPU RTX 4060.",
                "prompt": "Hola Antigravity, actúa como mi tutor de Inteligencia Artificial en Unity. Por favor lee este archivo y explícame cómo estructurar la clase FighterAgent heredando de Agent de ML-Agents, definir el espacio de observaciones continuas y acciones discretas, y verificar la conexión con Python y PyTorch.",
                "criteria": [
                    "FighterAgent implementa CollectObservations, OnActionReceived y Heuristic.",
                    "Espacio de observación incluye distancias relativas, vida y estados.",
                    "Comunicación con mlagents-learn validada en la GPU RTX 4060."
                ]
            },
            {
                "id": 20,
                "code": "SP4-MARCO-20",
                "branch": "feature/sp4-marco-behavioral-cloning",
                "title": "Entrenamiento de Behavioral Cloning (BC / GAIL) en GPU",
                "desc": "Entrenar la política de imitación con el dataset humano de telemetría y exportar el modelo AI_Imitation.onnx para inferencia nativa.",
                "prompt": "Hola Antigravity, actúa como mi tutor de Deep Reinforcement Learning. Por favor lee este archivo y explícame cómo configurar el archivo yaml de entrenamiento con Behavioral Cloning (BC) y GAIL, ejecutar el entrenamiento en mi RTX 4060 y exportar el modelo ONNX a Unity.",
                "criteria": [
                    "Modelo entrenado con el dataset de partidas humanas del laboratorio.",
                    "Archivo AI_Imitation.onnx exportado e integrado en Unity Sentis/Barracuda.",
                    "El bot toma decisiones tácticas humanoides (spacing, bloqueo y castigo)."
                ]
            }
        ],
        "Sebas": [
            {
                "id": 21,
                "code": "SP4-SEBAS-21",
                "branch": "feature/sp4-sebas-super-flash",
                "title": "Super Arts y Efecto Visual Super Flash (Ryu y Ken)",
                "desc": "Implementar el efecto de fondo oscuro (Super Flash), rayos de energía y súper ataques Shinkuu Hadouken y Shinryuken.",
                "prompt": "Hola Antigravity, actúa como mi tutor de efectos visuales en Unity. Por favor lee este archivo y explícame cómo programar la pausa temporal (Hitstop) de 30 frames con oscurecimiento de fondo (Super Flash) y animación del Súper Ataque de Ryu y Ken.",
                "criteria": [
                    "Al disparar Super Art: fondo se oscurece y suena el sonido de Super Flash.",
                    "Shinkuu Hadouken dispara rayo gigante de 5 hits.",
                    "Shinryuken de Ken genera vórtice de fuego vertical."
                ]
            },
            {
                "id": 22,
                "code": "SP4-SEBAS-22",
                "branch": "feature/sp4-sebas-intros-victories",
                "title": "Poses de Victoria e Intros Únicas de Personajes",
                "desc": "Integrar animaciones de intro rival (Ryu vs Ken) y poses de victoria con frases de voz arcade.",
                "prompt": "Hola Antigravity, actúa como mi tutor de cinemáticas en Unity. Por favor lee este archivo y explícame cómo coordinar la secuencia de intro al inicio del combate y la activación de la pose de victoria con frase de voz al ganar el round.",
                "criteria": [
                    "Intro especial se reproduce al iniciar la partida Ryu vs Ken.",
                    "Pose de victoria se activa al derrotar al oponente.",
                    "Frases de victoria reproducidas correctamente con SF3SoundManager."
                ]
            }
        ],
        "Kevin": [
            {
                "id": 23,
                "code": "SP4-KEVIN-23",
                "branch": "feature/sp4-kevin-chunli-super",
                "title": "Super Art de Chun-Li (Houyoku Sen / Senretsukyaku)",
                "desc": "Configurar la animación, hitboxes y partículas del súper ataque de ráfaga de patadas de Chun-Li.",
                "prompt": "Hola Antigravity, actúa como mi tutor de combate 2D. Por favor lee este archivo y explícame cómo configurar el Súper Ataque Houyoku Sen de Chun-Li con avance continuo, múltiples hitboxes de patadas y remate aéreo.",
                "criteria": [
                    "Houyoku Sen avanza golpeando en cadena al oponente.",
                    "Partículas de destello y sonido de súper activados.",
                    "Daño y medidor de Super calibrados."
                ]
            },
            {
                "id": 24,
                "code": "SP4-KEVIN-24",
                "branch": "feature/sp4-kevin-kinect-kicks-hadouken",
                "title": "Mapeo de Gestos de Patada y Hadouken en Azure Kinect (Lab)",
                "desc": "Detectar elevación de pierna para patada física y unión/empuje de dos manos para disparar Hadouken en Azure Kinect.",
                "prompt": "Hola Antigravity, actúa como mi tutor de visión y sensores. Por favor lee este archivo y explícame cómo calcular los umbrales de posición de tobillos/rodillas para detectar patadas y la distancia euclidiana entre ambas muñecas para el gesto de Hadouken.",
                "criteria": [
                    "Elevación de pierna activa patada en el personaje en pantalla.",
                    "Juntar y proyectar ambas manos dispara el Hadouken.",
                    "Validado en hardware físico en los martes de laboratorio."
                ]
            }
        ]
    },

    # ==================== SPRINT 5 ====================
    5: {
        "dates": "Nov 2 – Nov 15",
        "Marco": [
            {
                "id": 25,
                "code": "SP5-MARCO-25",
                "branch": "feature/sp5-marco-rl-difficulty-models",
                "title": "Entrenamiento por Refuerzo (PPO) de 3 Dificultades (Easy, Med, Hard)",
                "desc": "Entrenar políticas por refuerzo con recompensas por control de distancia, castigo y daño, exportando 3 modelos ONNX.",
                "prompt": "Hola Antigravity, actúa como mi tutor de Machine Learning. Por favor lee este archivo y explícame cómo diseñar las funciones de recompensa en C# y configurar PPO en PyTorch para entrenar 3 niveles de habilidad (Fácil, Medio, Difícil) en mi GPU RTX 4060.",
                "criteria": [
                    "3 modelos exportados: AI_Easy.onnx, AI_Medium.onnx, AI_Hard.onnx.",
                    "AI_Easy comete errores y deja aperturas.",
                    "AI_Hard castiga saltos con Shoryuken y aplica parry reactivo."
                ]
            },
            {
                "id": 26,
                "code": "SP5-MARCO-26",
                "branch": "feature/sp5-marco-adaptive-ai-manager",
                "title": "Gestor de Dificultad Dinámica Adaptativa (AdaptiveAIManager.cs)",
                "desc": "Script que analiza la telemetría del jugador en vivo y cambia dinámicamente el modelo o pesos del bot para mantener el reto equilibrado.",
                "prompt": "Hola Antigravity, actúa como mi tutor de sistemas adaptativos. Por favor lee este archivo y explícame cómo programar AdaptiveAIManager.cs para evaluar métricas del jugador en vivo (frecuencia de aciertos, daño por segundo) y alternar entre los modelos ONNX en tiempo real.",
                "criteria": [
                    "AdaptiveAIManager evalúa rendimiento del jugador entre rounds.",
                    "Alterna suavemente entre modelos ONNX sin congelar la pantalla.",
                    "Registra los cambios de dificultad en la base de datos SQLite."
                ]
            }
        ],
        "Sebas": [
            {
                "id": 27,
                "code": "SP5-SEBAS-27",
                "branch": "feature/sp5-sebas-announcer-rounds",
                "title": "Sistema de Anunciador Oficial de SF3 (Round 1, Fight, K.O.!)",
                "desc": "Coordinar voces oficiales del anunciador arcade con banners de texto animados en pantalla y lógica de 3 rounds.",
                "prompt": "Hola Antigravity, actúa como mi tutor de UI y audio en Unity. Por favor lee este archivo y explícame cómo sincronizar las voces del Announcer ('Round 1... Fight!', 'You Win!', 'K.O.!') con animaciones de texto en pantalla y control de rounds en GameManager.cs.",
                "criteria": [
                    "Banners 'Round 1', 'Fight!', 'K.O.!', 'Perfect!' aparecen con voz oficial.",
                    "Sistema de mejor de 3 rounds con reseteo de posiciones de combate.",
                    "Victoria otorgada al ganar 2 rounds."
                ]
            },
            {
                "id": 28,
                "code": "SP5-SEBAS-28",
                "branch": "feature/sp5-sebas-character-select",
                "title": "Menú de Selección de Personajes Arcade con Retratos",
                "desc": "Pantalla de selección interactiva para elegir entre Ryu, Ken y Chun-Li con retratos arcade y sonidos de confirmación.",
                "prompt": "Hola Antigravity, actúa como mi tutor de UI en Unity. Por favor lee este archivo y explícame cómo armar la pantalla de selección de personaje con retratos animados, navegación por teclado/Kinect y transición a la escena de pelea.",
                "criteria": [
                    "Menú permite seleccionar entre Ryu, Ken y Chun-Li.",
                    "Muestra retrato grande del luchador y reproduce su voz al confirmar.",
                    "Carga la escena de combate pasando la selección al GameManager."
                ]
            }
        ],
        "Kevin": [
            {
                "id": 29,
                "code": "SP5-KEVIN-29",
                "branch": "feature/sp5-kevin-hud-arcade",
                "title": "HUD Arcade Completo (Barras de Vida, Super Gauge y Timer de 99s)",
                "desc": "Diseñar e implementar el HUD oficial Pixel-Perfect: barras de vida verde/roja, temporizador de 99s y barra de Super Art.",
                "prompt": "Hola Antigravity, actúa como mi tutor de UI en Unity. Por favor lee este archivo y explícame cómo construir el HUD arcade de SF3 con Canvas Pixel-Perfect, barras de vida con efecto de daño residual amarillo, medidor de Super y reloj de 99 segundos.",
                "criteria": [
                    "Barras de vida reflejan el daño recibido con animación suave.",
                    "Temporizador cuenta regresiva de 99 a 0 segundos y activa Time Over.",
                    "Barra de Super Art se llena al golpear y recibir daño."
                ]
            },
            {
                "id": 30,
                "code": "SP5-KEVIN-30",
                "branch": "feature/sp5-kevin-kinect-silhouette",
                "title": "Guía Visual de Silueta Azure Kinect en Pantalla (Lab)",
                "desc": "Widget en esquina de la pantalla que muestra la silueta del usuario para saber si está en el rango óptimo del sensor (1.5m a 4m).",
                "prompt": "Hola Antigravity, actúa como mi tutor de interfaces interactivas. Por favor lee este archivo y explícame cómo crear un widget de silueta que cambie de color (verde = buena posición, rojo = fuera de rango) según la coordenada Z del usuario en Azure Kinect.",
                "criteria": [
                    "Widget visualiza si el jugador está bien posicionado frente a la cámara.",
                    "Alerta si está demasiado cerca (<1.5m) o lejos (>4m).",
                    "Validado en el laboratorio los martes."
                ]
            }
        ]
    },

    # ==================== SPRINT 6 ====================
    6: {
        "dates": "Nov 16 – Nov 30",
        "Marco": [
            {
                "id": 31,
                "code": "SP6-MARCO-31",
                "branch": "feature/sp6-marco-bot-latency-balance",
                "title": "Calibración de Latencia y Balance de Frame Data del Bot",
                "desc": "Ajustar tiempos de reacción e interpolación de decisiones del bot para que el combate contra humanos en Kinect se sienta natural y justo.",
                "prompt": "Hola Antigravity, actúa como mi tutor de Game Feel y balance. Por favor lee este archivo y explícame cómo añadir pequeñas ventanas de reacción humana (100-200ms) a las decisiones del bot de IA para que no sea injustamente instantáneo frente a los movimientos físicos.",
                "criteria": [
                    "El bot tiene tiempos de reacción calibrados y realistas.",
                    "Combate se siente emocionante y justo para el usuario frente a Kinect.",
                    "Probado en partidas continuas en el laboratorio."
                ]
            },
            {
                "id": 32,
                "code": "SP6-MARCO-32",
                "branch": "feature/sp6-marco-build-optimization",
                "title": "Auditoría de Integración y Build Standalone .exe a 60 FPS",
                "desc": "Generar el ejecutable de producción en Windows 64-bit, auditar rendimiento de CPU/GPU y optimizar memoria para 60 FPS fijos.",
                "prompt": "Hola Antigravity, actúa como mi tutor de optimización en Unity. Por favor lee este archivo y explícame cómo auditar el Unity Profiler, eliminar picos de Garbage Collector y configurar el Build Settings para generar un .exe standalone impecable a 60 FPS.",
                "criteria": [
                    "Build ejecutable (.exe) generado sin errores.",
                    "El juego corre a 60 FPS constantes en resolución 1080p.",
                    "Sin fugas de memoria tras 10 partidas consecutivas."
                ]
            }
        ],
        "Sebas": [
            {
                "id": 33,
                "code": "SP6-SEBAS-33",
                "branch": "feature/sp6-sebas-polish-audio-mix",
                "title": "Pulido de Assets, Shaders de Destello y Balance de Mezcla de Audio",
                "desc": "Normalizar volúmenes de SFX vs BGM vs Voces, ajustar shaders de destello de impacto y corregir detalles visuales de Ken y escenarios.",
                "prompt": "Hola Antigravity, actúa como mi tutor de pulido audiovisual en Unity. Por favor lee este archivo y explícame cómo balancear los AudioMixers para que la música no tape las voces de los luchadores, y cómo revisar que ningún sprite tenga artefactos visuales.",
                "criteria": [
                    "AudioMixer balanceado (Voces, SFX y Música tienen volumen armónico).",
                    "Todos los fondos y sprites verificados sin bordes borrosos.",
                    "Efectos visuales de impacto perfectamente alineados."
                ]
            },
            {
                "id": 34,
                "code": "SP6-SEBAS-34",
                "branch": "feature/sp6-sebas-user-manual-demo",
                "title": "Documentación y Manual de Usuario / Guía de Demostración",
                "desc": "Elaborar la guía de pasos para la presentación ante el jurado/profesor, explicando el flujo de la demo en vivo con Kinect e IA.",
                "prompt": "Hola Antigravity, actúa como mi tutor de documentación técnica. Por favor lee este archivo y explícame cómo estructurar un Manual de Demostración impecable para la sustentación ante el profesor, detallando los pasos de encendido de Kinect, inicio de partida y explicación técnica de la IA.",
                "criteria": [
                    "Manual de Demostración guardado en Docs/GUIA_DEMO_EXPOSICION.md.",
                    "Guía de calibración rápida de Azure Kinect incluida.",
                    "Flujo de exposición ensayado con el equipo."
                ]
            }
        ],
        "Kevin": [
            {
                "id": 35,
                "code": "SP6-KEVIN-35",
                "branch": "feature/sp6-kevin-kinect-noise-filter",
                "title": "Filtro de Suavizado de Ruido de Articulaciones en Azure Kinect (Lab)",
                "desc": "Aplicar filtros de suavizado (Moving Average / Exponential Smoothing) a las 32 articulaciones para eliminar falsos disparos en el sensor.",
                "prompt": "Hola Antigravity, actúa como mi tutor de procesamiento de señales en Unity. Por favor lee este archivo y explícame cómo programar un filtro de suavizado temporal para las coordenadas (X, Y, Z) de Azure Kinect que elimine el jitter sin añadir latencia perceptible.",
                "criteria": [
                    "Filtro de suavizado elimina temblores en las manos y pies.",
                    "Latencia de respuesta se mantiene por debajo de 50ms.",
                    "Probado y calibrado en el laboratorio con el sensor físico."
                ]
            },
            {
                "id": 36,
                "code": "SP6-KEVIN-36",
                "branch": "feature/sp6-kevin-stats-screen",
                "title": "Pantalla de Estadísticas Finales con Consultas SQLite",
                "desc": "Pantalla de resumen al terminar el combate que muestra golpes acertados, Hadoukens lanzados, precisión física y ganador desde SQLite.",
                "prompt": "Hola Antigravity, actúa como mi tutor de UI y bases de datos en Unity. Por favor lee este archivo y explícame cómo armar la pantalla de GameOver / Estadísticas consultando los datos de la última partida en SQLite y presentándolos con diseño arcade.",
                "criteria": [
                    "Pantalla de estadísticas muestra datos reales de la partida guardada.",
                    "Muestra precisión de gestos corporales con Kinect.",
                    "Botones para revancha o volver al menú principal funcionando."
                ]
            }
        ]
    }
}

def generate_task_markdown(sprint_num, dev_name, task):
    criteria_lines = "\n".join([f"- [ ] {c}" for c in task["criteria"]])
    content = f"""# 📌 Tarea #{task['id']} [{task['code']}]: {task['title']}
## Sprint {sprint_num} ({ALL_SPRINT_TASKS[sprint_num]['dates']}) | Asignado a: @{dev_name}

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b {task['branch']}
```

---

### 🎯 2. Explicación Técnica de la Tarea

{task['desc']}

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"{task['prompt']}"*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
{criteria_lines}

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: {task['title'].lower()} (#{task['id']})"

# 2. Subir rama a GitHub
git push -u origin {task['branch']}
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #{task['id']}`.
"""
    return content

def main():
    base_dir = os.path.join(os.getcwd(), "Devs")
    created_count = 0

    for sprint_num, sprint_data in ALL_SPRINT_TASKS.items():
        for dev_name in ["Marco", "Sebas", "Kevin"]:
            sprint_folder = os.path.join(base_dir, dev_name, f"Sprint_{sprint_num}")
            os.makedirs(sprint_folder, exist_ok=True)
            
            for task in sprint_data[dev_name]:
                filename = f"TASK_SP{sprint_num}_{task['id']:02d}_{task['branch'].split('-')[-1].upper()}.md"
                filepath = os.path.join(sprint_folder, filename)
                
                content = generate_task_markdown(sprint_num, dev_name, task)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content.strip())
                created_count += 1

    print(f"¡Éxito! Se generaron los {created_count} archivos markdown de tareas en Devs/")

if __name__ == "__main__":
    main()
