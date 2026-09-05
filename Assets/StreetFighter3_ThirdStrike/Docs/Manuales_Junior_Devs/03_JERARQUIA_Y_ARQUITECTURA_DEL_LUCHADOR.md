# 🏛️ Guía 03: Jerarquía y Arquitectura del Luchador
## Estructura de GameObjects para Combate y Compatibilidad con Kinect

En un juego de pelea profesional, **nunca se coloca todo en un solo GameObject**. Si mezclas las físicas, el sprite, los colisionadores de daño y el script de control en el mismo objeto, cuando quieras voltear al personaje para que mire a la izquierda o cuando conectes el sensor Kinect, las coordenadas de los huesos y los colisionadores se desfasarán por completo.

En esta guía construiremos la jerarquía estándar limpia que separa **Lógica y Físicas**, **Renderizado Visual** y **Cajas de Combate**.

---

### 🌳 El Árbol de Jerarquía Final
Así es como debe lucir tu personaje en la ventana **Hierarchy**:

```text
[GameObject] Fighter_Ryu            <-- Root (Físicas del mundo, posición X/Y, script maestro)
   │
   ├── [Child 1] Visuals             <-- SpriteRenderer y Animator (Gira a izq/der)
   │
   ├── [Child 2] Pushbox             <-- BoxCollider2D sólido (Impide que los luchadores se atraviesen)
   │
   ├── [Child 3] Hurtbox_Root        <-- BoxCollider2D Trigger (Donde Ryu recibe golpes)
   │
   └── [Child 4] Hitbox_Root         <-- BoxCollider2D Trigger (Donde el puño/pie de Ryu pega)
```

---

### 📍 Paso a Paso de Construcción en Unity

#### 1. Crear el GameObject Padre (Root)
1. En la ventana **Hierarchy**, haz clic derecho en un espacio vacío y selecciona:
   **Create Empty**.
2. En el Inspector, cámbiale el nombre a: **`Fighter_Ryu`**.
3. En el componente **Transform**, asegúrate de que **Position** esté en `(X: 0, Y: 0, Z: 0)`.
4. Asigna un **Tag**: En la parte superior del Inspector, haz clic en el desplegable **Tag** y selecciona **`Player`**.

#### 2. Configurar las Físicas (Rigidbody 2D)
1. Con `Fighter_Ryu` seleccionado, haz clic en el botón **Add Component** en el Inspector.
2. Escribe `Rigidbody 2D` y selecciónalo.
3. Modifica sus propiedades:
   * **Body Type:** `Dynamic`.
   * **Mass:** `1`.
   * **Linear Damping:** `0`.
   * **Gravity Scale:** Escribe **`3`** *(Nota: En los juegos de pelea la caída debe ser rápida y responsiva, no lenta como astronauta).*
   * **Collision Detection:** Cambia a **`Continuous`** *(Evita que un golpe rápido o salto atraviese el suelo).*
   * Despliega la sección **Constraints** (Restricciones):
     * Marca la casilla: **`Freeze Rotation Z` [X]**. *(¡Crítico! Si no marcas esto, cuando otro personaje empuje a Ryu, este se caerá de espaldas rodando).*

#### 3. Crear la Pushbox (Caja de Empuje Físico)
La Pushbox es la caja invisible que impide que Ryu y Ken se traspasen como fantasmas cuando caminan el uno hacia el otro:
1. Con `Fighter_Ryu` seleccionado, haz clic en **Add Component** ➔ **Box Collider 2D**.
2. Deja la casilla **Is Trigger** **DESMARCADA (False)**.
3. Haz clic en el botón **Edit Collider** (el icono cuadrado verde con cuatro puntos).
4. En la ventana **Scene**, ajusta los bordes para que cubran el cuerpo del personaje:
   * **Size:** `X: 0.6`, `Y: 1.6`.
   * **Offset:** `X: 0`, `Y: 0.8`.

---

