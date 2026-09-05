# 📌 Tarea #18 [SP3-KEVIN-18]: Módulo de Base de Datos Local SQLite (DatabaseManager.cs)
## Sprint 3 (Oct 5 – Oct 18) | Asignado a: @Kevin

---

### 🌿 1. Paso Inicial de Git (Creación de Rama)

Abre tu terminal en la carpeta del proyecto y ejecuta estos comandos:
```bash
# 1. Asegúrate de estar en main y actualizado
git checkout main
git pull origin main

# 2. Crea y pásate a tu rama de trabajo
git checkout -b feature/sp3-kevin-sqlite-database
```

---

### 🎯 2. Explicación Técnica de la Tarea

Crear el gestor de base de datos local SQLite para almacenar perfiles de usuario, historial de partidas, precisión física y puntuaciones.

---

### 🤖 3. Prompt de Aprendizaje para Antigravity (Tutoría Paso a Paso)

Copia y pega este prompt a tu asistente para que te enseñe a programarlo tú mismo:

> *"Hola Antigravity, actúa como mi tutor de bases de datos en Unity. Por favor lee este archivo y explícame cómo configurar SQLite (sqlite-net) en C#, crear las tablas de Perfiles, Partidas y Telemetría, y escribir métodos asíncronos para guardar y consultar estadísticas."*

---

### 📋 4. Criterios de Aceptación (Definition of Done)
- [ ] DatabaseManager crea la base de datos sf3_game.db en Application.persistentDataPath.
- [ ] Tablas Users, Matches y KinectMetrics creadas.
- [ ] Métodos para guardar resultado de partida y consultar historial funcionando.

---

### 🚀 5. Paso Final de Git (Commit, Push y Pull Request)

Cuando termines y verifiques en Unity:
```bash
# 1. Guardar cambios
git add .
git commit -m "feat: módulo de base de datos local sqlite (databasemanager.cs) (#18)"

# 2. Subir rama a GitHub
git push -u origin feature/sp3-kevin-sqlite-database
```
3. Ve a GitHub (`https://github.com/MarcoXMarquez/SF3-Kinect-Strike`) y abre el **Pull Request**.
4. En la descripción escribe: `Closes #18`.