using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using StreetFighter3.UI;

namespace StreetFighter3.Editor
{
    [InitializeOnLoad]
    public static class SF3CompleteStageBuilder
    {
        private const string ChinaFolder = "Assets/StreetFighter3_ThirdStrike/Stages/China_ChunLi";
        private const string JapanFolder = "Assets/StreetFighter3_ThirdStrike/Stages/Japan_Ryu";
        private const string TombFolder = "Assets/StreetFighter3_ThirdStrike/Stages/Tomb_Urien";

        private const string ChinaPrefabPath = "Assets/StreetFighter3_ThirdStrike/Prefabs/Stage_China.prefab";
        private const string JapanPrefabPath = "Assets/StreetFighter3_ThirdStrike/Prefabs/Stage_Japan.prefab";
        private const string TombPrefabPath = "Assets/StreetFighter3_ThirdStrike/Prefabs/Stage_Tomb.prefab";

        private const string ChinaScenePath = "Assets/StreetFighter3_ThirdStrike/Scenes/Sandbox_China.unity";
        private const string JapanScenePath = "Assets/StreetFighter3_ThirdStrike/Scenes/Sandbox_Sebas.unity";
        private const string TombScenePath = "Assets/StreetFighter3_ThirdStrike/Scenes/Sandbox_Tomb.unity";

        private const string MaterialPath = "Assets/StreetFighter3_ThirdStrike/Materials/Stage_ChromaKey.mat";
        private const string ShaderPath = "Assets/StreetFighter3_ThirdStrike/Shaders/SF3ChromaKeySprite.shader";

        static SF3CompleteStageBuilder()
        {
            EditorApplication.delayCall += CheckAndBuildStages;
        }

        private static void CheckAndBuildStages()
        {
            if (!File.Exists(TombPrefabPath) || !File.Exists(TombScenePath))
            {
                BuildAllStagesAndHUD();
            }
        }

        [MenuItem("Kinet Strike Tools/Build All Stages, Floors & HUD")]
        [MenuItem("SF3 Tools/Build All Stages, Floors & HUD")]
        public static void BuildAllStagesAndHUD()
        {
            Debug.Log("🥋 [KINET STRIKE] Iniciando construcción integral de escenarios, pisos visibles y HUD...");

            EnsureSortingLayers();
            Material stageMaterial = GetOrCreateStageMaterial();

            // 1. Construir / Actualizar Escenario China con piso visible
            BuildChinaStageWithFloor(stageMaterial);

            // 2. Construir / Actualizar Escenario Japón con piso visible
            BuildJapanStageWithFloor(stageMaterial);

            // 3. Construir Nuevo Escenario Tumba de Urien
            BuildTombStage(stageMaterial);

            // 4. Construir Prefab de Urien
            BuildUrienPrefab();

            // 5. Configurar Escena Sandbox_Tomb con HUD y combate
            SetupTombSandboxScene();

            // 6. Actualizar Sandbox_China con FightHUD
            UpdateChinaSceneWithHUD();

            // 7. Sincronizar Build Settings
            SyncBuildSettings();

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log("✅ [KINET STRIKE] Todos los escenarios, pisos y HUD han sido configurados exitosamente.");
        }

