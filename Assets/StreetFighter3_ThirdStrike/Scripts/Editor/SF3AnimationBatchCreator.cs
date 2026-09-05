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

    [MenuItem("SF3 Tools/Auto-Populate Animator Controller from Selected Folder")]
    public static void PopulateAnimatorController()
    {
        Object selectedObj = Selection.activeObject;
        if (selectedObj == null)
        {
            EditorUtility.DisplayDialog("SF3 Animator Populator", "Por favor selecciona una carpeta de personaje (ej. 02_Ryu) en el Project view.", "OK");
            return;
        }

        string rootPath = AssetDatabase.GetAssetPath(selectedObj);
        if (!Directory.Exists(rootPath))
        {
            EditorUtility.DisplayDialog("Error", "El elemento seleccionado no es una carpeta.", "OK");
            return;
        }

        // Buscar el AnimatorController en la carpeta o subcarpetas
        string[] controllerGuids = AssetDatabase.FindAssets("t:AnimatorController", new[] { rootPath });
        if (controllerGuids.Length == 0)
        {
            EditorUtility.DisplayDialog("SF3 Animator Populator", $"No se encontró ningún AnimatorController en {rootPath}. Crea uno primero (ej. Ryu_Animator.controller).", "OK");
            return;
        }

        string controllerPath = AssetDatabase.GUIDToAssetPath(controllerGuids[0]);
        UnityEditor.Animations.AnimatorController controller = AssetDatabase.LoadAssetAtPath<UnityEditor.Animations.AnimatorController>(controllerPath);

        if (controller == null || controller.layers.Length == 0)
        {
            EditorUtility.DisplayDialog("Error", "No se pudo cargar la capa base del AnimatorController.", "OK");
            return;
        }

        UnityEditor.Animations.AnimatorStateMachine rootStateMachine = controller.layers[0].stateMachine;

        // Buscar todos los clips .anim
        string[] animGuids = AssetDatabase.FindAssets("t:AnimationClip", new[] { rootPath });
        if (animGuids.Length == 0)
        {
            EditorUtility.DisplayDialog("SF3 Animator Populator", "No se encontraron AnimationClips en la carpeta seleccionada.", "OK");
            return;
        }

        // Obtener nombres de estados ya existentes para no duplicar
        HashSet<string> existingStates = new HashSet<string>();
        foreach (var childState in rootStateMachine.states)
        {
            existingStates.Add(childState.state.name);
        }

        int addedCount = 0;
        int col = 0;
        int row = 0;
        int statesPerRow = 6;
        float spacingX = 220f;
        float spacingY = 70f;
        Vector3 basePosition = new Vector3(300, 0, 0);

        UnityEditor.Animations.AnimatorState defaultState = null;

        foreach (string guid in animGuids)
        {
            string animPath = AssetDatabase.GUIDToAssetPath(guid);
            AnimationClip clip = AssetDatabase.LoadAssetAtPath<AnimationClip>(animPath);
            if (clip == null) continue;

            string clipName = clip.name;

            if (existingStates.Contains(clipName))
            {
                // Si ya existe pero no tiene motion asignado, asignarlo
                foreach (var childState in rootStateMachine.states)
                {
                    if (childState.state.name == clipName && childState.state.motion == null)
                    {
                        childState.state.motion = clip;
                    }
                    if (clipName == "idle_stance")
                    {
                        defaultState = childState.state;
                    }
                }
                continue;
            }

            // Crear nuevo estado y posicionarlo ordenadamente
            Vector3 pos = basePosition + new Vector3(col * spacingX, row * spacingY, 0);
            UnityEditor.Animations.AnimatorState newState = rootStateMachine.AddState(clipName, pos);
            newState.motion = clip;
            existingStates.Add(clipName);
            addedCount++;

            if (clipName == "idle_stance")
            {
                defaultState = newState;
            }

            col++;
            if (col >= statesPerRow)
            {
                col = 0;
                row++;
            }
        }

        // Asignar idle_stance como default si existe
        if (defaultState != null)
        {
            rootStateMachine.defaultState = defaultState;
        }

        EditorUtility.SetDirty(controller);
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();

        EditorUtility.DisplayDialog("SF3 Animator Populator", 
            $"¡Completado con éxito!\n\nSe sincronizaron los AnimationClips con: '{controller.name}'.\n• Nuevos estados añadidos: {addedCount}\n• Total de estados en el Animator: {existingStates.Count}\n• Estado por defecto: {(defaultState != null ? defaultState.name : "N/A")}", 
            "Excelente");
    }
}
