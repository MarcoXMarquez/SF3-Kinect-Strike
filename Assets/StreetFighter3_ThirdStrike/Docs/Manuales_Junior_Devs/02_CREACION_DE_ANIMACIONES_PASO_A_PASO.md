# 🎬 Guía 02: Creación de Animaciones Paso a Paso
## Cómo crear Animation Clips en Unity a 14 FPS Arcade

Si nunca has creado una animación en Unity, no te preocupes: en esta guía aprenderás paso a paso cómo convertir una secuencia de imágenes (`0.png`, `1.png`, `2.png`...) en una animación lista para reproducirse en combate.

---

### 📍 Paso 1: Abrir la Ventana de Animación
1. En la barra superior de menús de Unity, haz clic en **Window**.
2. Pasa el cursor sobre **Animation**.
3. Haz clic en **Animation** (o usa el atajo de teclado **`Ctrl + 6`**).
4. Se abrirá una ventana flotante llamada **Animation**.
5. **Consejo de comodidad:** Haz clic sobre la pestaña que dice *Animation* y arrástrala hacia el panel inferior de Unity, justo al lado de la pestaña *Project* o *Console*. Así tendrás una vista amplia para trabajar.

---

### 🚀 Método A: El Generador Automático en 1 Clic (Recomendado)
Para ahorrarte horas de trabajo manual, hemos programado una herramienta especial dentro del proyecto:

1. Ve a la ventana **Project**.
2. Navega hasta la carpeta del personaje que quieras animar (por ejemplo: `Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu`) o una categoría específica (ej. `01_Movement`).
3. Haz un clic izquierdo sobre la carpeta seleccionada.
4. Ahora mira la barra superior de menús de Unity. Verás un nuevo menú llamado **`SF3 Tools`**.
5. Haz clic en **SF3 Tools** ➔ **`Auto-Generate Animation Clips from Selected Folder`**.
6. **¡Listo!** El script hará lo siguiente automáticamente en 2 segundos:
   * Leerá recursivamente todas las subcarpetas organizadas en las 7 categorías (`01_Movement`, `02_Normals`, `03_Specials_Supers`, etc.).
   * Ordenará los fotogramas numéricamente (`0.png`, `1.png`, `2.png`...).
   * Creará los archivos `.anim` configurados a **14 FPS** (tasa arcade nativa CPS-3).
   * Activará la repetición infinita (`Loop`) en las animaciones de reposo y caminata (`idle_stance`, `walk_forward`, `walk_backward`, etc.).

---

### 🖐️ Método B: Creación Manual Paso a Paso (Para animaciones nuevas o efectos)
Si deseas crear o ajustar una animación específica a mano, sigue estos pasos:

#### 1. Seleccionar el GameObject en la Hierarchy
1. En la ventana **Hierarchy** (a la izquierda), selecciona el GameObject de tu personaje (ej. `Fighter_Ryu` o su hijo `Visuals`).
2. Asegúrate de que tenga añadido el componente **Animator** en el Inspector.

#### 2. Crear el Archivo de Animación (.anim)
1. Con el GameObject seleccionado, mira la ventana **Animation**.
2. Verás un botón en el centro que dice **Create**. Haz clic en él.
3. Se abrirá una ventana para guardar el archivo.
   * Navega a la carpeta de la acción (ej. `Assets/.../Characters/02_Ryu/01_Movement/idle_stance/`).
   * Ponle un nombre descriptivo: por ejemplo `Ryu_Idle_Stance.anim`.
   * Haz clic en **Guardar**.

#### 3. Arrastrar los Sprites a la Línea de Tiempo
1. En la ventana **Project**, abre la carpeta con las imágenes (ej. `01_Movement/idle_stance/`).
2. Selecciona todas las imágenes en orden: haz clic en `0.png`, mantén presionado **Shift**, y haz clic en la última imagen.
3. Arrastra las imágenes seleccionadas hacia el lado derecho de la ventana **Animation** (en la cuadrícula gris con números de tiempo).
4. Suelta el ratón: verás que aparecen pequeños rombos azules (*Keyframes*) a lo largo de la línea de tiempo.

#### 4. Configurar la Tasa de Cuadros a 14 FPS (CPS-3 Arcade Rate)
Por defecto, Unity crea animaciones a 60 FPS, lo que hará que tu animación dure un parpadeo y se vea absurdamente rápida.
1. En la esquina superior derecha de la ventana **Animation**, busca el campo llamado **Samples**.
   * *¿No ves el campo Samples?* Haz clic en el icono de los **tres puntos verticales `⋮`** (arriba a la derecha de la ventana Animation) y marca la casilla **Show Sample Rate**.
2. En la casilla **Samples**, borra el número `60` y escribe: **`14`**.
3. Presiona **Enter**.
4. Haz clic en el botón de **Play `▶`** en la ventana Animation para probarla: verás que ahora el personaje se mueve con la cadencia y fluidez idéntica a la máquina arcade original.

