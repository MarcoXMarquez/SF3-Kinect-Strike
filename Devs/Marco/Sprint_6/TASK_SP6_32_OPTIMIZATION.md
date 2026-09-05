# 📌 Tarea #32 [SP6-MARCO-32]: Auditoría de Integración y Build Standalone .exe a 60 FPS
## Sprint 6 (Nov 16 – Nov 30) | Asignado a: @Marco

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp6-marco-build-optimization
```

---

### 🎯 2. Explicación Técnica de la Tarea

Generar el ejecutable de producción en Windows 64-bit, auditar rendimiento de CPU/GPU y optimizar memoria para 60 FPS fijos.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de optimización en Unity. Por favor lee este archivo y explícame cómo auditar el Unity Profiler, eliminar picos de Garbage Collector y configurar el Build Settings para generar un .exe standalone impecable a 60 FPS."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Build ejecutable (.exe) generado sin errores.
- [ ] El juego corre a 60 FPS constantes en resolución 1080p.
- [ ] Sin fugas de memoria tras 10 partidas consecutivas.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: auditoría de integración y build standalone .exe a 60 fps (#32)"

# 2. Subir rama a GitHub
git push -u origin feature/sp6-marco-build-optimization
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #32`.