# 📌 Tarea #9 [SP2-SEBAS-09]: Hitboxes y Hurtboxes de Ken (01_Ken)
## Sprint 2 (Sep 21 – Oct 4) | Asignado a: @Sebas

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp2-sebas-ken-colliders
```

---

### 🎯 2. Explicación Técnica de la Tarea

Configurar las cajas de colisión de 3 piezas y los hitboxes de ataques normales y Shoryuken de Ken.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de Unity. Por favor lee este archivo y explícame paso a paso cómo colocar y calibrar los colliders de Hurtbox y Hitbox en el prefab de Ken (Fighter_Ken.prefab) para que coincidan con sus sprites a 100 PPU."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Hurtboxes de Ken cubren cabeza, torso y piernas adecuadamente.
- [ ] Hitbox de puños, patadas y Shoryuken calibradas.
- [ ] Probado en escena Sandbox_Sebas.unity.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: hitboxes y hurtboxes de ken (01_ken) (#9)"

# 2. Subir rama a GitHub
git push -u origin feature/sp2-sebas-ken-colliders
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #9`.