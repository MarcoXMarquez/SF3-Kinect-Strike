# 🥋 Street Fighter III: 3rd Strike - Manual del Desarrollador Junior
## Proyecto Arcade Interactivo con Control por Movimiento (Kinect)

¡Bienvenido al equipo de desarrollo! Este conjunto de manuales ha sido diseñado específicamente para que cualquier programador del equipo (incluso si nunca antes has abierto Unity o creado una animación) pueda **configurar, montar y dejar el juego 100% listo visual y mecánicamente**.

---

### 🎯 La Visión del Proyecto
Estamos construyendo una versión de **Street Fighter III: 3rd Strike en Unity** que será jugada **con el cuerpo humano mediante un sensor Kinect**, en lugar de usar un mando tradicional.
* Cuando el jugador lance un puñetazo al aire frente a la cámara $\rightarrow$ El personaje en pantalla debe ejecutar el golpe de inmediato.
* Cuando el jugador haga el gesto de dos manos al frente $\rightarrow$ Se disparará un **Hadouken**.
* Cuando alce el puño al cielo $\rightarrow$ Saldrá un **Shoryuken**.

Para que la fase de programación del Kinect sea fluida y divertida, **primero debemos dejar la base de Unity impecable**: sprites nítidos, animaciones a la velocidad correcta, colisionadores de impacto listos, escenarios con profundidad y sonidos coordinados.

---

### 📚 Índice de Guías Paso a Paso

Cada archivo en esta carpeta está enfocado en **una sola tarea específica** con instrucciones de "haz clic aquí, presiona este botón y cambia este valor":

1. **[01_CONFIGURACION_DE_SPRITES_PIXEL_PERFECT.md](./01_CONFIGURACION_DE_SPRITES_PIXEL_PERFECT.md)**
   * Cómo importar los sprites sin que se vean borrosos.
   * Dónde está cada opción en el Inspector (Point Filter, Compresión None, Pivote en los pies).
   * Evitar que el personaje se hunda en el suelo al agacharse.

2. **[02_CREACION_DE_ANIMACIONES_PASO_A_PASO.md](./02_CREACION_DE_ANIMACIONES_PASO_A_PASO.md)**
   * Dónde abrir la ventana Animation (`Ctrl + 6`).
   * Cómo usar el script automático de 1 clic para generar todas las animaciones.
   * Cómo crear animaciones manualmente arrastrando frames.
   * Ajuste de la tasa arcade a **14 FPS** y activación de repetición (`Loop`).

3. **[03_JERARQUIA_Y_ARQUITECTURA_DEL_LUCHADOR.md](./03_JERARQUIA_Y_ARQUITECTURA_DEL_LUCHADOR.md)**
   * Estructura de GameObjects para un personaje de peleas.
   * Creación del Root, componente `Rigidbody2D` y la `Pushbox` (caja física de empuje).
   * Separación del renderizador visual (`Visuals`) para voltear el personaje sin romper las coordenadas de Kinect.

4. **[04_ANIMATOR_CONTROLLER_Y_MAQUINA_DE_ESTADOS.md](./04_ANIMATOR_CONTROLLER_Y_MAQUINA_DE_ESTADOS.md)**
   * Creación del Animator Controller y conexión de estados (Idle, Walk, Attack, Hit, KO).
   * La regla de oro de los juegos de pelea: **Desmarcar `Has Exit Time`** y poner **`Transition Duration = 0`**.
   * Cómo hacer que el personaje responda al instante en el mismo fotograma.

5. **[05_HITBOXES_HURTBOXES_Y_EVENTOS_DE_ANIMACION.md](./05_HITBOXES_HURTBOXES_Y_EVENTOS_DE_ANIMACION.md)**
   * Diferencia entre Pushbox, Hurtbox (recibir daño) y Hitbox (hacer daño).
   * Configuración de capas (Layers) y matriz de colisiones de Unity Physics 2D.
   * Cómo agregar `Animation Events` en los frames exactos para activar el golpe y el sonido.

6. **[06_ESCENARIOS_PARALLAX_Y_CAMARA_2_5D.md](./06_ESCENARIOS_PARALLAX_Y_CAMARA_2_5D.md)**
   * Montaje de escenarios por capas (Cielo, Fondo, Templo, Suelo).
   * Configuración de Sorting Layers para evitar que el escenario tape a los luchadores.
   * Uso del script `ParallaxBackground.cs` para dar profundidad con la cámara ortográfica.

7. **[07_EFECTOS_VISUALES_Y_PREFABS.md](./07_EFECTOS_VISUALES_Y_PREFABS.md)**
   * Creación de Prefabs para el destello azul de Parry, chispas de golpe y el Hadouken.
   * Script de auto-destrucción al terminar la animación para no saturar la memoria.

8. **[08_AUDIO_VOCES_Y_SOUND_MANAGER.md](./08_AUDIO_VOCES_Y_SOUND_MANAGER.md)**
   * Dónde están las voces verificadas por IA y los efectos de sonido.
   * Uso del Singleton `SF3SoundManager` para reproducir música, golpes y frases de victoria con una sola línea de C#.

9. **[09_ARQUITECTURA_DE_ENTRADA_Y_PREPARACION_KINECT.md](./09_ARQUITECTURA_DE_ENTRADA_Y_PREPARACION_KINECT.md)**
   * **El puente hacia el Kinect:** La interfaz `IFighterInput`.
   * Cómo programar el control para que acepte tanto teclado (para pruebas en laptop) como Kinect (para la demostración final).
   * Mapeo conceptual de posturas corporales a ataques de Street Fighter.

10. **[10_CHECKLIST_DE_VERIFICACION_FINAL.md](./10_CHECKLIST_DE_VERIFICACION_FINAL.md)**
    * Lista interactiva con casillas de verificación para auditar tu trabajo antes de pasar a la programación de Kinect.

11. **[RECOMENDACION_PACKAGES_Y_HERRAMIENTAS_UNITY.md](../RECOMENDACION_PACKAGES_Y_HERRAMIENTAS_UNITY.md)** *(Nuevo)*
    * Guía técnica de paquetes esenciales de Unity, herramientas recomendadas (Input System, Cinemachine, URP 2D, Animancer, Frame Data), shaders de Super Flash y depuración para agilizar el desarrollo.

---

### 💡 Reglas de Oro del Proyecto
1. **Nunca escales los sprites en el Transform:** Siempre usa `Pixels Per Unit: 100` y mantén el scale en `(1, 1, 1)`.
2. **Siempre pivote abajo (`Bottom` / `BottomCenter`):** Los pies del luchador son el ancla al suelo. El lienzo original unificado de CPS-3 conserva los saltos y trayectorias reales sin necesidad de offsets manuales.
3. **Animaciones a 14 FPS:** No uses los 60 FPS por defecto de Unity; Street Fighter III fue dibujado artesanalmente a 14 fotogramas por segundo.
4. **Cero tiempo de transición en ataques (`Transition Duration = 0`):** En un juego de peleas, los ataques deben salir en el fotograma 1.
5. **Estructura en 7 Categorías:** Mantén la organización limpia (`01_Movement` a `07_Secondary_Extras`) con nombres completos y descriptivos.
