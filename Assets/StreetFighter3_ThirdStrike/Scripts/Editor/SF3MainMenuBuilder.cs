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
            titleRt.anchoredPosition = new Vector2(0f, -80f);
            titleRt.sizeDelta = new Vector2(1200f, 220f);

            CreateText("Header_CPS3", titleObj.transform, "SOMATOSENSORY 3D COMBAT SYSTEM", retroFont, 20, FontStyle.Bold,
                new Color(0.85f, 0.75f, 0.4f, 0.85f), new Vector2(0f, -20f), new Vector2(1000f, 30f));

            CreateText("Title_SF3", titleObj.transform, "KINET STRIKE", retroFont, 76, FontStyle.Bold,
                new Color(1f, 0.82f, 0.15f, 1f), new Vector2(0f, -75f), new Vector2(1200f, 95f));

            CreateText("Subtitle_Strike", titleObj.transform, "KINECT 3D & ADAPTIVE AI FIGHTING SYSTEM", retroFont, 36, FontStyle.Bold,
                new Color(0.2f, 0.9f, 1f, 1f), new Vector2(0f, -145f), new Vector2(1000f, 50f));

            // 7. Contenedor de Botones de Menú
            GameObject menuContainerObj = CreateUIElement("Menu_Container", canvasObj.transform);
            RectTransform menuRt = menuContainerObj.GetComponent<RectTransform>();
            menuRt.anchorMin = new Vector2(0.5f, 0.42f);
            menuRt.anchorMax = new Vector2(0.5f, 0.42f);
            menuRt.pivot = new Vector2(0.5f, 0.5f);
            menuRt.anchoredPosition = Vector2.zero;
            menuRt.sizeDelta = new Vector2(600f, 320f);

            // Panel Menú Principal
            GameObject rootPanel = CreateUIElement("RootMenu_Panel", menuContainerObj.transform);
            StretchFull(rootPanel.GetComponent<RectTransform>());

            Button btnStory = CreateMenuButton("Btn_ModoHistoria", rootPanel.transform, "MODO HISTORIA", retroFont, new Vector2(0f, 70f));
            Button btnVersus = CreateMenuButton("Btn_Versus", rootPanel.transform, "VERSUS", retroFont, new Vector2(0f, -10f));
            Button btnExit = CreateMenuButton("Btn_Salir", rootPanel.transform, "SALIR", retroFont, new Vector2(0f, -90f));

            // Panel Submenú Versus
            GameObject versusPanel = CreateUIElement("VersusSubmenu_Panel", menuContainerObj.transform);
            StretchFull(versusPanel.GetComponent<RectTransform>());
            versusPanel.SetActive(false);

            Button btnVersusBot = CreateMenuButton("Btn_VersusBot", versusPanel.transform, "VERSUS JAPÓN (Suzaku Castle)", retroFont, new Vector2(0f, 95f));
            Button btnVersus2P = CreateMenuButton("Btn_Versus2P", versusPanel.transform, "VERSUS CHINA (Crowded Street)", retroFont, new Vector2(0f, 35f));
            Button btnVersusTomb = CreateMenuButton("Btn_VersusTomb", versusPanel.transform, "VERSUS OLIMPO (Tomb of Urien)", retroFont, new Vector2(0f, -25f));
            Button btnBackVersus = CreateMenuButton("Btn_Volver", versusPanel.transform, "VOLVER (Atrás)", retroFont, new Vector2(0f, -85f));

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
            footerRt.sizeDelta = new Vector2(1000f, 40f);

            CreateText("Text_Instructions", footerObj.transform, "NAVEGACIÓN: [W / S o Flechas] Seleccionar   |   [ENTER o ESPACIO] Confirmar   |   [ESC] Volver",
                retroFont, 19, FontStyle.Normal, new Color(0.7f, 0.75f, 0.8f, 0.85f), Vector2.zero, new Vector2(1000f, 40f));

            // 8. Pantalla de Carga y Minijuego DBZ Tenkaichi 3
            GameObject loadingCanvasObj = CreateUIElement("Panel_LoadingScreen", canvasObj.transform);
            StretchFull(loadingCanvasObj.GetComponent<RectTransform>());
            CanvasGroup loadingGroup = loadingCanvasObj.AddComponent<CanvasGroup>();
            loadingGroup.alpha = 0f;
            loadingGroup.interactable = false;
            loadingGroup.blocksRaycasts = false;

            // Fondo pantalla de carga
            Image loadingBg = loadingCanvasObj.AddComponent<Image>();
            loadingBg.color = new Color(0.04f, 0.05f, 0.08f, 0.98f);

            // Header Loading
            Text loadingStatusText = CreateText("Text_LoadingTitle", loadingCanvasObj.transform, "NOW LOADING...", retroFont, 46, FontStyle.Bold,
                new Color(0.2f, 0.9f, 1f, 1f), new Vector2(0f, 410f), new Vector2(900f, 60f));

            // Barra de Carga (Más amplia)
            GameObject barBgObj = CreateUIElement("ProgressBar_BG", loadingCanvasObj.transform);
            RectTransform barBgRt = barBgObj.GetComponent<RectTransform>();
            barBgRt.anchoredPosition = new Vector2(0f, 350f);
            barBgRt.sizeDelta = new Vector2(960f, 26f);
            Image barBgImg = barBgObj.AddComponent<Image>();
            barBgImg.color = new Color(0.12f, 0.15f, 0.22f, 1f);

            GameObject barFillObj = CreateUIElement("ProgressBar_Fill", barBgObj.transform);
            StretchFull(barFillObj.GetComponent<RectTransform>());
            Image barFillImg = barFillObj.AddComponent<Image>();
            barFillImg.type = Image.Type.Filled;
            barFillImg.fillMethod = Image.FillMethod.Horizontal;
            barFillImg.fillOrigin = (int)Image.OriginHorizontal.Left;
            barFillImg.fillAmount = 0.15f;
            barFillImg.color = new Color(1f, 0.82f, 0.15f, 1f);

            Text progressPercentText = CreateText("Text_Percentage", loadingCanvasObj.transform, "15%", retroFont, 24, FontStyle.Bold,
                new Color(1f, 0.9f, 0.3f, 1f), new Vector2(0f, 310f), new Vector2(200f, 35f));

            Text promptContinueText = CreateText("Text_PromptContinue", loadingCanvasObj.transform, "ROUND READY! PRESIONA ENTER", retroFont, 24, FontStyle.Bold,
                new Color(0.3f, 1f, 0.4f, 1f), new Vector2(0f, 275f), new Vector2(800f, 35f));
            promptContinueText.gameObject.SetActive(false);

            // 9. Contenedor del Minijuego (DBZ Budokai Tenkaichi 3 Style - ÁREA AMPLIADA)
            GameObject minigameContainer = CreateUIElement("Minigame_Arena", loadingCanvasObj.transform);
            RectTransform miniRt = minigameContainer.GetComponent<RectTransform>();
            miniRt.anchoredPosition = new Vector2(0f, -40f);
            miniRt.sizeDelta = new Vector2(1460f, 580f);

            Image miniArenaImg = minigameContainer.AddComponent<Image>();
            miniArenaImg.color = new Color(0.08f, 0.1f, 0.15f, 0.88f);

            // Línea de suelo del dojo
            GameObject floorLine = CreateUIElement("Arena_Floor", minigameContainer.transform);
            RectTransform floorRt = floorLine.GetComponent<RectTransform>();
            floorRt.anchoredPosition = new Vector2(0f, -220f);
            floorRt.sizeDelta = new Vector2(1420f, 4f);
            Image floorImg = floorLine.AddComponent<Image>();
            floorImg.color = new Color(0.3f, 0.45f, 0.65f, 0.9f);

            // Cargar Sprites de Ryu para el MiniFighter
            Sprite[] ryuIdle = LoadSpriteSequence("Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu/01_Movement/idle_stance");
            Sprite[] ryuWalk = LoadSpriteSequence("Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu/01_Movement/walk_forward");
            Sprite[] ryuPunch = LoadSpriteSequence("Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu/02_Normals/light_punch");
            Sprite[] ryuJump = LoadSpriteSequence("Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu/01_Movement/jump_neutral");

            // Avatar del Jugador (MiniFighter - Escalado y con mayor rango de movimiento)
            GameObject playerFighterObj = CreateUIElement("MiniFighter_Player", minigameContainer.transform);
            RectTransform playerRt = playerFighterObj.GetComponent<RectTransform>();
            playerRt.anchoredPosition = new Vector2(0f, -215f);
            playerRt.sizeDelta = new Vector2(130f, 175f);
            Image playerImg = playerFighterObj.AddComponent<Image>();
            if (ryuIdle != null && ryuIdle.Length > 0) playerImg.sprite = ryuIdle[0];
            playerImg.preserveAspect = true;

            MiniFighterController miniFighter = playerFighterObj.AddComponent<MiniFighterController>();
            miniFighter.SetupSprites(ryuIdle, ryuWalk, ryuPunch, ryuJump);
            miniFighter.ConfigureBoundsAndGround(-215f, new Vector2(-670f, 670f), 650f, 400f);

            // Sprites de orbes y perseguidor
            Sprite orbSprite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/StreetFighter3_ThirdStrike/Effects/13_Hadouken_Energy_Aura_Blue/3.png");
            Sprite chaserSprite = AssetDatabase.LoadAssetAtPath<Sprite>("Assets/StreetFighter3_ThirdStrike/Effects/06_Hit_Spark_Electric_Yellow/10.png");

            AudioClip collectSfx = AssetDatabase.LoadAssetAtPath<AudioClip>("Assets/StreetFighter3_ThirdStrike/Audio/SFX/05_Announcer_and_Interface/Bonus_Basketball_Bounce.wav");
            AudioClip punchSfx = AssetDatabase.LoadAssetAtPath<AudioClip>("Assets/StreetFighter3_ThirdStrike/Audio/SFX/01_Combat_Hits/Hit_Punch_Light.wav");

            // Textos del Minijuego
            Text scoreText = CreateText("Text_Score", minigameContainer.transform, "PUNTOS DBZ: 0000", retroFont, 24, FontStyle.Bold,
                new Color(1f, 0.85f, 0.15f, 1f), new Vector2(-510f, 250f), new Vector2(360f, 40f));
            scoreText.alignment = TextAnchor.MiddleLeft;

            Text algoBadgeText = CreateText("Text_AlgoBadge", minigameContainer.transform, "⚡ CINEMÁTICA IA: [Wandering: 3 Orbes] + [Seeking: Perseguidor Hadouken]",
                retroFont, 18, FontStyle.Bold, new Color(0.2f, 0.9f, 1f, 1f), new Vector2(240f, 250f), new Vector2(800f, 40f));
            algoBadgeText.alignment = TextAnchor.MiddleRight;

            Text hintText = CreateText("Text_ControlsHint", minigameContainer.transform, "🎮 CONTROLES: [A / D] Moverse  |  [W] Saltar  |  [J / F / ESPACIO] Golpear Orbes",
                retroFont, 18, FontStyle.Normal, new Color(0.75f, 0.8f, 0.9f, 0.95f), new Vector2(0f, -255f), new Vector2(1200f, 35f));

            // LoadingMinigameManager (Área ampliada a 670 x 240)
            LoadingMinigameManager minigameMgr = minigameContainer.AddComponent<LoadingMinigameManager>();
            AssignField(minigameMgr, "minigameContainer", miniRt);
            AssignField(minigameMgr, "playerFighter", miniFighter);
            AssignField(minigameMgr, "scoreText", scoreText);
            AssignField(minigameMgr, "algoBadgeText", algoBadgeText);
            AssignField(minigameMgr, "hintText", hintText);
            AssignField(minigameMgr, "targetSprite", orbSprite);
            AssignField(minigameMgr, "chaserSprite", chaserSprite);
            AssignField(minigameMgr, "collectSound", collectSfx);
            AssignField(minigameMgr, "punchSound", punchSfx);
            AssignField(minigameMgr, "areaBounds", new Vector2(670f, 240f));

            // LoadingScreenController
            LoadingScreenController loadingCtrl = loadingCanvasObj.AddComponent<LoadingScreenController>();
            AssignField(loadingCtrl, "loadingCanvasGroup", loadingGroup);
            AssignField(loadingCtrl, "progressBarFill", barFillImg);
            AssignField(loadingCtrl, "loadingStatusText", loadingStatusText);
            AssignField(loadingCtrl, "progressPercentageText", progressPercentText);
            AssignField(loadingCtrl, "continuePromptText", promptContinueText);
            AssignField(loadingCtrl, "minigameManager", minigameMgr);

            // 10. Modal "PRÓXIMAMENTE" para Modo Historia
            GameObject modalObj = CreateUIElement("Modal_Proximamente", canvasObj.transform);
            StretchFull(modalObj.GetComponent<RectTransform>());
            Image modalBg = modalObj.AddComponent<Image>();
            modalBg.color = new Color(0.02f, 0.03f, 0.05f, 0.88f);

            GameObject modalBox = CreateUIElement("Modal_Box", modalObj.transform);
            RectTransform boxRt = modalBox.GetComponent<RectTransform>();
            boxRt.sizeDelta = new Vector2(880f, 460f);
            Image boxImg = modalBox.AddComponent<Image>();
            boxImg.color = new Color(0.08f, 0.10f, 0.16f, 0.98f);

            // Bordes dorados de la ventana
            CreateBorder(modalBox.transform, new Vector2(0f, 228f), new Vector2(880f, 4f), new Color(1f, 0.82f, 0.15f, 0.9f));
            CreateBorder(modalBox.transform, new Vector2(0f, -228f), new Vector2(880f, 4f), new Color(1f, 0.82f, 0.15f, 0.9f));
            CreateBorder(modalBox.transform, new Vector2(-438f, 0f), new Vector2(4f, 460f), new Color(1f, 0.82f, 0.15f, 0.9f));
            CreateBorder(modalBox.transform, new Vector2(438f, 0f), new Vector2(4f, 460f), new Color(1f, 0.82f, 0.15f, 0.9f));

            CreateText("Modal_Title", modalBox.transform, "MODO HISTORIA", retroFont, 40, FontStyle.Bold,
                new Color(1f, 0.85f, 0.15f, 1f), new Vector2(0f, 155f), new Vector2(800f, 50f));

            CreateText("Modal_Subtitle", modalBox.transform, "¡PRÓXIMAMENTE!", retroFont, 30, FontStyle.Bold,
                new Color(0.2f, 0.9f, 1f, 1f), new Vector2(0f, 105f), new Vector2(800f, 40f));

            CreateText("Modal_Description", modalBox.transform,
                "El Modo Historia integrará el control somatosensorial por hardware con Azure Kinect DK e IA Adaptativa.\n\nEn este modo enfrentarás la campaña ejecutando golpes, patadas y bloqueos con tu propio cuerpo en tiempo real.\n\nActualmente en desarrollo para el Sprint 2.",
                retroFont, 21, FontStyle.Normal, new Color(0.85f, 0.88f, 0.92f, 1f), new Vector2(0f, -10f), new Vector2(780f, 160f));

            CreateText("Modal_DismissPrompt", modalBox.transform, "[ PRESIONA ENTER, ESPACIO O ESC PARA VOLVER ]", retroFont, 20, FontStyle.Bold,
                new Color(1f, 0.88f, 0.2f, 1f), new Vector2(0f, -180f), new Vector2(800f, 35f));

            modalObj.SetActive(false);

            // 10. Audio Manager del Menú
            GameObject audioMgrObj = new GameObject("Menu_Audio");
            AudioSource bgmSource = audioMgrObj.AddComponent<AudioSource>();
            bgmSource.loop = true;
            bgmSource.playOnAwake = true;
            bgmSource.volume = 0.65f;
            AudioClip bgmClip = AssetDatabase.LoadAssetAtPath<AudioClip>("Assets/StreetFighter3_ThirdStrike/Audio/BGM/01_Opening_Demo.mp3")
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
            AssignField(menuCtrl, "cursorIndicator", cursorRt);
            AssignField(menuCtrl, "storyModeButton", btnStory);
            AssignField(menuCtrl, "versusButton", btnVersus);
            AssignField(menuCtrl, "exitButton", btnExit);
            AssignField(menuCtrl, "versusBotButton", btnVersusBot);
            AssignField(menuCtrl, "versus2PlayerButton", btnVersus2P);
            AssignField(menuCtrl, "versusTombButton", btnVersusTomb);
            AssignField(menuCtrl, "backVersusButton", btnBackVersus);
            AssignField(menuCtrl, "duelSceneChina", "Sandbox_China");
            AssignField(menuCtrl, "duelSceneTomb", "Sandbox_Tomb");
            AssignField(menuCtrl, "bgmAudioSource", bgmSource);
            AssignField(menuCtrl, "sfxAudioSource", sfxSource);
            AssignField(menuCtrl, "cursorMoveSfx", cursorSfx);
            AssignField(menuCtrl, "confirmSelectSfx", confirmSfx);
            AssignField(menuCtrl, "cancelBackSfx", cursorSfx);
            AssignField(menuCtrl, "loadingScreenController", loadingCtrl);
            AssignField(menuCtrl, "duelSceneName", "Sandbox_Sebas");
            AssignField(menuCtrl, "comingSoonModalPanel", modalObj);

            // 12. Guardar Escena
            if (!Directory.Exists(SceneFolder)) Directory.CreateDirectory(SceneFolder);
            EditorSceneManager.SaveScene(scene, ScenePath);
            Debug.Log($"✅ [SF3 Builder] Escena de Menú guardada exitosamente en: {ScenePath}");

            // 13. Sincronizar Build Settings
            EnsureBuildSettings(ScenePath, DuelScenePath);
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

        private static void EnsureBuildSettings(string menuPath, string duelPath)
        {
            var scenes = EditorBuildSettings.scenes.ToList();
            bool changed = false;

            if (!scenes.Any(s => s.path == menuPath))
            {
                scenes.Insert(0, new EditorBuildSettingsScene(menuPath, true));
                changed = true;
            }
            if (!scenes.Any(s => s.path == duelPath) && File.Exists(duelPath))
            {
                scenes.Add(new EditorBuildSettingsScene(duelPath, true));
                changed = true;
            }
            string chinaDuelPath = "Assets/StreetFighter3_ThirdStrike/Scenes/Sandbox_China.unity";
            if (!scenes.Any(s => s.path == chinaDuelPath) && File.Exists(chinaDuelPath))
            {
                scenes.Add(new EditorBuildSettingsScene(chinaDuelPath, true));
                changed = true;
            }
            string tombDuelPath = "Assets/StreetFighter3_ThirdStrike/Scenes/Sandbox_Tomb.unity";
            if (!scenes.Any(s => s.path == tombDuelPath) && File.Exists(tombDuelPath))
            {
                scenes.Add(new EditorBuildSettingsScene(tombDuelPath, true));
                changed = true;
            }

            if (changed)
            {
                EditorBuildSettings.scenes = scenes.ToArray();
                Debug.Log("🔄 [SF3 Builder] Escenas sincronizadas en EditorBuildSettings.");
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
            rt.sizeDelta = new Vector2(460f, 62f);

            Image img = btnObj.AddComponent<Image>();
            img.color = new Color(0.1f, 0.12f, 0.18f, 0.75f);

            Button btn = btnObj.AddComponent<Button>();

            // Texto interno
            Text txt = CreateText("Label", btnObj.transform, label, font, 28, FontStyle.Bold,
                new Color(0.85f, 0.85f, 0.85f, 1f), Vector2.zero, new Vector2(440f, 55f));
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
