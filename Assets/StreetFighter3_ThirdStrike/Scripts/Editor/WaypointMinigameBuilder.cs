#if UNITY_EDITOR
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UI;
using Minigame.Waypoints;
using StreetFighter3.Loading;

namespace Minigame.Editor
{
    public static class WaypointMinigameBuilder
    {
        private const string RYU_IDLE_PATH = "Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu/01_Movement/idle_stance";
        private const string RYU_WALK_PATH = "Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu/01_Movement/walk_forward";
        private const string RYU_HIT_PATH = "Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu/04_Defense_Hit/hit_standing";

        private const string KEN_IDLE_PATH = "Assets/StreetFighter3_ThirdStrike/Characters/11_Ken/01_Movement/idle_stance";
        private const string KEN_WALK_PATH = "Assets/StreetFighter3_ThirdStrike/Characters/11_Ken/01_Movement/walk_forward";

        private const string SEAN_IDLE_PATH = "Assets/StreetFighter3_ThirdStrike/Characters/12_Sean/01_Movement/idle_stance";
        private const string SEAN_WALK_PATH = "Assets/StreetFighter3_ThirdStrike/Characters/12_Sean/01_Movement/walk_forward";

        private const string ORB_SPARKS_PATH = "Assets/StreetFighter3_ThirdStrike/Effects/09_Guard_Block_Sparks";
        private const string MATERIAL_PATH = "Assets/StreetFighter3_ThirdStrike/Materials/StonePillar_Material.mat";

        private const string SCENE_PATH_1 = "Assets/Scenes/minijuegowaypoint.unity";
        private const string SCENE_PATH_2 = "Assets/StreetFighter3_ThirdStrike/Scenes/minijuegowaypoint.unity";

        [InitializeOnLoadMethod]
        private static void RegisterAutoBuildWatcher()
        {
            EditorApplication.update += CheckAutoBuildFlag;
        }

        private static void CheckAutoBuildFlag()
        {
            string flagPath = "Temp/rebuild_waypoints.flag";
            if (File.Exists(flagPath))
            {
                EditorApplication.update -= CheckAutoBuildFlag;
                try
                {
                    File.Delete(flagPath);
                }
                catch {}
                BuildMinigameScene();
            }
        }

        [MenuItem("Tools/Waypoints/Generar Escena Minijuego Waypoints")]
        public static void BuildMinigameScene()
        {
            EnsureDirectories();
            Debug.Log("[Waypoint Builder] Iniciando construccion de la escena minijuegowaypoint...");

            // 1. Cargar sprites
            Sprite[] ryuIdle = LoadSortedSprites(RYU_IDLE_PATH);
            Sprite[] ryuWalk = LoadSortedSprites(RYU_WALK_PATH);
            Sprite[] ryuHit = LoadSortedSprites(RYU_HIT_PATH);

            Sprite[] kenIdle = LoadSortedSprites(KEN_IDLE_PATH);
            Sprite[] kenWalk = LoadSortedSprites(KEN_WALK_PATH);

            Sprite[] seanIdle = LoadSortedSprites(SEAN_IDLE_PATH);
            Sprite[] seanWalk = LoadSortedSprites(SEAN_WALK_PATH);

            // Cargar orbes desde 09_Guard_Block_Sparks
            Sprite[] orbSparks = LoadSortedSprites(ORB_SPARKS_PATH);

            // 2. Crear material con shader de rocas
            Material stoneMaterial = GetOrCreateRockMaterial();

            // 3. Crear nueva escena vacia
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            // 4. GameObject Raiz
            GameObject root = new GameObject("MinijuegoWaypoints_Root");

            // 5. Camara Ortografica
            GameObject camObj = new GameObject("MainCamera");
            camObj.transform.SetParent(root.transform);
            camObj.transform.localPosition = new Vector3(0f, 0f, -10f);
            Camera cam = camObj.AddComponent<Camera>();
            cam.orthographic = true;
            cam.orthographicSize = 4.85f;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.05f, 0.06f, 0.09f);
            camObj.AddComponent<AudioListener>();