        private static void BuildChinaStageWithFloor(Material stageMaterial)
        {
            GameObject stageRoot = new GameObject("Stage_China");
            try
            {
                // Capa Distante: Río y cielo tradicional
                CreateSpriteLayer(stageRoot.transform, "Distant_Canal_Sky",
                    $"{ChinaFolder}/chun-li-bg-layer2.png", "Background_Distant", 0,
                    new Vector3(0f, 1.15f, 0f), new Vector3(1.22f, 1.22f, 1f), stageMaterial);

                // Capa de Mercado Callejero (Alineada para que las losas de la calle estén a Y = 0.0)
                CreateSpriteLayer(stageRoot.transform, "Crowded_Street",
                    $"{ChinaFolder}/chun-li-bg-layer1.png", "Floor_Ground", 0,
                    new Vector3(0f, 1.75f, 0f), new Vector3(1.15f, 1.15f, 1f), stageMaterial);

                // Piso Visible: Franja sólida de losas de piedra/adoquines debajo de los luchadores
                GameObject floorObj = new GameObject("Ground_Street_Floor");
                floorObj.transform.SetParent(stageRoot.transform, false);
                floorObj.transform.position = new Vector3(0f, -0.45f, 0f);
                floorObj.transform.localScale = new Vector3(14f, 0.9f, 1f);
                SpriteRenderer floorSr = floorObj.AddComponent<SpriteRenderer>();
                floorSr.sortingLayerName = "Floor_Ground";
                floorSr.sortingOrder = 5;
                floorSr.color = new Color(0.18f, 0.15f, 0.12f, 1f); // Tono granito chino oscuro
                floorSr.sprite = GetSolidSquareSprite();

                // Delimitadores físicos
                CreateBoxCollider(stageRoot.transform, "Ground_Collider", new Vector3(0f, -0.1f, 0f), new Vector2(14f, 0.2f));
                CreateBoxCollider(stageRoot.transform, "Wall_Left", new Vector3(-6.2f, 2f, 0f), new Vector2(0.5f, 6f));
                CreateBoxCollider(stageRoot.transform, "Wall_Right", new Vector3(6.2f, 2f, 0f), new Vector2(0.5f, 6f));

                PrefabUtility.SaveAsPrefabAsset(stageRoot, ChinaPrefabPath);
                Debug.Log("🏮 [KINET STRIKE] Prefab Stage_China actualizado con piso visible.");
            }
            finally
            {
                Object.DestroyImmediate(stageRoot);
            }
        }

        private static void BuildJapanStageWithFloor(Material stageMaterial)
        {
            GameObject stageRoot = new GameObject("Stage_Japan");
            try
            {
                // Cielo lejano
                CreateSpriteLayer(stageRoot.transform, "Sky",
                    $"{JapanFolder}/ryu-sky.png", "Background_Sky", 0,
                    new Vector3(0f, 2.2f, 0f), new Vector3(1.4f, 1.4f, 1f), stageMaterial);

                // Castillo Suzaku y Montañas
                CreateSpriteLayer(stageRoot.transform, "Suzaku_Castle",
                    $"{JapanFolder}/ryu-temple.png", "Background_Distant", 0,
                    new Vector3(0f, 1.5f, 0f), new Vector3(1.25f, 1.25f, 1f), stageMaterial);

                CreateSpriteLayer(stageRoot.transform, "Battle_Ground",
                    $"{JapanFolder}/ryu03.png", "Midground_Temple", 0,
                    new Vector3(0f, 1.15f, 0f), new Vector3(1.22f, 1.22f, 1f), stageMaterial);

                // PISO VISIBLE: Tejado de tejas japonesas auténticas de Suzaku Castle
                CreateSpriteLayer(stageRoot.transform, "Battle_Ground_RoofTiles",
                    $"{JapanFolder}/ryu-roof.png", "Floor_Ground", 5,
                    new Vector3(0f, -0.32f, 0f), new Vector3(1.45f, 1.45f, 1f), stageMaterial);

                // Base oscura debajo del tejado
                GameObject floorBase = new GameObject("Ground_Roof_Foundation");
                floorBase.transform.SetParent(stageRoot.transform, false);
                floorBase.transform.position = new Vector3(0f, -0.75f, 0f);
                floorBase.transform.localScale = new Vector3(14f, 0.7f, 1f);
                SpriteRenderer baseSr = floorBase.AddComponent<SpriteRenderer>();
                baseSr.sortingLayerName = "Floor_Ground";
                baseSr.sortingOrder = 4;
                baseSr.color = new Color(0.08f, 0.08f, 0.07f, 1f);
                baseSr.sprite = GetSolidSquareSprite();

                // Alero superior (Foreground Roof)
                CreateSpriteLayer(stageRoot.transform, "Foreground_Roof_Ceiling",
                    $"{JapanFolder}/ryu-roof.png", "Foreground_Props", 0,
                    new Vector3(0f, 3.45f, 0f), new Vector3(1.35f, 1.2f, 1f), stageMaterial);

                // Colisionadores
                CreateBoxCollider(stageRoot.transform, "Ground_Collider", new Vector3(0f, -0.32f, 0f), new Vector2(14f, 0.2f));
                CreateBoxCollider(stageRoot.transform, "Wall_Left", new Vector3(-6.2f, 2f, 0f), new Vector2(0.5f, 6f));
                CreateBoxCollider(stageRoot.transform, "Wall_Right", new Vector3(6.2f, 2f, 0f), new Vector2(0.5f, 6f));

                PrefabUtility.SaveAsPrefabAsset(stageRoot, JapanPrefabPath);
                Debug.Log("🏯 [KINET STRIKE] Prefab Stage_Japan actualizado con piso de tejas visible.");
            }
            finally
            {
                Object.DestroyImmediate(stageRoot);
            }
        }

