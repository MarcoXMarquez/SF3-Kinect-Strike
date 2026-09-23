using System.Collections;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

namespace StreetFighter3.UI
{
    /// <summary>
    /// Controlador principal de la Pantalla de Carga interactiva.
    /// Maneja el progreso visual de carga, la animación de estado y la transición
    /// asíncrona hacia la escena de combate seleccionada.
    /// </summary>
    public class LoadingScreenController : MonoBehaviour
    {
        [Header("Referencias UI")]
        [SerializeField] private CanvasGroup loadingCanvasGroup;
        [SerializeField] private Image progressBarFill;
        [SerializeField] private Text loadingStatusText;
        [SerializeField] private Text progressPercentageText;
        [SerializeField] private Text continuePromptText;
        [SerializeField] private LoadingMinigameManager minigameManager;

        [Header("Configuración")]
        [SerializeField] private float minimumLoadingTime = 4.0f; // Tiempo mínimo para disfrutar el minijuego
        [SerializeField] private bool waitForInputAfterLoad = false;

        private bool isLoading = false;
        private string targetSceneName = "Sandbox_Sebas";

        private void Awake()
        {
            if (loadingCanvasGroup == null) loadingCanvasGroup = GetComponent<CanvasGroup>();
            if (loadingCanvasGroup != null)
            {
                loadingCanvasGroup.alpha = 0f;
                loadingCanvasGroup.interactable = false;
                loadingCanvasGroup.blocksRaycasts = false;
            }
            if (continuePromptText != null)
            {
                continuePromptText.gameObject.SetActive(false);
            }
        }

        public void StartLoading(string sceneName, float minDuration = 4.0f)
        {
            if (isLoading) return;
            targetSceneName = sceneName;
            minimumLoadingTime = minDuration;
            gameObject.SetActive(true);
            StartCoroutine(LoadingRoutine());
        }

        private IEnumerator LoadingRoutine()
        {
            isLoading = true;

            // 1. Fade In del Canvas de Carga
            if (loadingCanvasGroup != null)
            {
                loadingCanvasGroup.interactable = true;
                loadingCanvasGroup.blocksRaycasts = true;
                float fade = 0f;
                while (fade < 1f)
                {
                    fade += Time.deltaTime * 3.5f;
                    loadingCanvasGroup.alpha = Mathf.Clamp01(fade);
                    yield return null;
                }
            }

            // Iniciar minijuego
            if (minigameManager != null)
            {
                minigameManager.SetupMinigame();
            }

            // 2. Proceso de Carga
            float timer = 0f;
            float asyncProgress = 0f;
            AsyncOperation asyncOp = null;

            // Intentar carga asíncrona real si la escena está en BuildSettings
            if (Application.CanStreamedLevelBeLoaded(targetSceneName))
            {
                asyncOp = SceneManager.LoadSceneAsync(targetSceneName);
                asyncOp.allowSceneActivation = false;
            }

            string[] dots = { ".", "..", "...", "...." };
            int dotIdx = 0;
            float dotTimer = 0f;

            while (timer < minimumLoadingTime || (asyncOp != null && asyncOp.progress < 0.9f))
            {
                timer += Time.deltaTime;
                float timeFactor = Mathf.Clamp01(timer / minimumLoadingTime);

                if (asyncOp != null)
                {
                    asyncProgress = Mathf.Clamp01(asyncOp.progress / 0.9f);
                }
                else
                {
                    asyncProgress = timeFactor;
                }

                float displayProgress = Mathf.Min(timeFactor, asyncProgress);

                if (progressBarFill != null)
                {
                    progressBarFill.fillAmount = displayProgress;
                }
                if (progressPercentageText != null)
                {
                    progressPercentageText.text = $"{Mathf.RoundToInt(displayProgress * 100f)}%";
                }

                // Animación de texto NOW LOADING...
                dotTimer += Time.deltaTime;
                if (dotTimer >= 0.25f)
                {
                    dotTimer = 0f;
                    dotIdx = (dotIdx + 1) % dots.Length;
                    if (loadingStatusText != null)
                    {
                        loadingStatusText.text = $"NOW LOADING{dots[dotIdx]}";
                    }
                }

                yield return null;
            }

            // 3. Completado al 100%
            if (progressBarFill != null) progressBarFill.fillAmount = 1f;
            if (progressPercentageText != null) progressPercentageText.text = "100%";
            if (loadingStatusText != null) loadingStatusText.text = "ROUND READY!";

            // 4. Continuar al combate
            if (waitForInputAfterLoad)
            {
                if (continuePromptText != null)
                {
                    continuePromptText.gameObject.SetActive(true);
                    continuePromptText.text = "¡CARGA COMPLETA! PRESIONA [ENTER] O [ESPACIO]";
                }

                while (!Input.GetKeyDown(KeyCode.Return) && !Input.GetKeyDown(KeyCode.Space))
                {
                    yield return null;
                }
            }
            else
            {
                yield return new WaitForSeconds(0.6f);
            }

            // 5. Activación de Escena
            if (asyncOp != null)
            {
                asyncOp.allowSceneActivation = true;
            }
            else if (Application.CanStreamedLevelBeLoaded(targetSceneName))
            {
                SceneManager.LoadScene(targetSceneName);
            }
            else
            {
                Debug.LogWarning($"[LoadingScreen] Escena '{targetSceneName}' no encontrada en Build Settings. Simulando retorno o carga.");
                // Si la escena no está aún en build settings, fade out
                if (loadingCanvasGroup != null)
                {
                    float fade = 1f;
                    while (fade > 0f)
                    {
                        fade -= Time.deltaTime * 2.5f;
                        loadingCanvasGroup.alpha = Mathf.Clamp01(fade);
                        yield return null;
                    }
                    loadingCanvasGroup.interactable = false;
                    loadingCanvasGroup.blocksRaycasts = false;
                }
                isLoading = false;
            }
        }
    }
}
