"""
Street Fighter III: 3rd Strike - Entrenador de Clasificador Cinemático ML
Entrena un modelo supervisado (RandomForest) con validación cruzada por grupos (sujetos),
evalúa métricas de precisión y exporta a formato ONNX para Unity Sentis / Python.
"""

import os
import sys
import argparse
import time
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, GroupKFold, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import joblib

try:
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType
    HAS_SKL2ONNX = True
except ImportError:
    HAS_SKL2ONNX = False

# Importar extractor cinemático local
sys.path.append(os.path.dirname(__file__))
from gesture_feature_extractor import (
    ACTION_CLASSES,
    ACTION_NAME_TO_ID,
    ACTION_ID_TO_NAME,
    FEATURE_NAMES,
    extract_clip_features,
    load_clip_from_csv
)


def generate_synthetic_dataset(output_dir: str, n_subjects: int = 10, reps_per_class: int = 20):
    """
    Genera un dataset sintético realista de cinemática corporal para los 10 sujetos y las 7 clases.
    Permite probar todo el pipeline de feature engineering, entrenamiento y exportación a ONNX
    sin necesidad de haber conectado el Azure Kinect físico.
    """
    print(f"🛠️ Generando dataset sintético ({n_subjects} sujetos, {reps_per_class} repeticiones/clase, 7 clases)...")

    np.random.seed(42)
    os.makedirs(output_dir, exist_ok=True)

    # Base skeleton template (32 joints, Azure Kinect coordinates en metros)
    base_skeleton = np.zeros((32, 3), dtype=np.float32)
    base_skeleton[0] = [0.0, 0.95, 2.2]    # Pelvis
    base_skeleton[1] = [0.0, 0.80, 2.2]    # Spine Navel
    base_skeleton[2] = [0.0, 0.65, 2.2]    # Spine Chest
    base_skeleton[3] = [0.0, 0.50, 2.2]    # Neck
    base_skeleton[26] = [0.0, 0.35, 2.2]   # Head
    base_skeleton[5] = [-0.18, 0.52, 2.2]  # Shoulder Left
    base_skeleton[6] = [-0.26, 0.72, 2.15] # Elbow Left
    base_skeleton[7] = [-0.24, 0.88, 2.05] # Wrist Left
    base_skeleton[12] = [0.18, 0.52, 2.2]  # Shoulder Right
    base_skeleton[13] = [0.26, 0.72, 2.15] # Elbow Right
    base_skeleton[14] = [0.24, 0.88, 2.05] # Wrist Right
    base_skeleton[18] = [-0.10, 0.98, 2.2] # Hip Left
    base_skeleton[19] = [-0.12, 1.35, 2.22]# Knee Left
    base_skeleton[20] = [-0.13, 1.75, 2.25]# Ankle Left
    base_skeleton[22] = [0.10, 0.98, 2.2]  # Hip Right
    base_skeleton[23] = [0.12, 1.35, 2.22] # Knee Right
    base_skeleton[24] = [0.13, 1.75, 2.25] # Ankle Right

    total_clips = 0
    n_frames = 35

    for subj_idx in range(1, n_subjects + 1):
        subj_name = f"subject_{subj_idx:02d}"
        # Variabilidad física por sujeto (estatura +/- 10%, distancia a cámara)
        height_scale = 1.0 + np.random.uniform(-0.08, 0.08)
        base_depth = 2.2 + np.random.uniform(-0.25, 0.25)

        for act_idx, act_name in enumerate(ACTION_CLASSES):
            act_dir = os.path.join(output_dir, subj_name, act_name)
            os.makedirs(act_dir, exist_ok=True)

            for rep in range(reps_per_class):
                # Generar clip temporal de 35 frames
                clip_frames = np.zeros((n_frames, 32, 3), dtype=np.float32)
                speed_factor = np.random.uniform(0.85, 1.15)
                noise_scale = 0.005

                for t in range(n_frames):
                    progress = t / float(n_frames - 1)
                    # Curva de campana suave para el movimiento cinemático
                    phase = np.sin(np.pi * np.clip(progress * speed_factor, 0.0, 1.0))

                    frame = base_skeleton.copy() * height_scale
                    frame[:, 2] += (base_depth - 2.2)

                    # Ruido de sensor realista
                    frame += np.random.normal(0, noise_scale, frame.shape)

                    # Aplicar deformación cinemática según la clase
                    if act_name == "idle":
                        # Respiración sutil en reposo
                        frame[2, 1] += 0.008 * np.sin(progress * 4.0)
                        frame[7, 1] += 0.005 * np.cos(progress * 2.0)
                        frame[14, 1] += 0.005 * np.cos(progress * 2.0)

                    elif act_name == "punch_right":
                        # Brazo derecho extiende al frente (menor Z, menor Y)
                        frame[14, 2] -= 0.58 * phase
                        frame[14, 1] -= 0.22 * phase
                        frame[14, 0] += 0.04 * phase
                        frame[13, 2] -= 0.32 * phase

                    elif act_name == "punch_left":
                        # Brazo izquierdo extiende al frente
                        frame[7, 2] -= 0.58 * phase
                        frame[7, 1] -= 0.22 * phase
                        frame[7, 0] -= 0.04 * phase
                        frame[6, 2] -= 0.32 * phase

                    elif act_name == "kick_right":
                        # Pierna derecha se eleva y extiende
                        frame[24, 1] -= 0.62 * phase
                        frame[24, 2] -= 0.45 * phase
                        frame[23, 1] -= 0.38 * phase

                    elif act_name == "kick_left":
                        # Pierna izquierda se eleva y extiende
                        frame[20, 1] -= 0.62 * phase
                        frame[20, 2] -= 0.45 * phase
                        frame[19, 1] -= 0.38 * phase

                    elif act_name == "crouch":
                        # Pelvis y tronco descienden en Y (+Y en Kinect = hacia abajo)
                        frame[:, 1] += 0.38 * phase
                        frame[19, 0] -= 0.08 * phase  # Rodillas abren
                        frame[23, 0] += 0.08 * phase

                    elif act_name == "jump":
                        # Pelvis y cuerpo entero ascienden (-Y en Kinect = hacia arriba)
                        frame[:, 1] -= 0.46 * phase
                        frame[20, 1] -= 0.15 * phase
                        frame[24, 1] -= 0.15 * phase

                    elif act_name == "block":
                        # Bloqueo: antebrazos y muñecas se cruzan frente al pecho
                        frame[14, 0] -= 0.18 * phase  # Muñeca der hacia el centro
                        frame[7, 0] += 0.18 * phase   # Muñeca izq hacia el centro
                        frame[14, 1] -= 0.20 * phase  # A la altura del pecho
                        frame[7, 1] -= 0.20 * phase
                        frame[14, 2] -= 0.15 * phase
                        frame[7, 2] -= 0.15 * phase
                        frame[13, 0] -= 0.08 * phase  # Codos cierran
                        frame[6, 0] += 0.08 * phase

                    clip_frames[t] = frame

                # Guardar CSV del clip
                sample_id = int(time.time() * 1000) + total_clips
                csv_filename = f"sample_{sample_id:06d}.csv"
                csv_path = os.path.join(act_dir, csv_filename)

                # Aplanar las coordenadas de los 32 joints en 96 columnas
                flat_data = clip_frames.reshape((n_frames, 32 * 3))
                cols = [f"joint_{j}_{ax}" for j in range(32) for ax in ("x", "y", "z")]
                df_clip = pd.DataFrame(flat_data, columns=cols)
                df_clip.insert(0, "frame_idx", list(range(n_frames)))
                df_clip.insert(1, "subject_id", subj_name)
                df_clip.insert(2, "action_id", act_name)

                df_clip.to_csv(csv_path, index=False)
                total_clips += 1

    print(f"✅ Dataset sintético generado con éxito: {total_clips} clips en '{output_dir}'.")


