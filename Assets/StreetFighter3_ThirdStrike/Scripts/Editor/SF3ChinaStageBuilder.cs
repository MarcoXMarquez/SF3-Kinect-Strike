using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

[InitializeOnLoad]
public static class SF3ChinaStageBuilder
{
    private const string StageFolder = "Assets/StreetFighter3_ThirdStrike/Stages/China_ChunLi";
    private const string PrefabPath = "Assets/StreetFighter3_ThirdStrike/Prefabs/Stage_China.prefab";
    private const string SandboxPath = "Assets/StreetFighter3_ThirdStrike/Scenes/Sandbox_China.unity";
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

    static SF3ChinaStageBuilder()
    {
        EditorApplication.delayCall += BuildIfMissing;
    }

    private static void BuildIfMissing()
    {
        GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath);
        if (prefab == null)
        {
            BuildChinaStage();
        }
    }

    [MenuItem("Kinet Strike Tools/Build China Stage (Crowded Street)")]
    [MenuItem("SF3 Tools/Build China Stage (Crowded Street)")]
    public static void BuildChinaStage()
    {
        EnsureSortingLayers();
        ConfigureStageSprites();
        Material stageMaterial = GetOrCreateStageMaterial();

        GameObject stageRoot = new GameObject("Stage_China");
        try
        {
            // 1. Capa Distante: Río, Pagodas Tradicionales y Cielo
            Transform distant = CreateLayer(
                stageRoot.transform,
                "Distant_Canal_Sky",
                $"{StageFolder}/chun-li-bg-layer2.png",
                "Background_Distant",
                0,
                new Vector3(0f, 1.15f, 0f),
                new Vector3(1.22f, 1.22f, 1f),
                stageMaterial);

            // 2. Capa Principal: Mercado Chino, Puente y Faroles
            Transform street = CreateLayer(
                stageRoot.transform,
                "Crowded_Street",
                $"{StageFolder}/chun-li-bg-layer1.png",
                "Floor_Ground",
                0,
                new Vector3(0f, 1.05f, 0f),
                new Vector3(1.15f, 1.15f, 1f),
                stageMaterial);

            // 3. Props y Espectadores Vivos Animados a 14 FPS (CPS-3)
            CreateAnimatedProp(
                street,
                "Awning_Market",
                $"{StageFolder}/animated_props/awning",
                "Foreground_Props",
                1,
                new Vector3(-2.8f, 0.78f, 0f),
                new Vector3(1.2f, 1.2f, 1f),
                14f);

            CreateAnimatedProp(
                street,
                "Spectator_Person1",
                $"{StageFolder}/animated_props/person1",
                "Floor_Ground",
                1,
                new Vector3(2.4f, -0.52f, 0f),
                new Vector3(1.1f, 1.1f, 1f),
                12f);

            CreateAnimatedProp(
                street,
                "Spectator_Person2",
                $"{StageFolder}/animated_props/person2",
                "Floor_Ground",
                1,
                new Vector3(3.2f, -0.55f, 0f),
                new Vector3(1.1f, 1.1f, 1f),
                12f);

            CreateAnimatedProp(
                street,
                "Bamboo_Steamer",
                $"{StageFolder}/animated_props/bamboo",
                "Floor_Ground",
                1,
                new Vector3(-3.5f, -0.05f, 0f),
                new Vector3(1f, 1f, 1f),
                10f);

            // 4. Colisionador Físico de Suelo (Superficie exacta Y=0)
            GameObject ground = new GameObject("Ground_Collider");
            ground.transform.SetParent(stageRoot.transform, false);
            ground.transform.localPosition = new Vector3(0f, -0.1f, 0f);
            BoxCollider2D floorCollider = ground.AddComponent<BoxCollider2D>();
            floorCollider.size = new Vector2(14f, 0.2f);

            // 5. Paredes Invisibles Laterales (Límites de Arena)
            GameObject leftWall = new GameObject("Wall_Left");
            leftWall.transform.SetParent(stageRoot.transform, false);
            leftWall.transform.localPosition = new Vector3(-6.5f, 2f, 0f);
            BoxCollider2D leftCol = leftWall.AddComponent<BoxCollider2D>();
            leftCol.size = new Vector2(0.5f, 6f);

            GameObject rightWall = new GameObject("Wall_Right");
            rightWall.transform.SetParent(stageRoot.transform, false);
            rightWall.transform.localPosition = new Vector3(6.5f, 2f, 0f);
            BoxCollider2D rightCol = rightWall.AddComponent<BoxCollider2D>();
            rightCol.size = new Vector2(0.5f, 6f);

            // 6. Efecto Parallax Desacoplado
            ParallaxBackground parallax = stageRoot.AddComponent<ParallaxBackground>();
            parallax.layers = new[]
            {
                new ParallaxBackground.ParallaxLayer
                {
                    layerTransform = distant,
                    parallaxFactorX = 0.25f,
                    parallaxFactorY = 0.04f
                },
                new ParallaxBackground.ParallaxLayer
                {
                    layerTransform = street,
                    parallaxFactorX = 1.00f,
                    parallaxFactorY = 0f
                }
            };

            // 7. Guardar como Prefab Oficial Reutilizable
            string prefabDir = Path.GetDirectoryName(PrefabPath);
            if (!Directory.Exists(prefabDir)) Directory.CreateDirectory(prefabDir);

            GameObject prefab = PrefabUtility.SaveAsPrefabAsset(stageRoot, PrefabPath);
            SetupChinaSandboxScene(prefab);

            Selection.activeObject = prefab;
            EditorGUIUtility.PingObject(prefab);
            Debug.Log("🏮 [KINET STRIKE] Escenario China (Stage_China.prefab) montado exitosamente con Parallax, Props a 14 FPS y límites de arena.");
        }
        finally
        {
            Object.DestroyImmediate(stageRoot);
        }
    }

    private static Transform CreateLayer(
        Transform parent,
        string objectName,
        string spritePath,
        string sortingLayer,
        int sortingOrder,
        Vector3 position,
        Vector3 scale,
        Material material)
    {
        Sprite sprite = AssetDatabase.LoadAssetAtPath<Sprite>(spritePath);
        if (sprite == null)
        {
            throw new MissingReferenceException($"No se encontró el sprite en {spritePath}.");
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

    private static void CreateAnimatedProp(
        Transform parent,
        string objectName,
        string framesFolder,
        string sortingLayer,
        int sortingOrder,
        Vector3 position,
        Vector3 scale,
        float fps)
    {
        string fullPath = Path.Combine(Application.dataPath, framesFolder.Replace("Assets/", ""));
        if (!Directory.Exists(fullPath)) return;

        string[] pngFiles = Directory.GetFiles(fullPath, "*.png")
            .OrderBy(f =>
            {
                string stem = Path.GetFileNameWithoutExtension(f);
                return int.TryParse(stem, out int val) ? val : 9999;
            })
            .ToArray();

        List<Sprite> sprites = new List<Sprite>();
        foreach (string file in pngFiles)
        {
            string relPath = "Assets" + file.Substring(Application.dataPath.Length).Replace('\\', '/');
            Sprite s = AssetDatabase.LoadAssetAtPath<Sprite>(relPath);
            if (s != null) sprites.Add(s);
        }

        if (sprites.Count == 0) return;

        GameObject propObj = new GameObject(objectName);
        propObj.transform.SetParent(parent, false);
        propObj.transform.localPosition = position;
        propObj.transform.localScale = scale;

        SpriteRenderer renderer = propObj.AddComponent<SpriteRenderer>();
        renderer.sprite = sprites[0];
        renderer.sortingLayerName = sortingLayer;
        renderer.sortingOrder = sortingOrder;

        AnimatedSpriteProp anim = propObj.AddComponent<AnimatedSpriteProp>();
        anim.Frames = sprites.ToArray();
        anim.FrameRate = fps;
    }

    private static Material GetOrCreateStageMaterial()
    {
        Shader shader = AssetDatabase.LoadAssetAtPath<Shader>(ShaderPath);
        if (shader == null)
        {
            shader = Shader.Find("SF3/ChromaKeySprite");
        }

        Material material = AssetDatabase.LoadAssetAtPath<Material>(MaterialPath);
        if (material == null && shader != null)
        {
            material = new Material(shader);
            AssetDatabase.CreateAsset(material, MaterialPath);
        }

        if (material != null)
        {
            material.SetFloat("_Cutoff", 0.22f);
            EditorUtility.SetDirty(material);
            AssetDatabase.SaveAssets();
        }

        return material;
    }

    private static void ConfigureStageSprites()
    {
        string[] spritePaths =
        {
            $"{StageFolder}/chun-li-bg-layer1.png",
            $"{StageFolder}/chun-li-bg-layer2.png"
        };

        foreach (string path in spritePaths)
        {
            TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
            if (importer == null) continue;

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

    private static void SetupChinaSandboxScene(GameObject stagePrefab)
    {
        Scene chinaScene;
        bool exists = File.Exists(SandboxPath);
        if (exists)
        {
            chinaScene = EditorSceneManager.OpenScene(SandboxPath, OpenSceneMode.Additive);
        }
        else
        {
            chinaScene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive);
        }

        foreach (GameObject root in chinaScene.GetRootGameObjects())
        {
            Object.DestroyImmediate(root);
        }

        // Cámara Ortográfica Arcade 2.3f
        GameObject camObj = new GameObject("Main Camera");
        camObj.tag = "MainCamera";
        SceneManager.MoveGameObjectToScene(camObj, chinaScene);
        Camera cam = camObj.AddComponent<Camera>();
        cam.orthographic = true;
        cam.orthographicSize = 2.3f;
        camObj.transform.position = new Vector3(0f, 1.65f, -10f);
        camObj.AddComponent<AudioListener>();

        // Parallax Tester para navegación horizontal
        StageParallaxTester tester = camObj.AddComponent<StageParallaxTester>();

        // JapanDuel (Motor de Combate Ken vs Ryu / Chun-Li con BGM de China)
        JapanDuel duel = camObj.AddComponent<JapanDuel>();

        // Instanciar Prefab del Escenario China
        GameObject stageInstance = PrefabUtility.InstantiatePrefab(stagePrefab, chinaScene) as GameObject;
        if (stageInstance != null)
        {
            stageInstance.transform.position = Vector3.zero;
        }

        EditorSceneManager.SaveScene(chinaScene, SandboxPath);
        EditorSceneManager.CloseScene(chinaScene, true);

        // Registrar en EditorBuildSettings
        var scenes = EditorBuildSettings.scenes.ToList();
        if (!scenes.Any(s => s.path == SandboxPath))
        {
            scenes.Add(new EditorBuildSettingsScene(SandboxPath, true));
            EditorBuildSettings.scenes = scenes.ToArray();
            Debug.Log("🔄 [KINET STRIKE] Sandbox_China.unity añadida a EditorBuildSettings.");
        }
    }
}
