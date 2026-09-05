# -*- coding: utf-8 -*-
"""
Script de Auto-Configuración del Entorno de Desarrollo para Street Fighter III Unity.
Ejecuta este script al clonar el repositorio para verificar tu entorno y configurar tu perfil.
Uso: python Tools/setup_team_workspace.py
"""

import os
import sys
import subprocess

def print_header(title):
    print("\n" + "=" * 65)
    print(f"🥋 {title}")
    print("=" * 65)

def check_git():
    print_header("1. Verificando Configuración de Git")
    try:
        name = subprocess.check_output(["git", "config", "user.name"]).decode().strip()
        email = subprocess.check_output(["git", "config", "user.email"]).decode().strip()
        print(f"✓ Git configurado: {name} <{email}>")
    except Exception:
        print("⚠️ Advertencia: No tienes configurado git user.name o user.email.")
        print("  Ejecuta: git config --global user.name \"Tu Nombre\"")
        print("  Ejecuta: git config --global user.email \"tu_correo@ejemplo.com\"")

def check_unity_structure():
    print_header("2. Verificando Estructura del Proyecto Unity")
    expected_dirs = [
        "Assets/StreetFighter3_ThirdStrike/Characters/01_Ken",
        "Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu",
        "Assets/StreetFighter3_ThirdStrike/Characters/03_ChunLi",
        "Assets/StreetFighter3_ThirdStrike/Scripts/Core",
        "Assets/StreetFighter3_ThirdStrike/Scripts/Combat",
        "Assets/StreetFighter3_ThirdStrike/Scripts/Input",
        "Assets/StreetFighter3_ThirdStrike/Scripts/Editor",
        "Devs/Marco",
        "Devs/Sebas",
        "Devs/Kevin",
        "Devs/Context"
    ]
    for d in expected_dirs:
        if os.path.exists(d):
            print(f"✓ Carpeta OK: {d}")
        else:
            print(f"⚠️ Creando carpeta faltante: {d}")
            os.makedirs(d, exist_ok=True)

def select_profile():
    print_header("3. Perfiles de Desarrollador del Equipo")
    print("Selecciona tu perfil:")
    print("  [1] Marco (Ryu / Arquitectura Core / ML-Agents GPU)")
    print("  [2] Sebas (Ken / Escenarios Parallax / VFX & Audio)")
    print("  [3] Kevin (Chun-Li / Azure Kinect SDK / SQLite & UI)")
    
    choice = input("\nIngresa tu número [1-3] (o presiona Enter para salir): ").strip()
    
    profiles = {
        "1": ("Marco", "Ryu (02_Ryu)", "Devs/Marco/Sprint_1/TASK_SP1_01_STATEMACHINE_PHYSICS.md", "feature/sp1-marco-statemachine"),
        "2": ("Sebas", "Ken (01_Ken)", "Devs/Sebas/Sprint_1/TASK_SP1_03_KEN_ANIMATION_PIPELINE.md", "feature/sp1-sebas-ken-anim"),
        "3": ("Kevin", "Chun-Li (03_ChunLi)", "Devs/Kevin/Sprint_1/TASK_SP1_05_CHUNLI_ANIMATION_PIPELINE.md", "feature/sp1-kevin-chunli-anim")
    }
    
    if choice in profiles:
        dev, char, task_file, branch = profiles[choice]
        print("\n" + "-" * 65)
        print(f"¡Bienvenido, {dev}!")
        print(f"• Tu Personaje Asignado: {char}")
        print(f"• Tu Primera Tarea del Sprint 1: {task_file}")
        print(f"• Tu Comando para Iniciar Rama:")
        print(f"    git checkout main && git pull origin main && git checkout -b {branch}")
        print("-" * 65)
        print("\n💡 Consejo: Abre tu tarea en Markdown y usa el prompt de tutoría con tu Antigravity.")

def main():
    print("=" * 65)
    print("🥋 AUTO-CONFIGURACIÓN DE ESPACIO DE TRABAJO - STREET FIGHTER III")
    print("=" * 65)
    check_git()
    check_unity_structure()
    select_profile()
    print("\n✓ ¡Entorno listo para desarrollar!")

if __name__ == "__main__":
    main()
