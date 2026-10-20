using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

namespace Minigame.Waypoints
{
    public enum StealthGameState
    {
        Playing,
        GameOverDetected,
        Victory
    }

    public class StealthMinigameManager : MonoBehaviour
    {
        [Header("Referencias Principales")]
        [SerializeField] private StealthPlayerController player;
        [SerializeField] private List<WaypointPatrolNPC> guards = new List<WaypointPatrolNPC>();
        [SerializeField] private List<StealthCollectible> collectibles = new List<StealthCollectible>();
        [SerializeField] private StealthGoal goal;

        [Header("Puntos de Inicio")]
        [SerializeField] private Vector3 playerStartPos = new Vector3(-6f, -3f, 0f);

        [Header("UI Canvas")]
        [SerializeField] private Text statusText;
        [SerializeField] private Text orbsCounterText;
        [SerializeField] private Text timerText;
        [SerializeField] private Text helperHintText;

        private StealthGameState currentState = StealthGameState.Playing;
        private int collectedCount = 0;
        private float gameTimer = 0f;

        public StealthGameState CurrentState => currentState;

        private void Start()
        {
            SetupGame();
        }

        private void Update()
        {
            if (currentState == StealthGameState.Playing)
            {
                gameTimer += Time.deltaTime;
                UpdateTimerDisplay();
            }

            // Atajo de reinicio con tecla R
            if (Input.GetKeyDown(KeyCode.R))
            {
                RestartGame();
            }

            // Atajo para volver al Menú Principal con ESC o M
            if (Input.GetKeyDown(KeyCode.Escape) || Input.GetKeyDown(KeyCode.M))
            {
                ReturnToMainMenu();
            }
        }

        public void ReturnToMainMenu()
        {
            Time.timeScale = 1f;
            SceneManager.LoadScene("MainMenu_Scene");
        }

        private void SetupGame()
        {
            currentState = StealthGameState.Playing;
            collectedCount = 0;
            gameTimer = 0f;

            if (player != null)
            {
                player.ResetPosition(playerStartPos);
            }

            for (int i = 0; i < guards.Count; i++)
            {
                if (guards[i] != null)
                {
                    guards[i].ResetToWaypoint(0);
                    guards[i].SetTargetPlayer(player != null ? player.transform : null);
                    guards[i].SetOnPlayerCaughtCallback(OnPlayerDetected);
                }
            }

            for (int i = 0; i < collectibles.Count; i++)
            {
                if (collectibles[i] != null)
                {
                    collectibles[i].ResetItem();
                    collectibles[i].SetTargetPlayer(player);
                    collectibles[i].SetOnCollectedCallback(OnItemCollected);
                }
            }

            if (goal != null)
            {
                goal.ResetGoal();
                goal.SetTargetPlayer(player);
                goal.SetOnGoalReachedCallback(OnVictoryReached);
            }

            UpdateUI();
        }

        private void OnItemCollected()
        {
            collectedCount++;
            UpdateUI();

            if (collectedCount >= collectibles.Count)
            {
                if (goal != null)
                {
                    goal.SetUnlocked(true);
                }

                if (statusText != null)
                {
                    statusText.text = "¡TODOS LOS ORBES RECOGIDOS! CRUZA EL PORTAL DIMENSIONAL";
                    statusText.color = new Color(0.75f, 0.4f, 1.0f);
                }
            }
        }

        private void OnPlayerDetected()
        {
            if (currentState != StealthGameState.Playing) return;

            currentState = StealthGameState.GameOverDetected;

            if (player != null)
            {
                player.OnCaught();
            }

            if (statusText != null)
            {
                statusText.text = "¡DETECTADO POR LA PATRULLA! [R] REINTENTAR | [ESC] MENÚ";
                statusText.color = new Color(1f, 0.25f, 0.2f);
            }
        }

        private void OnVictoryReached()
        {
            if (currentState != StealthGameState.Playing) return;

            currentState = StealthGameState.Victory;

            if (player != null)
            {
                player.OnVictory();
            }

            if (statusText != null)
            {
                statusText.text = string.Format("¡MISIÓN COMPLETADA! TIEMPO: {0:F1}s | [R] REPETIR | [ESC] MENÚ", gameTimer);
                statusText.color = new Color(0.3f, 1f, 0.6f);
            }
        }

        public void RestartGame()
        {
            SetupGame();
        }

        private void UpdateUI()
        {
            if (orbsCounterText != null)
            {
                orbsCounterText.text = string.Format("ORBES: {0} / {1}", collectedCount, collectibles.Count);
            }

            if (currentState == StealthGameState.Playing && collectedCount < collectibles.Count && statusText != null)
            {
                statusText.text = "OBJETIVO: EVITA LAS RUTAS DE WAYPOINTS Y RECOGE LOS ORBES";
                statusText.color = new Color(1f, 0.9f, 0.2f);
            }

            if (helperHintText != null)
            {
                helperHintText.text = "CONTROLES: [WASD / FLECHAS] Moverse  |  [R] Reiniciar  |  [ESC] Volver al Menú";
            }
        }

        private void UpdateTimerDisplay()
        {
            if (timerText != null)
            {
                int minutes = Mathf.FloorToInt(gameTimer / 60f);
                int seconds = Mathf.FloorToInt(gameTimer % 60f);
                timerText.text = string.Format("TIEMPO: {0:00}:{1:00}", minutes, seconds);
            }
        }

        public void SetReferences(StealthPlayerController p, List<WaypointPatrolNPC> g, List<StealthCollectible> c, StealthGoal gl)
        {
            player = p;
            guards = g;
            collectibles = c;
            goal = gl;
        }

        public void SetUIReferences(Text status, Text counter, Text timer, Text hint)
        {
            statusText = status;
            orbsCounterText = counter;
            timerText = timer;
            helperHintText = hint;
        }
    }
}