            // 6. Entorno visual y limites de la arena
            GameObject envRoot = new GameObject("Environment");
            envRoot.transform.SetParent(root.transform);

            // Fondo retro oscuro amplio para que nada se pierda en ningun aspect ratio
            CreateVisualQuad(envRoot.transform, "ArenaBackground", Vector3.zero, new Vector3(16.5f, 10.0f, 1f), new Color(0.07f, 0.08f, 0.12f));

            // Bordes delimitadores
            CreateVisualQuad(envRoot.transform, "Border_Top", new Vector3(0f, 4.0f, 0f), new Vector3(14.8f, 0.14f, 1f), new Color(0.2f, 0.6f, 0.9f, 0.85f));
            CreateVisualQuad(envRoot.transform, "Border_Bottom", new Vector3(0f, -4.0f, 0f), new Vector3(14.8f, 0.14f, 1f), new Color(0.2f, 0.6f, 0.9f, 0.85f));
            CreateVisualQuad(envRoot.transform, "Border_Left", new Vector3(-7.4f, 0f, 0f), new Vector3(0.14f, 8.14f, 1f), new Color(0.2f, 0.6f, 0.9f, 0.85f));
            CreateVisualQuad(envRoot.transform, "Border_Right", new Vector3(7.4f, 0f, 0f), new Vector3(0.14f, 8.14f, 1f), new Color(0.2f, 0.6f, 0.9f, 0.85f));

            // 7. Obstaculos con Shader y Material de Rocas
            GameObject obsRoot = new GameObject("Obstacles");
            obsRoot.transform.SetParent(envRoot.transform);

            // Obstaculo 1 (Pilar Izquierdo de Roca)
            GameObject pillarLeft = CreateVisualQuad(obsRoot.transform, "Pillar_Left_Rock", new Vector3(-2.8f, 0.8f, 0f), new Vector3(1.8f, 3.2f, 1f), Color.white, stoneMaterial);
            // Obstaculo 2 (Pilar Derecho de Roca)
            GameObject pillarRight = CreateVisualQuad(obsRoot.transform, "Pillar_Right_Rock", new Vector3(2.8f, -0.8f, 0f), new Vector3(1.8f, 3.2f, 1f), Color.white, stoneMaterial);
            // Obstaculo 3 (Muro Central de Roca)
            GameObject barrierCenter = CreateVisualQuad(obsRoot.transform, "Barrier_Center_Rock", new Vector3(0f, 0f, 0f), new Vector3(1.4f, 1.8f, 1f), Color.white, stoneMaterial);

            // 8. Circuitos de Waypoints
            GameObject circuitsRoot = new GameObject("WaypointCircuits");
            circuitsRoot.transform.SetParent(root.transform);

            // Circuito A: Patrulla Perimetral Exterior (Guardia 1 - Ken)
            GameObject circuitAObj = new GameObject("Circuit_Perimeter");
            circuitAObj.transform.SetParent(circuitsRoot.transform);
            WaypointCircuit circuitA = circuitAObj.AddComponent<WaypointCircuit>();

            Transform[] waypointsA = new Transform[6];
            waypointsA[0] = CreateWaypointNode(circuitAObj.transform, "WP_A1", new Vector3(-5.6f, 2.7f, 0f));
            waypointsA[1] = CreateWaypointNode(circuitAObj.transform, "WP_A2", new Vector3(0.0f, 2.8f, 0f));
            waypointsA[2] = CreateWaypointNode(circuitAObj.transform, "WP_A3", new Vector3(5.6f, 2.7f, 0f));
            waypointsA[3] = CreateWaypointNode(circuitAObj.transform, "WP_A4", new Vector3(5.6f, -2.7f, 0f));
            waypointsA[4] = CreateWaypointNode(circuitAObj.transform, "WP_A5", new Vector3(0.0f, -2.8f, 0f));
            waypointsA[5] = CreateWaypointNode(circuitAObj.transform, "WP_A6", new Vector3(-5.6f, -2.7f, 0f));
            circuitA.SetCustomWaypoints(waypointsA, WaypointTraversalMode.Loop);

