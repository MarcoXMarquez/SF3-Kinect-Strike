using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using StreetFighter3.UI;

namespace StreetFighter3.Editor
{
    public static class SF3StoryModeBuilder
    {
        private const string SceneFolder = "Assets/StreetFighter3_ThirdStrike/Scenes";
        private const string StoryScenePath = "Assets/StreetFighter3_ThirdStrike/Scenes/StoryMode_Scene.unity";

        [MenuItem("SF3 Tools/Build Story Mode Scene")]
        public static void BuildStoryModeScene()
        {
            Debug.Log("[SF3 Builder] Construyendo Escena del Modo Historia con Pantalla Negra Narrativa Ryu vs Ken...");

            if (!Directory.Exists(SceneFolder))
            {
                Directory.CreateDirectory(SceneFolder);
            }

            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            Font retroFont = GetRetroFont();

            // 1. Cámara 2D
            GameObject camObj = new GameObject("Main Camera");
            Camera cam = camObj.AddComponent<Camera>();
            cam.orthographic = true;
            cam.orthographicSize = 5f;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0.01f, 0.015f, 0.025f, 1f);
            camObj.transform.position = new Vector3(0f, 0f, -10f);
            camObj.AddComponent<AudioListener>();

            // 2. EventSystem
            GameObject eventSystemObj = new GameObject("EventSystem");
            eventSystemObj.AddComponent<UnityEngine.EventSystems.EventSystem>();
            eventSystemObj.AddComponent<UnityEngine.EventSystems.StandaloneInputModule>();

            // 3. Canvas Principal
            GameObject canvasObj = new GameObject("Canvas_StoryMode");
            Canvas canvas = canvasObj.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 0;

            CanvasScaler scaler = canvasObj.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920f, 1080f);
            scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
            scaler.matchWidthOrHeight = 0.5f;

            canvasObj.AddComponent<GraphicRaycaster>();

            // 4. Fondo Negro Sólido
            GameObject bgObj = CreateUIElement("Black_Background", canvasObj.transform);
            StretchFull(bgObj.GetComponent<RectTransform>());
            Image bgImg = bgObj.AddComponent<Image>();
            bgImg.color = new Color(0.015f, 0.02f, 0.03f, 1f);

            // 5. Marco Dorado y Bordes Decorativos CPS-3
            GameObject borderObj = CreateUIElement("Arcade_Border_Frame", canvasObj.transform);
            RectTransform borderRt = borderObj.GetComponent<RectTransform>();
            borderRt.anchorMin = new Vector2(0.04f, 0.05f);
            borderRt.anchorMax = new Vector2(0.96f, 0.95f);
            borderRt.offsetMin = Vector2.zero;
            borderRt.offsetMax = Vector2.zero;
            Image borderImg = borderObj.AddComponent<Image>();
            borderImg.color = new Color(0.05f, 0.07f, 0.12f, 0.85f);

            // Línea dorada superior
            GameObject topGoldLine = CreateUIElement("Gold_Line_Top", borderObj.transform);
            RectTransform topRt = topGoldLine.GetComponent<RectTransform>();
            topRt.anchorMin = new Vector2(0f, 1f);
            topRt.anchorMax = new Vector2(1f, 1f);
            topRt.pivot = new Vector2(0.5f, 1f);
            topRt.sizeDelta = new Vector2(0f, 4f);
            Image topImg = topGoldLine.AddComponent<Image>();
            topImg.color = new Color(1f, 0.82f, 0.18f, 0.95f);

            // Línea dorada inferior
            GameObject btmGoldLine = CreateUIElement("Gold_Line_Bottom", borderObj.transform);
            RectTransform btmRt = btmGoldLine.GetComponent<RectTransform>();
            btmRt.anchorMin = new Vector2(0f, 0f);
            btmRt.anchorMax = new Vector2(1f, 0f);
            btmRt.pivot = new Vector2(0.5f, 0f);
            btmRt.sizeDelta = new Vector2(0f, 4f);
            Image btmImg = btmGoldLine.AddComponent<Image>();
            btmImg.color = new Color(1f, 0.82f, 0.18f, 0.95f);

