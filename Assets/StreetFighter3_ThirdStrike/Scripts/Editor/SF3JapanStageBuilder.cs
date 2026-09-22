using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

[InitializeOnLoad]
public static class SF3JapanStageBuilder
{
    private const string StageFolder = "Assets/StreetFighter3_ThirdStrike/Stages/Japan_Ryu";
    private const string PrefabPath = "Assets/StreetFighter3_ThirdStrike/Prefabs/Stage_Japan.prefab";
    private const string SandboxPath = "Assets/StreetFighter3_ThirdStrike/Scenes/Sandbox_Sebas.unity";
    private const string ShaderPath = "Assets/StreetFighter3_ThirdStrike/Shaders/SF3ChromaKeySprite.shader";
    private const string MaterialPath = "Assets/StreetFighter3_ThirdStrike/Materials/Stage_ChromaKey.mat";

    private static readonly string[] RequiredSortingLayers =
    {
        "Background_Sky",
        "Background_Distant",
        "Midground_Temple",
        "Floor_Ground",
        "Fighters",
        "Foreground_Props"
    };

    static SF3JapanStageBuilder()
    {
        EditorApplication.delayCall += BuildIfMissing;
    }

    private static void BuildIfMissing()
    {
        GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath);
        if (prefab == null || AssetDatabase.LoadAssetAtPath<Material>(MaterialPath) == null)
        {
            BuildJapanStage();
        }
    }

    [MenuItem("SF3 Tools/Build Japan Stage (Sebas Task 4)")]
    public static void BuildJapanStage()
    {
        EnsureSortingLayers();
        ConfigureStageSprites();
        Material stageMaterial = GetOrCreateStageMaterial();

        GameObject stageRoot = new GameObject("Stage_Japan");
        try
        {
            Transform sky = CreateLayer(stageRoot.transform, "Sky", "ryu-sky.png", "Background_Sky", 0,
                new Vector3(0f, 1f, 0f), new Vector3(1.8f, 1.6f, 1f), stageMaterial);
            Transform distant = CreateLayer(stageRoot.transform, "Distant_Mountains", "ryu01.png", "Background_Distant", 0,
                new Vector3(0f, 1f, 0f), new Vector3(1.25f, 1.6f, 1f), stageMaterial);
            Transform temple = CreateLayer(stageRoot.transform, "Suzaku_Castle", "ryu-temple.png", "Midground_Temple", 0,
                new Vector3(0f, 1.2f, 0f), Vector3.one, stageMaterial);
            Transform floor = CreateLayer(stageRoot.transform, "Battle_Ground", "ryu03.png", "Floor_Ground", 0,
                new Vector3(0f, 1.08f, 0f), new Vector3(1.18f, 1f, 1f), stageMaterial);
            Transform foreground = CreateLayer(stageRoot.transform, "Foreground_Roof", "ryu-roof.png", "Foreground_Props", 0,
                new Vector3(0f, 3.35f, 0f), new Vector3(1.35f, 1.2f, 1f), stageMaterial);

            GameObject ground = new GameObject("Ground_Collider");
            ground.transform.SetParent(stageRoot.transform, false);
            ground.transform.localPosition = new Vector3(0f, -0.1f, 0f);
            BoxCollider2D collider = ground.AddComponent<BoxCollider2D>();
            collider.size = new Vector2(12f, 0.2f);

            ParallaxBackground parallax = stageRoot.AddComponent<ParallaxBackground>();
            parallax.layers = new[]
            {
                Layer(sky, 0.10f, 0.02f),
                Layer(distant, 0.25f, 0.04f),
                Layer(temple, 0.40f, 0.06f),
                Layer(floor, 1.00f, 0f),
                Layer(foreground, 0.80f, 0.08f)
            };

            GameObject prefab = PrefabUtility.SaveAsPrefabAsset(stageRoot, PrefabPath);
            AddStageToSandbox(prefab);

            Selection.activeObject = prefab;
            EditorGUIUtility.PingObject(prefab);
            Debug.Log("[SF3] Tarea #4 lista: Stage_Japan.prefab, Sorting Layers, Parallax y suelo Y=0 creados.");
        }
        finally
        {
            Object.DestroyImmediate(stageRoot);
        }
    }

    private static ParallaxBackground.ParallaxLayer Layer(Transform transform, float factorX, float factorY)
    {
        return new ParallaxBackground.ParallaxLayer
        {
            layerTransform = transform,
            parallaxFactorX = factorX,
            parallaxFactorY = factorY
        };
    }

    private static Transform CreateLayer(
        Transform parent,
        string objectName,
        string spriteFile,
        string sortingLayer,
        int sortingOrder,
        Vector3 position,
        Vector3 scale,
        Material material)
    {
        Sprite sprite = AssetDatabase.LoadAssetAtPath<Sprite>($"{StageFolder}/{spriteFile}");
        if (sprite == null)
        {
            throw new MissingReferenceException($"No se encontro el sprite {spriteFile}.");
        }

        GameObject layerObject = new GameObject(objectName);
        layerObject.transform.SetParent(parent, false);
        layerObject.transform.localPosition = position;
        layerObject.transform.localScale = scale;

        SpriteRenderer renderer = layerObject.AddComponent<SpriteRenderer>();
        renderer.sprite = sprite;
        renderer.sharedMaterial = material;
        renderer.sortingLayerName = sortingLayer;
        renderer.sortingOrder = sortingOrder;
        return layerObject.transform;
    }

    private static Material GetOrCreateStageMaterial()
    {
        AssetDatabase.ImportAsset(ShaderPath, ImportAssetOptions.ForceSynchronousImport);
        Shader shader = AssetDatabase.LoadAssetAtPath<Shader>(ShaderPath);
        if (shader == null)
        {
            throw new MissingReferenceException("No se pudo importar el shader SF3/ChromaKeySprite.");
        }

        Material material = AssetDatabase.LoadAssetAtPath<Material>(MaterialPath);
        if (material == null)
        {
            material = new Material(shader);
            AssetDatabase.CreateAsset(material, MaterialPath);
        }
        else
        {
            material.shader = shader;
        }

        material.SetFloat("_Cutoff", 0.22f);
        EditorUtility.SetDirty(material);
        AssetDatabase.SaveAssets();
        return material;
    }

    private static void ConfigureStageSprites()
    {
        string[] spriteFiles = { "ryu-sky.png", "ryu01.png", "ryu-temple.png", "ryu03.png", "ryu-roof.png" };
        foreach (string spriteFile in spriteFiles)
        {
            string path = $"{StageFolder}/{spriteFile}";
            TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
            if (importer == null)
            {
                throw new MissingReferenceException($"No se encontro el importador de {spriteFile}.");
            }

            importer.textureType = TextureImporterType.Sprite;
            importer.spriteImportMode = SpriteImportMode.Single;
            importer.spritePixelsPerUnit = 100f;
            importer.filterMode = FilterMode.Point;
            importer.mipmapEnabled = false;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.alphaIsTransparency = true;
            importer.SaveAndReimport();
        }
    }

    private static void EnsureSortingLayers()
    {
        Object tagManager = AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/TagManager.asset")[0];
        SerializedObject serializedTagManager = new SerializedObject(tagManager);
        SerializedProperty layers = serializedTagManager.FindProperty("m_SortingLayers");

        Dictionary<string, int> existingIds = new Dictionary<string, int>();
        List<string> extraLayers = new List<string>();
        for (int i = 0; i < layers.arraySize; i++)
        {
            SerializedProperty layer = layers.GetArrayElementAtIndex(i);
            string name = layer.FindPropertyRelative("name").stringValue;
            int id = layer.FindPropertyRelative("uniqueID").intValue;
            existingIds[name] = id;
            if (name != "Default" && !RequiredSortingLayers.Contains(name))
            {
                extraLayers.Add(name);
            }
        }

        List<string> orderedLayers = new List<string> { "Default" };
        orderedLayers.AddRange(RequiredSortingLayers);
        orderedLayers.AddRange(extraLayers);

        HashSet<int> usedIds = new HashSet<int>(existingIds.Values);
        layers.arraySize = orderedLayers.Count;
        for (int i = 0; i < orderedLayers.Count; i++)
        {
            string name = orderedLayers[i];
            SerializedProperty layer = layers.GetArrayElementAtIndex(i);
            layer.FindPropertyRelative("name").stringValue = name;
            layer.FindPropertyRelative("locked").boolValue = false;

            int id;
            if (name == "Default")
            {
                id = 0;
            }
            else if (!existingIds.TryGetValue(name, out id))
            {
                do
                {
                    id = Random.Range(1, int.MaxValue);
                }
                while (!usedIds.Add(id));
            }

            layer.FindPropertyRelative("uniqueID").intValue = id;
        }

        serializedTagManager.ApplyModifiedPropertiesWithoutUndo();
        EditorUtility.SetDirty(tagManager);
        AssetDatabase.SaveAssets();
    }

    private static void AddStageToSandbox(GameObject prefab)
    {
        Scene sandbox = SceneManager.GetSceneByPath(SandboxPath);
        bool openedForBuild = !sandbox.IsValid() || !sandbox.isLoaded;
        if (openedForBuild)
        {
            sandbox = EditorSceneManager.OpenScene(SandboxPath, OpenSceneMode.Additive);
        }

        foreach (GameObject root in sandbox.GetRootGameObjects())
        {
            if (root.name == "Ground_Test" || root.name == "Stage_Japan")
            {
                Object.DestroyImmediate(root);
            }
        }

        GameObject instance = PrefabUtility.InstantiatePrefab(prefab, sandbox) as GameObject;
        if (instance != null)
        {
            instance.transform.position = Vector3.zero;
        }

        Camera sandboxCamera = sandbox.GetRootGameObjects()
            .SelectMany(root => root.GetComponentsInChildren<Camera>(true))
            .FirstOrDefault(camera => camera.CompareTag("MainCamera"));
        if (sandboxCamera != null)
        {
            sandboxCamera.transform.position = new Vector3(0f, 1.65f, -10f);
            sandboxCamera.orthographic = true;
            sandboxCamera.orthographicSize = 2.3f;
        }

        EditorSceneManager.MarkSceneDirty(sandbox);
        EditorSceneManager.SaveScene(sandbox);

        if (openedForBuild)
        {
            EditorSceneManager.CloseScene(sandbox, true);
        }
    }

}