        private static void BuildTombStage(Material stageMaterial)
        {
            GameObject stageRoot = new GameObject("Stage_Tomb");
            try
            {
                // Capa 2: Cripta cavernosa y estatuas olímpicas de fondo
                CreateSpriteLayer(stageRoot.transform, "Distant_Crypt",
                    $"{TombFolder}/urien-bg-layer2.png", "Background_Distant", 0,
                    new Vector3(0f, 1.6f, 0f), new Vector3(1.18f, 1.18f, 1f), stageMaterial);

                // Capa 1: Templo con columnas corintias y piso de losas de mármol
                CreateSpriteLayer(stageRoot.transform, "Temple_Columns_Floor",
                    $"{TombFolder}/urien-bg-layer1.png", "Floor_Ground", 0,
                    new Vector3(0f, 2.10f, 0f), new Vector3(1.10f, 1.10f, 1f), stageMaterial);

                // Piso Visible: Base sólida de piedra antigua
                GameObject floorBase = new GameObject("Ground_Marble_Foundation");
                floorBase.transform.SetParent(stageRoot.transform, false);
                floorBase.transform.position = new Vector3(0f, -0.55f, 0f);
                floorBase.transform.localScale = new Vector3(14f, 0.9f, 1f);
                SpriteRenderer baseSr = floorBase.AddComponent<SpriteRenderer>();
                baseSr.sortingLayerName = "Floor_Ground";
                baseSr.sortingOrder = 5;
                baseSr.color = new Color(0.14f, 0.14f, 0.16f, 1f);
                baseSr.sprite = GetSolidSquareSprite();

                // Delimitadores físicos
                CreateBoxCollider(stageRoot.transform, "Ground_Collider", new Vector3(0f, -0.1f, 0f), new Vector2(14f, 0.2f));
                CreateBoxCollider(stageRoot.transform, "Wall_Left", new Vector3(-6.2f, 2f, 0f), new Vector2(0.5f, 6f));
                CreateBoxCollider(stageRoot.transform, "Wall_Right", new Vector3(6.2f, 2f, 0f), new Vector2(0.5f, 6f));

                PrefabUtility.SaveAsPrefabAsset(stageRoot, TombPrefabPath);
                Debug.Log("🏛️ [KINET STRIKE] Prefab Stage_Tomb creado con piso de templo visible.");
            }
            finally
            {
                Object.DestroyImmediate(stageRoot);
            }
        }

        private static void BuildUrienPrefab()
        {
            string urienPrefabPath = "Assets/StreetFighter3_ThirdStrike/Prefabs/Fighter_Urien.prefab";
            string urienIdlePath = "Assets/StreetFighter3_ThirdStrike/Characters/13_Urien/01_Movement/idle_stance/0.png";
            string urienAnimPath = "Assets/StreetFighter3_ThirdStrike/Characters/13_Urien/Urien_Animator.controller";

            GameObject root = new GameObject("Fighter_Urien");
            try
            {
                root.tag = "Player";
                BoxCollider2D box = root.AddComponent<BoxCollider2D>();
                box.offset = new Vector2(0f, 0.55f);
                box.size = new Vector2(0.6f, 1.1f);

                Rigidbody2D rb = root.AddComponent<Rigidbody2D>();
                rb.mass = 1f;
                rb.gravityScale = 3f;
                rb.freezeRotation = true;
                rb.collisionDetectionMode = CollisionDetectionMode2D.Continuous;

                FighterAnimationTester tester = root.AddComponent<FighterAnimationTester>();

                GameObject visuals = new GameObject("Visuals");
                visuals.transform.SetParent(root.transform, false);

                SpriteRenderer sr = visuals.AddComponent<SpriteRenderer>();
                sr.sortingLayerName = "Fighters";
                sr.sortingOrder = 10;
                Sprite initialSprite = AssetDatabase.LoadAssetAtPath<Sprite>(urienIdlePath);
                if (initialSprite != null) sr.sprite = initialSprite;

                Animator animator = visuals.AddComponent<Animator>();
                RuntimeAnimatorController ctrl = AssetDatabase.LoadAssetAtPath<RuntimeAnimatorController>(urienAnimPath);
                if (ctrl != null) animator.runtimeAnimatorController = ctrl;

                PrefabUtility.SaveAsPrefabAsset(root, urienPrefabPath);
                Debug.Log("⚡ [KINET STRIKE] Prefab Fighter_Urien creado y configurado.");
            }
            finally
            {
                Object.DestroyImmediate(root);
            }
        }

