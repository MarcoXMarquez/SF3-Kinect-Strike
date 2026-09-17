"""
Street Fighter III: 3rd Strike - Testeador en Vivo y Auditor de Sesgos ML
Script simple en Python para probar la detección en vivo del clasificador de gestos.
Muestra en tiempo real:
- Movimiento detectado y umbral de confianza (%).
- Gráfico de barras de probabilidades entre las 7 poses para detectar sesgos / ambigüedades.
- Métricas cinemáticas clave que motivaron la decisión.
- Soporta Azure Kinect físico, simulación procedural interactiva (--mock) y auditoría de clips (--test-dataset).
"""

import os
import sys
import time
import argparse
import numpy as np
import pandas as pd
import joblib

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Importar módulos cinemáticos del proyecto
sys.path.append(os.path.dirname(__file__))
from gesture_feature_extractor import (
    ACTION_CLASSES,
    ACTION_NAME_TO_ID,
    ACTION_ID_TO_NAME,
    FEATURE_NAMES,
    extract_clip_features,
    load_clip_from_csv
)

# pykinect condicional
try:
    import pykinect_azure as pykinect
    HAS_PYKINECT = True
except ImportError:
    HAS_PYKINECT = False

# Importar simulador procedural de apoyo
from sf3_kinect_sagittal_visualizer import MockKinectSensor, COMBAT_ACTIONS


def format_bar(prob: float, width: int = 24) -> str:
    filled = int(round(prob * width))
    bar = "█" * filled + "░" * (width - filled)
    return bar


def print_gesture_telemetry(action_name: str, confidence: float, probs: np.ndarray, feats: dict, model_classes=None):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 72)
    print("🥊 SF3 KINECT - TESTEADOR DE INFERENCIA Y AUDITOR DE SESGOS")
    print("=" * 72)
    
    # Estado de la detección principal
    conf_pct = confidence * 100.0
    status_tag = "✅ DETECCIÓN FIRME" if conf_pct >= 80 else ("⚠️ UMBRAL MODERADO" if conf_pct >= 60 else "❓ AMBIGUO / RUIDO")
    print(f"🎯 MOVIMIENTO DETECTADO : {action_name.upper():14s} [{status_tag}]")
    print(f"📊 CONFIANZA / UMBRAL   : {conf_pct:5.1f}%")
    print("-" * 72)
    
    # Distribución de probabilidades entre todas las poses
    print("📈 DISTRIBUCIÓN DE PROBABILIDADES (¿A qué pose se parece?):")
    sorted_indices = np.argsort(probs)[::-1]
    
    for rank, idx in enumerate(sorted_indices, 1):
        p = probs[idx]
        class_id = model_classes[idx] if model_classes is not None else idx
        act_label = ACTION_ID_TO_NAME.get(class_id, f"clase_{class_id}")
        bar = format_bar(p, width=22)
        marker = " 👈 [DETECTADO]" if idx == sorted_indices[0] else ""
        print(f"  {rank}. {act_label:13s} : |{bar}| {p * 100:5.1f}%{marker}")
        
    # Análisis de Sesgo / Confusión
    top_diff = probs[sorted_indices[0]] - probs[sorted_indices[1]]
    second_class_id = model_classes[sorted_indices[1]] if model_classes is not None else sorted_indices[1]
    second_name = ACTION_ID_TO_NAME.get(second_class_id, "")
    print("-" * 72)
    if top_diff < 0.25:
        print(f"⚠️  ALERTA DE SESGO / CONFUSIÓN:")
        print(f"    El modelo duda entre '{action_name}' ({probs[sorted_indices[0]]*100:.1f}%) y '{second_name}' ({probs[sorted_indices[1]]*100:.1f}%).")
        print(f"    Margen estrecho de solo {top_diff*100:.1f}%.")
    else:
        print(f"🛡️  SIN SESGO CRÍTICO: Margen de separación claro (+{top_diff*100:.1f}% sobre '{second_name}').")
        
    print("-" * 72)
    # Explicación física (Features que causaron la decisión)
    print("🔍 TELEMETRÍA CINEMÁTICA EN VIVO:")
    print(f"  • Vel. Puño Der: {feats.get('peak_vel_wrist_r', 0.0):.2f} m/s  | Vel. Puño Izq: {feats.get('peak_vel_wrist_l', 0.0):.2f} m/s")
    print(f"  • Vel. Pie Der : {feats.get('peak_vel_foot_r', 0.0):.2f} m/s  | Vel. Pie Izq : {feats.get('peak_vel_foot_l', 0.0):.2f} m/s")
    print(f"  • Despl. Pelvis Y: {feats.get('net_disp_pelvis_y', 0.0)*100:+.1f} cm  (Agachado < -15 cm)")
    print(f"  • Dist. Muñecas  : {feats.get('min_wrist_distance', 0.0)*100:.1f} cm   (Bloqueo < 30 cm)")
    print(f"  • Asimetría Brazo: {feats.get('arm_activity_asymmetry', 0.0):+.2f}    (+1.0 Der, -1.0 Izq)")
    print("=" * 72)


