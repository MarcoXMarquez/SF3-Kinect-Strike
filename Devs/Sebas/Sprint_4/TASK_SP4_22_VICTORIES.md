# 📌 Tarea #22 [SP4-SEBAS-22]: Poses de Victoria e Intros Únicas de Personajes
## Sprint 4 (Oct 19 – Nov 1) | Asignado a: @Sebas

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp4-sebas-intros-victories
```

---

### 🎯 2. Explicación Técnica de la Tarea

Integrar animaciones de intro rival (Ryu vs Ken) y poses de victoria con frases de voz arcade.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de cinemáticas en Unity. Por favor lee este archivo y explícame cómo coordinar la secuencia de intro al inicio del combate y la activación de la pose de victoria con frase de voz al ganar el round."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Intro especial se reproduce al iniciar la partida Ryu vs Ken.
- [ ] Pose de victoria se activa al derrotar al oponente.
- [ ] Frases de victoria reproducidas correctamente con SF3SoundManager.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: poses de victoria e intros únicas de personajes (#22)"

# 2. Subir rama a GitHub
git push -u origin feature/sp4-sebas-intros-victories
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #22`.