# 📌 Tarea #27 [SP5-SEBAS-27]: Sistema de Anunciador Oficial de SF3 (Round 1, Fight, K.O.!)
## Sprint 5 (Nov 2 – Nov 15) | Asignado a: @Sebas

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp5-sebas-announcer-rounds
```

---

### 🎯 2. Explicación Técnica de la Tarea

Coordinar voces oficiales del anunciador arcade con banners de texto animados en pantalla y lógica de 3 rounds.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de UI y audio en Unity. Por favor lee este archivo y explícame cómo sincronizar las voces del Announcer ('Round 1... Fight!', 'You Win!', 'K.O.!') con animaciones de texto en pantalla y control de rounds en GameManager.cs."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] Banners 'Round 1', 'Fight!', 'K.O.!', 'Perfect!' aparecen con voz oficial.
- [ ] Sistema de mejor de 3 rounds con reseteo de posiciones de combate.
- [ ] Victoria otorgada al ganar 2 rounds.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: sistema de anunciador oficial de sf3 (round 1, fight, k.o.!) (#27)"

# 2. Subir rama a GitHub
git push -u origin feature/sp5-sebas-announcer-rounds
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #27`.