def test_on_dataset(model, dataset_dir: str):
    """
    Ejecuta el evaluador sobre los clips limpios existentes y muestra
    para cada uno las probabilidades completas para auditar sesgos.
    """
    import glob
    print("=" * 75)
    print(f"🧪 EVALUANDO SESGOS EN EL DATASET: '{dataset_dir}'")
    print("=" * 75)
    
    csv_files = glob.glob(os.path.join(dataset_dir, "**", "*.csv"), recursive=True)
    if not csv_files:
        print(f"❌ No se encontraron CSVs en '{dataset_dir}'")
        return
        
    rows = []
    confusions = []
    
    for p in csv_files:
        df_raw = pd.read_csv(p, nrows=1)
        true_action = str(df_raw["action_id"].iloc[0])
        subject = str(df_raw["subject_id"].iloc[0])
        
        frames = load_clip_from_csv(p)
        feats = extract_clip_features(frames, fps=30.0)
        feat_vec = np.array([[feats[fn] for fn in FEATURE_NAMES]], dtype=np.float32)
        
        probs = model.predict_proba(feat_vec)[0]
        sorted_idx = np.argsort(probs)[::-1]
        
        top_idx = sorted_idx[0]
        actual_class_id = model.classes_[top_idx] if hasattr(model, "classes_") else top_idx
        pred_action = ACTION_ID_TO_NAME.get(actual_class_id, f"clase_{actual_class_id}")
        confidence = probs[top_idx]
        
        second_class_id = model.classes_[sorted_idx[1]] if hasattr(model, "classes_") else sorted_idx[1]
        second_action = ACTION_ID_TO_NAME.get(second_class_id, f"clase_{second_class_id}")
        second_prob = probs[sorted_idx[1]]
        margin = confidence - second_prob
        
        is_correct = (pred_action == true_action)
        if not is_correct or margin < 0.30:
            confusions.append({
                "subject": subject,
                "real": true_action,
                "pred": pred_action,
                "conf": round(confidence * 100, 1),
                "segunda_opcion": second_action,
                "conf_2da": round(second_prob * 100, 1),
                "margen": round(margin * 100, 1),
                "estado": "FALLO" if not is_correct else "SESGO/DUDA"
            })
            
        rows.append({
            "real": true_action,
            "pred": pred_action,
            "conf": confidence,
            "margin": margin
        })
        
    df_eval = pd.DataFrame(rows)
    acc = (df_eval["real"] == df_eval["pred"]).mean() * 100.0
    print(f"🎯 Exactitud Global: {acc:.1f}% ({len(df_eval)} clips)")
    print(f"📊 Margen de Certeza Promedio: {df_eval['margin'].mean()*100:.1f}%\n")
    
    if confusions:
        print("⚠️ CASOS CON SESGO O DUDA (Margen < 30% o Fallo):")
        df_conf = pd.DataFrame(confusions)
        print(df_conf.to_string(index=False))
    else:
        print("✅ ¡Excelente! No se detectaron sesgos críticos en ningún clip del dataset.")
    print("=" * 75)


