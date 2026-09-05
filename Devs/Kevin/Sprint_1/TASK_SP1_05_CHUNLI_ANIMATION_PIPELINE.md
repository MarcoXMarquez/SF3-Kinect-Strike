# 📌 Tarea #5 [SP1-KEVIN]: Pipeline de Sprites y Animaciones de Chun-Li (03_ChunLi)
## Sprint 1 (Sep 7 – Sep 20) | Asignado a: @Kevin

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

```bash
git checkout main
git pull origin main
git checkout -b feature/sp1-kevin-chunli-anim
```

---

### 🎯 2. Explicación Técnica de la Tarea

Debes estructurar y generar todas las animaciones de **Chun-Li** (`03_ChunLi`):
1. **Organización en 7 Categorías:** Verificar que la carpeta `Assets/StreetFighter3_ThirdStrike/Characters/03_ChunLi/` contenga las subcarpetas estandarizadas (`01_Movement/`, `02_Normals/`, `03_Specials_Supers/`, `04_Defense_Hit/`, `05_Throws/`, `06_Intros_Victories/`, `07_Secondary_Extras/`) con nombres descriptivos en inglés (`idle_stance`, `walk_forward`, `light_kick`, `hyakuretsukyaku`, `kikoken`, etc.).
2. **Generación de Clips a 14 FPS:**
   - Selecciona la carpeta `03_ChunLi` en la pestaña **Project** de Unity.
   - En la barra superior de Unity, haz clic en:  
     `SF3 Tools > Auto-Generate Animation Clips from Selected Folder`.
3. **Creación del Animator Controller:**
   - En `03_ChunLi/`, crea `ChunLi_Animator.controller`.
   - Haz clic en `SF3 Tools > Auto-Populate Animator Controller from Selected Folder`.
4. **Prefab de Chun-Li:**
   - Crear el prefab `Fighter_ChunLi.prefab` en `Assets/StreetFighter3_ThirdStrike/Prefabs/` y asignarle el `ChunLi_Animator`.
5. **Escena Sandbox:** Probarlo en `Assets/StreetFighter3_ThirdStrike/Scenes/Sandbox_Kevin.unity`.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a configurarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de animación y sprites en Unity. Por favor lee `Devs/Kevin/Sprint_1/TASK_SP1_05_CHUNLI_ANIMATION_PIPELINE.md` y explícame paso a paso cómo debo organizar las carpetas de `03_ChunLi`, cómo utilizar la herramienta `SF3 Tools` para generar los clips a 14 FPS y poblar el Animator, y cómo montar el Prefab de Chun-Li en mi escena `Sandbox_Kevin.unity`. Guíame para que yo mismo entienda y realice cada paso de la configuración."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] La carpeta `03_ChunLi/` tiene sus subcarpetas con nombres descriptivos.
- [ ] Se generaron los AnimationClips a 14 FPS con `Loop Time` activado en Idle y Walk.
- [ ] `ChunLi_Animator.controller` contiene todos los estados conectados sin errores.
- [ ] El prefab `Fighter_ChunLi.prefab` se reproduce en `Sandbox_Kevin.unity`.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

```bash
git add .
git commit -m "feat: estructurar y generar animaciones completas de Chun-Li (#5)"
git push -u origin feature/sp1-kevin-chunli-anim
```
Abre el Pull Request en GitHub con la descripción: `Closes #5`.
