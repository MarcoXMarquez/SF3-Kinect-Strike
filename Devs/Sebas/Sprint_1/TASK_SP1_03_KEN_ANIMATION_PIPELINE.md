# 📌 Tarea #3 [SP1-SEBAS]: Pipeline de Sprites y Animaciones de Ken (01_Ken)
## Sprint 1 (Sep 7 – Sep 20) | Asignado a: @Sebas

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea tu rama
git checkout -b feature/sp1-sebas-ken-anim
```

---

### 🎯 2. Explicación Técnica de la Tarea

Debes estructurar y generar todas las animaciones de **Ken Masters** (`01_Ken`):
1. **Organización en 7 Categorías:** Verificar que la carpeta `Assets/StreetFighter3_ThirdStrike/Characters/01_Ken/` contenga las subcarpetas estandarizadas (`01_Movement/`, `02_Normals/`, `03_Specials_Supers/`, `04_Defense_Hit/`, `05_Throws/`, `06_Intros_Victories/`, `07_Secondary_Extras/`) con nombres en inglés descriptivos (`idle_stance`, `walk_forward`, `light_punch`, `shoryuken`, etc.).
2. **Generación de Clips a 14 FPS:**
   - Selecciona la carpeta `01_Ken` en la pestaña **Project** de Unity.
   - En la barra superior de Unity, haz clic en:  
     `SF3 Tools > Auto-Generate Animation Clips from Selected Folder`.
3. **Creación del Animator Controller:**
   - En `01_Ken/`, crea `Ken_Animator.controller` (clic derecho > *Create > Animator Controller*).
   - Haz clic en `SF3 Tools > Auto-Populate Animator Controller from Selected Folder`.
4. **Prefab de Ken:**
   - Crear el prefab `Fighter_Ken.prefab` en `Assets/StreetFighter3_ThirdStrike/Prefabs/` y asignarle el `Ken_Animator`.
5. **Escena Sandbox:** Probarlo en `Assets/StreetFighter3_ThirdStrike/Scenes/Sandbox_Sebas.unity`.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a configurarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de desarrollo en Unity. Por favor lee el archivo `Devs/Sebas/Sprint_1/TASK_SP1_03_KEN_ANIMATION_PIPELINE.md` y explícame paso a paso cómo debo organizar las carpetas de `01_Ken`, cómo utilizar la herramienta de `SF3 Tools` para generar los clips a 14 FPS y poblar el Animator, y cómo montar el Prefab de Ken en mi escena `Sandbox_Sebas.unity`. Guíame en cada paso para que yo mismo haga la configuración y entienda el proceso."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] La carpeta `01_Ken/` tiene sus subcarpetas con nombres descriptivos.
- [ ] Se generaron los AnimationClips a 14 FPS con `Loop Time` activado en Idle y Walk.
- [ ] `Ken_Animator.controller` contiene todos los estados conectados sin errores.
- [ ] El prefab `Fighter_Ken.prefab` se reproduce en `Sandbox_Sebas.unity`.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

```bash
git add .
git commit -m "feat: estructurar y generar animaciones completas de Ken (#3)"
git push -u origin feature/sp1-sebas-ken-anim
```
Abre el Pull Request en GitHub con la descripción: `Closes #3`.
