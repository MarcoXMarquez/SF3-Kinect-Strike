# 📌 Tarea #8 [SP2-MARCO-08]: Motor de Combate: Daño, Hitstun, Blockstun y Ventana de Parry
## Sprint 2 (Sep 21 – Oct 4) | Asignado a: @Marco

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp2-marco-combat-core
```

---

### 🎯 2. Explicación Técnica de la Tarea

Implementar la lógica universal de impacto: cálculo de vida restada, aturdimiento (Hitstun), bloqueo y ventana de Parry de 0.2s con 0 daño.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de sistemas de lucha. Por favor lee este archivo y explícame cómo programar la detección de impacto entre Hitbox y Hurtbox, los estados de Hitstun/Blockstun y el algoritmo de Parry exacto de 12 frames (0.2s)."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Al impactar: el receptor entra en hit_standing y pierde vida.
- [ ] Si el receptor bloquea: entra en block_standing y recibe daño reducido.
- [ ] Si presiona adelante en ventana de 0.2s: se activa Parry con 0 daño y destello azul.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: motor de combate: daño, hitstun, blockstun y ventana de parry (#8)"

# 2. Subir rama a GitHub
git push -u origin feature/sp2-marco-combat-core
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #8`.