            // Circuito B: Patrulla Zig-zag esquivando pilares de roca (Guardia 2 - Sean)
            GameObject circuitBObj = new GameObject("Circuit_ObstacleAvoidance");
            circuitBObj.transform.SetParent(circuitsRoot.transform);
            WaypointCircuit circuitB = circuitBObj.AddComponent<WaypointCircuit>();

            Transform[] waypointsB = new Transform[4];
            waypointsB[0] = CreateWaypointNode(circuitBObj.transform, "WP_B1_DodgePillar1", new Vector3(-2.8f, -1.8f, 0f));
            waypointsB[1] = CreateWaypointNode(circuitBObj.transform, "WP_B2_CenterPath", new Vector3(-1.0f, 0.0f, 0f));
            waypointsB[2] = CreateWaypointNode(circuitBObj.transform, "WP_B3_DodgePillar2", new Vector3(2.8f, 1.8f, 0f));
            waypointsB[3] = CreateWaypointNode(circuitBObj.transform, "WP_B4_ReturnCenter", new Vector3(1.0f, 0.0f, 0f));
            circuitB.SetCustomWaypoints(waypointsB, WaypointTraversalMode.PingPong);

            // 9. Jugador (Ryu)
            GameObject playerObj = new GameObject("Player_Ryu");
            playerObj.transform.SetParent(root.transform);
            playerObj.transform.localPosition = new Vector3(-6.0f, -2.8f, 0f);

            SpriteRenderer playerRenderer = playerObj.AddComponent<SpriteRenderer>();
            playerRenderer.sortingOrder = 10;
            if (ryuIdle.Length > 0) playerRenderer.sprite = ryuIdle[0];

            SpriteFrameAnimator playerAnimator = playerObj.AddComponent<SpriteFrameAnimator>();
            StealthPlayerController playerController = playerObj.AddComponent<StealthPlayerController>();
            playerController.SetAnimationFrames(ryuIdle, ryuWalk, ryuHit);
            // Limites estrictos para que nunca se pierda fuera de la vista
            playerController.SetBounds(new Rect(-6.8f, -3.5f, 13.6f, 7.0f));

            // 10. Guardias con Waypoints
            GameObject guardsRoot = new GameObject("Guards");
            guardsRoot.transform.SetParent(root.transform);

            List<WaypointPatrolNPC> guardList = new List<WaypointPatrolNPC>();

            // Guardia 1: Ken en Circuito Perimetral
            GameObject guard1Obj = new GameObject("Guard_Ken_Perimeter");
            guard1Obj.transform.SetParent(guardsRoot.transform);
            guard1Obj.transform.localPosition = waypointsA[0].position;

            SpriteRenderer guard1Renderer = guard1Obj.AddComponent<SpriteRenderer>();
            guard1Renderer.sortingOrder = 9;
            if (kenIdle.Length > 0) guard1Renderer.sprite = kenIdle[0];

            SpriteFrameAnimator guard1Animator = guard1Obj.AddComponent<SpriteFrameAnimator>();
            WaypointPatrolNPC guard1 = guard1Obj.AddComponent<WaypointPatrolNPC>();
            guard1.SetCircuit(circuitA);
            guard1.SetAnimationFrames(kenIdle, kenWalk, kenIdle);
            guard1.SetTargetPlayer(playerObj.transform);
            SetPrivateField(guard1, "moveSpeed", 2.8f);
            SetPrivateField(guard1, "chaseSpeed", 3.8f);
            SetPrivateField(guard1, "detectionRadius", 2.3f);
            SetPrivateField(guard1, "waitTimeAtWaypoint", 0.8f);
            guardList.Add(guard1);

