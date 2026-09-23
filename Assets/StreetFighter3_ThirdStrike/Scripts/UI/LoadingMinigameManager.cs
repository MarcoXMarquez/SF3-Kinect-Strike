using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using StreetFighter3.AI.Steering;

namespace StreetFighter3.UI
{
    /// <summary>
    /// Administrador del minijuego interactivo de la pantalla de carga (estilo DBZ Tenkaichi 3).
    /// Coordina entidades autónomas con algoritmos cinemáticos de Wandering y Seeking,
    /// maneja el avatar del jugador y registra la puntuación de entrenamiento.
    /// </summary>
    public class LoadingMinigameManager : MonoBehaviour
    {
        [Header("Referencias")]
        [SerializeField] private RectTransform minigameContainer;
        [SerializeField] private MiniFighterController playerFighter;
        [SerializeField] private Text scoreText;
        [SerializeField] private Text algoBadgeText;
        [SerializeField] private Text hintText;

        [Header("Configuración de Algoritmos Cinemáticos")]
        [SerializeField] private int wanderingTargetsCount = 3;
        [SerializeField] private Sprite targetSprite;
        [SerializeField] private Sprite chaserSprite;
        [SerializeField] private AudioClip collectSound;
        [SerializeField] private AudioClip punchSound;

        [Header("Límites del Área (UI)")]
        [SerializeField] private Vector2 areaBounds = new Vector2(460f, 180f);

        private readonly List<SteeringUIEntity> wanderingEntities = new List<SteeringUIEntity>();
        private SteeringUIEntity seekingEntity;
        private SeekBehavior seekLogic;
        private int currentScore = 0;
        private AudioSource audioSource;

        private void Awake()
        {
            audioSource = GetComponent<AudioSource>();
            if (audioSource == null) audioSource = gameObject.AddComponent<AudioSource>();
        }

        public void InitializeMinigame(Sprite orbSprite, Sprite seekerSpr, AudioClip hitSfx, AudioClip bounceSfx)
        {
            if (orbSprite != null) targetSprite = orbSprite;
            if (seekerSpr != null) chaserSprite = seekerSpr;
            if (hitSfx != null) punchSound = hitSfx;
            if (bounceSfx != null) collectSound = bounceSfx;

            SetupMinigame();
        }

        private void Start()
        {
            if (wanderingEntities.Count == 0)
            {
                SetupMinigame();
            }
        }

        public void SetupMinigame()
        {
            if (minigameContainer == null) minigameContainer = GetComponent<RectTransform>();

            // 1. Limpiar entidades previas si existiesen
            foreach (var ent in wanderingEntities)
            {
                if (ent != null) Destroy(ent.gameObject);
            }
            wanderingEntities.Clear();

            if (seekingEntity != null)
            {
                Destroy(seekingEntity.gameObject);
                seekingEntity = null;
            }

            // 2. Instanciar Entidades con algoritmo WANDERING (Merodeo de Reynolds)
            for (int i = 0; i < wanderingTargetsCount; i++)
            {
                SteeringUIEntity orb = CreateEntity($"WanderOrb_{i + 1}", new Vector2(36f, 36f), targetSprite, new Color(0.2f, 0.85f, 1f, 0.95f));
                orb.SetBounds(-areaBounds, areaBounds);
                orb.SetSpeedAndForce(140f + i * 20f, 190f);

                // Algoritmo de Merodeo: radio 35, distancia 60, tasa de giro suave
                WanderBehavior wander = new WanderBehavior(35f, 60f, 35f);
                orb.SetBehavior(wander);

                // Posición inicial aleatoria
                RectTransform rt = orb.GetComponent<RectTransform>();
                rt.anchoredPosition = new Vector2(
                    Random.Range(-areaBounds.x * 0.7f, areaBounds.x * 0.7f),
                    Random.Range(-areaBounds.y * 0.4f, areaBounds.y * 0.8f)
                );

                wanderingEntities.Add(orb);
            }

            // 3. Instanciar Entidad con algoritmo SEEKING (Persecución de Reynolds)
            seekingEntity = CreateEntity("Seeker_Spirit", new Vector2(42f, 42f), chaserSprite, new Color(1f, 0.4f, 0.1f, 0.95f));
            seekingEntity.SetBounds(-areaBounds, areaBounds);
            seekingEntity.SetSpeedAndForce(175f, 240f);

            // Algoritmo de Persecución persiguiendo el primer orbe
            seekLogic = new SeekBehavior();
            seekingEntity.SetBehavior(seekLogic);

            RectTransform seekerRt = seekingEntity.GetComponent<RectTransform>();
            seekerRt.anchoredPosition = new Vector2(0f, areaBounds.y * 0.5f);

            // 4. Conectar evento de golpe del jugador
            if (playerFighter != null)
            {
                playerFighter.OnPunchTriggered = HandlePlayerPunch;
            }

            // 5. Configurar Textos HUD
            UpdateScoreUI();
            if (algoBadgeText != null)
            {
                algoBadgeText.text = "⚡ CINEMÁTICA IA: [Wandering: 3 Orbes Libres] + [Seeking: Orbe Perseguidor]";
            }
            if (hintText != null)
            {
                hintText.text = "🎮 Controles: [A/D: Mover] [W: Saltar] [J/F/Espacio: Golpear Orbes]";
            }
        }