def build_dataset_features(data_dir: str, processed_csv_path: str) -> pd.DataFrame:
    """
    Recorre recursivamente todos los clips CSV en dataset_raw/, extrae las 26 features cinemáticas
    y compila el dataset maestro tabular.
    """
    print(f"🔍 Escaneando clips en '{data_dir}'...")

    rows = []
    skipped = 0

    for root, _, files in os.walk(data_dir):
        csv_files = [f for f in files if f.endswith(".csv")]
        for f in csv_files:
            full_path = os.path.join(root, f)
            try:
                # Deducir sujeto y acción de la estructura de carpetas o metadatos
                # Formato Set:  data_dir/set_XX/subject_YY/action_name/sample_ZZZ.csv
                # Formato Flat: data_dir/subject_YY/action_name/sample_ZZZ.csv
                rel_parts = os.path.relpath(full_path, data_dir).replace("\\", "/").split("/")

                subject_id = "unknown"
                action_name = ""

                if len(rel_parts) >= 4 and rel_parts[0].startswith("set_"):
                    subject_id = rel_parts[1]
                    action_name = rel_parts[2]
                elif len(rel_parts) >= 3:
                    subject_id = rel_parts[0]
                    action_name = rel_parts[1]
                elif len(rel_parts) == 2:
                    action_name = rel_parts[0]

                # Cargar frames y extraer features
                frames = load_clip_from_csv(full_path)
                feats = extract_clip_features(frames, fps=30.0)

                # Si el CSV tenía columnas de metadatos, usarlas
                df_raw = pd.read_csv(full_path, nrows=1)
                if "action_id" in df_raw.columns:
                    action_name = str(df_raw["action_id"].iloc[0])
                if "subject_id" in df_raw.columns:
                    subject_id = str(df_raw["subject_id"].iloc[0])

                if action_name not in ACTION_NAME_TO_ID:
                    skipped += 1
                    continue

                row = {
                    "subject_id": subject_id,
                    "action_name": action_name,
                    "label": ACTION_NAME_TO_ID[action_name],
                    **feats
                }
                rows.append(row)

            except Exception as ex:
                skipped += 1
                # print(f"⚠️ Error procesando {full_path}: {ex}")

    if not rows:
        raise ValueError(f"No se encontraron clips válidos en '{data_dir}'.")

    df_processed = pd.DataFrame(rows)
    df_processed.to_csv(processed_csv_path, index=False)
    print(f"📊 Dataset procesado guardado en '{processed_csv_path}' con {len(df_processed)} muestras.")
    print(f"   (Clips omitidos por formato: {skipped})")
    print("\nDistribución por clase:")
    print(df_processed["action_name"].value_counts())

    return df_processed


