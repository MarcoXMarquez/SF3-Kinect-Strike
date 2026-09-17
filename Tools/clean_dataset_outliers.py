"""
Street Fighter III: 3rd Strike - Kinect Dataset Kinematic Outlier Cleaner
Detecta y limpia anomalías, discontinuidades de tracking y glitches de profundidad ToF,
preservando la dinámica de combate y estabilizando zonas constantes (reposo/guardia).
"""

import os
import sys
import argparse
import glob
import numpy as np
import pandas as pd

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Importar filtro One-Euro local
sys.path.append(os.path.dirname(__file__))
from gesture_feature_extractor import one_euro_filter_3d_clip, load_clip_from_csv


def clean_clip_joints(
    coords_raw: np.ndarray,
    fps: float = 30.0,
    max_step_dist: float = 0.25,
    mad_multiplier: float = 3.2
) -> tuple:
    """
    Limpia un clip de 35 frames (N, 32, 3) aplicando:
    1. Detección de picos espurios e interpolación con vecinos válidos.
    2. Filtrado adaptativo One-Euro para estabilizar componentes constantes.
    """
    n_frames, n_joints, _ = coords_raw.shape
    cleaned = coords_raw.copy()
    
    total_spikes = 0
    affected_joints = set()
    
    # 1. Detección por articulación y coordenada
    for j in range(n_joints):
        for k in range(3):
            signal = coords_raw[:, j, k].copy()
            is_bad = np.zeros(n_frames, dtype=bool)
            
            # Ventana móvil para estimación de tendencia y MAD
            w = 5
            half_w = w // 2
            for t in range(n_frames):
                i_min = max(0, t - half_w)
                i_max = min(n_frames, t + half_w + 1)
                window = signal[i_min:i_max]
                med = np.median(window)
                mad = np.median(np.abs(window - med)) + 1e-6
                
                d_prev = np.abs(signal[t] - signal[t - 1]) if t > 0 else 0.0
                d_next = np.abs(signal[t + 1] - signal[t]) if t < n_frames - 1 else 0.0
                
                # Caso 1: Pico aislado que salta y regresa bruscamente (reversión de signo)
                is_reversal = (
                    t > 0 and t < n_frames - 1 and
                    d_prev > max_step_dist and d_next > max_step_dist and
                    np.sign(signal[t] - signal[t - 1]) != np.sign(signal[t + 1] - signal[t])
                )
                
                # Caso 2: Desviación excesiva respecto a la mediana local con salto brusco
                is_hampel_outlier = (
                    np.abs(signal[t] - med) > (mad_multiplier * 1.4826 * mad) and
                    (d_prev > max_step_dist or d_next > max_step_dist)
                )
                
                # Caso 3: Salto anatómicamente imposible (> 0.45m en 33ms = > 13.5 m/s)
                is_impossible_jump = (d_prev > 0.45 or d_next > 0.45)
                
                if is_reversal or is_hampel_outlier or is_impossible_jump:
                    is_bad[t] = True
            
            # Si hay frames corruptos, interpolar con los frames sanos
            bad_indices = np.where(is_bad)[0]
            good_indices = np.where(~is_bad)[0]
            
            if len(bad_indices) > 0 and len(good_indices) >= 2:
                total_spikes += len(bad_indices)
                affected_joints.add(j)
                interp_vals = np.interp(bad_indices, good_indices, signal[good_indices])
                signal[bad_indices] = interp_vals
                cleaned[:, j, k] = signal

    # 2. Suavizado adaptativo One-Euro (preserva velocidad alta, estabiliza reposo)
    cleaned_final = one_euro_filter_3d_clip(cleaned, fps=fps, min_cutoff=1.1, beta=0.007)
    
    stats = {
        "spikes_interpolated": total_spikes,
        "joints_affected": sorted(list(affected_joints))
    }
    return cleaned_final, stats


