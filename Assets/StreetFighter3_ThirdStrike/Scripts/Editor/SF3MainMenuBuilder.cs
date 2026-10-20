using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using StreetFighter3.UI;
using StreetFighter3.AI.Steering;

namespace StreetFighter3.Editor
{
    [InitializeOnLoad]
    public static class SF3MainMenuBuilder
    {
        private const string SceneFolder = "Assets/StreetFighter3_ThirdStrike/Scenes";
        private const string ScenePath = "Assets/StreetFighter3_ThirdStrike/Scenes/MainMenu_Scene.unity";
        private const string DuelScenePath = "Assets/StreetFighter3_ThirdStrike/Scenes/Sandbox_Sebas.unity";
        private const string StoryScenePath = "Assets/StreetFighter3_ThirdStrike/Scenes/StoryMode_Scene.unity";
        private const string ChinaDuelPath = "Assets/StreetFighter3_ThirdStrike/Scenes/Sandbox_China.unity";
        private const string TombDuelPath = "Assets/StreetFighter3_ThirdStrike/Scenes/Sandbox_Tomb.unity";
        private const string WaypointScenePath = "Assets/StreetFighter3_ThirdStrike/Scenes/minijuegowaypoint.unity";
        private const string NeonSiegeScenePath = "Assets/StreetFighter3_ThirdStrike/Minigames/NeonSiege/NeonSiege.unity";

        static SF3MainMenuBuilder()
        {
            EditorApplication.delayCall += BuildIfMissing;
        }

        private static void BuildIfMissing()
        {
            if (!File.Exists(ScenePath))
            {
                BuildMainMenuScene();
            }
        }

        [MenuItem("SF3 Tools/Build All Project Scenes")]
        public static void BuildAllProjectScenes()
        {
            BuildMainMenuScene();
            SF3StoryModeBuilder.BuildStoryModeScene();
        }

        [MenuItem("SF3 Tools/Build Main Menu & Loading Scene")]
        public static void BuildMainMenuScene()
        {
            Debug.Log("[SF3 Builder] Construyendo Menú de Inicio y Pantalla de Carga interactiva...");

            // 1. Crear escena nueva vacía
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            Font retroFont = GetRetroFont();

            // 2. Cámara Principal 2D
            GameObject camObj = new GameObject("Main Camera");
            Camera cam = camObj.AddComponent<Camera>();
            cam.orthographic = true;
            cam.orthographicSize = 5f;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.04f, 0.05f, 0.07f, 1f);
            cam.nearClipPlane = 0.3f;
            cam.farClipPlane = 100f;
            camObj.transform.position = new Vector3(0f, 0f, -10f);

            // Audio Listener en la cámara
            camObj.AddComponent<AudioListener>();

            // 3. EventSystem para navegación con teclado
            GameObject eventSystemObj = new GameObject("EventSystem");
            eventSystemObj.AddComponent<UnityEngine.EventSystems.EventSystem>();
            eventSystemObj.AddComponent<UnityEngine.EventSystems.StandaloneInputModule>();

            // 4. Canvas Principal
            GameObject canvasObj = new GameObject("Canvas_MainMenu");
            Canvas canvas = canvasObj.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 0;

            CanvasScaler scaler = canvasObj.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920f, 1080f);
            scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
            scaler.matchWidthOrHeight = 0.5f;

            canvasObj.AddComponent<GraphicRaycaster>();

            // 5. Fondo del Menú (Escenario SF3 oscurecido con viñeta)
            Sprite bgSprite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/StreetFighter3_ThirdStrike/Stages/General_Stages/bonusbg2.png")
                ?? AssetDatabase.LoadAssetAtPath<Sprite>("Assets/StreetFighter3_ThirdStrike/Stages/USA_Ken_Alex/alex-bg.png")
                ?? AssetDatabase.LoadAssetAtPath<Sprite>("Assets/StreetFighter3_ThirdStrike/Stages/Japan_Ryu/ryu-temple.png");

            GameObject bgObj = CreateUIElement("Background_Image", canvasObj.transform);
            StretchFull(bgObj.GetComponent<RectTransform>());
            Image bgImg = bgObj.AddComponent<Image>();
            bgImg.sprite = bgSprite;
            bgImg.color = new Color(0.45f, 0.48f, 0.55f, 1f);

