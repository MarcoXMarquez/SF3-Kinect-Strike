# 📌 Tarea #7 [SP2-MARCO-07]: Hitboxes y Hurtboxes de Ryu (02_Ryu)
## Sprint 2 (Sep 21 – Oct 4) | Asignado a: @Marco

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp2-marco-ryu-colliders
```

---

### 🎯 2. Explicación Técnica de la Tarea

Configurar las cajas de colisión de 3 piezas (cabeza, torso, piernas) y hitboxes de ataques normales y Hadouken de Ryu con auto-ajuste al sprite.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de combate 2D. Por favor lee este archivo y explícame cómo configurar los componentes FighterHurtbox y FighterHitbox en Ryu, cómo funciona el auto-ajuste en saltos/agachadas y cómo activar hitboxes en frames específicos."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Hurtboxes de cabeza, torso y piernas siguen el cuerpo de Ryu en saltos y agachadas.
- [ ] Hitbox roja se enciende solo en frames activos del golpe.
- [ ] Probado en modo Play con FighterCombatColliders.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: hitboxes y hurtboxes de ryu (02_ryu) (#7)"

# 2. Subir rama a GitHub
git push -u origin feature/sp2-marco-ryu-colliders
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #7`.