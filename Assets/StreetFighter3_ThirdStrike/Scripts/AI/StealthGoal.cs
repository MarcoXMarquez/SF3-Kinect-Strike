using UnityEngine;

namespace Minigame.Waypoints
{
    [RequireComponent(typeof(SpriteRenderer))]
    public class StealthGoal : MonoBehaviour
    {
        [Header("Parametros")]
        [SerializeField] private float activationRadius = 1.0f;
        [SerializeField] private Color lockedColor = new Color(0.8f, 0.2f, 0.2f, 0.7f);
        [SerializeField] private Color unlockedColor = new Color(0.2f, 1f, 0.4f, 0.9f);

        [Header("Referencias")]
        [SerializeField] private SpriteRenderer spriteRenderer;
        [SerializeField] private StealthPlayerController player;

        private bool isUnlocked = false;
        private bool hasCompleted = false;
        private System.Action onGoalReachedCallback;

        public bool IsUnlocked => isUnlocked;

        private void Awake()
        {
            if (spriteRenderer == null) spriteRenderer = GetComponent<SpriteRenderer>();
            UpdateVisual();
        }

        private void Update()
        {
            if (!isUnlocked || hasCompleted || player == null || !player.CanControl) return;

            float dist = Vector2.Distance(transform.position, player.Position);
            if (dist <= activationRadius)
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
            UpdateVisual();
        }

        private void UpdateVisual()
        {
            if (spriteRenderer != null)
            {
                spriteRenderer.color = isUnlocked ? unlockedColor : lockedColor;
            }
        }

        private void OnDrawGizmos()
        {
            Gizmos.color = isUnlocked ? Color.green : Color.red;
            Gizmos.DrawWireSphere(transform.position, activationRadius);
        }
    }
}