            // Guardia 2: Sean en Circuito Evasion de Obstaculos
            GameObject guard2Obj = new GameObject("Guard_Sean_ObstaclePatrol");
            guard2Obj.transform.SetParent(guardsRoot.transform);
            guard2Obj.transform.localPosition = waypointsB[0].position;

            SpriteRenderer guard2Renderer = guard2Obj.AddComponent<SpriteRenderer>();
            guard2Renderer.sortingOrder = 9;
            if (seanIdle.Length > 0) guard2Renderer.sprite = seanIdle[0];

            SpriteFrameAnimator guard2Animator = guard2Obj.AddComponent<SpriteFrameAnimator>();
            WaypointPatrolNPC guard2 = guard2Obj.AddComponent<WaypointPatrolNPC>();
            guard2.SetCircuit(circuitB);
            guard2.SetAnimationFrames(seanIdle, seanWalk, seanIdle);
            guard2.SetTargetPlayer(playerObj.transform);
            SetPrivateField(guard2, "moveSpeed", 3.2f);
            SetPrivateField(guard2, "chaseSpeed", 4.0f);
            SetPrivateField(guard2, "detectionRadius", 2.2f);
            SetPrivateField(guard2, "waitTimeAtWaypoint", 1.2f);
            guardList.Add(guard2);

            // 11. Orbes Coleccionables usando 09_Guard_Block_Sparks
            GameObject itemsRoot = new GameObject("Collectibles");
            itemsRoot.transform.SetParent(root.transform);

            List<StealthCollectible> collectibleList = new List<StealthCollectible>();
            Vector3[] itemPositions = new Vector3[]
            {
                new Vector3(-4.5f, 1.4f, 0f),
                new Vector3(-1.0f, 2.2f, 0f),
                new Vector3(1.0f, -2.2f, 0f),
                new Vector3(4.5f, -1.4f, 0f)
            };

            for (int i = 0; i < itemPositions.Length; i++)
            {
                GameObject itemObj = new GameObject($"Orb_Sparks_Collectible_{i + 1}");
                itemObj.transform.SetParent(itemsRoot.transform);
                itemObj.transform.localPosition = itemPositions[i];
                itemObj.transform.localScale = new Vector3(1.7f, 1.7f, 1f);

                SpriteRenderer itemRenderer = itemObj.AddComponent<SpriteRenderer>();
                itemRenderer.sortingOrder = 8;
                if (orbSparks.Length > 0) itemRenderer.sprite = orbSparks[0];

                SpriteFrameAnimator itemAnimator = itemObj.AddComponent<SpriteFrameAnimator>();
                StealthCollectible collectible = itemObj.AddComponent<StealthCollectible>();
                collectible.SetFrames(orbSparks);
                collectible.SetTargetPlayer(playerController);
                collectibleList.Add(collectible);
            }

            // 12. Portal de Extraccion / Meta
            GameObject goalObj = new GameObject("Goal_ExtractionPortal");
            goalObj.transform.SetParent(root.transform);
            goalObj.transform.localPosition = new Vector3(6.0f, 2.8f, 0f);

            CreateVisualQuad(goalObj.transform, "PortalVisual", Vector3.zero, new Vector3(1.2f, 1.2f, 1f), new Color(0.8f, 0.2f, 0.2f, 0.7f));
            StealthGoal goal = goalObj.AddComponent<StealthGoal>();
            goal.SetTargetPlayer(playerController);

            // 13. UI Canvas con formato amplio sin cortes en los bordes
            CanvasReferences ui = BuildMinigameUI(root.transform);

            // 14. Manager del Minijuego
            GameObject managerObj = new GameObject("StealthMinigameManager");
            managerObj.transform.SetParent(root.transform);
            StealthMinigameManager manager = managerObj.AddComponent<StealthMinigameManager>();
            manager.SetReferences(playerController, guardList, collectibleList, goal);
            manager.SetUIReferences(ui.StatusText, ui.OrbsText, ui.TimerText, ui.ControlsText);

