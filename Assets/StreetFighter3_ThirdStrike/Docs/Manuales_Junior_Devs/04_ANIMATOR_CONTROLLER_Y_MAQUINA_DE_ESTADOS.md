# 🕹️ Guía 04: Animator Controller y Máquina de Estados
## Configuración de Estados y Respuesta Instantánea Frame-Perfect

El **Animator Controller** es el cerebro que decide qué animación debe reproducirse en cada momento (si el personaje está quieto, caminando, agachado o lanzando un Hadouken).

En los juegos de pelea, el retraso (*input lag*) es inaceptable: si el jugador lanza un puñetazo, la animación debe comenzar **en ese mismísimo milisegundo**, sin esperar a que termine el paso de caminata. En esta guía aprenderás cómo configurar las transiciones de forma **Frame-Perfect**.

---

### 📍 Paso 1: Crear el Animator Controller
1. En la ventana **Project**, ve a la carpeta de tu personaje (ej. `Characters/02_Ryu/`).
2. Haz clic derecho en un espacio vacío ➔ **Create** ➔ **Animator Controller**.
3. Nómbralo: **`Ryu_AnimatorController`**.
4. Ve a la Hierarchy, selecciona el GameObject **`Visuals`** de Ryu.
5. En el Inspector, arrastra tu nuevo `Ryu_AnimatorController` al campo **Controller** del componente `Animator`.

---

### 📍 Paso 2: Abrir la Ventana Animator
1. Haz doble clic sobre el archivo `Ryu_AnimatorController` en la ventana Project.
2. Se abrirá la ventana **Animator** (una cuadrícula con nodos como `Entry`, `Any State` y `Exit`).

---

### 📍 Paso 3: Crear los Parámetros de Control
Los parámetros son variables que tus scripts (y posteriormente el Kinect) modificarán para activar animaciones:
1. En la esquina superior izquierda de la ventana Animator, haz clic en la pestaña **Parameters** (al lado de *Layers*).
2. Haz clic en el botón con el símbolo **`+`** para agregar cada uno de los siguientes parámetros:

| Tipo | Nombre Exacto | Uso |
| :--- | :--- | :--- |
| **Float** | `MoveSpeed` | Velocidad horizontal (0 = quieto, >0.1 = caminar adelante, <-0.1 = caminar atrás). |
| **Bool** | `isGrounded` | `true` si está en el suelo, `false` si está en el aire. |
| **Bool** | `isCrouching` | `true` si el jugador se agacha. |
| **Trigger** | `Attack_LP` | Disparo instantáneo de puño débil. |
| **Trigger** | `Attack_HP` | Disparo instantáneo de puño fuerte. |
| **Trigger** | `Special_Hadouken` | Disparo del Hadouken. |
| **Trigger** | `Special_Shoryuken` | Disparo del Shoryuken. |
| **Trigger** | `TakeHit` | Se activa cuando el personaje recibe un golpe. |
| **Bool** | `isDead` | `true` cuando la barra de vida llega a cero. |

---

### 📍 Paso 4: Colocar los Estados en la Cuadrícula
1. Ve a la ventana **Project** donde están tus archivos de animación (`.anim`) generados dentro de las categorías de tu personaje:
2. Arrastra `idle_stance.anim` (de `01_Movement/idle_stance/`) al centro de la cuadrícula.
   * Se volverá de color **naranja**. Esto significa que es el **Estado por Defecto** (*Default State*): la animación con la que Ryu inicia la pelea.
3. Arrastra los demás clips:
   * `walk_forward.anim` (de `01_Movement/walk_forward/`)
   * `walk_backward.anim` (de `01_Movement/walk_backward/`)
   * `light_punch.anim` (de `02_Normals/light_punch/`)
   * `special_hadouken.anim` (de `03_Specials_Supers/special_hadouken/`)
   * `hurt_light_1.anim` (de `04_Defense_Hit/hurt_light_1/`)
   * `knockdown_face_down.anim` (de `04_Defense_Hit/knockdown_face_down/`)

---

### 📍 Paso 5: Conectar las Transiciones (Flechas)
1. Haz clic derecho sobre el bloque **idle_stance** ➔ Selecciona **Make Transition**.
2. Lleva la flecha hasta **walk_forward** y haz clic izquierdo para fijarla.
3. Haz clic derecho sobre **walk_forward** ➔ **Make Transition** ➔ Conecta de regreso a **idle_stance**.

---

### ⚠️ Paso 6: La Regla de Oro (Frame-Perfect Input)
**¡Mucha atención aquí!** Si no haces este paso, tus ataques se sentirán lentos, torpes y retrasados:

1. Haz clic sobre la flechita de transición que va de **idle_stance** a **walk_forward**.
2. Mira el panel **Inspector** a la derecha:
   * **DESMARCA la casilla `Has Exit Time`** (debe quedar sin palomita).
   * Haz clic en la pequeña flecha de **Settings** para desplegar los detalles.
   * En **`Transition Duration (s)`**, borra el valor y escribe: **`0`**.
   * En **`Transition Offset`**, escribe: **`0`**.
3. En la parte inferior del Inspector, busca la lista **Conditions**:
   * Haz clic en el botón **`+`**.
   * Selecciona el parámetro: **`MoveSpeed`**.
   * Cambia el operador a **`Greater`** y escribe: **`0.1`**.

4. **Repite lo mismo para la flecha de regreso (de walk_forward a idle_stance):**
   * Desmarca `Has Exit Time`.
   * `Transition Duration` = `0`.
   * Condition: `MoveSpeed` **`Less`** `0.1`.

#### Para los Ataques (ej. de idle_stance a light_punch):
* Desmarca `Has Exit Time`.
* `Transition Duration` = `0`.
* Condition: Selecciona el trigger **`Attack_LP`**.

#### Para Recibir Daño (desde Any State):
Cualquier ataque recibido debe interrumpir inmediatamente lo que sea que Ryu esté haciendo:
1. Haz clic derecho en el bloque azul claro **Any State** ➔ **Make Transition** ➔ Conéctalo a **hurt_light_1**.
2. En el Inspector:
   * Desmarca `Has Exit Time`.
   * `Transition Duration` = `0`.
   * Condition: Añade el trigger **`TakeHit`**.
