# 📌 Tarea #21 [SP4-SEBAS-21]: Super Arts y Efecto Visual Super Flash (Ryu y Ken)
## Sprint 4 (Oct 19 – Nov 1) | Asignado a: @Sebas

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp4-sebas-super-flash
```

---

### 🎯 2. Explicación Técnica de la Tarea

Implementar el efecto de fondo oscuro (Super Flash), rayos de energía y súper ataques Shinkuu Hadouken y Shinryuken.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de efectos visuales en Unity. Por favor lee este archivo y explícame cómo programar la pausa temporal (Hitstop) de 30 frames con oscurecimiento de fondo (Super Flash) y animación del Súper Ataque de Ryu y Ken."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Al disparar Super Art: fondo se oscurece y suena el sonido de Super Flash.
- [ ] Shinkuu Hadouken dispara rayo gigante de 5 hits.
- [ ] Shinryuken de Ken genera vórtice de fuego vertical.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: super arts y efecto visual super flash (ryu y ken) (#21)"

# 2. Subir rama a GitHub
git push -u origin feature/sp4-sebas-super-flash
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #21`.