            // Capa de viñeta oscura para contraste
            GameObject vignetteObj = CreateUIElement("Vignette_Overlay", canvasObj.transform);
            StretchFull(vignetteObj.GetComponent<RectTransform>());
            Image vignetteImg = vignetteObj.AddComponent<Image>();
            vignetteImg.color = new Color(0.02f, 0.03f, 0.06f, 0.65f);

            // 6. Header / Título del Juego
            GameObject titleObj = CreateUIElement("Title_Panel", canvasObj.transform);
            RectTransform titleRt = titleObj.GetComponent<RectTransform>();
            titleRt.anchorMin = new Vector2(0.5f, 1f);
            titleRt.anchorMax = new Vector2(0.5f, 1f);
            titleRt.pivot = new Vector2(0.5f, 1f);
            titleRt.anchoredPosition = new Vector2(0f, -70f);
            titleRt.sizeDelta = new Vector2(1200f, 220f);

            CreateText("Header_CPS3", titleObj.transform, "SOMATOSENSORY 3D COMBAT SYSTEM — CPS-3", retroFont, 20, FontStyle.Bold,
                new Color(0.85f, 0.75f, 0.4f, 0.85f), new Vector2(0f, -20f), new Vector2(1000f, 30f));

            CreateText("Title_SF3", titleObj.transform, "STREET FIGHTER III: 3rd STRIKE", retroFont, 68, FontStyle.Bold,
                new Color(1f, 0.82f, 0.15f, 1f), new Vector2(0f, -75f), new Vector2(1400f, 85f));

            CreateText("Subtitle_Strike", titleObj.transform, "KINECT 3D & ADAPTIVE AI FIGHTING SYSTEM", retroFont, 30, FontStyle.Bold,
                new Color(0.2f, 0.9f, 1f, 1f), new Vector2(0f, -140f), new Vector2(1000f, 45f));

            // 7. Contenedor de Botones de Menú
            GameObject menuContainerObj = CreateUIElement("Menu_Container", canvasObj.transform);
            RectTransform menuRt = menuContainerObj.GetComponent<RectTransform>();
            menuRt.anchorMin = new Vector2(0.5f, 0.40f);
            menuRt.anchorMax = new Vector2(0.5f, 0.40f);
            menuRt.pivot = new Vector2(0.5f, 0.5f);
            menuRt.anchoredPosition = Vector2.zero;
            menuRt.sizeDelta = new Vector2(680f, 360f);

            // Panel Menú Principal
            GameObject rootPanel = CreateUIElement("RootMenu_Panel", menuContainerObj.transform);
            StretchFull(rootPanel.GetComponent<RectTransform>());

            Button btnStory = CreateMenuButton("Btn_ModoHistoria", rootPanel.transform, "MODO HISTORIA (Ryu vs Ken)", retroFont, new Vector2(0f, 105f));
            Button btnVersus = CreateMenuButton("Btn_Versus", rootPanel.transform, "VERSUS (Duelos)", retroFont, new Vector2(0f, 35f));
            Button btnMinijuegos = CreateMenuButton("Btn_Minijuegos", rootPanel.transform, "MINIJUEGOS ARCADE", retroFont, new Vector2(0f, -35f));
            Button btnExit = CreateMenuButton("Btn_Salir", rootPanel.transform, "SALIR", retroFont, new Vector2(0f, -105f));

            // Panel Submenú Versus
            GameObject versusPanel = CreateUIElement("VersusSubmenu_Panel", menuContainerObj.transform);
            StretchFull(versusPanel.GetComponent<RectTransform>());
            versusPanel.SetActive(false);

            Button btnVersusBot = CreateMenuButton("Btn_VersusBot", versusPanel.transform, "VERSUS JAPÓN (Suzaku Castle)", retroFont, new Vector2(0f, 105f));
            Button btnVersus2P = CreateMenuButton("Btn_Versus2P", versusPanel.transform, "VERSUS CHINA (Crowded Street)", retroFont, new Vector2(0f, 35f));
            Button btnVersusTomb = CreateMenuButton("Btn_VersusTomb", versusPanel.transform, "VERSUS GRECIA (Tomb of Urien)", retroFont, new Vector2(0f, -35f));
            Button btnBackVersus = CreateMenuButton("Btn_VolverVersus", versusPanel.transform, "VOLVER (Atrás)", retroFont, new Vector2(0f, -105f));