            // 15. Guardar escena en ambas rutas para compatibilidad total
            EditorSceneManager.SaveScene(scene, SCENE_PATH_1);
            Debug.Log($"[Waypoint Builder] Escena guardada en: {SCENE_PATH_1}");

            EditorSceneManager.SaveScene(scene, SCENE_PATH_2);
            Debug.Log($"[Waypoint Builder] Escena guardada en: {SCENE_PATH_2}");

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log("[Waypoint Builder] Minijuego de Waypoints regenerado con exito.");
        }

        private static Material GetOrCreateRockMaterial()
        {
            Material mat = AssetDatabase.LoadAssetAtPath<Material>(MATERIAL_PATH);
            if (mat == null)
            {
                Shader shader = Shader.Find("Custom/RockStone2D");
                if (shader == null)
                {
                    Debug.LogWarning("[Waypoint Builder] Shader Custom/RockStone2D no encontrado en Shader.Find, usando Sprites/Default como respaldo.");
                    shader = Shader.Find("Sprites/Default");
                }

                mat = new Material(shader);
                mat.name = "StonePillar_Material";
                mat.SetColor("_BaseRockColor", new Color(0.28f, 0.31f, 0.36f, 1f));
                mat.SetColor("_HighlightRockColor", new Color(0.44f, 0.48f, 0.55f, 1f));
                mat.SetColor("_CrackColor", new Color(0.11f, 0.12f, 0.15f, 1f));
                mat.SetFloat("_Scale", 5.5f);
                mat.SetFloat("_CrackIntensity", 0.7f);
                mat.SetFloat("_EdgeDarkness", 0.45f);

                AssetDatabase.CreateAsset(mat, MATERIAL_PATH);
                AssetDatabase.SaveAssets();
                Debug.Log($"[Waypoint Builder] Material de roca creado en: {MATERIAL_PATH}");
            }
            return mat;
        }

        private static Transform CreateWaypointNode(Transform parent, string name, Vector3 pos)
        {
            GameObject node = new GameObject(name);
            node.transform.SetParent(parent);
            node.transform.localPosition = pos;
            return node.transform;
        }

        private static GameObject CreateVisualQuad(Transform parent, string name, Vector3 pos, Vector3 scale, Color color, Material customMat = null)
        {
            GameObject quad = new GameObject(name);
            quad.transform.SetParent(parent);
            quad.transform.localPosition = pos;
            quad.transform.localScale = scale;

            SpriteRenderer sr = quad.AddComponent<SpriteRenderer>();
            sr.color = color;
            sr.sortingOrder = 2;

            if (customMat != null)
            {
                sr.material = customMat;
            }

            Texture2D tex = new Texture2D(1, 1);
            tex.SetPixel(0, 0, Color.white);
            tex.Apply();
            Sprite dummy = Sprite.Create(tex, new Rect(0, 0, 1, 1), new Vector2(0.5f, 0.5f), 1f);
            sr.sprite = dummy;

            return quad;
        }

        private struct CanvasReferences
        {
            public Text TitleText;
            public Text StatusText;
            public Text OrbsText;
            public Text TimerText;
            public Text ControlsText;
        }

        private static CanvasReferences BuildMinigameUI(Transform parent)
        {
            CanvasReferences refs = new CanvasReferences();

            GameObject canvasObj = new GameObject("Minigame_Canvas");
            canvasObj.transform.SetParent(parent);
            Canvas canvas = canvasObj.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 20;

            CanvasScaler scaler = canvasObj.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920, 1080);
            scaler.matchWidthOrHeight = 0.5f;

            canvasObj.AddComponent<GraphicRaycaster>();

            Font font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            if (font == null) font = Resources.GetBuiltinResource<Font>("Arial.ttf");

