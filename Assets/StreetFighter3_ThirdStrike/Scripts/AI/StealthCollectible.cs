using UnityEngine;
using StreetFighter3.Loading;

namespace Minigame.Waypoints
{
    [RequireComponent(typeof(SpriteRenderer))]
    public class StealthCollectible : MonoBehaviour
    {
        [Header("Configuracion")]
        [SerializeField] private float pickupRadius = 0.85f;
        [SerializeField] private float floatSpeed = 3.5f;
        [SerializeField] private float floatAmplitude = 0.15f;

        [Header("Animacion")]
        [SerializeField] private Sprite[] orbFrames;

        [Header("Referencias")]
        [SerializeField] private SpriteRenderer spriteRenderer;
        [SerializeField] private SpriteFrameAnimator frameAnimator;
        [SerializeField] private StealthPlayerController playerTarget;

        private Vector3 basePosition;
        private bool isCollected = false;
        private System.Action onCollectedCallback;

        public bool IsCollected => isCollected;

        private void Awake()
        {
            if (spriteRenderer == null) spriteRenderer = GetComponent<SpriteRenderer>();
            if (frameAnimator == null)
            {
                frameAnimator = GetComponent<SpriteFrameAnimator>();
                if (frameAnimator == null) frameAnimator = gameObject.AddComponent<SpriteFrameAnimator>();
            }
            basePosition = transform.position;
        }

        private void Start()
        {
            if (frameAnimator != null && orbFrames != null && orbFrames.Length > 0)
            {
                frameAnimator.PlayAnimation(orbFrames, true);
            }
        }

        private void Update()
        {
            if (isCollected) return;

            // Animacion flotante en Y
            transform.position = basePosition + new Vector3(0f, Mathf.Sin(Time.time * floatSpeed) * floatAmplitude, 0f);

            // Comprobacion de proximidad con el jugador
            if (playerTarget != null && playerTarget.CanControl)
            {
                float dist = Vector2.Distance(transform.position, playerTarget.Position);
                if (dist <= pickupRadius)
                {
                    Collect();
                }
            }
        }

        private void Collect()
        {
            isCollected = true;
            gameObject.SetActive(false);
            onCollectedCallback?.Invoke();
        }

        public void SetTargetPlayer(StealthPlayerController player)
        {
            playerTarget = player;
        }

        public void SetFrames(Sprite[] frames)
        {
            orbFrames = frames;
            if (frameAnimator != null && orbFrames != null && orbFrames.Length > 0)
            {
                frameAnimator.PlayAnimation(orbFrames, true);
            }
        }

        public void SetOnCollectedCallback(System.Action callback)
        {
            onCollectedCallback = callback;
        }

        public void ResetItem()
        {
            isCollected = false;
            transform.position = basePosition;
            gameObject.SetActive(true);
        }

        private void OnDrawGizmosSelected()
        {
            Gizmos.color = Color.green;
            Gizmos.DrawWireSphere(transform.position, pickupRadius);
        }
    }
}