            // Panel Submenú Minijuegos
            GameObject minigamesPanel = CreateUIElement("MinigamesSubmenu_Panel", menuContainerObj.transform);
            StretchFull(minigamesPanel.GetComponent<RectTransform>());
            minigamesPanel.SetActive(false);

            Button btnMinigameWaypoint = CreateMenuButton("Btn_MinigameWaypoint", minigamesPanel.transform, "1. SIGILO & WAYPOINTS (Rinnegan)", retroFont, new Vector2(0f, 105f));
            Button btnMinigameNeonSiege = CreateMenuButton("Btn_MinigameNeonSiege", minigamesPanel.transform, "2. NEON SIEGE (Balística 2D)", retroFont, new Vector2(0f, 35f));
            Button btnMinigameLoading = CreateMenuButton("Btn_MinigameLoading", minigamesPanel.transform, "3. AVATAR DE CARGA DBZ", retroFont, new Vector2(0f, -35f));
            Button btnBackMinigames = CreateMenuButton("Btn_VolverMinigames", minigamesPanel.transform, "VOLVER (Atrás)", retroFont, new Vector2(0f, -105f));

            // Cursor Indicador (>>)
            GameObject cursorObj = CreateUIElement("Cursor_Indicator", menuContainerObj.transform);
            RectTransform cursorRt = cursorObj.GetComponent<RectTransform>();
            cursorRt.sizeDelta = new Vector2(50f, 50f);
            Text cursorText = cursorObj.AddComponent<Text>();
            cursorText.font = retroFont;
            cursorText.text = ">>";
            cursorText.fontSize = 38;
            cursorText.fontStyle = FontStyle.Bold;
            cursorText.alignment = TextAnchor.MiddleCenter;
            cursorText.color = new Color(1f, 0.85f, 0.1f, 1f);

            // Pie de página con instrucciones
            GameObject footerObj = CreateUIElement("Footer_Help", canvasObj.transform);
            RectTransform footerRt = footerObj.GetComponent<RectTransform>();
            footerRt.anchorMin = new Vector2(0.5f, 0f);
            footerRt.anchorMax = new Vector2(0.5f, 0f);
            footerRt.pivot = new Vector2(0.5f, 0f);
            footerRt.anchoredPosition = new Vector2(0f, 35f);
            footerRt.sizeDelta = new Vector2(1200f, 40f);

            CreateText("Text_Instructions", footerObj.transform, "NAVEGACIÓN: [W / S o Flechas] Seleccionar   |   [ENTER o ESPACIO] Confirmar   |   [ESC] Volver",
                retroFont, 19, FontStyle.Normal, new Color(0.7f, 0.75f, 0.8f, 0.85f), Vector2.zero, new Vector2(1200f, 40f));

            // 8. Pantalla de Carga y Minijuego DBZ Tenkaichi 3
            GameObject loadingCanvasObj = CreateUIElement("Panel_LoadingScreen", canvasObj.transform);
            StretchFull(loadingCanvasObj.GetComponent<RectTransform>());
            CanvasGroup loadingGroup = loadingCanvasObj.AddComponent<CanvasGroup>();
            loadingGroup.alpha = 0f;
            loadingGroup.interactable = false;
            loadingGroup.blocksRaycasts = false;

            Image loadingBg = loadingCanvasObj.AddComponent<Image>();
            loadingBg.color = new Color(0.04f, 0.05f, 0.08f, 0.98f);

            Text loadingStatusText = CreateText("Text_LoadingTitle", loadingCanvasObj.transform, "NOW LOADING...", retroFont, 46, FontStyle.Bold,
                new Color(0.2f, 0.9f, 1f, 1f), new Vector2(0f, 410f), new Vector2(900f, 60f));

            // Barra de Carga
            GameObject barBgObj = CreateUIElement("ProgressBar_BG", loadingCanvasObj.transform);
            RectTransform barBgRt = barBgObj.GetComponent<RectTransform>();
            barBgRt.anchoredPosition = new Vector2(0f, 340f);
            barBgRt.sizeDelta = new Vector2(760f, 28f);
            Image barBgImg = barBgObj.AddComponent<Image>();
            barBgImg.color = new Color(0.12f, 0.15f, 0.22f, 0.9f);