            // 1. Panel de Cabecera (Anclado arriba en todo el ancho con fondo oscuro)
            GameObject headerObj = new GameObject("HeaderPanel");
            headerObj.transform.SetParent(canvasObj.transform, false);
            RectTransform headerRt = headerObj.AddComponent<RectTransform>();
            headerRt.anchorMin = new Vector2(0f, 1f);
            headerRt.anchorMax = new Vector2(1f, 1f);
            headerRt.pivot = new Vector2(0.5f, 1f);
            headerRt.anchoredPosition = Vector2.zero;
            headerRt.sizeDelta = new Vector2(0f, 100f);

            Image headerBg = headerObj.AddComponent<Image>();
            headerBg.color = new Color(0.04f, 0.05f, 0.08f, 0.90f);
            headerBg.raycastTarget = false;

            // Titulo principal
            refs.TitleText = CreateSafeUIText("TitleText", headerObj.transform, "DOJO STEALTH: WAYPOINTS MISSION", font, 28, FontStyle.Bold, new Color(1f, 0.85f, 0.2f));
            RectTransform titleRt = refs.TitleText.rectTransform;
            titleRt.anchorMin = new Vector2(0f, 1f);
            titleRt.anchorMax = new Vector2(0f, 1f);
            titleRt.pivot = new Vector2(0f, 1f);
            titleRt.anchoredPosition = new Vector2(35f, -15f);
            titleRt.sizeDelta = new Vector2(800f, 40f);
            refs.TitleText.alignment = TextAnchor.MiddleLeft;

            // Texto de estado / objetivo
            refs.StatusText = CreateSafeUIText("StatusText", headerObj.transform, "OBJETIVO: EVITA LAS RUTAS DE WAYPOINTS Y RECOGE LOS ORBES", font, 20, FontStyle.Bold, Color.white);
            RectTransform statusRt = refs.StatusText.rectTransform;
            statusRt.anchorMin = new Vector2(0f, 1f);
            statusRt.anchorMax = new Vector2(0f, 1f);
            statusRt.pivot = new Vector2(0f, 1f);
            statusRt.anchoredPosition = new Vector2(35f, -55f);
            statusRt.sizeDelta = new Vector2(1000f, 35f);
            refs.StatusText.alignment = TextAnchor.MiddleLeft;

            // Temporizador
            refs.TimerText = CreateSafeUIText("TimerText", headerObj.transform, "TIEMPO: 00:00", font, 26, FontStyle.Bold, new Color(0.3f, 0.9f, 1f));
            RectTransform timerRt = refs.TimerText.rectTransform;
            timerRt.anchorMin = new Vector2(1f, 1f);
            timerRt.anchorMax = new Vector2(1f, 1f);
            timerRt.pivot = new Vector2(1f, 1f);
            timerRt.anchoredPosition = new Vector2(-35f, -15f);
            timerRt.sizeDelta = new Vector2(400f, 40f);
            refs.TimerText.alignment = TextAnchor.MiddleRight;

            // Contador de orbes
            refs.OrbsText = CreateSafeUIText("OrbsText", headerObj.transform, "ORBES: 0 / 4", font, 22, FontStyle.Bold, new Color(1f, 0.7f, 0.2f));
            RectTransform orbsRt = refs.OrbsText.rectTransform;
            orbsRt.anchorMin = new Vector2(1f, 1f);
            orbsRt.anchorMax = new Vector2(1f, 1f);
            orbsRt.pivot = new Vector2(1f, 1f);
            orbsRt.anchoredPosition = new Vector2(-35f, -55f);
            orbsRt.sizeDelta = new Vector2(400f, 35f);
            refs.OrbsText.alignment = TextAnchor.MiddleRight;

            // 2. Panel de Pie (Anclado abajo en todo el ancho con controles)
            GameObject footerObj = new GameObject("FooterPanel");
            footerObj.transform.SetParent(canvasObj.transform, false);
            RectTransform footerRt = footerObj.AddComponent<RectTransform>();
            footerRt.anchorMin = new Vector2(0f, 0f);
            footerRt.anchorMax = new Vector2(1f, 0f);
            footerRt.pivot = new Vector2(0.5f, 0f);
            footerRt.anchoredPosition = Vector2.zero;
            footerRt.sizeDelta = new Vector2(0f, 50f);

