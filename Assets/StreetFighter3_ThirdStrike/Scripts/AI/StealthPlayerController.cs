using UnityEngine;
using StreetFighter3.Loading;

namespace Minigame.Waypoints
{
    [RequireComponent(typeof(SpriteRenderer))]
    [RequireComponent(typeof(Rigidbody2D))]
    [RequireComponent(typeof(CircleCollider2D))]
    public class StealthPlayerController : MonoBehaviour
    {
        [Header("Movimiento")]
        [SerializeField] private float moveSpeed = 4.0f;
        [SerializeField] private Rect moveBounds = new Rect(-6.8f, -3.5f, 13.6f, 7.0f);
        [SerializeField] private LayerMask obstacleLayerMask = ~0;

        [Header("Animaciones")]
        [SerializeField] private Sprite[] idleFrames;
        [SerializeField] private Sprite[] walkFrames;
        [SerializeField] private Sprite[] hitFrames;

        [Header("Referencias")]
        [SerializeField] private SpriteRenderer spriteRenderer;
        [SerializeField] private SpriteFrameAnimator frameAnimator;
        [SerializeField] private Rigidbody2D rb;
        [SerializeField] private CircleCollider2D circleCollider;

        private bool canControl = true;
        private bool isMoving = false;
        private Vector2 movementInput = Vector2.zero;
        private Vector3 spawnPosition;
        private const float COLLIDER_RADIUS = 0.38f;
        private static readonly Vector2 COLLIDER_OFFSET = new Vector2(0f, 0.4f);
        private readonly RaycastHit2D[] hitResults = new RaycastHit2D[6];
        private ContactFilter2D contactFilter;

        public bool CanControl => canControl;
        public Vector2 Position => rb != null ? rb.position : (Vector2)transform.position;

        private void Awake()
        {
            if (spriteRenderer == null) spriteRenderer = GetComponent<SpriteRenderer>();
            if (frameAnimator == null)
            {
                frameAnimator = GetComponent<SpriteFrameAnimator>();
                if (frameAnimator == null) frameAnimator = gameObject.AddComponent<SpriteFrameAnimator>();
            }

            if (rb == null) rb = GetComponent<Rigidbody2D>();
            if (rb != null)
            {
                rb.bodyType = RigidbodyType2D.Dynamic;
                rb.gravityScale = 0f;
                rb.freezeRotation = true;
                rb.collisionDetectionMode = CollisionDetectionMode2D.Continuous;
                rb.interpolation = RigidbodyInterpolation2D.Interpolate;
            }

            if (circleCollider == null) circleCollider = GetComponent<CircleCollider2D>();
            if (circleCollider != null)
            {
                circleCollider.radius = COLLIDER_RADIUS;
                circleCollider.offset = COLLIDER_OFFSET;
                circleCollider.isTrigger = false;
            }

            contactFilter = new ContactFilter2D();
            contactFilter.useTriggers = false;
            contactFilter.SetLayerMask(obstacleLayerMask);
            contactFilter.useLayerMask = true;

            spawnPosition = transform.position;
        }

        private void Start()
        {
            PlayIdle();
        }

        private void Update()
        {
            if (!canControl)
            {
                movementInput = Vector2.zero;
                return;
            }

            float horizontal = Input.GetAxisRaw("Horizontal");
            float vertical = Input.GetAxisRaw("Vertical");

            movementInput = new Vector2(horizontal, vertical);

            if (movementInput.sqrMagnitude > 0.01f)
            {
                movementInput.Normalize();

                if (horizontal > 0.05f) spriteRenderer.flipX = false;
                else if (horizontal < -0.05f) spriteRenderer.flipX = true;

                if (!isMoving)
                {
                    isMoving = true;
                    PlayWalk();
                }
            }
            else
            {
                movementInput = Vector2.zero;
                if (isMoving)
                {
                    isMoving = false;
                    PlayIdle();
                }
            }
        }

        private void FixedUpdate()
        {
            if (rb == null) return;

            if (!canControl || movementInput.sqrMagnitude < 0.001f)
            {
                rb.linearVelocity = Vector2.zero;
                return;
            }

            Vector2 desiredVel = movementInput * moveSpeed;
            float castDistance = moveSpeed * Time.fixedDeltaTime + 0.05f;

            // Deteccion predictiva de obstaculos mediante rb.Cast para frenar y deslizar en paredes
            int hitCount = rb.Cast(movementInput, contactFilter, hitResults, castDistance);
            for (int i = 0; i < hitCount; i++)
            {
                RaycastHit2D hit = hitResults[i];
                if (hit.collider != null && !hit.collider.isTrigger && hit.collider != circleCollider)
                {
                    Vector2 normal = hit.normal;
                    float dotNormal = Vector2.Dot(desiredVel, normal);
                    if (dotNormal < 0f)
                    {
                        // Deslizar tangencialmente a lo largo de la superficie del obstaculo
                        desiredVel -= normal * dotNormal;
                    }
                    break;
                }
            }

            // Aplicar velocidad fisica
            rb.linearVelocity = desiredVel;

            // Restringir posicion dentro de los limites seguros de la arena
            Vector2 pos = rb.position;
            if (moveBounds.width > 0f && moveBounds.height > 0f)
            {
                float clampedX = Mathf.Clamp(pos.x, moveBounds.xMin, moveBounds.xMax);
                float clampedY = Mathf.Clamp(pos.y, moveBounds.yMin, moveBounds.yMax);

                if (clampedX != pos.x || clampedY != pos.y)
                {
                    rb.position = new Vector2(clampedX, clampedY);
                }
            }
        }

        public void SetBounds(Rect bounds)
        {
            moveBounds = bounds;
        }

        public void SetAnimationFrames(Sprite[] idle, Sprite[] walk, Sprite[] hit = null)
        {
            idleFrames = idle;
            walkFrames = walk;
            hitFrames = hit;
        }

        public void OnCaught()
        {
            canControl = false;
            isMoving = false;
            movementInput = Vector2.zero;
            if (rb != null) rb.linearVelocity = Vector2.zero;

            if (frameAnimator != null && hitFrames != null && hitFrames.Length > 0)
            {
                frameAnimator.PlayAnimation(hitFrames, false);
            }
        }

        public void OnVictory()
        {
            canControl = false;
            isMoving = false;
            movementInput = Vector2.zero;
            if (rb != null) rb.linearVelocity = Vector2.zero;
            PlayIdle();
        }

        public void ResetPosition(Vector3 position)
        {
            transform.position = position;
            if (rb != null)
            {
                rb.position = position;
                rb.linearVelocity = Vector2.zero;
            }
            canControl = true;
            isMoving = false;
            movementInput = Vector2.zero;
            PlayIdle();
        }

        private void PlayIdle()
        {
            if (frameAnimator != null && idleFrames != null && idleFrames.Length > 0)
            {
                frameAnimator.PlayAnimation(idleFrames, true);
            }
        }

        private void PlayWalk()
        {
            if (frameAnimator != null && walkFrames != null && walkFrames.Length > 0)
            {
                frameAnimator.PlayAnimation(walkFrames, true);
            }
        }
    }
}