            GameObject barFillObj = CreateUIElement("ProgressBar_Fill", barBgObj.transform);
            RectTransform barFillRt = barFillObj.GetComponent<RectTransform>();
            barFillRt.anchorMin = new Vector2(0f, 0f);
            barFillRt.anchorMax = new Vector2(0f, 1f);
            barFillRt.pivot = new Vector2(0f, 0.5f);
            barFillRt.sizeDelta = new Vector2(0f, 0f);
            Image barFillImg = barFillObj.AddComponent<Image>();
            barFillImg.color = new Color(1f, 0.82f, 0.15f, 1f);
            barFillImg.type = Image.Type.Filled;
            barFillImg.fillMethod = Image.FillMethod.Horizontal;
            barFillImg.fillAmount = 0f;

            Text progressText = CreateText("Text_ProgressPercent", barBgObj.transform, "0%", retroFont, 18, FontStyle.Bold,
                Color.white, Vector2.zero, new Vector2(200f, 26f));

            // Área del Minijuego
            GameObject minigameAreaObj = CreateUIElement("Area_MinigamePlayable", loadingCanvasObj.transform);
            RectTransform areaRt = minigameAreaObj.GetComponent<RectTransform>();
            areaRt.anchoredPosition = new Vector2(0f, -40f);
            areaRt.sizeDelta = new Vector2(1460f, 580f);

            Image areaBg = minigameAreaObj.AddComponent<Image>();
            areaBg.color = new Color(0.02f, 0.03f, 0.06f, 0.75f);

            // Bordes arcade
            CreateBorder(minigameAreaObj.transform, new Vector2(0f, 290f), new Vector2(1460f, 4f), new Color(0.2f, 0.9f, 1f, 0.9f));
            CreateBorder(minigameAreaObj.transform, new Vector2(0f, -290f), new Vector2(1460f, 4f), new Color(0.2f, 0.9f, 1f, 0.9f));
            CreateBorder(minigameAreaObj.transform, new Vector2(-730f, 0f), new Vector2(4f, 580f), new Color(0.2f, 0.9f, 1f, 0.9f));
            CreateBorder(minigameAreaObj.transform, new Vector2(730f, 0f), new Vector2(4f, 580f), new Color(0.2f, 0.9f, 1f, 0.9f));

            // Sprite de Hadouken para los orbes de carga
            Sprite hadoukenSprite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu/08_Super_Arts/Ryu_SA1_ShinkuHadouken_SuperFreeze/01.png")
                ?? AssetDatabase.LoadAssetAtPath<Sprite>("Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu/03_Special_Moves/Ryu_Hadouken_Startup/01.png");

            // Avatar Jugable
            GameObject fighterObj = CreateUIElement("MiniFighter_Player", minigameAreaObj.transform);
            RectTransform fighterRt = fighterObj.GetComponent<RectTransform>();
            fighterRt.sizeDelta = new Vector2(110f, 140f);
            fighterRt.anchoredPosition = new Vector2(-450f, -190f);

            Image fighterImg = fighterObj.AddComponent<Image>();
            Sprite ryuDefaultSprite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu/01_Core_Locomotion/Ryu_Idle/01.png");
            if (ryuDefaultSprite != null) fighterImg.sprite = ryuDefaultSprite;

            MiniFighterController miniFighter = fighterObj.AddComponent<MiniFighterController>();
            AssignField(miniFighter, "idleSprites", LoadSpriteSequence("Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu/01_Core_Locomotion/Ryu_Idle"));
            AssignField(miniFighter, "walkSprites", LoadSpriteSequence("Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu/01_Core_Locomotion/Ryu_Walk_Forward"));
            AssignField(miniFighter, "punchSprites", LoadSpriteSequence("Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu/02_Normal_Attacks/Ryu_Standing_Far_LP_Jab"));
            AssignField(miniFighter, "groundY", -190f);
            AssignField(miniFighter, "minX", -670f);
            AssignField(miniFighter, "maxX", 670f);
            AssignField(miniFighter, "jumpForce", 620f);
            AssignField(miniFighter, "moveSpeed", 360f);