        private static void SetupTombSandboxScene()
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            // 1. Main Camera con FightHUD y Audio
            GameObject camObj = new GameObject("Main Camera");
            camObj.tag = "MainCamera";
            Camera cam = camObj.AddComponent<Camera>();
            cam.orthographic = true;
            cam.orthographicSize = 2.3f;
            camObj.transform.position = new Vector3(0f, 1.65f, -10f);
            camObj.AddComponent<AudioListener>();

            // BGM Tumba Olímpica
            AudioClip tombBgm = Resources.Load<AudioClip>("Audio/BGM_Tomb");
            if (tombBgm != null)
            {
                AudioSource src = camObj.AddComponent<AudioSource>();
                src.clip = tombBgm;
                src.loop = true;
                src.volume = 0.55f;
                src.playOnAwake = true;
            }

            // HUD Arcade oficial con barra de vida de Urien y Ryu, y contador de 99s
            FightHUD hud = camObj.AddComponent<FightHUD>();
            hud.p1Name = "URIEN";
            hud.p2Name = "RYU";
            hud.roundDurationSeconds = 99f;

            camObj.AddComponent<StageParallaxTester>();

            // 2. Instanciar Escenario Tumba
            GameObject tombPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(TombPrefabPath);
            if (tombPrefab != null)
            {
                GameObject stage = PrefabUtility.InstantiatePrefab(tombPrefab, scene) as GameObject;
                if (stage != null) stage.transform.position = Vector3.zero;
            }

            // 3. Instanciar Urien (P1)
            GameObject urienPrefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/StreetFighter3_ThirdStrike/Prefabs/Fighter_Urien.prefab");
            if (urienPrefab != null)
            {
                GameObject p1 = PrefabUtility.InstantiatePrefab(urienPrefab, scene) as GameObject;
                if (p1 != null)
                {
                    p1.name = "Fighter_Urien (Player)";
                    p1.transform.position = new Vector3(-1.5f, 0f, 0f);
                }
            }

            // 4. Instanciar Ryu (P2 / Rival)
            GameObject ryuPrefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/StreetFighter3_ThirdStrike/Prefabs/Fighter_Ryu.prefab");
            if (ryuPrefab != null)
            {
                GameObject p2 = PrefabUtility.InstantiatePrefab(ryuPrefab, scene) as GameObject;
                if (p2 != null)
                {
                    p2.name = "Fighter_Ryu (Opponent)";
                    p2.tag = "Enemy";
                    p2.transform.position = new Vector3(1.5f, 0f, 0f);
                    p2.transform.localScale = new Vector3(-1f, 1f, 1f); // Mirando a la izquierda hacia Urien
                }
            }

            EditorSceneManager.SaveScene(scene, TombScenePath);
            Debug.Log("🏛️ [KINET STRIKE] Escena Sandbox_Tomb.unity creada con éxito.");
        }