            // 6. Header y Títulos
            GameObject headerObj = CreateUIElement("Header_Panel", borderObj.transform);
            RectTransform headerRt = headerObj.GetComponent<RectTransform>();
            headerRt.anchorMin = new Vector2(0.5f, 1f);
            headerRt.anchorMax = new Vector2(0.5f, 1f);
            headerRt.pivot = new Vector2(0.5f, 1f);
            headerRt.anchoredPosition = new Vector2(0f, -25f);
            headerRt.sizeDelta = new Vector2(1600f, 130f);

            Text headerTitle = CreateText("Header_Subtitle", headerObj.transform,
                "CAPCOM PLAY SYSTEM 3 — ARCADIA CINEMATIC PROLOGUE", retroFont, 18, FontStyle.Bold,
                new Color(0.85f, 0.75f, 0.35f, 0.85f), new Vector2(0f, 45f), new Vector2(1500f, 30f));

            Text mainTitle = CreateText("Header_MainTitle", headerObj.transform,
                "STREET FIGHTER III: 3rd STRIKE", retroFont, 52, FontStyle.Bold,
                new Color(1f, 0.84f, 0.15f, 1f), new Vector2(0f, 5f), new Vector2(1500f, 65f));

            Text epTitle = CreateText("Header_EpisodeTitle", headerObj.transform,
                "EPISODIO I: LA LLAMA DEL ANSATSUKEN — RYU VS KEN", retroFont, 24, FontStyle.Bold,
                new Color(0.2f, 0.9f, 1f, 1f), new Vector2(0f, -38f), new Vector2(1500f, 35f));

            // 7. Contenedor de Texto Principal (Pantalla Negra Narrativa)
            GameObject storyBoxObj = CreateUIElement("Story_TextBox", borderObj.transform);
            RectTransform storyBoxRt = storyBoxObj.GetComponent<RectTransform>();
            storyBoxRt.anchorMin = new Vector2(0.5f, 0.5f);
            storyBoxRt.anchorMax = new Vector2(0.5f, 0.5f);
            storyBoxRt.pivot = new Vector2(0.5f, 0.5f);
            storyBoxRt.anchoredPosition = new Vector2(0f, -20f);
            storyBoxRt.sizeDelta = new Vector2(1500f, 480f);

            // Fondo sutil del texto para legibilidad perfecta
            Image storyBoxBg = storyBoxObj.AddComponent<Image>();
            storyBoxBg.color = new Color(0.02f, 0.03f, 0.05f, 0.75f);

            GameObject textContentObj = CreateUIElement("Body_StoryText", storyBoxObj.transform);
            RectTransform textRt = textContentObj.GetComponent<RectTransform>();
            textRt.anchorMin = new Vector2(0f, 0f);
            textRt.anchorMax = new Vector2(1f, 1f);
            textRt.offsetMin = new Vector2(45f, 35f);
            textRt.offsetMax = new Vector2(-45f, -35f);

            Text bodyStoryText = textContentObj.AddComponent<Text>();
            bodyStoryText.font = retroFont;
            bodyStoryText.fontSize = 28;
            bodyStoryText.lineSpacing = 1.35f;
            bodyStoryText.color = new Color(0.96f, 0.96f, 0.98f, 1f);
            bodyStoryText.alignment = TextAnchor.UpperLeft;
            bodyStoryText.horizontalOverflow = HorizontalWrapMode.Wrap;
            bodyStoryText.verticalOverflow = VerticalWrapMode.Truncate;
            bodyStoryText.text = "Cargando narrativa de la batalla...";

            // 8. Indicador de Progreso
            GameObject promptObj = CreateUIElement("Prompt_Indicator", borderObj.transform);
            RectTransform promptRt = promptObj.GetComponent<RectTransform>();
            promptRt.anchorMin = new Vector2(0.5f, 0f);
            promptRt.anchorMax = new Vector2(0.5f, 0f);
            promptRt.pivot = new Vector2(0.5f, 0f);
            promptRt.anchoredPosition = new Vector2(0f, 100f);
            promptRt.sizeDelta = new Vector2(1500f, 40f);

            Text promptText = promptObj.AddComponent<Text>();
            promptText.font = retroFont;
            promptText.fontSize = 22;
            promptText.fontStyle = FontStyle.Bold;
            promptText.alignment = TextAnchor.MiddleCenter;
            promptText.color = new Color(1f, 0.85f, 0.2f, 1f);
            promptText.text = ">> PRESIONA [ESPACIO / ENTER] PARA CONTINUAR >>";