            // Textos del Minijuego
            Text scoreText = CreateText("Text_MinigameScore", minigameAreaObj.transform, "ORBES: 0", retroFont, 24, FontStyle.Bold,
                new Color(1f, 0.85f, 0.1f, 1f), new Vector2(-540f, 250f), new Vector2(300f, 40f));
            scoreText.alignment = TextAnchor.MiddleLeft;

            Text minigameHelp = CreateText("Text_MinigameHelp", minigameAreaObj.transform,
                "MINIJUEGO INTERACTIVO: [A / D] Moverse   |   [W / Espacio] Saltar   |   [J] Puñetazo",
                retroFont, 18, FontStyle.Normal, new Color(0.85f, 0.85f, 0.9f, 0.9f), new Vector2(0f, -255f), new Vector2(1000f, 35f));

            // Administrador del Minijuego de Carga
            LoadingMinigameManager minigameMgr = loadingCanvasObj.AddComponent<LoadingMinigameManager>();
            AssignField(minigameMgr, "minigameContainer", areaRt);
            AssignField(minigameMgr, "playerFighter", miniFighter);
            AssignField(minigameMgr, "scoreText", scoreText);
            AssignField(minigameMgr, "targetSprite", hadoukenSprite);
            AssignField(minigameMgr, "areaBounds", new Vector2(680f, 260f));

            // Controlador de Pantalla de Carga
            LoadingScreenController loadingCtrl = loadingCanvasObj.AddComponent<LoadingScreenController>();
            AssignField(loadingCtrl, "loadingCanvasGroup", loadingGroup);
            AssignField(loadingCtrl, "progressBarFill", barFillImg);
            AssignField(loadingCtrl, "progressPercentText", progressText);
            AssignField(loadingCtrl, "loadingStatusText", loadingStatusText);
            AssignField(loadingCtrl, "minigameManager", minigameMgr);

            // 9. Ventana Modal "Próximamente"
            GameObject modalObj = CreateUIElement("Modal_ComingSoon_Kinect", canvasObj.transform);
            StretchFull(modalObj.GetComponent<RectTransform>());
            modalObj.SetActive(false);

            Image modalDimmer = modalObj.AddComponent<Image>();
            modalDimmer.color = new Color(0.02f, 0.03f, 0.05f, 0.85f);

            GameObject modalCard = CreateUIElement("Modal_Card", modalObj.transform);
            RectTransform cardRt = modalCard.GetComponent<RectTransform>();
            cardRt.sizeDelta = new Vector2(750f, 420f);
            Image cardBg = modalCard.AddComponent<Image>();
            cardBg.color = new Color(0.08f, 0.10f, 0.16f, 0.98f);

            CreateBorder(modalCard.transform, new Vector2(0f, 210f), new Vector2(750f, 3f), new Color(1f, 0.82f, 0.15f, 1f));
            CreateBorder(modalCard.transform, new Vector2(0f, -210f), new Vector2(750f, 3f), new Color(1f, 0.82f, 0.15f, 1f));

            CreateText("Modal_Title", modalCard.transform, "MODO HISTORIA — KINET STRIKE", retroFont, 32, FontStyle.Bold,
                new Color(1f, 0.82f, 0.15f, 1f), new Vector2(0f, 140f), new Vector2(700f, 50f));

            CreateText("Modal_Desc", modalCard.transform,
                "El Modo Historia integra cinemáticas somatosensoriales y combates por capítulos.\n\n" +
                "El Episodio I te llevará a la batalla de Suzaku Castle entre Ryu y Ken con narrativa estilo arcade.\n\n" +
                "Presiona ENTER o ESPACIO para continuar.",
                retroFont, 20, FontStyle.Normal, new Color(0.9f, 0.9f, 0.95f, 1f), new Vector2(0f, 15f), new Vector2(650f, 180f));

            Button btnModalClose = CreateMenuButton("Btn_ModalClose", modalCard.transform, "ENTENDIDO [ENTER]", retroFont, new Vector2(0f, -140f));