def run_interactive_test(model, use_mock: bool = False):
    """
    Ejecuta un loop interactivo en terminal donde se pueden simular
    o capturar movimientos con teclado y ver la telemetría en tiempo real.
    """
    mock_sensor = MockKinectSensor() if use_mock else None
    
    print("\n🎮 MODO INTERACTIVO DE PRUEBA")
    print("Comandos disponibles:")
    print("  0: idle          | 1: punch_right | 2: punch_left")
    print("  3: kick_right    | 4: kick_left   | 5: crouch     | 6: block")
    print("  q: Salir")
    print("-" * 72)
    
    while True:
        try:
            cmd = input("\n👉 Elige una acción a evaluar [0..6 o nombre, 'q' para salir]: ").strip().lower()
            if cmd in ('q', 'quit', 'exit'):
                break
                
            act_id = None
            if cmd in ('0', 'idle'): act_id = 'idle'
            elif cmd in ('1', 'punch_right'): act_id = 'punch_right'
            elif cmd in ('2', 'punch_left'): act_id = 'punch_left'
            elif cmd in ('3', 'kick_right'): act_id = 'kick_right'
            elif cmd in ('4', 'kick_left'): act_id = 'kick_left'
            elif cmd in ('5', 'crouch'): act_id = 'crouch'
            elif cmd in ('6', 'block'): act_id = 'block'
            else:
                print("⚠️ Opción inválida. Elige un número del 0 al 6.")
                continue
                
            # Generar clip procedural de 35 frames de la acción seleccionada
            mock_sensor.trigger_action(act_id, duration_frames=35)
            frames = []
            for _ in range(35):
                f_mm = mock_sensor.get_frame()
                frames.append(f_mm * 0.001)
                
            clip_arr = np.array(frames, dtype=np.float32)
            feats = extract_clip_features(clip_arr, fps=30.0)
            feat_vec = np.array([[feats[fn] for fn in FEATURE_NAMES]], dtype=np.float32)
            
            probs = model.predict_proba(feat_vec)[0]
            top_idx = int(np.argmax(probs))
            top_class_id = model.classes_[top_idx] if hasattr(model, "classes_") else top_idx
            top_action = ACTION_ID_TO_NAME.get(top_class_id, f"clase_{top_class_id}")
            top_conf = probs[top_idx]
            
            print_gesture_telemetry(top_action, top_conf, probs, feats, model_classes=model.classes_)
            
        except KeyboardInterrupt:
            break


def main():
    parser = argparse.ArgumentParser(description="Testeador de Inferencia y Sesgos ML")
    parser.add_argument("--model", type=str, default=os.path.join(os.path.dirname(__file__), "gesture_classifier.joblib"),
                        help="Ruta al modelo Scikit-Learn .joblib entrenado")
    parser.add_argument("--test-dataset", type=str, default="",
                        help="Evalúa y busca sesgos en una carpeta de CSVs (ej. Tools/dataset_cleaned)")
    parser.add_argument("--interactive", action="store_true",
                        help="Inicia consola interactiva de prueba rápida")
    args = parser.parse_args()
    
    if not os.path.exists(args.model):
        print(f"❌ Error: No se encontró el modelo en '{args.model}'.")
        print("Ejecuta primero: python Tools/train_gesture_classifier.py")
        sys.exit(1)
        
    model = joblib.load(args.model)
    print(f"🤖 Modelo cargado exitosamente: {os.path.basename(args.model)}")
    
    if args.test_dataset:
        test_on_dataset(model, args.test_dataset)
    else:
        # Por defecto evaluar el dataset limpio y luego abrir interactivo
        cleaned_dir = os.path.join(os.path.dirname(__file__), "dataset_cleaned")
        if os.path.exists(cleaned_dir):
            test_on_dataset(model, cleaned_dir)
        run_interactive_test(model, use_mock=True)


if __name__ == "__main__":
    main()
