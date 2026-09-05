# ✅ Guía 10: Checklist de Verificación Final
## Lista de Control de Calidad antes de pasar al Motor de Kinect

Antes de dar por concluida la fase de preparación de assets e iniciar la programación del motor de detección de movimiento con Kinect, cada desarrollador del equipo debe verificar esta lista en su escena de Unity:

---

### 🎨 1. Sprites y Calidad Visual
- [ ] Todos los sprites tienen **Filter Mode** configurado en `Point (no filter)`.
- [ ] Todos los sprites tienen **Compression** en `None`.
- [ ] Todos los sprites tienen **Generate Mip Maps** desmarcado.
- [ ] Todos los sprites tienen **Pivot** en `Bottom` (o en la base de los pies).
- [ ] No se observan bordes borrosos ni manchas de compresión en la vista Game.

---

### 🎬 2. Animaciones y Animator
- [ ] Todas las animaciones corren a **14 FPS** (Sample Rate = 14).
- [ ] Las animaciones de reposo (`idle_stance`) y caminata (`walk_forward`, `walk_backward`, etc.) tienen marcada la casilla **Loop Time**.
- [ ] Las animaciones de ataque NO tienen marcado Loop Time.
- [ ] En el Animator Controller, **todas las transiciones de ataque tienen `Has Exit Time` desmarcado**.
- [ ] En todas las transiciones de ataque, el campo **`Transition Duration (s)` está en `0`**.
- [ ] Al presionar el botón de ataque, el golpe se dispara en el mismo fotograma sin retraso.

---

### 💥 3. Jerarquía y Colisiones
- [ ] El personaje tiene la estructura de 4 niveles: `Root`, `Visuals`, `Pushbox`, `Hurtbox_Root` y `Hitbox_Root`.
- [ ] El Rigidbody2D tiene activado **Freeze Rotation Z**.
- [ ] La Pushbox (`BoxCollider2D`) tiene `Is Trigger = False` e impide que los personajes se traspasen.
- [ ] La Hurtbox tiene `Is Trigger = True` y está en la capa `Hurtbox`.
- [ ] La Hitbox tiene `Is Trigger = True` y está en la capa `Hitbox`.
- [ ] En **Physics 2D**, la matriz de colisiones está configurada para que `Hitbox` solo colisione con `Hurtbox`.
- [ ] Se han colocado **Animation Events** para encender la Hitbox en el impacto y apagarla al terminar.

---

### 🏯 4. Escenario y Parallax
- [ ] Se han configurado las **Sorting Layers** en el orden correcto (`Stage_Sky`, `Stage_Distant`, `Stage_Mid`, `Stage_Floor`, `Fighters`, `Hit_Effects`).
- [ ] El suelo físico tiene un colisionador que detiene a los personajes.
- [ ] El script `ParallaxBackground.cs` está vinculado a la cámara principal.
- [ ] Al mover la cámara, el fondo muestra sensación de profundidad 2.5D fluida.
- [ ] La cámara es **Ortográfica** con un tamaño aproximado de `3.8` a `4.2`.

---

### 🔊 5. Audio y Efectos
- [ ] El GameObject `SoundManager` está en la escena con `SF3SoundManager.cs`.
- [ ] La música BGM se reproduce en bucle continuo sin cortes.
- [ ] Los efectos de sonido de golpes se disparan en el frame de impacto.
- [ ] Las voces de movimientos especiales coinciden auditivamente con lo que dice el personaje (Hadouken, Shoryuken, etc.).

---

### 🕺 6. Preparación para Kinect
- [ ] El script `FighterController` utiliza la interfaz `IFighterInput`.
- [ ] El juego se puede jugar y probar completamente con el teclado mediante `KeyboardFighterInput`.
- [ ] Ningún script de animación o combate contiene llamadas directas a `Input.GetKeyDown()`.
- [ ] El proyecto está 100% limpio y listo para recibir el adaptador de Kinect.
