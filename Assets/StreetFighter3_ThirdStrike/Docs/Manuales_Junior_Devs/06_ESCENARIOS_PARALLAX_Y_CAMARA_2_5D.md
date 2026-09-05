# 🏯 Guía 06: Escenarios Parallax y Cámara 2.5D
## Montaje de Fondos con Profundidad Arcade en Unity

En Street Fighter III, los escenarios no son una imagen plana: tienen un efecto de profundidad llamado **Parallax Scrolling**, donde las nubes lejanas se mueven muy despacio, los edificios se mueven a velocidad media, y el suelo se mueve a la misma velocidad de los luchadores.

En esta guía aprenderás cómo organizar las capas en **Sorting Layers**, cómo configurar la cámara ortográfica y cómo usar el script `ParallaxBackground.cs` incluido en el proyecto.

---

### 📍 Paso 1: Configurar las Sorting Layers (Orden Visual)
Para garantizar que el cielo quede al fondo, el suelo en medio y los luchadores al frente:
1. En la barra superior de Unity, ve a: **Edit** ➔ **Project Settings**.
2. Haz clic en **Tags and Layers** (a la izquierda).
3. Despliega la lista **Sorting Layers**.
4. Haz clic en el botón **`+`** para agregar las capas en este **orden exacto** (las capas de arriba se dibujan al fondo, las de abajo se dibujan encima):

```text
1. Default
2. Stage_Sky            <-- Cielo y nubes lejanas
3. Stage_Distant        <-- Edificios, montañas o barcos al fondo
4. Stage_Mid            <-- Templo, puentes, barandas
5. Stage_Floor          <-- El suelo donde pisan los luchadores
6. Fighters             <-- Ryu, Ken, Chun-Li, etc.
7. Hit_Effects          <-- Chispas de golpe, proyectiles Hadouken
8. Foreground_Props     <-- Lámparas o elementos en primerísimo plano
```

---

### 📍 Paso 2: Montar las Capas en la Escena
Usemos como ejemplo el escenario de Japón de Ryu (`Assets/.../Stages/Japan_Ryu/`):

1. En la ventana **Hierarchy**, haz clic derecho ➔ **Create Empty**.
2. Nómbralo: **`Stage_Japan_Ryu`**.
3. Dentro de `Stage_Japan_Ryu`, crea 4 GameObjects hijos vacíos:
   * `01_Sky`
   * `02_Distant`
   * `03_Midground`
   * `04_Floor`

4. Selecciona cada hijo, añádele un componente **Sprite Renderer** (`Add Component > Sprite Renderer`), y asígnale su sprite y su Sorting Layer correspondiente:

| GameObject Hijo | Sprite a Asignar | Sorting Layer | Order in Layer |
| :--- | :--- | :--- | :--- |
| `01_Sky` | `Stage_Sky.png` | **`Stage_Sky`** | 0 |
| `02_Distant` | `Stage_Distant.png` | **`Stage_Distant`** | 0 |
| `03_Midground` | `Stage_Mid.png` | **`Stage_Mid`** | 0 |
| `04_Floor` | `Stage_Floor.png` | **`Stage_Floor`** | 0 |

---

### 📍 Paso 3: Configurar el Suelo Físico (Ground Collider)
Para que los personajes no caigan al vacío por la gravedad del Rigidbody2D:
1. Selecciona el GameObject `04_Floor`.
2. Haz clic en **Add Component** ➔ **Box Collider 2D**.
3. Deja la casilla **Is Trigger** **DESMARCADA**.
4. Haz clic en **Edit Collider** y ajusta la caja verde para que coincida exactamente con la superficie horizontal donde deben pisar los pies de los luchadores.

---

### 📍 Paso 4: Aplicar el Script de Parallax
Hemos incluido el script listo `Assets/StreetFighter3_ThirdStrike/Scripts/Environment/ParallaxBackground.cs`:

1. En la Hierarchy, selecciona el GameObject padre **`Stage_Japan_Ryu`**.
2. Haz clic en **Add Component** y escribe: **`Parallax Background`**.
3. En el Inspector verás los campos del script:
   * **Main Camera:** Arrastra tu `Main Camera` desde la Hierarchy.
   * **Parallax Layers:** En la lista de capas, asigna los multiplicadores:
     * Capa 1 (`01_Sky`): **Parallax Factor X = `0.1`** (se mueve casi nada).
     * Capa 2 (`02_Distant`): **Parallax Factor X = `0.3`**.
     * Capa 3 (`03_Midground`): **Parallax Factor X = `0.6`**.
     * Capa 4 (`04_Floor`): **Parallax Factor X = `1.0`** (se mueve exactamente a la velocidad de la cámara).

---

### 📍 Paso 5: Configurar la Cámara Arcade
1. Selecciona la **Main Camera** en la Hierarchy.
2. En el componente **Camera** en el Inspector:
   * **Projection:** Cámbialo a **`Orthographic`**.
   * **Size:** Escribe **`3.8`** a **`4.2`** (esto da el encuadre vertical perfecto del arcade CPS-3).
   * **Near:** `0.3`.
   * **Far:** `1000`.
