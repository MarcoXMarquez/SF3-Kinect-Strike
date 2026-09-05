# 📌 Tarea #36 [SP6-KEVIN-36]: Pantalla de Estadísticas Finales con Consultas SQLite
## Sprint 6 (Nov 16 – Nov 30) | Asignado a: @Kevin

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp6-kevin-stats-screen
```

---

### 🎯 2. Explicación Técnica de la Tarea

Pantalla de resumen al terminar el combate que muestra golpes acertados, Hadoukens lanzados, precisión física y ganador desde SQLite.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de UI y bases de datos en Unity. Por favor lee este archivo y explícame cómo armar la pantalla de GameOver / Estadísticas consultando los datos de la última partida en SQLite y presentándolos con diseño arcade."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Pantalla de estadísticas muestra datos reales de la partida guardada.
- [ ] Muestra precisión de gestos corporales con Kinect.
- [ ] Botones para revancha o volver al menú principal funcionando.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: pantalla de estadísticas finales con consultas sqlite (#36)"

# 2. Subir rama a GitHub
git push -u origin feature/sp6-kevin-stats-screen
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #36`.