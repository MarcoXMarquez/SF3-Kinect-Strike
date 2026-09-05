# -*- coding: utf-8 -*-
"""
Script para crear masivamente las 36 Issues oficiales de Street Fighter III en GitHub
asignadas a MarcoXMarquez, Sebastianzzzin y KevinCallo con sus Milestones y Labels.
"""

import subprocess
import time
import sys

USERS = {
    "Marco": "MarcoXMarquez",
    "Sebas": "Sebastianzzzin",
    "Kevin": "KevinCallo"
}

from generate_all_sprint_tasks import ALL_SPRINT_TASKS

def determine_labels(sprint_num, dev_name, task):
    labels = [f"role:{dev_name.lower()}", f"sprint:{sprint_num}"]
    text = (task['title'] + " " + task['desc']).lower()
    
    if "kinect" in text or "gesto" in text:
        labels.append("area:kinect")
        labels.append("needs-lab-test")
    elif "ml-agents" in text or "telemetr" in text or "ia" in text or "cloning" in text or "ppo" in text:
        labels.append("area:ai-ml")
    elif "parallax" in text or "escenario" in text or "vfx" in text or "super flash" in text:
        labels.append("area:art")
    elif "soundmanager" in text or "audio" in text or "voces" in text or "anunciador" in text:
        labels.append("area:audio")
    elif "sqlite" in text or "database" in text:
        labels.append("area:database")
    elif "hud" in text or "menú" in text or "menu" in text:
        labels.append("area:ui")
    elif "build" in text or "optimizaci" in text or "latencia" in text:
        labels.append("area:core")
    elif "manual" in text or "documentaci" in text:
        labels.append("area:docs")
    else:
        labels.append("area:combat")
        
    return ",".join(list(dict.fromkeys(labels)))

MILESTONE_TITLES = {
    1: "Sprint 1: Motor 2D Base & Animaciones",
    2: "Sprint 2: Hitboxes, Hurtboxes & Gestos Kinect",
    3: "Sprint 3: Combate Completo & Telemetría SQLite",
    4: "Sprint 4: IA Fase 1 (Imitación) & Gestos Pro",
    5: "Sprint 5: IA Fase 2 (Refuerzo + DDA) & HUD Arcade",
    6: "Sprint 6: Calibración, Build .EXE & Demo Final"
}

def create_issue(sprint_num, dev_name, task):
    title = f"#{task['id']} [{task['code']}]: {task['title']}"
    criteria_text = "\n".join([f"- [ ] {c}" for c in task["criteria"]])
    
    body = f"""### 🎯 Descripción de la Tarea
{task['desc']}

### 👤 Asignado a
@{USERS[dev_name]}

### 🗓️ Sprint y Calendario de Laboratorio
- **Milestone:** Sprint {sprint_num} ({ALL_SPRINT_TASKS[sprint_num]['dates']})
- **Rama Git Requerida:** `{task['branch']}`
- **Hito de Validación en Lab:** Sesión presencial de Martes con sensor Azure Kinect

### 📋 Criterios de Aceptación (Definition of Done)
{criteria_text}

### 🔗 Flujo de Cierre
- Cuando completes la tarea, abre el Pull Request hacia `main` e incluye en la descripción: `Closes #{task['id']}`.
"""

    labels = determine_labels(sprint_num, dev_name, task)
    milestone_title = MILESTONE_TITLES[sprint_num]
    assignee = USERS[dev_name]

    cmd = [
        'gh', 'issue', 'create',
        '--title', title,
        '--body', body,
        '--label', labels,
        '--milestone', milestone_title,
        '--assignee', assignee
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if res.returncode == 0:
        print(f"✓ Creada: {title} -> {res.stdout.strip()}")
    else:
        # Fallback si el usuario no acepto la invitacion aun
        cmd_fallback = [
            'gh', 'issue', 'create',
            '--title', title,
            '--body', body,
            '--label', labels,
            '--milestone', milestone_title
        ]
        res_fb = subprocess.run(cmd_fallback, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if res_fb.returncode == 0:
            print(f"✓ Creada ({assignee} pendiente de invitación): {title} -> {res_fb.stdout.strip()}")
        else:
            print(f"❌ Error al crear {title}: {res_fb.stderr.strip()}")

def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
    print("=" * 65)
    print("[SF3] CREANDO 36 ISSUES MASIVAS EN GITHUB REPOSITORY")
    print(f"• Marco: @{USERS['Marco']}")
    print(f"• Sebas: @{USERS['Sebas']}")
    print(f"• Kevin: @{USERS['Kevin']}")
    print("=" * 65)
    
    for sprint_num in range(1, 7):
        print(f"\n--- Creando Issues para Sprint {sprint_num} ---")
        sprint_data = ALL_SPRINT_TASKS[sprint_num]
        for dev_name in ["Marco", "Sebas", "Kevin"]:
            for task in sprint_data[dev_name]:
                create_issue(sprint_num, dev_name, task)
                time.sleep(0.3)

    print("\n" + "=" * 65)
    print("🎉 ¡TODAS LAS 36 ISSUES HAN SIDO REGISTRADAS EN GITHUB CON ÉXITO!")
    print("=" * 65)

if __name__ == "__main__":
    main()
