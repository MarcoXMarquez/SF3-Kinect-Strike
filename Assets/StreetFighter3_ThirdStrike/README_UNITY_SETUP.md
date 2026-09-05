# Guía de Configuración e Integración en Unity
## Street Fighter III: 3rd Strike - Complete Asset Pack

Este paquete ha sido estructurado y organizado semánticamente para su importación inmediata en **Unity (2021.3 LTS, 2022.3 LTS, Unity 6 o superior)**.

---

## 1. Estructura Organizada del Paquete

```text
Assets/StreetFighter3_ThirdStrike/
├── Characters/                  # 20 Luchadores organizados en 7 categorías estándar con nombres descriptivos
│   ├── 00_Gill/                 # 121 acciones (3,384 frames)
│   ├── 01_Alex/                 # 80 acciones (2,024 frames)
│   ├── 02_Ryu/                  # 66 acciones (1,109 frames) - Traje blanco y cinta roja
│   │   ├── 01_Movement/         # idle_stance, walk_forward, walk_backward, dash_forward, jump_neutral...
│   │   ├── 02_Normals/          # light_punch, heavy_kick, crouch_medium_kick, jump_forward_heavy_punch...
│   │   ├── 03_Specials_Supers/  # special_hadouken, special_shoryuken, super_art_shinku_hadouken...
│   │   ├── 04_Defense_Hit/      # parry_high, parry_low, hurt_light_1, knockdown_air, wakeup_recovery...
│   │   ├── 05_Throws/           # throw_shoulder_slam, throw_air_slam...
│   │   ├── 06_Intros_Victories/ # intro_taunt, victory_pose_1, victory_pose_2...
│   │   └── 07_Secondary_Extras/ # taunt_audio, hitstop_stun_extra...
│   ├── 03_Yun/                  # 73 acciones (1,302 frames)
│   ├── 04_Dudley/               # 73 acciones (1,620 frames)
│   ├── 05_Necro/                # 82 acciones (1,706 frames)
│   ├── 06_Hugo/                 # 69 acciones (2,097 frames)
│   ├── 07_Ibuki/                # 105 acciones (3,363 frames)
│   ├── 08_Elena/                # 72 acciones (1,669 frames)
│   ├── 09_Oro/                  # 57 acciones (1,288 frames)
│   ├── 10_Yang/                 # 72 acciones (1,355 frames)
│   ├── 11_Ken/                  # 79 acciones (1,327 frames)
│   ├── 12_Sean/                 # 74 acciones (1,260 frames)
│   ├── 13_Urien/                # 67 acciones (2,032 frames)
│   ├── 14_Akuma_Gouki/          # 77 acciones (1,654 frames)
│   ├── 16_Chun_Li/              # 79 acciones (1,714 frames) - Qipao azul clásico oficial
│   ├── 17_Makoto/               # 79 acciones (2,006 frames)
│   ├── 18_Q/                    # 65 acciones (1,677 frames)
│   ├── 19_Twelve/               # 93 acciones (2,429 frames)
│   └── 20_Remy/                 # 78 acciones (1,727 frames)
│
├── Effects/                     # Efectos visuales clasificados por nombres y carpetas
│   ├── 01_Energy_Beam_Blast/
│   ├── 02_Vertical_Spark_Beam/
│   ├── 03_Flame_Burst_Impact/
│   ├── 04_White_Flash_Spark/
│   ├── 05_Parry_Blue_Flash_Iconic/         # Destello azul oficial del Parry
│   ├── 06_Hit_Spark_Electric_Yellow/       # Chispas de impacto de golpe medio/fuerte
│   ├── 07_Dust_Ground_Movement/            # Polvo para dashes, saltos y caídas
│   ├── 08_Impact_Point_Burst/
│   ├── 09_Guard_Block_Sparks/              # Chispas al bloquear un golpe
│   ├── 10_Impact_Flash_Ring/
│   ├── 11_Shadow_Silhouettes/
│   ├── 12_Smoke_Impact_Clouds/
│   ├── 13_Hadouken_Energy_Aura_Blue/
│   ├── 14_Dark_Hadou_Aura_Purple/
│   ├── 15_Super_Art_Flash_Burst/           # Explosión de luz al activar un Super Art
│   ├── 16_Blue_Electricity_Sparks/
│   ├── 17_Ground_Debris_Pebbles/
│   ├── 18_Hit_Sparks_Multi_Impacts/
│   ├── 19_Super_Art_Screen_Flashes/        # Fondos oscuros / rayos de pantalla de Super
│   ├── 20_Critical_Hit_Sparks_Red/         # Chispas rojas de contraataque / golpe crítico
│   ├── Projectiles_Ryu_Hadouken/
│   ├── Projectiles_Ryu_Denjin/
│   ├── Projectiles_Akuma_GouHadou/
│   └── Projectiles_Urien_AegisReflector/
│
├── Stages/                      # Fondos de escenario con capas de scroll/parallax y props
│   ├── China_ChunLi/            # Capas + props animados (toldos, bambú, comensales)
│   ├── Japan_Ryu/               # Templo budista, cielo y tejados separados
│   ├── USA_Ken_Alex/            # Estación de metro y calles de NY
│   ├── London_Dudley/           # Calles de Londres y estación
│   ├── Japan_Makoto/            # Dojo de karate
│   ├── Africa_Elena/            # Sabana africana y suelo
│   ├── Russia_Necro_Twelve/     # Fábrica y paisaje nevado
│   └── Mediterranean_Gill/      # Templo colosal
│
├── Audio/
│   ├── BGM/                     # 14 pistas de música completas de escenarios (MP3)
│   ├── SFX/                     # Efectos de sonido con nombres descriptivos (WAV)
│   │   ├── 01_Combat_Hits/      # Hit_Punch_Light, Hit_Kick_Heavy, Hit_Critical_Counter...
│   │   ├── 02_Defense_and_Parry/# Parry_Success_Iconic_SF3, Guard_Block_Light/Heavy...
│   │   ├── 03_Super_Arts_and_EX/# Super_Art_Activation_Flash, Super_Art_Finish_Impact...
│   │   ├── 04_Movement_and_Physics/ # Jump_Takeoff, Ground_Landing, Dash_Forward...
│   │   ├── 05_Announcer_and_Interface/ # Round_One_Ready, Fight_Call, K_O_Victory...
│   │   └── 06_All_Raw_Arcade_SFX/   # Los 76 archivos originales SE_00000.wav a SE_00109.wav
│   └── Voices/                  # Carpetas individuales de voces por personaje (WAV)
│       ├── 00_Gill/ (21 clips)
│       ├── 01_Alex/ (19 clips)
│       ├── 02_Ryu/ (20 clips)   # Hadouken, Shoryuken, Tatsumaki, K.O. scream...
│       ├── 03_Yun/ (19 clips)
│       ├── 04_Dudley/ (20 clips)
│       ├── 05_Necro/ (22 clips)
│       ├── 06_Hugo/ (29 clips)
│       ├── 07_Ibuki/ (20 clips)
│       ├── 08_Elena/ (27 clips)
│       ├── 09_Oro/ (21 clips)
│       ├── 10_Yang/ (22 clips)
│       ├── 11_Ken/ (22 clips)   # Hadouken, Shoryuken de fuego, Shinryuken...
│       ├── 12_Sean/ (25 clips)
│       ├── 13_Urien/ (22 clips)
│       ├── 14_Akuma_Gouki/ (18 clips) # Messatsu, Shun Goku Satsu shouts...
│       ├── 16_Chun_Li/ (29 clips)     # Kikoken, Spinning Bird, Kikosho, Yatta!...
│       ├── 17_Makoto/ (32 clips)
│       ├── 18_Q/ (18 clips)
│       ├── 19_Twelve/ (23 clips)
│       ├── 20_Remy/ (22 clips)
│       ├── Announcer/ (34 clips)# "Yeah that's it!", "Fight!", "Round 1", "You Win"...
│       └── 3S_Voice_Collection.mp3
└── README_UNITY_SETUP.md
```

