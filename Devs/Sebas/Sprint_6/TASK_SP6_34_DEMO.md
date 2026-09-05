# 📌 Tarea #34 [SP6-SEBAS-34]: Documentación y Manual de Usuario / Guía de Demostración
## Sprint 6 (Nov 16 – Nov 30) | Asignado a: @Sebas

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp6-sebas-user-manual-demo
```

---

### 🎯 2. Explicación Técnica de la Tarea

Elaborar la guía de pasos para la presentación ante el jurado/profesor, explicando el flujo de la demo en vivo con Kinect e IA.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de documentación técnica. Por favor lee este archivo y explícame cómo estructurar un Manual de Demostración impecable para la sustentación ante el profesor, detallando los pasos de encendido de Kinect, inicio de partida y explicación técnica de la IA."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Manual de Demostración guardado en Docs/GUIA_DEMO_EXPOSICION.md.
- [ ] Guía de calibración rápida de Azure Kinect incluida.
- [ ] Flujo de exposición ensayado con el equipo.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: documentación y manual de usuario / guía de demostración (#34)"

# 2. Subir rama a GitHub
git push -u origin feature/sp6-sebas-user-manual-demo
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #34`.