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
   * En **Sorting Layer**, selecciona **`Fighters`**.
   * En **Order in Layer**, pon **`10`**.
5. Añade el componente **Animator**:
   * Clic en **Add Component** ➔ **`Animator`**.
   * En el campo **Controller**, arrastra el `Ryu_Animator` que creaste en la Guía 02.

> [!IMPORTANT]
> **¿Por qué el SpriteRenderer va en un hijo llamado `Visuals`?**
> Para hacer que Ryu mire a la izquierda, tu código solo cambiará:
> `Visuals.transform.localScale = new Vector3(-1, 1, 1);`
> Al voltear solo el hijo visual, el Root principal mantiene sus coordenadas limpias, lo cual es **vital para no distorsionar las posiciones de los sensores Kinect**.

---

#### 5. Crear las Hurtboxes y Hitboxes
1. Haz clic derecho sobre `Fighter_Ryu` ➔ **Create Empty**. Llámalo **`Hurtbox_Root`**.
   * Añade un **Box Collider 2D**.
   * Marca la casilla **`Is Trigger` [X]** (True).
   * Ajusta el tamaño para que cubra la cabeza, torso y piernas de Ryu.
   * Añade el script incluido: `Assets/.../Scripts/Combat/FighterHurtbox.cs`.

2. Haz clic derecho sobre `Fighter_Ryu` ➔ **Create Empty**. Llámalo **`Hitbox_Root`**.
   * Añade un **Box Collider 2D**.
   * Marca la casilla **`Is Trigger` [X]** (True).
   * Por defecto, **desactiva** este GameObject (desmarcando la casilla de verificación junto a su nombre en la parte superior izquierda del Inspector). Solo se activará mediante eventos de animación cuando Ryu lance un puño o patada.
   * Añade el script incluido: `Assets/.../Scripts/Combat/FighterHitbox.cs`.
