using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace StreetFighter3.UI
{
    [System.Serializable]
    public enum DialogueSpeaker
    {
        Left,
        Right,
        Narrator
    }

    [System.Serializable]
    public class DialogueLine
    {
        public DialogueSpeaker speaker = DialogueSpeaker.Left;
        [TextArea(2, 4)]
        public string text;
        public string customSpeakerTitle = "";
        public AudioClip voiceClip;
    }

    [System.Serializable]
    public class StoryChapter
    {
        public string chapterNumber = "EPISODIO I";
        public string chapterTitle = "DESPERTAR EN SUZAKU CASTLE";
        public string locationName = "Suzaku Castle — Japón";
        public string p1Name = "KEN MASTERS";
        public string p1Title = "Piromante Biocinético";
        public string p2Name = "RYU";
        public string p2Title = "El Peregrino Cinético";
        public string battleSceneName = "Sandbox_Sebas";
        public Sprite leftPortrait;
        public Sprite rightPortrait;
        public List<DialogueLine> dialogueLines = new List<DialogueLine>();
    }

    /// <summary>
    /// Sistema de diálogos y cinemáticas estilo Dragon Ball Z: Budokai Tenkaichi 3.
    /// Cuenta con bustos/retratos de personajes a izquierda y derecha,
    /// efecto máquina de escribir, placa de nombre iluminada según el hablante activo,
    /// selector de capítulos y transición fluida al combate.
    /// </summary>
    public class TenkaichiDialogueManager : MonoBehaviour
    {
        public static TenkaichiDialogueManager Instance { get; private set; }

        [Header("Capítulos del Modo Historia")]
        [SerializeField] public List<StoryChapter> storyChapters = new List<StoryChapter>();
        [SerializeField] public int currentChapterIndex = 0;

        [Header("Audio")]
        [SerializeField] private AudioSource bgmAudioSource;
        [SerializeField] private AudioSource sfxAudioSource;
        [SerializeField] private AudioClip typeSfx;
        [SerializeField] private AudioClip nextLineSfx;
        [SerializeField] private AudioClip fightCallSfx;

        [Header("Parámetros Visuales DBZ Tenkaichi")]
        [SerializeField] private float typingSpeed = 38f; // Caracteres por segundo
        [SerializeField] private Color activeColor = Color.white;
        [SerializeField] private Color inactiveColor = new Color(0.45f, 0.45f, 0.5f, 0.85f);
        [SerializeField] private Color boxBgColor = new Color(0.04f, 0.06f, 0.10f, 0.94f);
        [SerializeField] private Color goldBorderColor = new Color(1f, 0.82f, 0.18f, 1f);
        [SerializeField] private Color cyanAccentColor = new Color(0.2f, 0.85f, 1f, 1f);

        // Estado interno del diálogo
        private int currentLineIndex = 0;
        private string displayedText = "";
        private bool isTyping = false;
        private float typingProgress = 0f;
        private bool isTransitioningToBattle = false;
        private float transitionAlpha = 0f;
        private Texture2D whiteTexture;
        private bool isShowingKinectNotice = false;

        private void Awake()
        {
            Instance = this;
            whiteTexture = Texture2D.whiteTexture;

            if (sfxAudioSource == null) sfxAudioSource = gameObject.AddComponent<AudioSource>();
            if (bgmAudioSource == null) bgmAudioSource = gameObject.AddComponent<AudioSource>();

            if (typeSfx == null) typeSfx = Resources.Load<AudioClip>("Audio/Menu_Cursor_Select");
            if (nextLineSfx == null) nextLineSfx = Resources.Load<AudioClip>("Audio/Menu_Confirm_Start");

            InitializeDefaultStoryChapters();
        }

        private void Start()
        {
            StartChapter(currentChapterIndex);
        }

        private void InitializeDefaultStoryChapters()
        {
            if (storyChapters != null && storyChapters.Count > 0) return;

            storyChapters = new List<StoryChapter>();

            // =========================================================
            // CAPÍTULO 1: JAPÓN (SUZAKU CASTLE) - KEN VS RYU
            // =========================================================
            StoryChapter ch1 = new StoryChapter
            {
                chapterNumber = "EPISODIO I",
                chapterTitle = "LA RESONANCIA DEL HADOU",
                locationName = "Suzaku Castle — Kyoto, Japón",
                p1Name = "KEN MASTERS",
                p1Title = "Campeón Biocinético",
                p2Name = "RYU",
                p2Title = "El Peregrino Cinético",
                battleSceneName = "Sandbox_Sebas",
                dialogueLines = new List<DialogueLine>
                {
                    new DialogueLine
                    {
                        speaker = DialogueSpeaker.Narrator,
                        text = "AÑO 2048. Tras el descubrimiento del Bio-Kinetic Core, los artistas marciales del mundo canalizan energía cinético-vital pura. Pero una anomalía masiva amenaza con colapsar las redes de energía planetarias..."
                    },
                    new DialogueLine
                    {
                        speaker = DialogueSpeaker.Left,
                        text = "¡Ryu! Los sensores cinéticos de la fundación registraron una distorsión descomunal. Alguien en el Mediterráneo está cosechando la energía cinética del mundo a la fuerza.",
                        customSpeakerTitle = "KEN MASTERS"
                    },
                    new DialogueLine
                    {
                        speaker = DialogueSpeaker.Right,
                        text = "Lo he sentido en el viento, Ken. El flujo natural del Hadou está perdiendo su balance. Una fuerza artificial está drenando la tierra.",
                        customSpeakerTitle = "RYU"
                    },
                    new DialogueLine
                    {
                        speaker = DialogueSpeaker.Left,
                        text = "Es el sindicato Olympus... su líder, Urien, activó el resonador Aegis. Antes de que viajes a detenerlo, quiero asegurarme de que tu cuerpo soporte la resonancia. ¡Pruébame tu verdadero nivel!",
                        customSpeakerTitle = "KEN MASTERS"
                    },
                    new DialogueLine
                    {
                        speaker = DialogueSpeaker.Right,
                        text = "Bien dicho, Ken. ¡Probemos el poder de nuestros puños en este duelo de calibración!",
                        customSpeakerTitle = "RYU"
                    }
                }
            };

            // =========================================================
            // CAPÍTULO 2: CHINA (CROWDED STREET) - RYU VS CHUN-LI
            // =========================================================
            StoryChapter ch2 = new StoryChapter
            {
                chapterNumber = "EPISODIO II",
                chapterTitle = "SOMBRAS EN EL MERCADO DE SHANGHÁI",
                locationName = "Crowded Street — Shanghái, China",
                p1Name = "RYU",
                p1Title = "El Peregrino Cinético",
                p2Name = "CHUN-LI",
                p2Title = "Inspectora Especial Interpol",
                battleSceneName = "Sandbox_China",
                dialogueLines = new List<DialogueLine>
                {
                    new DialogueLine
                    {
                        speaker = DialogueSpeaker.Narrator,
                        text = "Siguiendo los rastros de las frecuencias bio-resonantes, Ryu llega al populoso mercado callejero de Shanghái, donde se rumorea el tráfico de núcleos cinéticos modificados genéticamente."
                    },
                    new DialogueLine
                    {
                        speaker = DialogueSpeaker.Right,
                        text = "¡Alto ahí, forastero! Interpol tiene esta zona acordonada. Estamos incautando amplificadores cinéticos no autorizados de contrabando.",
                        customSpeakerTitle = "CHUN-LI"
                    },
                    new DialogueLine
                    {
                        speaker = DialogueSpeaker.Left,
                        text = "No busco alterar el orden, inspectora. Rastreo un pulso de energía que alimenta las baterías de Olympus Labs.",
                        customSpeakerTitle = "RYU"
                    },
                    new DialogueLine
                    {
                        speaker = DialogueSpeaker.Right,
                        text = "¿Olympus Labs? Entonces sabes sobre la Tumba Olímpica. Mis informantes dicen que Urien busca guerreros con alta densidad biocinética para sacrificarlos. Si vas a intervenir, ¡debo comprobar si puedes defenderte!",
                        customSpeakerTitle = "CHUN-LI"
                    },
                    new DialogueLine
                    {
                        speaker = DialogueSpeaker.Left,
                        text = "Tu velocidad y tu espíritu marcial son admirables, Chun-Li. ¡Comprobemos nuestra fuerza antes de descender a la cripta!",
                        customSpeakerTitle = "RYU"
                    }
                }
            };

            // =========================================================
            // CAPÍTULO 3: GRECIA (TOMB OF URIEN) - RYU VS URIEN
            // =========================================================
            StoryChapter ch3 = new StoryChapter
            {
                chapterNumber = "EPISODIO III (CLÍMAX)",
                chapterTitle = "LA CRIPTA DEL TITÁN DE AEGIS",
                locationName = "Olympian Tomb — Mar Mediterráneo",
                p1Name = "URIEN",
                p1Title = "Titán Transhumano de Olympus",
                p2Name = "RYU",
                p2Title = "El Peregrino Cinético",
                battleSceneName = "Sandbox_Tomb",
                dialogueLines = new List<DialogueLine>
                {
                    new DialogueLine
                    {
                        speaker = DialogueSpeaker.Narrator,
                        text = "En las profundidades subterráneas de un templo griego sumergido, Urien activa el monolito Aegis Core, listo para absorber toda la energía del torneo Kinet Strike..."
                    },
                    new DialogueLine
                    {
                        speaker = DialogueSpeaker.Left,
                        text = "Miren quién se atreve a profanar mi santuario... Insectos mortales cegados por viejas tradiciones marciales.",
                        customSpeakerTitle = "URIEN"
                    },
                    new DialogueLine
                    {
                        speaker = DialogueSpeaker.Right,
                        text = "Tu ambición termina aquí, Urien. Drenar la fuerza vital de la Tierra con tus máquinas no es evolución, es tiranía.",
                        customSpeakerTitle = "RYU"
                    },
                    new DialogueLine
                    {
                        speaker = DialogueSpeaker.Left,
                        text = "¡Silencio! La carne humana es imperfecta y caduca. Con el poder de este núcleo cinético forjaré una nueva era de dioses metálicos. ¡Y ustedes serán el primer tributo de mi reinado!",
                        customSpeakerTitle = "URIEN"
                    },
                    new DialogueLine
                    {
                        speaker = DialogueSpeaker.Right,
                        text = "¡El verdadero Hadou nace de la armonía entre cuerpo y espíritu! ¡Prepárate, Urien!",
                        customSpeakerTitle = "RYU"
                    },
                    new DialogueLine
                    {
                        speaker = DialogueSpeaker.Left,
                        text = "¡JAJAJAJA! ¡Quebraré tus huesos contra mi barrera Aegis! ¡ENGAGE KINET STRIKE!",
                        customSpeakerTitle = "URIEN"
                    }
                }
            };

            storyChapters.Add(ch1);
            storyChapters.Add(ch2);
            storyChapters.Add(ch3);
        }

        public void StartChapter(int index)
        {
            if (index < 0 || index >= storyChapters.Count) index = 0;
            currentChapterIndex = index;
            currentLineIndex = 0;
            isTransitioningToBattle = false;
            isShowingKinectNotice = false;
            transitionAlpha = 0f;

            LoadPortraitsForChapter(storyChapters[currentChapterIndex]);
            StartLine(0);
        }

        private void LoadPortraitsForChapter(StoryChapter chapter)
        {
            // Cargar retratos dinámicamente si no están asignados en el inspector
            if (chapter.leftPortrait == null)
            {
                if (chapter.p1Name.Contains("KEN"))
                    chapter.leftPortrait = Resources.Load<Sprite>("Portraits/Ken") ?? LoadFirstSprite("Assets/StreetFighter3_ThirdStrike/Characters/11_Ken/01_Movement/idle_stance/0.png");
                else if (chapter.p1Name.Contains("URIEN"))
                    chapter.leftPortrait = Resources.Load<Sprite>("Portraits/Urien") ?? LoadFirstSprite("Assets/StreetFighter3_ThirdStrike/Characters/13_Urien/01_Movement/idle_stance/0.png");
                else
                    chapter.leftPortrait = Resources.Load<Sprite>("Portraits/Ryu") ?? LoadFirstSprite("Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu/01_Movement/idle_stance/0.png");
            }

            if (chapter.rightPortrait == null)
            {
                if (chapter.p2Name.Contains("CHUN"))
                    chapter.rightPortrait = Resources.Load<Sprite>("Portraits/ChunLi") ?? LoadFirstSprite("Assets/StreetFighter3_ThirdStrike/Characters/16_Chun_Li/01_Movement/idle_stance/0.png");
                else if (chapter.p2Name.Contains("URIEN"))
                    chapter.rightPortrait = Resources.Load<Sprite>("Portraits/Urien") ?? LoadFirstSprite("Assets/StreetFighter3_ThirdStrike/Characters/13_Urien/01_Movement/idle_stance/0.png");
                else
                    chapter.rightPortrait = Resources.Load<Sprite>("Portraits/Ryu") ?? LoadFirstSprite("Assets/StreetFighter3_ThirdStrike/Characters/02_Ryu/01_Movement/idle_stance/0.png");
            }
        }

        private Sprite LoadFirstSprite(string path)
        {
#if UNITY_EDITOR
            return UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(path);
#else
            return null;
#endif
        }

        private void StartLine(int lineIndex)
        {
            StoryChapter chapter = storyChapters[currentChapterIndex];
            if (lineIndex >= chapter.dialogueLines.Count)
            {
                isShowingKinectNotice = true;
                return;
            }

            currentLineIndex = lineIndex;
            displayedText = "";
            typingProgress = 0f;
            isTyping = true;

            DialogueLine line = chapter.dialogueLines[currentLineIndex];
            if (line.voiceClip != null && sfxAudioSource != null)
            {
                sfxAudioSource.PlayOneShot(line.voiceClip);
            }
        }

        private void Update()
        {
            if (isTransitioningToBattle)
            {
                transitionAlpha = Mathf.MoveTowards(transitionAlpha, 1f, 1.5f * Time.deltaTime);
                if (transitionAlpha >= 1f)
                {
                    LoadBattleScene();
                }
                return;
            }

            // Si está activa la ventana informativa de Kinect / Modo Versus
            if (isShowingKinectNotice)
            {
                if (Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.KeypadEnter) || Input.GetKeyDown(KeyCode.Space))
                {
                    TriggerBattleTransition();
                }
                else if (Input.GetKeyDown(KeyCode.Escape))
                {
                    SceneManager.LoadScene("MainMenu_Scene");
                }
                else if (Input.GetKeyDown(KeyCode.Alpha1)) StartChapter(0);
                else if (Input.GetKeyDown(KeyCode.Alpha2)) StartChapter(1);
                else if (Input.GetKeyDown(KeyCode.Alpha3)) StartChapter(2);
                return;
            }

            StoryChapter chapter = storyChapters[currentChapterIndex];
            if (currentLineIndex >= chapter.dialogueLines.Count)
            {
                isShowingKinectNotice = true;
                return;
            }

            DialogueLine line = chapter.dialogueLines[currentLineIndex];

            // 1. Efecto máquina de escribir
            if (isTyping)
            {
                typingProgress += typingSpeed * Time.deltaTime;
                int targetCharCount = Mathf.Min(Mathf.FloorToInt(typingProgress), line.text.Length);

                if (targetCharCount > displayedText.Length)
                {
                    displayedText = line.text.Substring(0, targetCharCount);
                    // Reproducir blip suave cada 3 caracteres
                    if (targetCharCount % 3 == 0 && typeSfx != null && sfxAudioSource != null)
                    {
                        sfxAudioSource.PlayOneShot(typeSfx, 0.35f);
                    }
                }

                if (displayedText.Length >= line.text.Length)
                {
                    isTyping = false;
                }
            }

            // 2. Control de Teclado (ESPACIO, ENTER, CLIC)
            if (Input.GetKeyDown(KeyCode.Space) || Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.KeypadEnter) || Input.GetMouseButtonDown(0))
            {
                if (isTyping)
                {
                    // Saltar máquina de escribir y mostrar texto completo de inmediato
                    displayedText = line.text;
                    isTyping = false;
                }
                else
                {
                    // Avanzar a la siguiente línea
                    if (nextLineSfx != null && sfxAudioSource != null)
                    {
                        sfxAudioSource.PlayOneShot(nextLineSfx, 0.75f);
                    }
                    StartLine(currentLineIndex + 1);
                }
            }

            // 3. Volver al menú con ESC o ver opciones Versus con TAB
            if (Input.GetKeyDown(KeyCode.Escape))
            {
                SceneManager.LoadScene("MainMenu_Scene");
                return;
            }
            if (Input.GetKeyDown(KeyCode.Tab))
            {
                isShowingKinectNotice = true;
            }

            // 4. Selector de capítulos con teclas numéricas [1], [2], [3]
            if (Input.GetKeyDown(KeyCode.Alpha1)) StartChapter(0);
            if (Input.GetKeyDown(KeyCode.Alpha2)) StartChapter(1);
            if (Input.GetKeyDown(KeyCode.Alpha3)) StartChapter(2);
        }

        private void TriggerBattleTransition()
        {
            if (isTransitioningToBattle) return;
            isTransitioningToBattle = true;
            if (fightCallSfx != null && sfxAudioSource != null)
            {
                sfxAudioSource.PlayOneShot(fightCallSfx, 0.9f);
            }
        }

        private void LoadBattleScene()
        {
            string sceneToLoad = storyChapters[currentChapterIndex].battleSceneName;
            if (!string.IsNullOrEmpty(sceneToLoad))
            {
                SceneManager.LoadScene(sceneToLoad);
            }
            else
            {
                SceneManager.LoadScene("MainMenu_Scene");
            }
        }

        private void OnGUI()
        {
            // Matriz virtual arcade 960x540 adaptativa
            float scale = Mathf.Min(Screen.width / 960f, Screen.height / 540f);
            Matrix4x4 old = GUI.matrix;
            GUI.matrix = Matrix4x4.TRS(
                new Vector3((Screen.width - 960f * scale) / 2f, (Screen.height - 540f * scale) / 2f, 0f),
                Quaternion.identity,
                Vector3.one * scale);

            StoryChapter chapter = storyChapters[currentChapterIndex];
            bool hasValidLine = currentLineIndex < chapter.dialogueLines.Count;
            DialogueLine currentLine = hasValidLine ? chapter.dialogueLines[currentLineIndex] : null;

            // ==========================================
            // 1. FRANJA SUPERIOR CINEMÁTICA (CAPÍTULO Y LOCACIÓN)
            // ==========================================
            DrawRect(new Rect(0, 0, 960, 48), new Color(0.03f, 0.04f, 0.07f, 0.95f));
            DrawRect(new Rect(0, 46, 960, 2), goldBorderColor);

            GUIStyle titleStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 15,
                fontStyle = FontStyle.Bold,
                alignment = TextAnchor.MiddleLeft
            };
            titleStyle.normal.textColor = goldBorderColor;
            GUI.Label(new Rect(25, 6, 600, 20), $"🥋 {chapter.chapterNumber}: {chapter.chapterTitle}", titleStyle);

            GUIStyle locStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 12,
                fontStyle = FontStyle.Normal,
                alignment = TextAnchor.MiddleLeft
            };
            locStyle.normal.textColor = new Color(0.75f, 0.85f, 0.95f, 0.9f);
            GUI.Label(new Rect(25, 26, 600, 18), $"📍 Ubicación: {chapter.locationName}", locStyle);

            // Botón / Indicador de Salto
            GUIStyle skipStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 12,
                fontStyle = FontStyle.Bold,
                alignment = TextAnchor.MiddleRight
            };
            skipStyle.normal.textColor = new Color(0.85f, 0.9f, 1f, 0.8f);
            GUI.Label(new Rect(700, 14, 235, 20), "[ESC] Menú  |  [TAB] Opciones", skipStyle);

            // ==========================================
            // 2. BUSTOS / RETRATOS DE PERSONAJES (DBZ BUDOKAI TENKAICHI 3)
            // ==========================================
            bool isLeftSpeaking = currentLine != null && currentLine.speaker == DialogueSpeaker.Left;
            bool isRightSpeaking = currentLine != null && currentLine.speaker == DialogueSpeaker.Right;
            bool isNarrator = currentLine != null && currentLine.speaker == DialogueSpeaker.Narrator;

            // Retrato Izquierdo
            if (chapter.leftPortrait != null && !isNarrator)
            {
                float breathe = isLeftSpeaking ? Mathf.Sin(Time.time * 6f) * 4f : 0f;
                Rect leftRect = new Rect(80, 130 - breathe, 220, 240);

                // Marco de brillo si está hablando
                if (isLeftSpeaking)
                {
                    DrawRect(new Rect(leftRect.x - 4, leftRect.y - 4, leftRect.width + 8, leftRect.height + 8), new Color(1f, 0.85f, 0.2f, 0.35f));
                }

                DrawSprite(leftRect, chapter.leftPortrait, isLeftSpeaking ? activeColor : inactiveColor, false);

                // Placa inferior con nombre de personaje izquierdo
                Rect p1Badge = new Rect(70, 325, 240, 26);
                DrawRect(p1Badge, new Color(0.06f, 0.08f, 0.14f, 0.92f));
                DrawRectBorder(p1Badge, isLeftSpeaking ? goldBorderColor : new Color(0.4f, 0.45f, 0.55f, 0.7f), 2);
                GUIStyle p1NameStyle = new GUIStyle(GUI.skin.label)
                {
                    fontSize = 12,
                    fontStyle = FontStyle.Bold,
                    alignment = TextAnchor.MiddleCenter
                };
                p1NameStyle.normal.textColor = isLeftSpeaking ? goldBorderColor : new Color(0.6f, 0.65f, 0.7f);
                GUI.Label(p1Badge, chapter.p1Name, p1NameStyle);
            }

            // Retrato Derecho (Flipped hacia la izquierda)
            if (chapter.rightPortrait != null && !isNarrator)
            {
                float breathe = isRightSpeaking ? Mathf.Sin(Time.time * 6f) * 4f : 0f;
                Rect rightRect = new Rect(660, 130 - breathe, 220, 240);

                // Marco de brillo si está hablando
                if (isRightSpeaking)
                {
                    DrawRect(new Rect(rightRect.x - 4, rightRect.y - 4, rightRect.width + 8, rightRect.height + 8), new Color(0.2f, 0.85f, 1f, 0.35f));
                }

                DrawSprite(rightRect, chapter.rightPortrait, isRightSpeaking ? activeColor : inactiveColor, true);

                // Placa inferior con nombre de personaje derecho
                Rect p2Badge = new Rect(650, 325, 240, 26);
                DrawRect(p2Badge, new Color(0.06f, 0.08f, 0.14f, 0.92f));
                DrawRectBorder(p2Badge, isRightSpeaking ? cyanAccentColor : new Color(0.4f, 0.45f, 0.55f, 0.7f), 2);
                GUIStyle p2NameStyle = new GUIStyle(GUI.skin.label)
                {
                    fontSize = 12,
                    fontStyle = FontStyle.Bold,
                    alignment = TextAnchor.MiddleCenter
                };
                p2NameStyle.normal.textColor = isRightSpeaking ? cyanAccentColor : new Color(0.6f, 0.65f, 0.7f);
                GUI.Label(p2Badge, chapter.p2Name, p2NameStyle);
            }

            // ==========================================
            // 3. CUADRO DE DIÁLOGO INFERIOR (ESTILO TENKAICHI 3)
            // ==========================================
            Rect boxRect = new Rect(60, 360, 840, 145);

            // Sombra y fondo
            DrawRect(new Rect(boxRect.x + 4, boxRect.y + 4, boxRect.width, boxRect.height), new Color(0f, 0f, 0f, 0.65f));
            DrawRect(boxRect, boxBgColor);

            // Doble borde estilo Budokai Tenkaichi
            Color currentBorder = isNarrator ? cyanAccentColor : (isLeftSpeaking ? goldBorderColor : cyanAccentColor);
            DrawRectBorder(boxRect, currentBorder, 3);
            DrawRectBorder(new Rect(boxRect.x + 4, boxRect.y + 4, boxRect.width - 8, boxRect.height - 8), new Color(1f, 1f, 1f, 0.15f), 1);

            // Esquinas ornamentales estilo arcade
            DrawRect(new Rect(boxRect.x - 2, boxRect.y - 2, 10, 10), currentBorder);
            DrawRect(new Rect(boxRect.x + boxRect.width - 8, boxRect.y - 2, 10, 10), currentBorder);
            DrawRect(new Rect(boxRect.x - 2, boxRect.y + boxRect.height - 8, 10, 10), currentBorder);
            DrawRect(new Rect(boxRect.x + boxRect.width - 8, boxRect.y + boxRect.height - 8, 10, 10), currentBorder);

            // ==========================================
            // 4. PLACA DEL HABLANTE ACTIVO
            // ==========================================
            string speakerName = "NARRADOR";
            if (currentLine != null)
            {
                if (!string.IsNullOrEmpty(currentLine.customSpeakerTitle))
                {
                    speakerName = currentLine.customSpeakerTitle;
                }
                else if (currentLine.speaker == DialogueSpeaker.Left)
                {
                    speakerName = $"{chapter.p1Name} [{chapter.p1Title}]";
                }
                else if (currentLine.speaker == DialogueSpeaker.Right)
                {
                    speakerName = $"{chapter.p2Name} [{chapter.p2Title}]";
                }
            }

            float speakerX = isRightSpeaking ? 530 : 80;
            Rect speakerPlate = new Rect(speakerX, 342, 350, 32);
            DrawRect(speakerPlate, new Color(0.08f, 0.12f, 0.20f, 0.98f));
            DrawRectBorder(speakerPlate, currentBorder, 2);

            GUIStyle speakerStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 14,
                fontStyle = FontStyle.Bold,
                alignment = TextAnchor.MiddleCenter
            };
            speakerStyle.normal.textColor = currentBorder;
            GUI.Label(speakerPlate, speakerName, speakerStyle);

            // ==========================================
            // 5. TEXTO CON EFECTO MÁQUINA DE ESCRIBIR
            // ==========================================
            GUIStyle textStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 18,
                fontStyle = FontStyle.Normal,
                wordWrap = true,
                alignment = TextAnchor.UpperLeft
            };
            textStyle.normal.textColor = Color.white;

            Rect textRect = new Rect(90, 385, 780, 95);
            // Sombra del texto
            textStyle.normal.textColor = new Color(0f, 0f, 0f, 0.9f);
            GUI.Label(new Rect(textRect.x + 1, textRect.y + 1, textRect.width, textRect.height), displayedText, textStyle);
            // Texto principal
            textStyle.normal.textColor = isNarrator ? new Color(0.9f, 0.95f, 1f) : new Color(1f, 0.98f, 0.92f);
            GUI.Label(textRect, displayedText, textStyle);

            // ==========================================
            // 6. INDICADOR DE CONTINUAR PARPADEANTE (▼)
            // ==========================================
            if (!isTyping)
            {
                float blink = Mathf.PingPong(Time.time * 4f, 1f);
                GUIStyle promptStyle = new GUIStyle(GUI.skin.label)
                {
                    fontSize = 13,
                    fontStyle = FontStyle.Bold,
                    alignment = TextAnchor.MiddleRight
                };
                promptStyle.normal.textColor = Color.Lerp(goldBorderColor, Color.white, blink);
                GUI.Label(new Rect(650, 475, 230, 24), "▼ [ESPACIO / ENTER]", promptStyle);
            }

            // Selector rápido de episodios
            GUIStyle epHintStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 11,
                fontStyle = FontStyle.Normal,
                alignment = TextAnchor.MiddleLeft
            };
            epHintStyle.normal.textColor = new Color(0.6f, 0.65f, 0.75f, 0.7f);
            GUI.Label(new Rect(90, 480, 500, 20), "Capítulos: [1] Japón  |  [2] China  |  [3] Tumba de Urien", epHintStyle);

            // ==========================================
            // 6.5 MODAL INFORMATIVO KINECT / TRANSICIÓN VERSUS
            // ==========================================
            if (isShowingKinectNotice && !isTransitioningToBattle)
            {
                DrawRect(new Rect(0, 0, 960, 540), new Color(0f, 0f, 0f, 0.82f));

                Rect modalRect = new Rect(140, 85, 680, 370);
                DrawRect(modalRect, new Color(0.04f, 0.06f, 0.12f, 0.98f));
                DrawRectBorder(modalRect, goldBorderColor, 3);
                DrawRectBorder(new Rect(modalRect.x + 4, modalRect.y + 4, modalRect.width - 8, modalRect.height - 8), cyanAccentColor, 1);

                GUIStyle modalTitleStyle = new GUIStyle(GUI.skin.label)
                {
                    fontSize = 20,
                    fontStyle = FontStyle.Bold,
                    alignment = TextAnchor.MiddleCenter
                };
                modalTitleStyle.normal.textColor = goldBorderColor;
                GUI.Label(new Rect(140, 105, 680, 30), "« MODO HISTORIA — KINET STRIKE »", modalTitleStyle);

                GUIStyle subBadgeStyle = new GUIStyle(GUI.skin.label)
                {
                    fontSize = 12,
                    fontStyle = FontStyle.Bold,
                    alignment = TextAnchor.MiddleCenter
                };
                subBadgeStyle.normal.textColor = cyanAccentColor;
                GUI.Label(new Rect(140, 138, 680, 24), "[ CONTROL SOMATOSENSORIAL CON AZURE KINECT REQUERIDO ]", subBadgeStyle);

                GUIStyle bodyStyle = new GUIStyle(GUI.skin.label)
                {
                    fontSize = 13,
                    fontStyle = FontStyle.Normal,
                    alignment = TextAnchor.MiddleCenter,
                    wordWrap = true
                };
                bodyStyle.normal.textColor = new Color(0.9f, 0.92f, 0.96f);
                string bodyNotice = 
                    "La campaña cinemática del Modo Historia está diseñada para control somatosensorial con el Sensor Azure Kinect (rastreo corporal 3D en tiempo real).\n\n" +
                    $"¡El enfrentamiento de este episodio en '{chapter.locationName}' está disponible en el MODO VERSUS con controles para 2 Jugadores!\n\n" +
                    "• Jugador 1: Teclas [W / A / S / D] + [J/K/L/O/U/I]\n" +
                    "• Jugador 2: [FLECHAS DE DIRECCIÓN] + [Keypad / B,N,M,,]";
                GUI.Label(new Rect(170, 170, 620, 170), bodyNotice, bodyStyle);

                Rect btnVersus = new Rect(170, 385, 290, 44);
                DrawRect(btnVersus, new Color(0.12f, 0.38f, 0.22f, 0.95f));
                DrawRectBorder(btnVersus, new Color(0.3f, 1f, 0.5f), 2);
                GUIStyle btnStyle = new GUIStyle(GUI.skin.label)
                {
                    fontSize = 13,
                    fontStyle = FontStyle.Bold,
                    alignment = TextAnchor.MiddleCenter
                };
                btnStyle.normal.textColor = Color.white;
                GUI.Label(btnVersus, "▶ [ENTER] Jugar en Versus", btnStyle);

                Rect btnMenu = new Rect(500, 385, 290, 44);
                DrawRect(btnMenu, new Color(0.38f, 0.12f, 0.15f, 0.95f));
                DrawRectBorder(btnMenu, new Color(1f, 0.35f, 0.4f), 2);
                GUI.Label(btnMenu, "⮌ [ESC] Volver al Menú", btnStyle);
            }

            // ==========================================
            // 7. TRANSICIÓN A BATALLA (FADE A NEGRO Y FIGHT!)
            // ==========================================
            if (isTransitioningToBattle)
            {
                DrawRect(new Rect(0, 0, 960, 540), new Color(0f, 0f, 0f, transitionAlpha));

                GUIStyle fightStyle = new GUIStyle(GUI.skin.label)
                {
                    fontSize = 44,
                    fontStyle = FontStyle.Bold,
                    alignment = TextAnchor.MiddleCenter
                };
                fightStyle.normal.textColor = new Color(1f, 0.85f, 0.2f, transitionAlpha);
                GUI.Label(new Rect(0, 230, 960, 60), "— ¡ENGAGE KINET STRIKE! —", fightStyle);
            }

            GUI.matrix = old;
        }

        private void DrawSprite(Rect screenRect, Sprite sprite, Color tint, bool flipX)
        {
            if (sprite == null || sprite.texture == null) return;

            Texture2D tex = sprite.texture;
            Rect spriteRect = sprite.rect;
            Rect texCoords = new Rect(
                spriteRect.x / tex.width,
                spriteRect.y / tex.height,
                spriteRect.width / tex.width,
                spriteRect.height / tex.height);

            if (flipX)
            {
                texCoords.x += texCoords.width;
                texCoords.width = -texCoords.width;
            }

            GUI.color = tint;
            GUI.DrawTextureWithTexCoords(screenRect, tex, texCoords);
            GUI.color = Color.white;
        }

        private void DrawRect(Rect rect, Color color)
        {
            GUI.color = color;
            GUI.DrawTexture(rect, whiteTexture);
            GUI.color = Color.white;
        }

        private void DrawRectBorder(Rect rect, Color color, float thickness)
        {
            DrawRect(new Rect(rect.x, rect.y, rect.width, thickness), color);
            DrawRect(new Rect(rect.x, rect.y + rect.height - thickness, rect.width, thickness), color);
            DrawRect(new Rect(rect.x, rect.y, thickness, rect.height), color);
            DrawRect(new Rect(rect.x + rect.width - thickness, rect.y, thickness, rect.height), color);
        }
    }
}