        private SteeringUIEntity CreateEntity(string entityName, Vector2 size, Sprite sprite, Color tint)
        {
            GameObject go = new GameObject(entityName);
            go.transform.SetParent(minigameContainer, false);

            RectTransform rt = go.AddComponent<RectTransform>();
            rt.sizeDelta = size;

            Image img = go.AddComponent<Image>();
            if (sprite != null)
            {
                img.sprite = sprite;
                img.color = Color.white;
            }
            else
            {
                img.color = tint;
            }

            SteeringUIEntity entity = go.AddComponent<SteeringUIEntity>();
            return entity;
        }

        private void Update()
        {
            // 1. Actualizar objetivo del algoritmo SEEKING (perseguir el orbe más cercano)
            UpdateSeekingTarget();

            // 2. Comprobar colisiones por proximidad con el jugador
            CheckPlayerProximity();

            // 3. Comprobar si el perseguidor atrapa algún orbe
            CheckSeekerCapture();
        }

        private void UpdateSeekingTarget()
        {
            if (seekLogic == null || seekingEntity == null) return;

            SteeringUIEntity closestOrb = null;
            float minDist = float.MaxValue;
            Vector2 seekerPos = seekingEntity.Position;

            for (int i = 0; i < wanderingEntities.Count; i++)
            {
                var orb = wanderingEntities[i];
                if (orb == null) continue;

                float d = Vector2.Distance(seekerPos, orb.Position);
                if (d < minDist)
                {
                    minDist = d;
                    closestOrb = orb;
                }
            }

            if (closestOrb != null)
            {
                seekLogic.TargetPosition = closestOrb.Position;
            }
            else if (playerFighter != null)
            {
                seekLogic.TargetPosition = playerFighter.Position + Vector2.up * 40f;
            }
        }

        private void CheckPlayerProximity()
        {
            if (playerFighter == null) return;

            Vector2 playerPos = playerFighter.Position + Vector2.up * 40f;
            float touchRadius = 45f;
            float punchRadius = playerFighter.AttackRange;

            for (int i = wanderingEntities.Count - 1; i >= 0; i--)
            {
                var orb = wanderingEntities[i];
                if (orb == null) continue;

                float dist = Vector2.Distance(playerPos, orb.Position);

                // Si el jugador está golpeando y está a rango de ataque
                if (playerFighter.IsAttacking && dist < punchRadius)
                {
                    PopOrb(orb, 20, true);
                }
                // O si simplemente lo toca al saltar/caminar
                else if (dist < touchRadius)
                {
                    PopOrb(orb, 10, false);
                }
            }
        }

        private void HandlePlayerPunch()
        {
            if (punchSound != null && audioSource != null)
            {
                audioSource.PlayOneShot(punchSound, 0.7f);
            }
        }

        private void CheckSeekerCapture()
        {
            if (seekingEntity == null) return;

            Vector2 seekerPos = seekingEntity.Position;
            float captureRadius = 32f;

            for (int i = wanderingEntities.Count - 1; i >= 0; i--)
            {
                var orb = wanderingEntities[i];
                if (orb == null) continue;

                if (Vector2.Distance(seekerPos, orb.Position) < captureRadius)
                {
                    PopOrb(orb, 5, false);
                }
            }
        }

        private void PopOrb(SteeringUIEntity orb, int points, bool isPunch)
        {
            currentScore += points;
            UpdateScoreUI();

            if (collectSound != null && audioSource != null)
            {
                audioSource.PlayOneShot(collectSound, 0.8f);
            }

            // Reubicar orbe recolectado con nuevo rumbo aleatorio (respawn)
            RectTransform rt = orb.GetComponent<RectTransform>();
            rt.anchoredPosition = new Vector2(
                Random.Range(-areaBounds.x * 0.8f, areaBounds.x * 0.8f),
                Random.Range(-areaBounds.y * 0.2f, areaBounds.y * 0.8f)
            );
        }

        private void UpdateScoreUI()
        {
            if (scoreText != null)
            {
                scoreText.text = $"PUNTOS DBZ: {currentScore:D4}";
            }
        }
    }
}
