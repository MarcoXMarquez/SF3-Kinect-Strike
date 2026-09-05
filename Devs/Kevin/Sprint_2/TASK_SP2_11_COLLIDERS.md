# 📌 Tarea #11 [SP2-KEVIN-11]: Hitboxes y Hurtboxes de Chun-Li (03_ChunLi)
## Sprint 2 (Sep 21 – Oct 4) | Asignado a: @Kevin

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp2-kevin-chunli-colliders
```

---

### 🎯 2. Explicación Técnica de la Tarea

Configurar las cajas de colisión de 3 piezas y los hitboxes de patadas normales y Hyakuretsukyaku de Chun-Li.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de Unity. Por favor lee este archivo y explícame paso a paso cómo colocar y calibrar los colliders de Hurtbox y Hitbox en Fighter_ChunLi.prefab para que coincidan con sus poses y ráfaga de patadas."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Hurtboxes de Chun-Li cubren cabeza, torso y piernas.
- [ ] Hitbox de patadas normales y patadas rápidas configuradas.
- [ ] Probado en escena Sandbox_Kevin.unity.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: hitboxes y hurtboxes de chun-li (03_chunli) (#11)"

# 2. Subir rama a GitHub
git push -u origin feature/sp2-kevin-chunli-colliders
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #11`.