---

## 2. Configuración Esencial de Sprites en Unity (Pixel-Perfect 2D)

1. Selecciona las imágenes en Unity Inspector.
2. Aplica los siguientes parámetros:
   * **Texture Type:** `Sprite (2D and UI)`
   * **Sprite Mode:** `Single`
   * **Pixels Per Unit:** `100` (ajustar según la escala de la cámara)
   * **Pivot:** `Bottom` (recomendado para que los pies de los luchadores toquen el suelo al cambiar de animación)
   * **Filter Mode:** `Point (no filter)` *(¡CRÍTICO! Evita que el pixel art se desenfoque)*
   * **Compression:** `None` *(mantiene los colores puros y nítidos)*
   * **Alpha Is Transparency:** `Activado (Checked)`
3. Haz clic en **Apply**.

---

## 3. Lienzo Unificado y Espacio Transparente (Canvas Baseline CPS-3)

Al inspeccionar los sprites notarás que algunos fotogramas tienen un espacio transparente amplio arriba o abajo. **Esto es intencional y fundamental para la física del juego**:
* **Línea de suelo fija (Floor Baseline):** En la placa arcade CPS-3 de Capcom, todas las animaciones de un personaje comparten un lienzo de referencia unificado.
* **Saltos y Elevación Natural:** En un salto vertical o en un *Shoryuken*, el fotograma 0 está en el suelo (espacio vacío arriba), mientras que los fotogramas en el aire tienen a Ryu elevado en la parte superior del lienzo (espacio vacío debajo).
* **Cero desfases en Unity:** Al mantener este lienzo original y configurar el pivote en **`Bottom` (`Vector2(0.5f, 0.0f)`)**, la trayectoria aérea, la altura del salto y el retroceso de los golpes ocurren **de forma 100% natural** en Unity sin tener que programar offsets manuales frame a frame ni recalibrar pivotes.