            // 9. Botones de Acción (Iniciar Combate & Volver al Menú)
            GameObject buttonContainer = CreateUIElement("Buttons_Container", borderObj.transform);
            RectTransform btnContRt = buttonContainer.GetComponent<RectTransform>();
            btnContRt.anchorMin = new Vector2(0.5f, 0f);
            btnContRt.anchorMax = new Vector2(0.5f, 0f);
            btnContRt.pivot = new Vector2(0.5f, 0f);
            btnContRt.anchoredPosition = new Vector2(0f, 30f);
            btnContRt.sizeDelta = new Vector2(1500f, 60f);

            Button btnFight = CreateActionButton("Btn_FightImmediate", buttonContainer.transform,
                "⚔ ENTRAR AL COMBATE (FIGHT)", retroFont, new Vector2(-280f, 0f), new Vector2(480f, 52f),
                new Color(0.85f, 0.45f, 0.1f, 0.85f), new Color(1f, 0.9f, 0.2f, 1f));

            Button btnMenu = CreateActionButton("Btn_ReturnMenu", buttonContainer.transform,
                "VOLVER AL MENÚ PRINCIPAL", retroFont, new Vector2(280f, 0f), new Vector2(420f, 52f),
                new Color(0.15f, 0.2f, 0.35f, 0.85f), new Color(0.85f, 0.85f, 0.95f, 1f));

            // 10. Imagen de Fundido en Negro (Blackout Overlay)
            GameObject blackoutObj = CreateUIElement("Blackout_Fade_Image", canvasObj.transform);
            StretchFull(blackoutObj.GetComponent<RectTransform>());
            Image blackoutImg = blackoutObj.AddComponent<Image>();
            blackoutImg.color = new Color(0, 0, 0, 1f);
            blackoutImg.raycastTarget = false;

            // 11. Manager de la Escena (StoryPrologueController)
            GameObject managerObj = new GameObject("StoryPrologueManager");
            StoryPrologueController controller = managerObj.AddComponent<StoryPrologueController>();

            // Asignación de campos
            AssignField(controller, "battleSceneName", "Sandbox_Sebas");
            AssignField(controller, "mainMenuSceneName", "MainMenu_Scene");
            AssignField(controller, "headerTitleText", headerTitle);
            AssignField(controller, "episodeTitleText", epTitle);
            AssignField(controller, "bodyStoryText", bodyStoryText);
            AssignField(controller, "promptIndicatorText", promptText);
            AssignField(controller, "skipToFightButton", btnFight);
            AssignField(controller, "returnToMenuButton", btnMenu);
            AssignField(controller, "blackoutFadeImage", blackoutImg);

            // Guardar Escena
            EditorSceneManager.SaveScene(scene, StoryScenePath);
            Debug.Log($"✅ [SF3 Builder] Escena Modo Historia guardada exitosamente en '{StoryScenePath}'.");

            // Sincronizar Build Settings
            SyncBuildScenes();
        }

        private static Button CreateActionButton(string name, Transform parent, string label, Font font, Vector2 position, Vector2 size, Color bgColor, Color textColor)
        {
            GameObject btnObj = CreateUIElement(name, parent);
            RectTransform rt = btnObj.GetComponent<RectTransform>();
            rt.anchoredPosition = position;
            rt.sizeDelta = size;

            Image img = btnObj.AddComponent<Image>();
            img.color = bgColor;

            Button btn = btnObj.AddComponent<Button>();

            Text txt = CreateText("Label", btnObj.transform, label, font, 20, FontStyle.Bold,
                textColor, Vector2.zero, size);
            txt.alignment = TextAnchor.MiddleCenter;

            return btn;
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

        private static void AssignField(object target, string fieldName, object value)
        {
            var field = target.GetType().GetField(fieldName, System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance);
            if (field != null)
            {
                field.SetValue(target, value);
            }
        }

        private static void SyncBuildScenes()
        {
            List<EditorBuildSettingsScene> scenes = EditorBuildSettings.scenes.ToList();
            if (!scenes.Any(s => s.path == StoryScenePath))
            {
                scenes.Add(new EditorBuildSettingsScene(StoryScenePath, true));
                EditorBuildSettings.scenes = scenes.ToArray();
                Debug.Log($"🔄 [SF3 Builder] Escena '{StoryScenePath}' añadida a EditorBuildSettings.");
            }
        }
    }
}