def preview_file(csv_path: str):
    """
    Ejecuta el análisis comparativo (ANTES vs DESPUÉS) en un archivo específico.
    """
    print("=" * 75)
    print(f"🔬 PREVIEW DE LIMPIEZA BIOMECÁNICA: {os.path.basename(csv_path)}")
    print("=" * 75)
    
    df = pd.read_csv(csv_path)
    joint_cols = [c for c in df.columns if c.startswith("joint_")]
    coords_raw = df[joint_cols].values.reshape((len(df), 32, 3))
    
    coords_clean, stats = clean_clip_joints(coords_raw)
    
    dt = 1.0 / 30.0
    # Saltos máximos cuadro a cuadro
    diff_orig = np.linalg.norm(np.diff(coords_raw, axis=0), axis=-1)
    diff_clean = np.linalg.norm(np.diff(coords_clean, axis=0), axis=-1)
    
    max_orig_jump = np.max(diff_orig)
    max_clean_jump = np.max(diff_clean)
    
    # Articulación con mayor salto
    max_frame_orig, max_joint_orig = np.unravel_index(np.argmax(diff_orig), diff_orig.shape)
    
    print(f"📊 Puntos anómalos detectados y corregidos : {stats['spikes_interpolated']}")
    print(f"🦴 Articulaciones corregidas                : {stats['joints_affected']}")
    print(f"⚡ Salto máximo instantáneo ANTES           : {max_orig_jump:.3f} m (Frame {max_frame_orig}, Joint {max_joint_orig})")
    print(f"⚡ Salto máximo instantáneo DESPUÉS         : {max_clean_jump:.3f} m")
    print(f"📉 Reducción de discontinuidad              : {((max_orig_jump - max_clean_jump)/max_orig_jump)*100:.1f}%\n")
    
    # Mostrar tabla comparativa de frames alrededor del salto crítico
    start_f = max(0, max_frame_orig - 3)
    end_f = min(len(df), max_frame_orig + 4)
    
    comp_rows = []
    for f in range(start_f, end_f):
        comp_rows.append({
            "Frame": f,
            "X_Antes": round(coords_raw[f, max_joint_orig, 0], 3),
            "X_Limpio": round(coords_clean[f, max_joint_orig, 0], 3),
            "Y_Antes": round(coords_raw[f, max_joint_orig, 1], 3),
            "Y_Limpio": round(coords_clean[f, max_joint_orig, 1], 3),
            "Z_Antes": round(coords_raw[f, max_joint_orig, 2], 3),
            "Z_Limpio": round(coords_clean[f, max_joint_orig, 2], 3)
        })
    df_comp = pd.DataFrame(comp_rows)
    print(f"Tabla de Coordenadas de Articulación {max_joint_orig} (Frames {start_f} a {end_f - 1}):")
    print(df_comp.to_string(index=False))
    print("=" * 75)