---

## 4. Estructura de las 7 Categorías Estándar

Todos los personajes contienen exactamente 7 carpetas funcionales:
1. **`01_Movement`**: Reposo (`idle_stance`), caminar (`walk_forward`, `walk_backward`), carreras (`dash_forward`, `dash_backward`), saltos (`jump_neutral`, `jump_forward`, `jump_backward`) y agacharse (`crouch_down`, `crouch_idle`).
2. **`02_Normals`**: Todos los golpes básicos completos (`light_punch`, `medium_punch`, `heavy_punch`, `light_kick`, `medium_kick`, `heavy_kick`, versiones agachadas y aéreas).
3. **`03_Specials_Supers`**: Movimientos especiales icónicos (`special_hadouken`, `special_shoryuken`, `special_tatsumaki`) y Super Arts (`super_art_shinku_hadouken`, `super_art_denjin_hadouken`, etc.).
4. **`04_Defense_Hit`**: Sistema defensivo (`parry_high`, `parry_low`, `parry_air`), reacciones de impacto (`hurt_light_1`, `hurt_crouch_1`, `knockdown_face_down`) y recuperación (`wakeup_recovery`).
5. **`05_Throws`**: Agarres y derribos estándar y aéreos (`throw_forward_shoulder_slam`, `throw_backward_trip`).
6. **`06_Intros_Victories`**: Poses de entrada al combate, burlas (`intro_taunt`) y poses de victoria (`victory_pose_1`, `victory_pose_2`).
7. **`07_Secondary_Extras`**: Efectos complementarios de impacto, sombras y transiciones específicas del luchador.

---

## 5. Creación Automática de Animaciones

1. Selecciona la carpeta del personaje o una categoría y ve al menú:
   **`SF3 Tools` ➔ `Auto-Generate Animation Clips from Selected Folder`**.
2. El script escaneará recursivamente todas las carpetas con fotogramas, ordenará `0.png` a `N.png` y generará los archivos `.anim` a **14 FPS** (tasa arcade nativa), activando `Loop` automáticamente en reposo y caminata.
3. Para animaciones individuales, selecciona los fotogramas y arrástralos a la ventana **Hierarchy** o **Scene**.

