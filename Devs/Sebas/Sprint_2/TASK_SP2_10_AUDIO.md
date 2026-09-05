# 📌 Tarea #10 [SP2-SEBAS-10]: Prefabs de VFX (Hadouken/Chispas) y Audio en SF3SoundManager
## Sprint 2 (Sep 21 – Oct 4) | Asignado a: @Sebas

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp2-sebas-vfx-audio
```

---

### 🎯 2. Explicación Técnica de la Tarea

Crear prefabs de proyectil Hadouken, chispas de impacto, destello azul de parry y conectar los bancos de sonido en SF3SoundManager.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de efectos y audio en Unity. Por favor lee este archivo y explícame cómo armar el prefab del proyectil Hadouken con auto-destrucción, partículas de chispa de golpe y cómo reproducir voces y golpes con SF3SoundManager.cs."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Prefab de Hadouken avanza a velocidad constante y colisiona.
- [ ] Partículas de chispa de impacto y destello azul de parry se auto-destruyen.
- [ ] SF3SoundManager reproduce voces de Ryu y Ken y SFX de golpes.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: prefabs de vfx (hadouken/chispas) y audio en sf3soundmanager (#10)"

# 2. Subir rama a GitHub
git push -u origin feature/sp2-sebas-vfx-audio
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #10`.