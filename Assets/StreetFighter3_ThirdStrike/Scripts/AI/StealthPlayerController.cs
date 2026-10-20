using UnityEngine;
using StreetFighter3.Loading;

namespace Minigame.Waypoints
{
    [RequireComponent(typeof(SpriteRenderer))]
    public class StealthPlayerController : MonoBehaviour
    {
        [Header("Movimiento")]
        [SerializeField] private float moveSpeed = 4.0f;
        [SerializeField] private Rect moveBounds = new Rect(-7.5f, -4f, 15f, 8f);

        [Header("Animaciones")]
        [SerializeField] private Sprite[] idleFrames;
        [SerializeField] private Sprite[] walkFrames;
        [SerializeField] private Sprite[] hitFrames;

        [Header("Referencias")]
        [SerializeField] private SpriteRenderer spriteRenderer;
        [SerializeField] private SpriteFrameAnimator frameAnimator;

        private bool canControl = true;
        private bool isMoving = false;
        private Vector3 spawnPosition;

        public bool CanControl => canControl;
        public Vector2 Position => transform.position;

        private void Awake()
        {
            if (spriteRenderer == null) spriteRenderer = GetComponent<SpriteRenderer>();
            if (frameAnimator == null)
            {
                frameAnimator = GetComponent<SpriteFrameAnimator>();
                if (frameAnimator == null) frameAnimator = gameObject.AddComponent<SpriteFrameAnimator>();
            }
            spawnPosition = transform.position;
        }

        private void Start()
        {
            PlayIdle();
        }

        private void Update()
        {
            if (!canControl) return;

            float horizontal = Input.GetAxisRaw("Horizontal");
            float vertical = Input.GetAxisRaw("Vertical");

            Vector2 inputDir = new Vector2(horizontal, vertical);

            if (inputDir.sqrMagnitude > 0.01f)
            {
                inputDir.Normalize();
                Vector3 delta = (Vector3)(inputDir * (moveSpeed * Time.deltaTime));
                Vector3 newPos = transform.position + delta;

                // Restringir dentro de los limites del mapa
                if (moveBounds.width > 0f && moveBounds.height > 0f)
                {
                    newPos.x = Mathf.Clamp(newPos.x, moveBounds.xMin, moveBounds.xMax);
                    newPos.y = Mathf.Clamp(newPos.y, moveBounds.yMin, moveBounds.yMax);
                }

                transform.position = newPos;

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
                if (isMoving)
                {
                    isMoving = false;
                    PlayIdle();
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
            if (frameAnimator != null && hitFrames != null && hitFrames.Length > 0)
            {
                frameAnimator.PlayAnimation(hitFrames, false);
            }
        }

        public void OnVictory()
        {
            canControl = false;
            isMoving = false;
            PlayIdle();
        }

        public void ResetPosition(Vector3 position)
        {
            transform.position = position;
            canControl = true;
            isMoving = false;
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
