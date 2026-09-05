# -*- coding: utf-8 -*-
"""
Script de automatización para generar las 36 Issues de GitHub en bulk para Street Fighter III.
Cada desarrollador es dueño 100% de su personaje:
- Marco: Ryu (02_Ryu) + Core / ML-Agents
- Sebas: Ken (01_Ken) + Escenario Japón / VFX / Audio
- Kevin: Chun-Li (03_ChunLi) + Azure Kinect / SQLite / UI
"""

import subprocess
import sys

# Mapeo de nombres de usuario de GitHub (Se actualizan con los @users reales)
GITHUB_USERS = {
    "marco": "MarcoXMarquez",
    "sebas": "sebas",      # Reemplazar con el user real
    "kevin": "kevin"       # Reemplazar con el user real
}

ISSUES = [
    # ==================== SPRINT 1 ====================
    {
        "milestone": "Sprint 1: Motor 2D Base & Animaciones",
        "title": "[SP1-MARCO] Máquina de Estados Core (FighterStateMachine.cs y FighterPhysics.cs)",
        "body": "### Descripción\nImplementar la máquina de estados desacoplada en C# y la física de salto parabólico/locomoción.\n\n### Asignado\n@" + GITHUB_USERS["marco"] + "\n\n### Criterios de Aceptación\n- [ ] Estados: Idle, Walk, Crouch, Jump con física parabólica.\n- [ ] Funciona en teclado para desarrollo offline (miércoles a lunes).",
        "labels": "role:marco,sprint:1,area:combat",
        "assignee": GITHUB_USERS["marco"]
    },
    {
        "title": "[SP1-MARCO] Pipeline de Animaciones de Ryu (02_Ryu)",
        "body": "### Descripción\nSincronizar los 64 AnimationClips de Ryu en Ryu_Animator.controller y verificar retornos a reposo.\n\n### Asignado\n@" + GITHUB_USERS["marco"] + "\n\n### Criterios de Aceptación\n- [ ] Auto-popular Ryu_Animator.controller con las 7 categorías.\n- [ ] Verificar retorno a idle de puños, patadas y specials en FighterAnimationTester.",
        "labels": "role:marco,sprint:1,area:combat",
        "assignee": GITHUB_USERS["marco"]
    },
    {
        "title": "[SP1-SEBAS] Pipeline de Animaciones de Ken (01_Ken)",
        "body": "### Descripción\nOrganizar las 7 categorías de Ken, generar AnimationClips con SF3 Tools y poblar Ken_Animator.controller.\n\n### Asignado\n@" + GITHUB_USERS["sebas"] + "\n\n### Criterios de Aceptación\n- [ ] Organizar carpetas de 01_Ken con nombres descriptivos.\n- [ ] Generar todos los .anim a 14 FPS con SF3AnimationBatchCreator.\n- [ ] Auto-popular Ken_Animator.controller.",
        "labels": "role:sebas,sprint:1,area:combat",
        "assignee": GITHUB_USERS["sebas"]
    },
    {
        "title": "[SP1-SEBAS] Montaje del Escenario Japón (Suzaku Castle) con Parallax",
        "body": "### Descripción\nMontar el escenario con múltiples capas de profundidad usando ParallaxBackground.cs.\n\n### Asignado\n@" + GITHUB_USERS["sebas"] + "\n\n### Criterios de Aceptación\n- [ ] Configurar Sorting Layers (Background, Midground, Floor).\n- [ ] Configurar ParallaxBackground.cs con cámara ortográfica.\n- [ ] Pixels Per Unit a 100 y scale (1,1,1).",
        "labels": "role:sebas,sprint:1,area:art",
        "assignee": GITHUB_USERS["sebas"]
    },
    {
        "title": "[SP1-KEVIN] Pipeline de Animaciones de Chun-Li (03_ChunLi)",
        "body": "### Descripción\nOrganizar las 7 categorías de Chun-Li, generar AnimationClips con SF3 Tools y poblar ChunLi_Animator.controller.\n\n### Asignado\n@" + GITHUB_USERS["kevin"] + "\n\n### Criterios de Aceptación\n- [ ] Organizar carpetas de 03_ChunLi con nombres descriptivos.\n- [ ] Generar todos los .anim a 14 FPS con SF3AnimationBatchCreator.\n- [ ] Auto-popular ChunLi_Animator.controller.",
        "labels": "role:kevin,sprint:1,area:combat",
        "assignee": GITHUB_USERS["kevin"]
    },
    {
        "title": "[SP1-KEVIN] Arquitectura de Entrada IFighterInput.cs y Emulador de Teclado",
        "body": "### Descripción\nDiseñar la interfaz desacoplada de entrada y el adaptador de teclado para pruebas offline (miércoles a lunes).\n\n### Asignado\n@" + GITHUB_USERS["kevin"] + "\n\n### Criterios de Aceptación\n- [ ] Crear interfaz IFighterInput con métodos IsAttacking, GetMovementDirection, IsBlocking.\n- [ ] Crear KeyboardFighterInput implementando la interfaz.",
        "labels": "role:kevin,sprint:1,area:kinect",
        "assignee": GITHUB_USERS["kevin"]
    },

    # ==================== SPRINT 2 ====================
    {
        "title": "[SP2-MARCO] Hitboxes y Hurtboxes de Ryu (02_Ryu)",
        "body": "### Descripción\nConfigurar cajas de colisión de 3 piezas (cabeza, torso, piernas) y hitboxes de golpes normales y Hadouken de Ryu.\n\n### Asignado\n@" + GITHUB_USERS["marco"] + "\n\n### Criterios de Aceptación\n- [ ] Cajas de colisión de Ryu se ajustan al sprite en saltos y agachadas.\n- [ ] Hitboxes se encienden en frames activos de ataque.",
        "labels": "role:marco,sprint:2,area:combat",
        "assignee": GITHUB_USERS["marco"]
    },
    {
        "title": "[SP2-MARCO] Motor de Combate: Daño, Hitstun, Blockstun y Ventana de Parry",
        "body": "### Descripción\nImplementar cálculo de vida restada, aturdimiento de impacto, bloqueo y ventana de parry de 0.2s.\n\n### Asignado\n@" + GITHUB_USERS["marco"] + "\n\n### Criterios de Aceptación\n- [ ] Al recibir golpe: animar hit_standing/hit_crouching y restar vida.\n- [ ] Al presionar adelante en ventana de 0.2s: activar Parry con destello azul y 0 daño.",
        "labels": "role:marco,sprint:2,area:combat",
        "assignee": GITHUB_USERS["marco"]
    },
    {
        "title": "[SP2-SEBAS] Hitboxes y Hurtboxes de Ken (01_Ken)",
        "body": "### Descripción\nConfigurar cajas de colisión de 3 piezas y hitboxes de ataques normales y Shoryuken de Ken.\n\n### Asignado\n@" + GITHUB_USERS["sebas"] + "\n\n### Criterios de Aceptación\n- [ ] Cajas de colisión de Ken se adaptan al sprite en saltos y agachadas.\n- [ ] Hitbox de Shoryuken configurada con daño y elevación.",
        "labels": "role:sebas,sprint:2,area:combat",
        "assignee": GITHUB_USERS["sebas"]
    },
    {
        "title": "[SP2-SEBAS] Prefabs de VFX (Hadouken/Chispas) y Audio en SF3SoundManager",
        "body": "### Descripción\nCrear el prefab del Hadouken con animación y partículas de chispa de golpe/parry, conectando el SoundManager.\n\n### Asignado\n@" + GITHUB_USERS["sebas"] + "\n\n### Criterios de Aceptación\n- [ ] Hadouken avanza a velocidad constante y desaparece al impactar.\n- [ ] Sonidos de golpes débiles/fuertes y voces de Ryu y Ken conectadas.",
        "labels": "role:sebas,sprint:2,area:art",
        "assignee": GITHUB_USERS["sebas"]
    },
    {
        "title": "[SP2-KEVIN] Hitboxes y Hurtboxes de Chun-Li (03_ChunLi)",
        "body": "### Descripción\nConfigurar cajas de colisión de 3 piezas y hitboxes de patadas normales y Hyakuretsukyaku de Chun-Li.\n\n### Asignado\n@" + GITHUB_USERS["kevin"] + "\n\n### Criterios de Aceptación\n- [ ] Cajas de colisión de Chun-Li se adaptan al sprite en saltos y agachadas.\n- [ ] Hitboxes de patadas rápidas configuradas con daño consecutivo.",
        "labels": "role:kevin,sprint:2,area:combat",
        "assignee": GITHUB_USERS["kevin"]
    },
    {
        "title": "[SP2-KEVIN] Clasificador Somatosensorial Azure Kinect (Puñetazo y Bloqueo)",
        "body": "### Descripción\nAlgoritmo de detección de puño por velocidad de muñeca y bloqueo por brazos cruzados en Azure Kinect.\n\n### Asignado\n@" + GITHUB_USERS["kevin"] + "\n\n### Criterios de Aceptación\n- [ ] Extensión rápida de brazo activa puño en el personaje.\n- [ ] Cruzar brazos activa estado de bloqueo en Kinect (martes).",
        "labels": "role:kevin,sprint:2,area:kinect,needs-lab-test",
        "assignee": GITHUB_USERS["kevin"]
    }
]

def main():
    print("=" * 60)
    print("🥋 GENERADOR DE ISSUES DE GITHUB - SF3 PROYECTO")
    print("=" * 60)
    print(f"Total de tareas preparadas: {len(ISSUES)}")
    print("Cada dev tiene su personaje asignado al 100%:")
    print("• Marco: Ryu")
    print("• Sebas: Ken")
    print("• Kevin: Chun-Li")

if __name__ == "__main__":
    main()
