using UnityEngine;

namespace Minigame.Waypoints
{
    [RequireComponent(typeof(SpriteRenderer))]
    [RequireComponent(typeof(CircleCollider2D))]
    public class StealthGoal : MonoBehaviour
    {
        [Header("Parametros")]
        [SerializeField] private float activationRadius = 1.3f;
        [SerializeField] private float baseScale = 1.8f;
        [SerializeField] private Material portalMaterial;

        [Header("Referencias")]
        [SerializeField] private SpriteRenderer spriteRenderer;
        [SerializeField] private CircleCollider2D triggerCollider;
        [SerializeField] private StealthPlayerController player;

        private bool isUnlocked = false;
        private bool hasCompleted = false;
        private System.Action onGoalReachedCallback;
        private Material materialInstance;

        public bool IsUnlocked => isUnlocked;

        private void Awake()
        {
            if (spriteRenderer == null) spriteRenderer = GetComponent<SpriteRenderer>();

            if (triggerCollider == null) triggerCollider = GetComponent<CircleCollider2D>();
            if (triggerCollider != null)
            {
                triggerCollider.isTrigger = true;
                triggerCollider.radius = activationRadius * 0.6f;
            }

            if (spriteRenderer != null && spriteRenderer.sharedMaterial != null)
            {
                materialInstance = spriteRenderer.material;
            }

            transform.localScale = new Vector3(baseScale, baseScale, 1f);
            UpdateVisual();
        }

        private void Update()
        {
            // Efecto de pulsacion dimensional continua
            float pulse = 1f + Mathf.Sin(Time.time * (isUnlocked ? 4.5f : 2.0f)) * 0.05f;
            transform.localScale = new Vector3(baseScale * pulse, baseScale * pulse, 1f);

            if (hasCompleted) return;

            // Deteccion redundante por distancia para maxima robustez
            if (player != null && player.CanControl)
            {
                float dist = Vector2.Distance(transform.position, player.Position);
                if (dist <= activationRadius)
                {
                    TryActivateGoal();
                }
            }
        }

        private void OnTriggerEnter2D(Collider2D other)
        {
            if (hasCompleted) return;

            StealthPlayerController p = other.GetComponent<StealthPlayerController>();
            if (p != null && p.CanControl)
            {
                TryActivateGoal();
            }
        }

        private void TryActivateGoal()
        {
            if (hasCompleted) return;

            if (isUnlocked)
            {
                hasCompleted = true;
                onGoalReachedCallback?.Invoke();
            }
        }

        public void SetUnlocked(bool unlocked)
        {
            isUnlocked = unlocked;
            UpdateVisual();
        }

        public void SetTargetPlayer(StealthPlayerController target)
        {
            player = target;
        }

        public void SetOnGoalReachedCallback(System.Action callback)
        {
            onGoalReachedCallback = callback;
        }

        public void ResetGoal()
        {
            isUnlocked = false;
            hasCompleted = false;
            transform.localScale = new Vector3(baseScale, baseScale, 1f);
            UpdateVisual();
        }

        private void UpdateVisual()
        {
            if (materialInstance != null)
            {
                materialInstance.SetFloat("_IsUnlocked", isUnlocked ? 1.0f : 0.0f);
            }
            else if (spriteRenderer != null && spriteRenderer.material != null)
            {
                materialInstance = spriteRenderer.material;
                materialInstance.SetFloat("_IsUnlocked", isUnlocked ? 1.0f : 0.0f);
            }
        }

        private void OnDrawGizmos()
        {
            Gizmos.color = isUnlocked ? new Color(0.6f, 0.2f, 1f, 0.8f) : new Color(0.3f, 0.1f, 0.4f, 0.5f);
            Gizmos.DrawWireSphere(transform.position, activationRadius);
        }
    }
}