            // 10. Audio Manager
            GameObject audioMgrObj = new GameObject("AudioManager_MainMenu");
            AudioSource bgmSource = audioMgrObj.AddComponent<AudioSource>();
            bgmSource.loop = true;
            bgmSource.volume = 0.45f;
            bgmSource.playOnAwake = false;

            AudioClip bgmClip = AssetDatabase.LoadAssetAtPath<AudioClip>("Assets/StreetFighter3_ThirdStrike/Resources/Audio/BGM_Japan.mp3")
                ?? AssetDatabase.LoadAssetAtPath<AudioClip>("Assets/StreetFighter3_ThirdStrike/Audio/BGM/02_Player_Select.mp3");
            bgmSource.clip = bgmClip;
            if (bgmClip != null) bgmSource.Play();

            AudioSource sfxSource = audioMgrObj.AddComponent<AudioSource>();
            sfxSource.playOnAwake = false;

            AudioClip cursorSfx = AssetDatabase.LoadAssetAtPath<AudioClip>("Assets/StreetFighter3_ThirdStrike/Audio/SFX/05_Announcer_and_Interface/Menu_Cursor_Select.wav");
            AudioClip confirmSfx = AssetDatabase.LoadAssetAtPath<AudioClip>("Assets/StreetFighter3_ThirdStrike/Audio/SFX/05_Announcer_and_Interface/Menu_Confirm_Start.wav");

            // 11. MainMenuController
            MainMenuController menuCtrl = canvasObj.AddComponent<MainMenuController>();
            AssignField(menuCtrl, "rootMenuPanel", rootPanel);
            AssignField(menuCtrl, "versusSubmenuPanel", versusPanel);
            AssignField(menuCtrl, "minigamesSubmenuPanel", minigamesPanel);
            AssignField(menuCtrl, "cursorIndicator", cursorRt);
            AssignField(menuCtrl, "storyModeButton", btnStory);
            AssignField(menuCtrl, "versusButton", btnVersus);
            AssignField(menuCtrl, "minigamesButton", btnMinijuegos);
            AssignField(menuCtrl, "exitButton", btnExit);

            AssignField(menuCtrl, "versusBotButton", btnVersusBot);
            AssignField(menuCtrl, "versus2PlayerButton", btnVersus2P);
            AssignField(menuCtrl, "versusTombButton", btnVersusTomb);
            AssignField(menuCtrl, "backVersusButton", btnBackVersus);

            AssignField(menuCtrl, "minigameWaypointButton", btnMinigameWaypoint);
            AssignField(menuCtrl, "minigameNeonSiegeButton", btnMinigameNeonSiege);
            AssignField(menuCtrl, "minigameLoadingButton", btnMinigameLoading);
            AssignField(menuCtrl, "backMinigamesButton", btnBackMinigames);

            AssignField(menuCtrl, "duelSceneName", "Sandbox_Sebas");
            AssignField(menuCtrl, "duelSceneChina", "Sandbox_China");
            AssignField(menuCtrl, "duelSceneTomb", "Sandbox_Tomb");
            AssignField(menuCtrl, "storyModeScene", "StoryMode_Scene");
            AssignField(menuCtrl, "waypointSceneName", "minijuegowaypoint");
            AssignField(menuCtrl, "neonSiegeSceneName", "NeonSiege");

            AssignField(menuCtrl, "bgmAudioSource", bgmSource);
            AssignField(menuCtrl, "sfxAudioSource", sfxSource);
            AssignField(menuCtrl, "cursorMoveSfx", cursorSfx);
            AssignField(menuCtrl, "confirmSelectSfx", confirmSfx);
            AssignField(menuCtrl, "cancelBackSfx", cursorSfx);
            AssignField(menuCtrl, "loadingScreenController", loadingCtrl);
            AssignField(menuCtrl, "comingSoonModalPanel", modalObj);

            // 12. Guardar Escena
            if (!Directory.Exists(SceneFolder)) Directory.CreateDirectory(SceneFolder);
            EditorSceneManager.SaveScene(scene, ScenePath);
            Debug.Log($"✅ [SF3 Builder] Escena de Menú guardada exitosamente en: {ScenePath}");

