# 📌 Tarea #4 [SP1-SEBAS]: Montaje del Escenario Japón (Suzaku Castle) con Parallax
## Sprint 1 (Sep 7 – Sep 20) | Asignado a: @Sebas

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

```bash
git checkout main
git pull origin main
git checkout -b feature/sp1-sebas-japan-stage
```

---

### 🎯 2. Explicación Técnica de la Tarea

Debes montar el escenario de **Japón (Suzaku Castle)** con efecto de profundidad Parallax 2.5D:
1. **Sorting Layers:** En Unity (*Tags & Layers > Sorting Layers*), crea estas capas en orden de atrás hacia adelante:
   - `Background_Sky`
   - `Background_Distant`
   - `Midground_Temple`
   - `Floor_Ground`
   - `Fighters` (para los personajes)
   - `Foreground_Props`
2. **Sprites del Escenario:** Ubicados en `Assets/StreetFighter3_ThirdStrike/Stages/01_Japan_Suzaku_Castle/` (o la carpeta de fondos del proyecto). Configurar con `Pixels Per Unit: 100`, `Filter Mode: Point (no filter)` y `Compression: None`.
3. **Efecto Parallax:** Colocar el script [`ParallaxBackground.cs`](file:///c:/Users/marco/2026%20B/Desarrollo%20de%20Juegos/StreetFighter3_ThirdStrike/Assets/StreetFighter3_ThirdStrike/Scripts/Environment/ParallaxBackground.cs) en cada capa del fondo asignando la cámara principal y un `parallaxFactor` diferente (ej. Cielo: 0.1, Castillo: 0.4, Suelo: 1.0).
4. **Límites de Suelo:** Crear un `BoxCollider2D` estático en el suelo para que los luchadores tengan piso firme ($Y=0$).

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a configurarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de diseño de niveles 2D en Unity. Por favor lee `Devs/Sebas/Sprint_1/TASK_SP1_04_JAPAN_STAGE_PARALLAX.md` y explícame paso a paso cómo debo configurar las Sorting Layers en Unity, cómo colocar los sprites del escenario de Suzaku Castle, cómo configurar los factores de desplazamiento en `ParallaxBackground.cs` para lograr el efecto de profundidad 2.5D, y cómo guardar el escenario como un Prefab reutilizable con colisión de suelo."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Las Sorting Layers están configuradas y ningún fondo tapa a los luchadores.
- [ ] Al mover la cámara en horizontal, las capas lejanas se mueven más lento que las cercanas (efecto Parallax).
- [ ] El suelo tiene colisionador a $Y=0$.
- [ ] Escenario guardado como Prefab reutilizable (`Stage_Japan.prefab`).

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

```bash
git add .
git commit -m "feat: montar escenario de Japon con Parallax 2.5D (#4)"
git push -u origin feature/sp1-sebas-japan-stage
```
Abre el Pull Request en GitHub con la descripción: `Closes #4`.