#### 5. Activar la Repetición Infinita (Loop)
Las animaciones continuas de reposo (`idle_stance`), caminar (`walk_forward`/`walk_backward`) y agacharse deben repetirse cíclicamente.
1. Ve a la ventana **Project** y haz clic sobre el archivo `.anim` que creaste (ej. `Ryu_Idle_Stance.anim`).
2. Mira el **Inspector** a la derecha.
3. Busca la casilla **Loop Time**.
4. **MÁRCALA** (debe quedar con una palomita `[X]`).
5. Haz clic en **Apply**.

---

### 📖 Glosario de Nombres y Categorías de Street Fighter III
Todos los personajes están organizados bajo un estándar claro de 7 categorías con nombres completos en inglés técnico:

#### 1. `01_Movement` (Movilidad y Locomoción)
| Nombre de Carpeta | Tipo de Acción | ¿Debe tener Loop? |
| :--- | :--- | :--- |
| `idle_stance` | Reposo / De pie respirando (Idle) | **SÍ (Loop = True)** |
| `walk_forward` | Caminar hacia adelante | **SÍ (Loop = True)** |
| `walk_backward` | Caminar hacia atrás | **SÍ (Loop = True)** |
| `dash_forward` | Impulso rápido hacia adelante (Run/Dash) | NO |
| `dash_backward` | Retroceso rápido (Backdash) | NO |
| `crouch_down` | Transición de pie a agachado | NO |
| `crouch_idle` | Mantenerse agachado | **SÍ (Loop = True)** |
| `jump_neutral` | Salto vertical estático | NO |
| `jump_forward` | Salto en parábola hacia adelante | NO |
| `jump_backward` | Salto en parábola hacia atrás | NO |

#### 2. `02_Normals` (Golpes Básicos)
| Nombre de Carpeta | Tipo de Acción | ¿Debe tener Loop? |
| :--- | :--- | :--- |
| `light_punch` | Puño débil (Jab) de pie | NO |
| `medium_punch` | Puño medio (Strong) de pie | NO |
| `heavy_punch` | Puño fuerte (Fierce) de pie | NO |
| `light_kick` | Patada débil (Short) de pie | NO |
| `medium_kick` | Patada media (Forward) de pie | NO |
| `heavy_kick` | Patada fuerte (Roundhouse) de pie | NO |
| `crouch_light_punch` | Puño débil agachado | NO |
| `crouch_medium_kick` | Patada media agachada (Low poke) | NO |
| `crouch_heavy_kick` | Barrida / Patada fuerte agachada (Sweep) | NO |
| `jump_forward_heavy_punch` | Puño fuerte en salto hacia adelante | NO |
| `jump_neutral_heavy_kick` | Patada fuerte en salto vertical | NO |

#### 3. `03_Specials_Supers` (Especiales y Super Arts)
| Nombre de Carpeta | Tipo de Acción | ¿Debe tener Loop? |
| :--- | :--- | :--- |
| `special_hadouken` | Bola de energía Hadouken / Kikoken | NO |
| `special_shoryuken` | Golpe de dragón Shoryuken ascendente | NO |
| `special_tatsumaki` | Patada giratoria Tatsumaki Senpuu-kyaku | NO |
| `super_art_shinku_hadouken` | Super Art I: Gran ráfaga de energía | NO |
| `super_art_shinryuken` | Super Art II: Tornado de fuego | NO |
| `super_art_denjin_hadouken` | Super Art III: Proyectil eléctrico cargable | NO |

#### 4. `04_Defense_Hit` (Defensa, Parries e Impactos)
| Nombre de Carpeta | Tipo de Acción | ¿Debe tener Loop? |
| :--- | :--- | :--- |
| `parry_high` | Bloqueo perfecto alto (Parry de pie) | NO |
| `parry_low` | Bloqueo perfecto bajo (Parry agachado) | NO |
| `parry_air` | Bloqueo perfecto en el aire | NO |
| `hurt_light_1`, `hurt_heavy_1` | Reacción a impacto de pie | NO |
| `hurt_crouch_1` | Reacción a impacto estando agachado | NO |
| `knockdown_face_up` | Caída y derribo al suelo boca arriba | NO |
| `knockdown_face_down` | Caída y derribo al suelo boca abajo | NO |
| `wakeup_recovery` | Levantarse del suelo | NO |

#### 5. `05_Throws`, `06_Intros_Victories` y `07_Secondary_Extras`
| Nombre de Carpeta | Categoría | Tipo de Acción |
| :--- | :--- | :--- |
| `throw_shoulder_slam` | `05_Throws` | Agarre hacia adelante con lanzamiento al suelo |
| `throw_air_slam` | `05_Throws` | Derribo aéreo |
| `intro_taunt` | `06_Intros_Victories` | Animación de entrada o burla previa al asalto |
| `victory_pose_1`, `victory_pose_2` | `06_Intros_Victories` | Poses triunfales tras ganar el combate |
| `taunt_audio`, `hitstop_stun_extra` | `07_Secondary_Extras` | Efectos o fotogramas específicos de recuperación |
