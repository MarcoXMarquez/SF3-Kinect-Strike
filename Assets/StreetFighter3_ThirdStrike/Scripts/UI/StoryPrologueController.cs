using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

namespace StreetFighter3.UI
{
    /// <summary>
    /// Controlador del Prólogo Cinemático del Modo Historia (Ryu vs Ken).
    /// Presenta una pantalla negra CPS-3 con máquina de escribir,
    /// explicando con detalle canónico la razón por la que Ryu y Ken se enfrentan
    /// antes de iniciar el combate en Suzaku Castle (Sandbox_Sebas).
    /// </summary>
    public class StoryPrologueController : MonoBehaviour
    {
        [Header("Escena de Combate")]
        [SerializeField] private string battleSceneName = "Sandbox_Sebas";
        [SerializeField] private string mainMenuSceneName = "MainMenu_Scene";

        [Header("Referencias de UI")]
        [SerializeField] private Text headerTitleText;
        [SerializeField] private Text episodeTitleText;
        [SerializeField] private Text bodyStoryText;
        [SerializeField] private Text promptIndicatorText;
        [SerializeField] private Button skipToFightButton;
        [SerializeField] private Button returnToMenuButton;
        [SerializeField] private Image blackoutFadeImage;

        [Header("Audio")]
        [SerializeField] private AudioSource bgmAudioSource;
        [SerializeField] private AudioSource sfxAudioSource;
        [SerializeField] private AudioClip typeSfx;
        [SerializeField] private AudioClip confirmSfx;
        [SerializeField] private AudioClip fightCallSfx;

        [Header("Configuración de Máquina de Escribir")]
        [SerializeField] private float charactersPerSecond = 42f;

        // Párrafos narrativos de la historia de Ryu y Ken
        private readonly List<string> storyParagraphs = new List<string>
        {
            "AÑO 1999. Tras años de riguroso adiestramiento en las solitarias montañas de Japón bajo la tutela del venerable maestro Gouken, Ryu y Ken forjaron un lazo más fuerte que la sangre a través del arte sagrado del Ansatsuken.",

            "Al culminar su aprendizaje, sus destinos tomaron rumbos opuestos.\n\nKen Masters regresó a América, alcanzando la cúspide de la fama en los circuitos mundiales. Formó una familia junto a Eliza y celebró la llegada de su hijo Mel, encontrando la plenitud en la calidez de su hogar y la paz.",

            "Por el contrario, Ryu abrazó el sendero eterno del peregrino ('Shugyosha').\n\nSin hogar, riquezas ni ataduras materiales, recorre el planeta buscando la respuesta a qué significa ser un verdadero artista marcial. Sin embargo, su camino se ha oscurecido: la latente amenaza del 'Satsui no Hadou' —el impulso asesino— susurra en su interior, llenando su espíritu de incertidumbre y temor.",

            "Sintiendo la perturbación en el flujo del Hadou y el aislamiento de su hermano de armas, Ken cruzó los océanos hasta las terrazas del milenario Castillo Suzaku en Kioto.\n\nBajo la luz plateada de la luna llena, Ken no encontró al fiero rival de su juventud, sino a un guerrero paralizado por la duda de su propio destino.",

            "Ken ajusta sus guantes rojos y enciende las llamas de su Shoryuken con una sonrisa desafiante. Sabe que las palabras vacías no salvarán a Ryu de la sombra; la única forma de reavivar el fuego de su alma es mediante el lenguaje supremo de sus vidas:\n\n¡EL CHOQUE HONESTO Y ABRASADOR DE SUS PUÑOS!\n\n«¡Ryu! Si tus puños dudan, la oscuridad ganará. ¡Ponte en guardia y muéstrame el verdadero Hadou!»"
        };

        private int currentParagraphIndex = 0;
        private bool isTyping = false;
        private Coroutine typingCoroutine;
        private bool isTransitioning = false;

        private void Awake()
        {
            if (sfxAudioSource == null) sfxAudioSource = gameObject.AddComponent<AudioSource>();
            if (bgmAudioSource == null) bgmAudioSource = gameObject.AddComponent<AudioSource>();

            if (typeSfx == null) typeSfx = Resources.Load<AudioClip>("Audio/Menu_Cursor_Select");
            if (confirmSfx == null) confirmSfx = Resources.Load<AudioClip>("Audio/Menu_Confirm_Start");
            if (fightCallSfx == null) fightCallSfx = Resources.Load<AudioClip>("Audio/SFX/06_Announcer/05_Now_Fight");

            AudioClip bgm = Resources.Load<AudioClip>("Audio/BGM_Japan");
            if (bgm != null)
            {
                bgmAudioSource.clip = bgm;
                bgmAudioSource.loop = true;
                bgmAudioSource.volume = 0.35f;
                bgmAudioSource.Play();
            }

            if (skipToFightButton != null)
            {
                skipToFightButton.onClick.AddListener(StartCombatImmediate);
            }

            if (returnToMenuButton != null)
            {
                returnToMenuButton.onClick.AddListener(ReturnToMainMenu);
            }
        }

        private void Start()
        {
            if (blackoutFadeImage != null)
            {
                blackoutFadeImage.gameObject.SetActive(true);
                blackoutFadeImage.color = new Color(0, 0, 0, 1f);
                StartCoroutine(FadeFromBlack());
            }

            DisplayParagraph(0);
        }

        private void Update()
        {
            if (isTransitioning) return;

            // [ENTER / ESPACIO] Avanzar o completar máquina de escribir
            if (Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.Space) || Input.GetKeyDown(KeyCode.KeypadEnter))
            {
                OnAdvancePressed();
            }

            // [ESC / S] Saltar directamente al combate
            if (Input.GetKeyDown(KeyCode.Escape) || Input.GetKeyDown(KeyCode.S))
            {
                StartCombatImmediate();
            }

