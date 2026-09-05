using UnityEngine;
using UnityEditor;
using System.IO;
using System.Collections.Generic;

public class SF3AnimationBatchCreator : EditorWindow
{
    [MenuItem("SF3 Tools/Auto-Generate Animation Clips from Selected Folder")]
    public static void GenerateClips()
    {
        Object selectedObj = Selection.activeObject;
        if (selectedObj == null)
        {
            EditorUtility.DisplayDialog("SF3 Animation Generator", "Por favor selecciona una carpeta de personaje (ej. 02_Ryu) en el Project view.", "OK");
            return;
        }

        string rootPath = AssetDatabase.GetAssetPath(selectedObj);
        if (!Directory.Exists(rootPath))
        {
            EditorUtility.DisplayDialog("Error", "El elemento seleccionado no es una carpeta.", "OK");
            return;
        }

        // Escanear recursivamente todas las subcarpetas que contengan fotogramas PNG
        // Esto soporta la seleccion de la carpeta del personaje (ej. 02_Ryu), una categoria (ej. 01_Movement), o una accion individual
        List<string> dirsToProcess = new List<string>(Directory.GetDirectories(rootPath, "*", SearchOption.AllDirectories));
        if (Directory.GetFiles(rootPath, "*.png").Length > 0)
        {
            dirsToProcess.Add(rootPath);
        }

        int createdCount = 0;

        foreach (string dir in dirsToProcess)
        {
            string actionName = Path.GetFileName(dir);
            string[] pngFiles = Directory.GetFiles(dir, "*.png");
            if (pngFiles.Length == 0) continue;

            // Ordenar numericamente 0.png, 1.png...
            System.Array.Sort(pngFiles, (a, b) => {
                int na, nb;
                bool parsedA = int.TryParse(Path.GetFileNameWithoutExtension(a), out na);
                bool parsedB = int.TryParse(Path.GetFileNameWithoutExtension(b), out nb);
                if (parsedA && parsedB) return na.CompareTo(nb);
                return string.Compare(a, b);
            });

            AnimationClip clip = new AnimationClip();
            clip.frameRate = 14; // Tasa CPS-3 arcade nativa

            EditorCurveBinding curveBinding = new EditorCurveBinding();
            curveBinding.type = typeof(SpriteRenderer);
            curveBinding.path = "";
            curveBinding.propertyName = "m_Sprite";

            ObjectReferenceKeyframe[] keyframes = new ObjectReferenceKeyframe[pngFiles.Length];
            for (int i = 0; i < pngFiles.Length; i++)
            {
                Sprite sprite = AssetDatabase.LoadAssetAtPath<Sprite>(pngFiles[i]);
                keyframes[i] = new ObjectReferenceKeyframe
                {
                    time = i / 14f,
                    value = sprite
                };
            }

            AnimationUtility.SetObjectReferenceCurve(clip, curveBinding, keyframes);

            // Loop si es reposo o caminar
            if (actionName.Contains("stance") || actionName.Contains("idle") || actionName.Contains("walk"))
            {
                AnimationClipSettings settings = AnimationUtility.GetAnimationClipSettings(clip);
                settings.loopTime = true;
                AnimationUtility.SetAnimationClipSettings(clip, settings);
            }

            string clipPath = Path.Combine(dir, actionName + ".anim");
            AssetDatabase.CreateAsset(clip, clipPath);
            createdCount++;
        }

        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        EditorUtility.DisplayDialog("SF3 Animation Generator", $"¡Éxito! Se generaron {createdCount} AnimationClips listos para usar en: {rootPath}", "Genial");
    }
}
