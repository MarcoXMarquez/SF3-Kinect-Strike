# 🎨 Guía 01: Configuración de Sprites Pixel-Perfect
## Cómo importar y configurar texturas 2D en Unity sin perder calidad

En los juegos de pelea clásicos de Capcom en 2D, el arte está hecho píxel a píxel (*pixel art*). Si importas las imágenes a Unity con la configuración por defecto, Unity intentará "suavizarlas" con un filtro borroso y comprimirlas, haciendo que se vean borrosas y con colores alterados.

En esta guía aprenderás **exactamente dónde hacer clic en Unity** para que los sprites se vean 100% nítidos, con sus colores arcade auténticos y con el pivote correcto.

---

### 📍 Paso 1: Localizar los Sprites en la ventana Project
1. Abre tu proyecto en Unity.
2. Mira la parte inferior de la pantalla: ahí se encuentra la ventana **Project** (el explorador de archivos de Unity).
3. Navega por las carpetas hasta encontrar un personaje:
   `Assets` ➔ `StreetFighter3_ThirdStrike` ➔ `Characters` ➔ `02_Ryu` ➔ `01_Movement` ➔ `idle_stance` (o cualquier otra carpeta de acción dentro de las 7 categorías).
4. Verás una lista de archivos PNG numerados (`0.png`, `1.png`, `2.png`...).

---

### 📍 Paso 2: Seleccionar todas las imágenes a la vez
Para no repetir esto imagen por imagen:
1. Haz un solo clic sobre la primera imagen (`0.png`).
2. Mantén presionada la tecla **Shift** en tu teclado.
3. Haz un solo clic sobre la última imagen de la carpeta.
4. **¡Listo!** Ahora todas las imágenes estarán seleccionadas y resaltadas en azul.

---

### 📍 Paso 3: Configurar el Inspector (Panel Derecho)
Mira ahora hacia el lado derecho de la pantalla, en la ventana **Inspector**. Modifica los siguientes campos exactamente como se indica:

#### 1. Texture Type
* Haz clic en el desplegable junto a **Texture Type**.
* Selecciona: **`Sprite (2D and UI)`**.

#### 2. Sprite Mode
* Asegúrate de que esté seleccionado: **`Single`**.

#### 3. Pixels Per Unit (PPU)
* Busca la casilla de texto **Pixels Per Unit**.
* Borra lo que haya y escribe: **`100`**.
*(Nota: Esto define que 100 píxeles de la imagen equivalen a 1 metro en el mundo de físicas de Unity).*

#### 4. Advanced (Opciones Avanzadas)
* Haz clic en la pequeña flechita junto a la palabra **Advanced** para desplegar sus opciones.
* Busca la casilla **Generate Mip Maps**.
* **DESMÁRCALA** (debe quedar en blanco, sin palomita). 
*(¿Por qué? Si está marcado, Unity creará versiones reducidas y borrosas cuando la cámara se aleje ligeramente).*

#### 5. Filter Mode (¡EL MÁS IMPORTANTE!)
* Busca el desplegable **Filter Mode** (por defecto suele decir *Bilinear*).
* Haz clic y cámbialo a: **`Point (no filter)`**.
*(¿Por qué? Esto desactiva el desenfoque artificial y mantiene cada píxel nítido y cuadrado como en la máquina arcade).*

#### 6. Compression (Compresión de Color)
* En la parte inferior del Inspector, busca el desplegable **Compression** (suele decir *Normal Quality* o *Low Quality*).
* Haz clic y cámbialo a: **`None`** (sin compresión).
*(¿Por qué? La compresión crea manchas de color en el pixel art y arruina la paleta CPS-3).*

#### 7. Pivot (Punto de Anclaje del Personaje)
* Busca el desplegable llamado **Pivot** (suele decir *Center*).
* Haz clic y cámbialo a: **`Bottom`** (Abajo).
*(¿Por qué? En un juego de peleas, si el pivote está en el centro del sprite, cuando el personaje pase de estar de pie a agacharse, como el sprite agachado es más bajo, el centro cambiará y el personaje flotará en el aire. Al poner el pivote en `Bottom`, los pies siempre tocan el suelo exactamente en la misma coordenada Y).*

---

### 📍 Paso 4: Guardar los Cambios (Botón Apply)
1. Ve a la esquina inferior derecha del panel **Inspector**.
2. Verás dos botones: **Revert** y **Apply**.
3. Haz clic en el botón azul **Apply**.
4. Verás una barra de progreso breve mientras Unity procesa las imágenes.

---

### ⚡ Atajo Automatizado del Proyecto
En este paquete hemos incluido el script `Assets/StreetFighter3_ThirdStrike/Scripts/Editor/SF3AutoSpriteImporter.cs`.
* Cuando arrastras una carpeta completa dentro de `StreetFighter3_ThirdStrike`, este script aplica automáticamente todos los ajustes descritos arriba (`Point`, `None`, `Bottom`, `PPU 100`).
* **Usa esta guía manual** siempre que agregues sprites nuevos por fuera o si necesitas verificar que un sprite conserve sus ajustes correctos.

---

### ❓ Preguntas Frecuentes y Solución de Problemas

* **¿Por qué mi sprite se ve borroso en la escena?**
  Revisa el **Filter Mode**. Casi siempre se debe a que quedó en `Bilinear`. Cámbialo a `Point (no filter)` y haz clic en `Apply`.

* **¿Por qué mi personaje se hunde en el suelo cuando se agacha?**
  El **Pivot** quedó configurado en `Center`. Cámbialo a `Bottom` en todas las imágenes de la animación de agacharse.

* **¿Por qué los colores se ven descoloridos o con artefactos?**
  La **Compression** está activada. Ponla en `None`.

* **¿Por qué varias imágenes tienen un gran espacio transparente vacío arriba o abajo?**
  Esto es intencional y necesario. En los sprites arcade originales de CPS-3, todos los fotogramas comparten un lienzo con la misma línea de suelo (*Floor Baseline*). Por ejemplo, en un salto o Shoryuken, el fotograma en el suelo tiene espacio arriba, y cuando sube al aire, el personaje ocupa la parte alta dejando espacio abajo. Al mantener este lienzo y fijar el **Pivot** en `Bottom`, Unity calcula las alturas y parábolas reales de salto sin necesidad de ajustar offsets manuales frame a frame.
