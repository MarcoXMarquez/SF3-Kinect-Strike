# 📌 Tarea #28 [SP5-SEBAS-28]: Menú de Selección de Personajes Arcade con Retratos
## Sprint 5 (Nov 2 – Nov 15) | Asignado a: @Sebas

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp5-sebas-character-select
```

---

### 🎯 2. Explicación Técnica de la Tarea

Pantalla de selección interactiva para elegir entre Ryu, Ken y Chun-Li con retratos arcade y sonidos de confirmación.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de UI en Unity. Por favor lee este archivo y explícame cómo armar la pantalla de selección de personaje con retratos animados, navegación por teclado/Kinect y transición a la escena de pelea."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Menú permite seleccionar entre Ryu, Ken y Chun-Li.
- [ ] Muestra retrato grande del luchador y reproduce su voz al confirmar.
- [ ] Carga la escena de combate pasando la selección al GameManager.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: menú de selección de personajes arcade con retratos (#28)"

# 2. Subir rama a GitHub
git push -u origin feature/sp5-sebas-character-select
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #28`.