def train_and_export(df: pd.DataFrame, output_onnx: str, unity_output: str = None):
    """
    Entrena el clasificador Random Forest supervisado, evalúa generalización inter-sujeto
    y exporta a formato ONNX.
    """
    X = df[FEATURE_NAMES].values.astype(np.float32)
    y = df["label"].values.astype(np.int64)
    subjects = df["subject_id"].values

    print("\n" + "=" * 65)
    print("🧠 ENTRENAMIENTO DEL CLASIFICADOR TABULAR SUPERVISADO")
    print("=" * 65)
    print(f"Total características: {X.shape[1]} cinemáticas")
    print(f"Total muestras: {X.shape[0]}")
    print(f"Sujetos únicos: {len(np.unique(subjects))}")

    # 1. Validación cruzada agrupada por sujeto (GroupKFold)
    # Evalúa si el modelo generaliza con personas completamente nuevas no vistas en entrenamiento
    n_splits = min(5, len(np.unique(subjects)))
    if n_splits > 1:
        gkf = GroupKFold(n_splits=n_splits)
        clf_eval = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)
        cv_scores = cross_val_score(clf_eval, X, y, groups=subjects, cv=gkf, scoring="accuracy")
        print(f"🎯 Exactitud Cross-Validation por Grupos (GroupKFold {n_splits} splits): {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%")
        print(f"   Scores individuales: {[round(s * 100, 1) for s in cv_scores]}%")

    # 2. Entrenamiento del modelo final sobre todo el dataset
    clf = RandomForestClassifier(
        n_estimators=120,
        max_depth=14,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X, y)

    # Evaluación sobre el conjunto de entrenamiento
    y_pred = clf.predict(X)
    print("\n📊 Reporte de Clasificación:")
    target_names = [ACTION_ID_TO_NAME[i] for i in sorted(np.unique(y))]
    print(classification_report(y, y_pred, target_names=target_names, digits=4))

    # Importancia de características
    importances = clf.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]
    print("🌟 Top 8 Características más influyentes:")
    for rank, idx in enumerate(sorted_idx[:8], 1):
        print(f"   {rank}. {FEATURE_NAMES[idx]:25s}: {importances[idx]*100:.2f}%")

    # 3. Guardar modelo Joblib para Python local
    joblib_path = output_onnx.replace(".onnx", ".joblib")
    joblib.dump(clf, joblib_path)
    print(f"\n💾 Modelo Scikit-Learn guardado en: {joblib_path}")

    # 4. Exportar a formato ONNX para Unity Sentis y Python ONNXRuntime
    if HAS_SKL2ONNX:
        print("📦 Convirtiendo modelo a formato ONNX (target_opset=12)...")
        initial_type = [('float_input', FloatTensorType([None, len(FEATURE_NAMES)]))]
        onnx_model = convert_sklearn(
            clf,
            initial_types=initial_type,
            target_opset=12,
            options={id(clf): {'zipmap': False}}  # Produce tensor plano de probabilidades sin zipmap
        )

        # Guardar en ruta local
        os.makedirs(os.path.dirname(os.path.abspath(output_onnx)), exist_ok=True)
        with open(output_onnx, "wb") as f:
            f.write(onnx_model.SerializeToString())
        print(f"✅ Modelo ONNX guardado exitosamente en: {output_onnx}")

        # Copiar a Unity Models si se especificó
        if unity_output:
            try:
                os.makedirs(os.path.dirname(os.path.abspath(unity_output)), exist_ok=True)
                with open(unity_output, "wb") as f:
                    f.write(onnx_model.SerializeToString())
                print(f"🚀 Modelo copiado a Assets de Unity: {unity_output}")
            except Exception as ex:
                print(f"⚠️ No se pudo copiar a Unity: {ex}")
    else:
        print("⚠️ skl2onnx no está instalado. Instálalo con: pip install skl2onnx")