            Image footerBg = footerObj.AddComponent<Image>();
            footerBg.color = new Color(0.04f, 0.05f, 0.08f, 0.90f);
            footerBg.raycastTarget = false;

            refs.ControlsText = CreateSafeUIText("ControlsText", footerObj.transform, "CONTROLES: [WASD / FLECHAS] Moverse  |  [R] Reiniciar Mision", font, 20, FontStyle.Normal, new Color(0.85f, 0.85f, 0.85f, 0.95f));
            RectTransform controlsRt = refs.ControlsText.rectTransform;
            controlsRt.anchorMin = new Vector2(0.5f, 0.5f);
            controlsRt.anchorMax = new Vector2(0.5f, 0.5f);
            controlsRt.pivot = new Vector2(0.5f, 0.5f);
            controlsRt.anchoredPosition = Vector2.zero;
            controlsRt.sizeDelta = new Vector2(1400f, 40f);
            refs.ControlsText.alignment = TextAnchor.MiddleCenter;

            return refs;
        }

        private static Text CreateSafeUIText(string name, Transform parent, string content, Font font, int size, FontStyle style, Color color)
        {
            GameObject textObj = new GameObject(name);
            textObj.transform.SetParent(parent, false);
            RectTransform rt = textObj.AddComponent<RectTransform>();

            Text t = textObj.AddComponent<Text>();
            t.text = content;
            t.font = font;
            t.fontSize = size;
            t.fontStyle = style;
            t.color = color;
            t.raycastTarget = false;

            // Configuracion crucial para evitar que las letras se corten por los lados o lineas
            t.horizontalOverflow = HorizontalWrapMode.Overflow;
            t.verticalOverflow = VerticalWrapMode.Overflow;

            Outline outline = textObj.AddComponent<Outline>();
            outline.effectColor = new Color(0f, 0f, 0f, 0.9f);
            outline.effectDistance = new Vector2(1.5f, -1.5f);

            return t;
        }

        private static Sprite[] LoadSortedSprites(string folderPath)
        {
            if (!Directory.Exists(folderPath))
            {
                Debug.LogWarning($"[Waypoint Builder] No se encontro el directorio: {folderPath}");
                return new Sprite[0];
            }

            string[] files = Directory.GetFiles(folderPath, "*.png");
            System.Array.Sort(files, (a, b) =>
            {
                int na, nb;
                bool parsedA = int.TryParse(Path.GetFileNameWithoutExtension(a), out na);
                bool parsedB = int.TryParse(Path.GetFileNameWithoutExtension(b), out nb);
                if (parsedA && parsedB) return na.CompareTo(nb);
                return string.Compare(a, b);
            });

            List<Sprite> sprites = new List<Sprite>();
            foreach (string file in files)
            {
                string unityPath = file.Replace("\\", "/");
                Sprite sp = AssetDatabase.LoadAssetAtPath<Sprite>(unityPath);
                if (sp != null)
                {
                    sprites.Add(sp);
                }
            }

            return sprites.ToArray();
        }

        private static void SetPrivateField(object target, string fieldName, object value)
        {
            var field = target.GetType().GetField(fieldName, System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            if (field != null)
            {
                field.SetValue(target, value);
            }
            else
            {
                Debug.LogWarning($"[Waypoint Builder] Campo no encontrado: {fieldName} en {target.GetType().Name}");
            }
        }

        private static void EnsureDirectories()
        {
            string dir1 = Path.GetDirectoryName(SCENE_PATH_1);
            if (!Directory.Exists(dir1)) Directory.CreateDirectory(dir1);

            string dir2 = Path.GetDirectoryName(SCENE_PATH_2);
            if (!Directory.Exists(dir2)) Directory.CreateDirectory(dir2);

            string matDir = Path.GetDirectoryName(MATERIAL_PATH);
            if (!Directory.Exists(matDir)) Directory.CreateDirectory(matDir);
        }
    }
}
#endif