#### 4. Crear el Hijo Visual (`Visuals`)
1. Haz clic derecho sobre `Fighter_Ryu` en la Hierarchy y selecciona **Create Empty**.
2. Cámbiale el nombre a: **`Visuals`**.
3. Asegúrate de que su **Position** en el Transform esté en `(0, 0, 0)`.
4. Añade el componente **Sprite Renderer**:
   * Clic en **Add Component** ➔ **`Sprite Renderer`**.
   * **¡MUY IMPORTANTE (El Sprite de Referencia)!**: En el campo **Sprite**, arrastra la primera imagen de reposo:
     `Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu/01_Movement/idle_stance/0.png`.
     *(¿Por qué? Esto hace que Ryu aparezca inmediatamente visible en la ventana Scene. Así tendrás su silueta como "maniquí" para ajustar los colisionadores de daño en el siguiente paso).*
   * En **Sorting Layer**, selecciona **`Fighters`**.
   * En **Order in Layer**, pon **`10`**.
5. Añade el componente **Animator**:
   * Clic en **Add Component** ➔ **`Animator`**.
   * En el campo **Controller**, arrastra el `Ryu_AnimatorController` que creaste en la Guía 02.

> [!IMPORTANT]
> **¿Por qué el SpriteRenderer va en un hijo llamado `Visuals`?**
> Para hacer que Ryu mire a la izquierda, tu código solo cambiará:
> `Visuals.transform.localScale = new Vector3(-1, 1, 1);`
> Al voltear solo el hijo visual, el Root principal mantiene sus coordenadas limpias, lo cual es **vital para no distorsionar las posiciones de los sensores Kinect**.

---

#### 5. Crear las Hurtboxes y Hitboxes

Ahora que Ryu es visible en la escena, ajustaremos sus cajas de combate:

1. **Crear la Hurtbox (`Hurtbox_Root` - Donde Ryu RECIBE daño):**
   * Haz clic derecho sobre `Fighter_Ryu` ➔ **Create Empty**. Llámalo **`Hurtbox_Root`**.
   * En el Inspector, cambia su **Layer** a: **`Hurtbox`** (creada en la Guía 05).
   * Clic en **Add Component** ➔ **Box Collider 2D**:
     * Marca la casilla **`Is Trigger` [X]** (True).
     * **Valores de referencia para Ryu:**
       * **Offset:** `X: 0`, `Y: 0.85`
       * **Size:** `X: 0.7`, `Y: 1.65`
     * *(Opcional): Haz clic en el botón **Edit Collider** (cuadrado verde con 4 puntos) para ajustar manualmente los bordes verdes alrededor de la cabeza, torso y piernas de Ryu en la ventana Scene.*
   * Clic en **Add Component** ➔ busca el script **`FighterHurtbox`** (incluido en `Assets/.../Scripts/Combat/FighterCombatColliders.cs`):
     * En el campo **Owner**, arrastra el GameObject raíz **`Fighter_Ryu`**. *(Esto evita que Ryu se golpee a sí mismo).*

2. **Crear la Hitbox (`Hitbox_Root` - Donde Ryu HACE daño al atacar):**
   * Haz clic derecho sobre `Fighter_Ryu` ➔ **Create Empty**. Llámalo **`Hitbox_Root`**.
   * En el Inspector, cambia su **Layer** a: **`Hitbox`**.
   * Clic en **Add Component** ➔ **Box Collider 2D**:
     * Marca la casilla **`Is Trigger` [X]** (True).
     * **Valores de referencia para un puñetazo:**
       * **Offset:** `X: 0.65`, `Y: 1.1` (justo al frente del pecho/hombro de Ryu).
       * **Size:** `X: 0.5`, `Y: 0.4`
   * Clic en **Add Component** ➔ busca el script **`FighterHitbox`**:
     * **Damage:** `10`.
     * **Hit Stun Duration:** `0.2`.
   * **¡CRÍTICO! Desactiva este GameObject por defecto:**
     * En la parte superior izquierda del Inspector de `Hitbox_Root`, **desmarca la casilla de verificación junto al nombre** para apagarlo.
     * La Hitbox **solo** debe encenderse durante los fotogramas del golpe mediante los Animation Events que aprenderás en la Guía 05.
