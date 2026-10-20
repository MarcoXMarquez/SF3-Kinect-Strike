using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace StreetFighter3.UI
{
    public enum MainMenuState
    {
        Root,
        VersusSubmenu
    }

    /// <summary>
    /// Controlador del MenÃº Principal arcade de Street Fighter III.
    /// Soporta navegaciÃ³n 100% por teclado, submenÃºs jerÃ¡rquicos (Versus Bot / Versus 2P),
    /// efectos de cursor/pulsaciÃ³n CPS-3 y transiciÃ³n hacia la pantalla de carga.
    /// </summary>
    public class MainMenuController : MonoBehaviour
    {
        [Header("Referencias de MenÃºs")]
        [SerializeField] private GameObject rootMenuPanel;
        [SerializeField] private GameObject versusSubmenuPanel;
        [SerializeField] private RectTransform cursorIndicator;

        [Header("Botones MenÃº Principal")]
        [SerializeField] private Button storyModeButton;
        [SerializeField] private Button versusButton;
        [SerializeField] private Button exitButton;

        [Header("Botones Submenú Versus")]
        [SerializeField] private Button versusBotButton;
        [SerializeField] private Button versus2PlayerButton;
        [SerializeField] private Button versusTombButton;
        [SerializeField] private Button backVersusButton;

        [Header("Audio")]
        [SerializeField] private AudioSource bgmAudioSource;
        [SerializeField] private AudioSource sfxAudioSource;
        [SerializeField] private AudioClip cursorMoveSfx;
        [SerializeField] private AudioClip confirmSelectSfx;
        [SerializeField] private AudioClip cancelBackSfx;

        [Header("Controlador de Carga")]
        [SerializeField] private LoadingScreenController loadingScreenController;
        [SerializeField] private string duelSceneName = "Sandbox_Sebas";
        [SerializeField] private string duelSceneChina = "Sandbox_China";
        [SerializeField] private string duelSceneTomb = "Sandbox_Tomb";
        [SerializeField] private string storyModeScene = "StoryMode_Scene";

        [Header("Modal PrÃ³ximamente (Modo Historia)")]
        [SerializeField] private GameObject comingSoonModalPanel;

        [Header("ConfiguraciÃ³n Visual")]
        [SerializeField] private Color normalColor = new Color(0.85f, 0.85f, 0.85f, 1f);
        [SerializeField] private Color selectedColor = new Color(1f, 0.88f, 0.15f, 1f);
        [SerializeField] private float pulseSpeed = 7f;
        [SerializeField] private float pulseAmount = 0.08f;

        private MainMenuState currentState = MainMenuState.Root;
        private int selectedIndex = 0;
        private bool isModalOpen = false;
        private readonly List<Button> currentButtons = new List<Button>();
        private readonly List<Vector3> originalScales = new List<Vector3>();

        private void Start()
        {
            if (sfxAudioSource == null) sfxAudioSource = gameObject.AddComponent<AudioSource>();
            EnterState(MainMenuState.Root);
        }

        public void EnterState(MainMenuState newState)
        {
            currentState = newState;
            selectedIndex = 0;

            // Restaurar escalas
            ResetButtonVisuals();

            currentButtons.Clear();
            originalScales.Clear();

            if (currentState == MainMenuState.Root)
            {
                if (rootMenuPanel != null) rootMenuPanel.SetActive(true);
                if (versusSubmenuPanel != null) versusSubmenuPanel.SetActive(false);

                if (storyModeButton != null) currentButtons.Add(storyModeButton);
                if (versusButton != null) currentButtons.Add(versusButton);
                if (exitButton != null) currentButtons.Add(exitButton);
            }
            else if (currentState == MainMenuState.VersusSubmenu)
            {
                if (rootMenuPanel != null) rootMenuPanel.SetActive(false);
                if (versusSubmenuPanel != null) versusSubmenuPanel.SetActive(true);

                if (versusBotButton != null) currentButtons.Add(versusBotButton);
                if (versus2PlayerButton != null) currentButtons.Add(versus2PlayerButton);
                if (versusTombButton != null) currentButtons.Add(versusTombButton);
                if (backVersusButton != null) currentButtons.Add(backVersusButton);
            }

            for (int i = 0; i < currentButtons.Count; i++)
            {
                originalScales.Add(currentButtons[i].transform.localScale);
            }

            UpdateSelectionVisuals(false);
        }

        private void Update()
        {
            if (loadingScreenController != null && loadingScreenController.gameObject.activeSelf && loadingScreenController.GetComponent<CanvasGroup>() != null && loadingScreenController.GetComponent<CanvasGroup>().alpha > 0.01f)
            {
                // Si la pantalla de carga estÃ¡ activa, suspender el menÃº
                return;
            }

            HandleKeyboardInput();
            AnimateSelectedButton();
        }

        private void HandleKeyboardInput()
        {
            if (isModalOpen)
            {
                if (Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.Space) ||
                    Input.GetKeyDown(KeyCode.KeypadEnter) || Input.GetKeyDown(KeyCode.Escape) ||
                    Input.GetKeyDown(KeyCode.Backspace))
                {
                    CloseComingSoonModal();
                }
                return;
            }

            if (currentButtons.Count == 0) return;

            // NavegaciÃ³n Vertical (W / S o Flechas)
            if (Input.GetKeyDown(KeyCode.W) || Input.GetKeyDown(KeyCode.UpArrow))
            {
                Navigate(-1);
            }
            else if (Input.GetKeyDown(KeyCode.S) || Input.GetKeyDown(KeyCode.DownArrow))
            {
                Navigate(1);
            }

            // ConfirmaciÃ³n (Enter / Espacio)
            if (Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.Space) || Input.GetKeyDown(KeyCode.KeypadEnter))
            {
                ConfirmSelection();
            }

            // Volver / Cancelar (Escape / Backspace)
            if (Input.GetKeyDown(KeyCode.Escape) || Input.GetKeyDown(KeyCode.Backspace))
            {
                if (currentState == MainMenuState.VersusSubmenu)
                {
                    PlaySFX(cancelBackSfx);
                    EnterState(MainMenuState.Root);
                }
            }
        }

        public void OpenComingSoonModal()
        {
            isModalOpen = true;
            if (comingSoonModalPanel != null)
            {
                comingSoonModalPanel.SetActive(true);
            }
        }

        public void CloseComingSoonModal()
        {
            isModalOpen = false;
            if (comingSoonModalPanel != null)
            {
                comingSoonModalPanel.SetActive(false);
            }
            PlaySFX(cancelBackSfx);
        }

        private void Navigate(int direction)
        {
            if (currentButtons.Count == 0) return;

            int prevIndex = selectedIndex;
            selectedIndex = (selectedIndex + direction + currentButtons.Count) % currentButtons.Count;

            if (selectedIndex != prevIndex)
            {
                PlaySFX(cursorMoveSfx);
                UpdateSelectionVisuals(true);
            }
        }

        private void ConfirmSelection()
        {
            if (selectedIndex < 0 || selectedIndex >= currentButtons.Count) return;

            PlaySFX(confirmSelectSfx);

            if (currentState == MainMenuState.Root)
            {
                switch (selectedIndex)
                {
                    case 0: // Modo Historia -> Cinemática y Diálogos DBZ Tenkaichi 3
                        Debug.Log("[MainMenu] Modo Historia seleccionado. Iniciando Modo Historia y Cinemáticas DBZ Tenkaichi de KINET STRIKE...");
                        LaunchLoadingScreen(storyModeScene, 2.5f);
                        break;
                    case 1: // Versus (Abrir SubmenÃº)
                        EnterState(MainMenuState.VersusSubmenu);
                        break;
                    case 2: // Salir
                        QuitApplication();
                        break;
                }
            }
            else if (currentState == MainMenuState.VersusSubmenu)
            {
                if (currentButtons.Contains(versusTombButton))
                {
                    switch (selectedIndex)
                    {
                        case 0: // Japón (Suzaku Castle)
                            Debug.Log("[MainMenu] Iniciando Duelo en Suzaku Castle (Japón)...");
                            LaunchLoadingScreen(duelSceneName, 4.5f);
                            break;
                        case 1: // China (Crowded Street)
                            Debug.Log("[MainMenu] Iniciando Duelo en Crowded Street (China)...");
                            LaunchLoadingScreen(duelSceneChina, 4.0f);
                            break;
                        case 2: // Grecia (Tomb of Urien)
                            Debug.Log("[MainMenu] Iniciando Duelo en Olympian Tomb (Grecia - Urien)...");
                            LaunchLoadingScreen(duelSceneTomb, 4.0f);
                            break;
                        case 3: // Volver
                            EnterState(MainMenuState.Root);
                            break;
                    }
                }
                else
                {
                    switch (selectedIndex)
                    {
                        case 0:
                            LaunchLoadingScreen(duelSceneName, 4.5f);
                            break;
                        case 1:
                            LaunchLoadingScreen(duelSceneChina, 4.0f);
                            break;
                        case 2:
                            EnterState(MainMenuState.Root);
                            break;
                    }
                }
            }
        }

        private void LaunchLoadingScreen(string sceneName, float minDuration)
        {
            if (loadingScreenController != null)
            {
                loadingScreenController.StartLoading(sceneName, minDuration);
            }
            else
            {
                Debug.LogWarning($"[MainMenu] Cargando directamente '{sceneName}' sin pantalla de carga.");
                UnityEngine.SceneManagement.SceneManager.LoadScene(sceneName);
            }
        }

        private void QuitApplication()
        {
            Debug.Log("[MainMenu] Cerrando juego...");
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
        }

        private void UpdateSelectionVisuals(bool snapCursor)
        {
            for (int i = 0; i < currentButtons.Count; i++)
            {
                Button btn = currentButtons[i];
                if (btn == null) continue;

                Text btnText = btn.GetComponentInChildren<Text>();
                bool isSelected = (i == selectedIndex);

                if (btnText != null)
                {
                    btnText.color = isSelected ? selectedColor : normalColor;
                }

                if (!isSelected && i < originalScales.Count)
                {
                    btn.transform.localScale = originalScales[i];
                }
            }

            // Posicionar cursor indicador
            if (cursorIndicator != null && selectedIndex >= 0 && selectedIndex < currentButtons.Count)
            {
                Button currentBtn = currentButtons[selectedIndex];
                RectTransform btnRt = currentBtn.GetComponent<RectTransform>();

                Vector3 targetPos = btnRt.position + new Vector3(-btnRt.rect.width * 0.5f - 30f, 0f, 0f);
                if (snapCursor)
                {
                    cursorIndicator.position = targetPos;
                }
                else
                {
                    cursorIndicator.position = targetPos;
                }
            }
        }

        private void AnimateSelectedButton()
        {
            if (selectedIndex < 0 || selectedIndex >= currentButtons.Count) return;

            Button activeBtn = currentButtons[selectedIndex];
            if (activeBtn == null || selectedIndex >= originalScales.Count) return;

            // PulsaciÃ³n de escala con onda senoidal
            float scaleMultiplier = 1f + Mathf.Sin(Time.unscaledTime * pulseSpeed) * pulseAmount;
            activeBtn.transform.localScale = originalScales[selectedIndex] * scaleMultiplier;

            // Ligera oscilaciÃ³n horizontal del cursor
            if (cursorIndicator != null)
            {
                float cursorOffset = Mathf.Sin(Time.unscaledTime * 8f) * 6f;
                RectTransform btnRt = activeBtn.GetComponent<RectTransform>();
                cursorIndicator.position = btnRt.position + new Vector3(-btnRt.rect.width * 0.5f - 30f + cursorOffset, 0f, 0f);
            }
        }

        private void ResetButtonVisuals()
        {
            for (int i = 0; i < currentButtons.Count; i++)
            {
                if (currentButtons[i] != null && i < originalScales.Count)
                {
                    currentButtons[i].transform.localScale = originalScales[i];
                }
            }
        }

        private void PlaySFX(AudioClip clip)
        {
            if (clip != null && sfxAudioSource != null)
            {
                sfxAudioSource.PlayOneShot(clip, 0.9f);
            }
        }
    }
}