            // 13. Sincronizar Build Settings
            EnsureBuildSettings();
        }

        private static void CreateBorder(Transform parent, Vector2 pos, Vector2 size, Color color)
        {
            GameObject border = CreateUIElement("Border", parent);
            RectTransform rt = border.GetComponent<RectTransform>();
            rt.anchoredPosition = pos;
            rt.sizeDelta = size;
            Image img = border.AddComponent<Image>();
            img.color = color;
        }

        public static void EnsureBuildSettings()
        {
            var scenes = EditorBuildSettings.scenes.ToList();
            bool changed = false;

            string[] requiredScenes = new string[]
            {
                ScenePath,
                StoryScenePath,
                DuelScenePath,
                ChinaDuelPath,
                TombDuelPath,
                WaypointScenePath,
                NeonSiegeScenePath
            };

            for (int i = 0; i < requiredScenes.Length; i++)
            {
                string path = requiredScenes[i];
                if (!scenes.Any(s => s.path == path) && File.Exists(path))
                {
                    scenes.Add(new EditorBuildSettingsScene(path, true));
                    changed = true;
                }
            }

            if (changed)
            {
                EditorBuildSettings.scenes = scenes.ToArray();
                Debug.Log("🔄 [SF3 Builder] Todas las escenas sincronizadas en EditorBuildSettings.");
            }
        }

        private static GameObject CreateUIElement(string name, Transform parent)
        {
            GameObject go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.AddComponent<RectTransform>();
            return go;
        }

        private static void StretchFull(RectTransform rt)
        {
            rt.anchorMin = Vector2.zero;
            rt.anchorMax = Vector2.one;
            rt.offsetMin = Vector2.zero;
            rt.offsetMax = Vector2.zero;
        }

        private static Button CreateMenuButton(string name, Transform parent, string label, Font font, Vector2 position)
        {
            GameObject btnObj = CreateUIElement(name, parent);
            RectTransform rt = btnObj.GetComponent<RectTransform>();
            rt.anchoredPosition = position;
            rt.sizeDelta = new Vector2(520f, 56f);

            Image img = btnObj.AddComponent<Image>();
            img.color = new Color(0.08f, 0.10f, 0.16f, 0.85f);

            Button btn = btnObj.AddComponent<Button>();

            Text txt = CreateText("Label", btnObj.transform, label, font, 24, FontStyle.Bold,
                new Color(0.85f, 0.85f, 0.85f, 1f), Vector2.zero, new Vector2(500f, 50f));
            txt.alignment = TextAnchor.MiddleCenter;

            return btn;
        }

        private static Text CreateText(string name, Transform parent, string content, Font font, int size, FontStyle style, Color color, Vector2 pos, Vector2 sizeDelta)
        {
            GameObject go = CreateUIElement(name, parent);
            RectTransform rt = go.GetComponent<RectTransform>();
            rt.anchoredPosition = pos;
            rt.sizeDelta = sizeDelta;

            Text txt = go.AddComponent<Text>();
            txt.font = font;
            txt.text = content;
            txt.fontSize = size;
            txt.fontStyle = style;
            txt.color = color;
            txt.alignment = TextAnchor.MiddleCenter;

            return txt;
        }

        private static Font GetRetroFont()
        {
            Font font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            if (font == null) font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            return font;
        }

        private static Sprite[] LoadSpriteSequence(string folderPath)
        {
            if (!Directory.Exists(folderPath)) return new Sprite[0];

            string[] files = Directory.GetFiles(folderPath, "*.png");
            System.Array.Sort(files, (a, b) =>
            {
                string na = Path.GetFileNameWithoutExtension(a);
                string nb = Path.GetFileNameWithoutExtension(b);
                int ia, ib;
                if (int.TryParse(na, out ia) && int.TryParse(nb, out ib)) return ia.CompareTo(ib);
                return string.Compare(na, nb, System.StringComparison.Ordinal);
            });

            List<Sprite> sprites = new List<Sprite>();
            foreach (string file in files)
            {
                Sprite sp = AssetDatabase.LoadAssetAtPath<Sprite>(file);
                if (sp != null) sprites.Add(sp);
            }
            return sprites.ToArray();
        }

        private static void AssignField(object target, string fieldName, object value)
        {
            var field = target.GetType().GetField(fieldName, System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance);
            if (field != null)
            {
                field.SetValue(target, value);
            }
        }
    }
}