def main():
    parser = argparse.ArgumentParser(description="SF3 Azure Kinect - Entrenador ML Cinemático")
    parser.add_argument("--data-dir", type=str, default=os.path.join(os.path.dirname(__file__), "dataset_raw"),
                        help="Directorio raíz con los clips brutos organizados por sujeto y acción")
    parser.add_argument("--processed-csv", type=str, default=os.path.join(os.path.dirname(__file__), "dataset_processed.csv"),
                        help="Ruta de guardado del dataset procesado con características tabulares")
    parser.add_argument("--output-onnx", type=str, default=os.path.join(os.path.dirname(__file__), "gesture_classifier.onnx"),
                        help="Ruta de exportación del modelo ONNX")
    parser.add_argument("--unity-output", type=str,
                        default=os.path.join(os.path.dirname(__file__), "..", "Assets", "StreetFighter3_ThirdStrike", "Models", "gesture_classifier.onnx"),
                        help="Ruta de destino en Unity Assets")
    parser.add_argument("--generate-synthetic", action="store_true",
                        help="Genera un dataset sintético para 10 personas antes de entrenar")
    parser.add_argument("--subjects", type=int, default=10,
                        help="Número de sujetos a generar si se usa --generate-synthetic")

    args = parser.parse_args()

    if args.generate_synthetic:
        generate_synthetic_dataset(args.data_dir, n_subjects=args.subjects, reps_per_class=20)

    if not os.path.exists(args.data_dir):
        print(f"❌ Error: El directorio '{args.data_dir}' no existe. Ejecuta con --generate-synthetic primero.")
        sys.exit(1)

    df = build_dataset_features(args.data_dir, args.processed_csv)
    train_and_export(df, args.output_onnx, args.unity_output)


if __name__ == "__main__":
    main()