        private static void UpdateChinaSceneWithHUD()
        {
            if (!File.Exists(ChinaScenePath)) return;

            Scene scene = EditorSceneManager.OpenScene(ChinaScenePath, OpenSceneMode.Single);
            GameObject cam = GameObject.FindWithTag("MainCamera");
            if (cam != null)
            {
                FightHUD hud = cam.GetComponent<FightHUD>();
                if (hud == null) hud = cam.AddComponent<FightHUD>();
                hud.p1Name = "RYU";
                hud.p2Name = "CHUN-LI";
                hud.roundDurationSeconds = 99f;
            }

            // Re-instanciar stage si es necesario para asegurar piso actualizado
            GameObject existingStage = GameObject.Find("Stage_China") ?? GameObject.Find("Stage_China(Clone)");
            if (existingStage != null) Object.DestroyImmediate(existingStage);

            GameObject stagePrefab = AssetDatabase.LoadAssetAtPath<GameObject>(ChinaPrefabPath);
            if (stagePrefab != null)
            {
                GameObject stage = PrefabUtility.InstantiatePrefab(stagePrefab, scene) as GameObject;
                if (stage != null) stage.transform.position = Vector3.zero;
            }

            EditorSceneManager.SaveScene(scene, ChinaScenePath);
            Debug.Log("🇨🇳 [KINET STRIKE] Sandbox_China.unity actualizada con FightHUD y piso reforzado.");
        }

        private static void SyncBuildSettings()
        {
            var scenes = EditorBuildSettings.scenes.ToList();
            string[] requiredScenes =
            {
                "Assets/StreetFighter3_ThirdStrike/Scenes/MainMenu_Scene.unity",
                JapanScenePath,
                ChinaScenePath,
                TombScenePath
            };

            bool modified = false;
            foreach (string p in requiredScenes)
            {
                if (File.Exists(p) && !scenes.Any(s => s.path == p))
                {
                    scenes.Add(new EditorBuildSettingsScene(p, true));
                    modified = true;
                }
            }

            if (modified)
            {
                EditorBuildSettings.scenes = scenes.ToArray();
                Debug.Log("🔄 [KINET STRIKE] EditorBuildSettings actualizado con todas las escenas.");
            }
        }

        private static Transform CreateSpriteLayer(Transform parent, string name, string spritePath, string sortingLayer, int order, Vector3 pos, Vector3 scale, Material mat)
        {
            GameObject layer = new GameObject(name);
            layer.transform.SetParent(parent, false);
            layer.transform.localPosition = pos;
            layer.transform.localScale = scale;

            SpriteRenderer sr = layer.AddComponent<SpriteRenderer>();
            sr.sortingLayerName = sortingLayer;
            sr.sortingOrder = order;

            Sprite spr = AssetDatabase.LoadAssetAtPath<Sprite>(spritePath);
            if (spr != null) sr.sprite = spr;
            if (mat != null) sr.material = mat;

            return layer.transform;
        }

        private static void CreateBoxCollider(Transform parent, string name, Vector3 pos, Vector2 size)
        {
            GameObject col = new GameObject(name);
            col.transform.SetParent(parent, false);
            col.transform.localPosition = pos;
            BoxCollider2D box = col.AddComponent<BoxCollider2D>();
            box.size = size;
        }

        private static Sprite GetSolidSquareSprite()
        {
            // Textura 1x1 blanca sólida para base del piso
            Texture2D tex = new Texture2D(1, 1);
            tex.SetPixel(0, 0, Color.white);
            tex.Apply();
            return Sprite.Create(tex, new Rect(0, 0, 1, 1), new Vector2(0.5f, 0.5f), 1f);
        }

        private static Material GetOrCreateStageMaterial()
        {
            Shader shader = AssetDatabase.LoadAssetAtPath<Shader>(ShaderPath) ?? Shader.Find("SF3/ChromaKeySprite");
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

        private static void EnsureSortingLayers()
        {
            // Asegurar las capas de ordenamiento necesarias
            string[] required = { "Background_Sky", "Background_Distant", "Midground_Temple", "Floor_Ground", "Fighters", "Foreground_Props" };
            var tagManager = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/TagManager.asset")[0]);
            var layers = tagManager.FindProperty("m_SortingLayers");

            var names = new HashSet<string>();
            for (int i = 0; i < layers.arraySize; i++)
            {
                names.Add(layers.GetArrayElementAtIndex(i).FindPropertyRelative("name").stringValue);
            }

            foreach (var req in required)
            {
                if (!names.Contains(req))
                {
                    int idx = layers.arraySize;
                    layers.InsertArrayElementAtIndex(idx);
                    var el = layers.GetArrayElementAtIndex(idx);
                    el.FindPropertyRelative("name").stringValue = req;
                    el.FindPropertyRelative("uniqueID").intValue = Random.Range(100000, 9999999);
                }
            }
            tagManager.ApplyModifiedProperties();
        }
    }
}
