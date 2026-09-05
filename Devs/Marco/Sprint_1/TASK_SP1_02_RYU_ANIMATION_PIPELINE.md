# 📌 Tarea #2 [SP1-MARCO]: Pipeline de Animaciones de Ryu (02_Ryu)
## Sprint 1 (Sep 7 – Sep 20) | Asignado a: @Marco

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea tu rama
git checkout -b feature/sp1-marco-ryu-anim
```

---

### 🎯 2. Explicación Técnica de la Tarea

Debes verificar y dejar al 100% el pipeline de animaciones de **Ryu** (`02_Ryu`):
1. **Verificación de AnimationClips:** Los 64 AnimationClips de Ryu deben estar generados a **14 FPS** nativos CPS-3.
2. **Auto-Populate Animator Controller:** Usar la herramienta `SF3 Tools > Auto-Populate Animator Controller from Selected Folder` seleccionando `Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu` para sincronizar los 64 estados en `Ryu_Animator.controller`.
3. **Calibración de Pivote:** Verificar que en `light_punch`, el puñetazo no mueva a Ryu hacia atrás (Pivote Custom $X=0.32, Y=0$ si es necesario) y que `idle_stance` mantenga la línea de suelo en $Y=0$.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a configurarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor técnico de animación en Unity. Por favor lee `Devs/Marco/Sprint_1/TASK_SP1_02_RYU_ANIMATION_PIPELINE.md` y explícame paso a paso cómo debo verificar los 64 AnimationClips de Ryu, cómo funciona la herramienta de auto-poblado en el Animator, cómo detectar problemas de pivotes en los sprites y cómo probar las transiciones en `FighterAnimationTester.cs` para asegurarme de que todo esté perfecto."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] `Ryu_Animator.controller` contiene los 64 estados organizados en la cuadrícula del Animator.
- [ ] `idle_stance` es el estado por defecto (naranja).
- [ ] Al presionar `J`, `K`, `L`, `U`, `I` en modo Play, Ryu ejecuta las animaciones y vuelve a `idle_stance`.
- [ ] No hay desplazamientos visuales erróneos en el pie de apoyo.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

```bash
git add .
git commit -m "feat: sincronizar y calibrar 64 animaciones de Ryu (#2)"
git push -u origin feature/sp1-marco-ryu-anim
```
Abre el Pull Request en GitHub con la descripción: `Closes #2`.
