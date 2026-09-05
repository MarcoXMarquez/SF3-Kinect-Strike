# 🧠 Contexto de Arquitectura y Convenciones Técnicas del Proyecto
## Street Fighter III: 3rd Strike (Unity + Azure Kinect + IA Adaptativa)

Este documento proporciona a los asistentes de IA (Antigravity) y desarrolladores el contexto técnico completo de la arquitectura del juego.

---

### 1. Principios Técnicos Fundamentales

1. **Pixel-Perfect a 100 PPU:**
   * Todos los sprites usan `Pixels Per Unit: 100`, `Filter Mode: Point (no filter)` y `Compression: None`.
   * La escala de los Transforms en escena siempre debe ser `(1, 1, 1)`.
2. **Tasa de Cuadros Arcade CPS-3 (14 FPS):**
   * Todas las animaciones fueron dibujadas a 14 fotogramas por segundo. Los `AnimationClip` deben tener `frameRate = 14`.
3. **Lienzo Unificado y Pivote Inferior (`BottomCenter`):**
   * Los pies del personaje representan la línea de suelo ($Y = 0$).
   * Los sprites de salto conservan el espacio transparente original debajo para mantener la trayectoria exacta dibujada por Capcom.
4. **Prohibida la "Telaraña de Flechas" en Mecanim:**
   * En lugar de dibujar cientos de flechas en el `Animator`, el juego utiliza la arquitectura desacoplada:  
     `animator.Play(clipName, 0, 0f)`.
   * Cero tiempo de transición en ataques: los golpes deben salir en el frame 1 exacto.
5. **Separación Visual vs Lógica:**
   * El GameObject raíz (`Fighter_Ryu`) controla la posición física en el mundo ($X, Y$), la `Pushbox` y el `Rigidbody2D`.
   * El GameObject hijo `Visuals` contiene el `SpriteRenderer` y el `Animator`. Esto permite voltear visualmente al personaje (`flipX`) sin desfasar las coordenadas 3D del sensor Kinect.

---

### 2. Estructura de Carpetas de Scripts (`Assets/.../Scripts/`)

* **`Core/`**: `FighterStateMachine.cs`, `FighterPhysics.cs`, `GameManager.cs`.
* **`Combat/`**: `FighterHurtbox.cs`, `FighterHitbox.cs`, `FighterCombatColliders.cs`, `SF3AutoHurtboxFitter.cs`.
* **`Input/`**: `IFighterInput.cs`, `KeyboardFighterInput.cs`, `AzureKinectInput.cs`.
* **`AI/`**: `FighterAgent.cs`, `AdaptiveAIManager.cs`, `MatchTelemetryLogger.cs`.
* **`Audio/`**: `SF3SoundManager.cs`.
* **`Environment/`**: `ParallaxBackground.cs`.
* **`UI/`**: `FighterHUD.cs`, `CharacterSelectMenu.cs`.
* **`Database/`**: `DatabaseManager.cs`.
* **`Testing/`**: `FighterAnimationTester.cs`.
* **`Editor/`**: `SF3AnimationBatchCreator.cs`, `SF3AutoSpriteImporter.cs`.
