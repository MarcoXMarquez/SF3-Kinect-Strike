# 📌 Tarea #17 [SP3-KEVIN-17]: Movimientos Especiales de Chun-Li (Kikoken y Hyakuretsukyaku)
## Sprint 3 (Oct 5 – Oct 18) | Asignado a: @Kevin

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp3-kevin-chunli-specials
```

---

### 🎯 2. Explicación Técnica de la Tarea

Configurar ráfaga de patadas rápidas (Hyakuretsukyaku), proyectil Kikoken y voces de Chun-Li.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de combate 2D. Por favor lee este archivo y explícame cómo implementar el disparo del Kikoken con su animación de proyectil y el estado de ráfaga de patadas rápidas con hitboxes consecutivas en Chun-Li."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Kikoken dispara proyectil con animación de impacto.
- [ ] Hyakuretsukyaku genera ráfaga de patadas con daño consecutivo.
- [ ] Voces arcade de Chun-Li conectadas al SoundManager.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: movimientos especiales de chun-li (kikoken y hyakuretsukyaku) (#17)"

# 2. Subir rama a GitHub
git push -u origin feature/sp3-kevin-chunli-specials
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #17`.