def clean_all_dataset(input_dir: str, output_dir: str):
    """
    Procesa todos los archivos CSV de input_dir y guarda las versiones
    limpias en output_dir manteniendo intacta la estructura de carpetas y metadatos.
    """
    print("\n" + "=" * 75)
    print(f"🚀 INICIANDO LIMPIEZA DEL DATASET: '{input_dir}' -> '{output_dir}'")
    print("=" * 75)
    
    csv_files = glob.glob(os.path.join(input_dir, "**", "*.csv"), recursive=True)
    if not csv_files:
        print(f"⚠️ No se encontraron archivos CSV en '{input_dir}'")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Copiar también subject_profiles.json si existe
    profiles_src = os.path.join(input_dir, "subject_profiles.json")
    if os.path.exists(profiles_src):
        import shutil
        shutil.copy2(profiles_src, os.path.join(output_dir, "subject_profiles.json"))
        print(f"📋 Copiado 'subject_profiles.json' a '{output_dir}'")
    
    processed_count = 0
    total_spikes_fixed = 0
    
    for p in csv_files:
        rel_path = os.path.relpath(p, input_dir)
        dest_path = os.path.join(output_dir, rel_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        df = pd.read_csv(p)
        joint_cols = [c for c in df.columns if c.startswith("joint_")]
        meta_cols = [c for c in df.columns if not c.startswith("joint_")]
        
        coords_raw = df[joint_cols].values.reshape((len(df), 32, 3))
        coords_clean, stats = clean_clip_joints(coords_raw)
        
        # Aplanar coordenadas limpias (35, 96)
        flat_clean = coords_clean.reshape((len(df), 32 * 3))
        df_clean_data = pd.DataFrame(flat_clean, columns=joint_cols)
        
        # Concatenar metadatos intactos al inicio
        df_final = pd.concat([df[meta_cols], df_clean_data], axis=1)
        df_final.to_csv(dest_path, index=False)
        
        processed_count += 1
        total_spikes_fixed += stats["spikes_interpolated"]
    
    print(f"✅ Limpieza finalizada con éxito:")
    print(f"   - Archivos procesados y guardados : {processed_count} / {len(csv_files)}")
    print(f"   - Puntos anómalos corregidos     : {total_spikes_fixed}")
    print(f"   - Destino seguro                 : {output_dir}")
    print("=" * 75)


def compare_datasets(raw_dir: str, cleaned_dir: str):
    """
    Compara ambos datasets a nivel global para verificar la mejora estadística
    y asegurar que no se haya degradado ninguna dinámica legítima.
    """
    print("\n" + "=" * 75)
    print(f"🔍 AUDITORÍA DE REVISIÓN GLOBAL: '{raw_dir}' vs '{cleaned_dir}'")
    print("=" * 75)
    
    raw_files = glob.glob(os.path.join(raw_dir, "**", "*.csv"), recursive=True)
    cleaned_files = glob.glob(os.path.join(cleaned_dir, "**", "*.csv"), recursive=True)
    
    print(f"Archivos originales: {len(raw_files)} | Archivos limpios: {len(cleaned_files)}")
    
    raw_jumps = []
    clean_jumps = []
    raw_spikes_over_30cm = 0
    clean_spikes_over_30cm = 0
    
    for p_raw in raw_files:
        rel = os.path.relpath(p_raw, raw_dir)
        p_clean = os.path.join(cleaned_dir, rel)
        if not os.path.exists(p_clean):
            continue
            
        df_r = pd.read_csv(p_raw)
        df_c = pd.read_csv(p_clean)
        
        j_cols = [c for c in df_r.columns if c.startswith("joint_")]
        c_r = df_r[j_cols].values.reshape((len(df_r), 32, 3))
        c_c = df_c[j_cols].values.reshape((len(df_c), 32, 3))
        
        diff_r = np.linalg.norm(np.diff(c_r, axis=0), axis=-1)
        diff_c = np.linalg.norm(np.diff(c_c, axis=0), axis=-1)
        
        raw_jumps.append(np.max(diff_r))
        clean_jumps.append(np.max(diff_c))
        
        raw_spikes_over_30cm += int(np.sum(diff_r > 0.30))
        clean_spikes_over_30cm += int(np.sum(diff_c > 0.30))
    
    print("\n--- COMPARATIVA DE DISCONTINUIDADES TEMPORALES (SALTOS > 30 CM) ---")
    print(f"Saltos espurios (> 30 cm en 33ms) en Raw     : {raw_spikes_over_30cm}")
    print(f"Saltos espurios (> 30 cm en 33ms) en Cleaned : {clean_spikes_over_30cm}")
    print(f"Reducción total de anomalías                 : {((raw_spikes_over_30cm - clean_spikes_over_30cm)/max(1, raw_spikes_over_30cm))*100:.1f}%\n")
    
    print("--- ESTADÍSTICAS DE SALTO MÁXIMO POR CLIP (EN METROS) ---")
    print(f"Salto máximo promedio por clip (Raw)     : {np.mean(raw_jumps):.3f} m")
    print(f"Salto máximo promedio por clip (Cleaned) : {np.mean(clean_jumps):.3f} m")
    print(f"Salto máximo absoluto del dataset (Raw)  : {np.max(raw_jumps):.3f} m")
    print(f"Salto máximo absoluto (Cleaned)          : {np.max(clean_jumps):.3f} m")
    print("=" * 75)


def main():
    parser = argparse.ArgumentParser(description="Limpiador de Outliers Cinemáticos de Kinect")
    parser.add_argument("--preview", type=str, default="", help="Ruta a un archivo CSV para previsualizar antes vs después")
    parser.add_argument("--clean", action="store_true", help="Ejecutar limpieza completa de dataset_raw a dataset_cleaned")
    parser.add_argument("--compare", action="store_true", help="Auditar y comparar dataset_raw vs dataset_cleaned")
    parser.add_argument("--input-dir", type=str, default=os.path.join(os.path.dirname(__file__), "dataset_raw"))
    parser.add_argument("--output-dir", type=str, default=os.path.join(os.path.dirname(__file__), "dataset_cleaned"))
    args = parser.parse_args()
    
    if args.preview:
        preview_file(args.preview)
    elif args.clean:
        clean_all_dataset(args.input_dir, args.output_dir)
    elif args.compare:
        compare_datasets(args.input_dir, args.output_dir)
    else:
        # Por defecto hacer el preview del archivo con mayor pico
        sample_bad = os.path.join(args.input_dir, "set_01", "subject_08", "kick_right", "sample_1789485117495.csv")
        if os.path.exists(sample_bad):
            preview_file(sample_bad)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
