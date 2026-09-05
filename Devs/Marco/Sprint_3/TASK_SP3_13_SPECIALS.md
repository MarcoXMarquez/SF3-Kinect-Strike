# 📌 Tarea #13 [SP3-MARCO-13]: Movimientos Especiales de Ryu (Hadouken, Shoryuken, Tatsumaki)
## Sprint 3 (Oct 5 – Oct 18) | Asignado a: @Marco

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp3-marco-ryu-specials
```

---

### 🎯 2. Explicación Técnica de la Tarea

Calibrar frame data, proyectiles, elevación física y balance de daño de los ataques especiales de Ryu.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de combate 2D. Por favor lee este archivo y explícame cómo conectar el disparo de proyectil en el frame exacto de Hadouken, la elevación vertical del Shoryuken y la rotación de Tatsumaki Senpukyaku en Ryu."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Hadouken instancia el proyectil en el frame de salida.
- [ ] Shoryuken eleva a Ryu del suelo y aplica daño múltiple.
- [ ] Tatsumaki desplaza a Ryu horizontalmente en el aire.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: movimientos especiales de ryu (hadouken, shoryuken, tatsumaki) (#13)"

# 2. Subir rama a GitHub
git push -u origin feature/sp3-marco-ryu-specials
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #13`.