            // [M] Volver al Menú Principal
            if (Input.GetKeyDown(KeyCode.M))
            {
                ReturnToMainMenu();
            }

            // Parpadeo sutil del indicador de progreso
            if (promptIndicatorText != null)
            {
                float alpha = 0.5f + Mathf.PingPong(Time.unscaledTime * 2.5f, 0.5f);
                Color c = promptIndicatorText.color;
                c.a = alpha;
                promptIndicatorText.color = c;
            }
        }

        public void OnAdvancePressed()
        {
            if (isTyping)
            {
                // Si aún está escribiendo, completar de golpe el texto
                if (typingCoroutine != null) StopCoroutine(typingCoroutine);
                bodyStoryText.text = storyParagraphs[currentParagraphIndex];
                isTyping = false;
                UpdatePromptText();
            }
            else
            {
                // Pasar al siguiente párrafo o iniciar combate si ya terminó
                if (currentParagraphIndex < storyParagraphs.Count - 1)
                {
                    PlaySFX(confirmSfx);
                    currentParagraphIndex++;
                    DisplayParagraph(currentParagraphIndex);
                }
                else
                {
                    StartCombatImmediate();
                }
            }
        }

        private void DisplayParagraph(int index)
        {
            if (index < 0 || index >= storyParagraphs.Count) return;

            if (episodeTitleText != null)
            {
                episodeTitleText.text = $"EPISODIO I: LA LLAMA DEL ANSATSUKEN  ({index + 1} / {storyParagraphs.Count})";
            }

            if (typingCoroutine != null) StopCoroutine(typingCoroutine);
            typingCoroutine = StartCoroutine(TypewriterRoutine(storyParagraphs[index]));
        }

        private IEnumerator TypewriterRoutine(string fullText)
        {
            isTyping = true;
            bodyStoryText.text = "";
            UpdatePromptText();

            float delay = 1f / charactersPerSecond;
            int sfxCounter = 0;

            for (int i = 0; i < fullText.Length; i++)
            {
                bodyStoryText.text += fullText[i];

                sfxCounter++;
                if (sfxCounter % 3 == 0 && typeSfx != null && sfxAudioSource != null && !char.IsWhiteSpace(fullText[i]))
                {
                    sfxAudioSource.PlayOneShot(typeSfx, 0.35f);
                }

                // Pausa ligeramente mayor tras puntuación
                if (fullText[i] == '.' || fullText[i] == '!' || fullText[i] == '?')
                {
                    yield return new WaitForSeconds(0.28f);
                }
                else if (fullText[i] == ',')
                {
                    yield return new WaitForSeconds(0.12f);
                }
                else
                {
                    yield return new WaitForSeconds(delay);
                }
            }

            isTyping = false;
            UpdatePromptText();
        }

        private void UpdatePromptText()
        {
            if (promptIndicatorText == null) return;

            if (isTyping)
            {
                promptIndicatorText.text = "[ESPACIO / ENTER] Mostrar todo  |  [ESC / S] Saltar al combate  |  [M] Menú";
                promptIndicatorText.color = new Color(0.7f, 0.7f, 0.7f, 1f);
            }
            else
            {
                if (currentParagraphIndex < storyParagraphs.Count - 1)
                {
                    promptIndicatorText.text = ">> PRESIONA [ESPACIO / ENTER] PARA CONTINUAR >>";
                    promptIndicatorText.color = new Color(1f, 0.85f, 0.2f, 1f);
                }
                else
                {
                    promptIndicatorText.text = "⚔ ¡PRESIONA [ESPACIO / ENTER] PARA ENTRAR AL COMBATE! ⚔";
                    promptIndicatorText.color = new Color(0.2f, 0.95f, 1f, 1f);
                }
            }
        }

        public void StartCombatImmediate()
        {
            if (isTransitioning) return;
            isTransitioning = true;

            PlaySFX(fightCallSfx ?? confirmSfx);
            StartCoroutine(TransitionToBattleRoutine());
        }

        private IEnumerator TransitionToBattleRoutine()
        {
            float duration = 1.0f;
            float elapsed = 0f;

            if (blackoutFadeImage != null)
            {
                blackoutFadeImage.gameObject.SetActive(true);
                while (elapsed < duration)
                {
                    elapsed += Time.deltaTime;
                    float t = Mathf.Clamp01(elapsed / duration);
                    blackoutFadeImage.color = new Color(0, 0, 0, t);
                    if (bgmAudioSource != null) bgmAudioSource.volume = Mathf.Lerp(0.35f, 0f, t);
                    yield return null;
                }
            }
            else
            {
                yield return new WaitForSeconds(0.5f);
            }

            Time.timeScale = 1f;
            SceneManager.LoadScene(battleSceneName);
        }

        public void ReturnToMainMenu()
        {
            if (isTransitioning) return;
            isTransitioning = true;
            Time.timeScale = 1f;
            SceneManager.LoadScene(mainMenuSceneName);
        }

        private IEnumerator FadeFromBlack()
        {
            float duration = 0.8f;
            float elapsed = 0f;
            while (elapsed < duration)
            {
                elapsed += Time.deltaTime;
                float t = 1f - Mathf.Clamp01(elapsed / duration);
                if (blackoutFadeImage != null)
                {
                    blackoutFadeImage.color = new Color(0, 0, 0, t);
                }
                yield return null;
            }
            if (blackoutFadeImage != null) blackoutFadeImage.gameObject.SetActive(false);
        }

        private void PlaySFX(AudioClip clip)
        {
            if (clip != null && sfxAudioSource != null)
            {
                sfxAudioSource.PlayOneShot(clip, 0.85f);
            }
        }
    }
}
