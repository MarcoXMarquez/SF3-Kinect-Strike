using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace StreetFighter3.UI
{
    /// <summary>
    /// Controlador del avatar interactivo estilo DBZ Tenkaichi 3 en la pantalla de carga.
    /// Permite desplazarse, saltar y dar golpes durante los tiempos de espera.
    /// </summary>
    [RequireComponent(typeof(RectTransform))]
    public class MiniFighterController : MonoBehaviour
    {
        [Header("Movimiento")]
        [SerializeField] private float moveSpeed = 320f;
        [SerializeField] private float jumpForce = 520f;
        [SerializeField] private float gravity = 1200f;
        [SerializeField] private float groundY = -140f;
        [SerializeField] private Vector2 horizontalBounds = new Vector2(-420f, 420f);

        [Header("Sprites de Animación")]
        [SerializeField] private Sprite[] idleFrames;
        [SerializeField] private Sprite[] walkFrames;
        [SerializeField] private Sprite[] punchFrames;
        [SerializeField] private Sprite[] jumpFrames;

        private RectTransform rectTransform;
        private Image image;
        private float verticalVelocity = 0f;
        private bool isGrounded = true;
        private bool isAttacking = false;
        private float attackTimer = 0f;
        private const float AttackDuration = 0.28f;

        private float animTimer = 0f;
        private int currentFrame = 0;
        private const float FrameRate = 1f / 12f;

        public Vector2 Position => rectTransform != null ? rectTransform.anchoredPosition : Vector2.zero;
        public bool IsAttacking => isAttacking;
        public float AttackRange => 65f;

        public System.Action OnPunchTriggered;

        private void Awake()
        {
            rectTransform = GetComponent<RectTransform>();
            image = GetComponent<Image>();
        }

        public void SetupSprites(Sprite[] idle, Sprite[] walk, Sprite[] punch, Sprite[] jump)
        {
            idleFrames = idle;
            walkFrames = walk;
            punchFrames = punch;
            jumpFrames = jump;
        }

        private void Update()
        {
            float dt = Time.deltaTime;
            if (dt <= 0f) return;

            // 1. Entrada de control (Teclado)
            float moveInput = 0f;
            if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow)) moveInput -= 1f;
            if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow)) moveInput += 1f;

            // Ataque (J, F, Espacio)
            if (!isAttacking && (Input.GetKeyDown(KeyCode.J) || Input.GetKeyDown(KeyCode.F) || Input.GetKeyDown(KeyCode.Space)))
            {
                TriggerAttack();
            }

            // Salto (W, UpArrow)
            if (isGrounded && (Input.GetKeyDown(KeyCode.W) || Input.GetKeyDown(KeyCode.UpArrow)))
            {
                verticalVelocity = jumpForce;
                isGrounded = false;
            }

            // 2. Física y gravedad
            Vector2 pos = rectTransform.anchoredPosition;

            if (!isGrounded)
            {
                verticalVelocity -= gravity * dt;
                pos.y += verticalVelocity * dt;
                if (pos.y <= groundY)
                {
                    pos.y = groundY;
                    verticalVelocity = 0f;
                    isGrounded = true;
                }
            }
            else
            {
                pos.y = groundY;
            }

            // Desplazamiento horizontal
            pos.x += moveInput * moveSpeed * dt;
            pos.x = Mathf.Clamp(pos.x, horizontalBounds.x, horizontalBounds.y);
            rectTransform.anchoredPosition = pos;

            // Flip horizontal según dirección
            if (Mathf.Abs(moveInput) > 0.01f)
            {
                Vector3 scale = rectTransform.localScale;
                scale.x = (moveInput < 0) ? -Mathf.Abs(scale.x) : Mathf.Abs(scale.x);
                rectTransform.localScale = scale;
            }

            // 3. Manejo de estado de ataque
            if (isAttacking)
            {
                attackTimer -= dt;
                if (attackTimer <= 0f)
                {
                    isAttacking = false;
                }
            }

            // 4. Animación de sprites
            UpdateAnimation(dt, moveInput);
        }

        private void TriggerAttack()
        {
            isAttacking = true;
            attackTimer = AttackDuration;
            currentFrame = 0;
            animTimer = 0f;
            OnPunchTriggered?.Invoke();
        }

        private void UpdateAnimation(float dt, float moveInput)
        {
            if (image == null) return;

            Sprite[] activeSet = idleFrames;

            if (isAttacking && punchFrames != null && punchFrames.Length > 0)
            {
                activeSet = punchFrames;
            }
            else if (!isGrounded && jumpFrames != null && jumpFrames.Length > 0)
            {
                activeSet = jumpFrames;
            }
            else if (Mathf.Abs(moveInput) > 0.01f && walkFrames != null && walkFrames.Length > 0)
            {
                activeSet = walkFrames;
            }

            if (activeSet != null && activeSet.Length > 0)
            {
                animTimer += dt;
                if (animTimer >= FrameRate)
                {
                    animTimer = 0f;
                    currentFrame = (currentFrame + 1) % activeSet.Length;
                }
                currentFrame = Mathf.Clamp(currentFrame, 0, activeSet.Length - 1);
                image.sprite = activeSet[currentFrame];
            }
        }
    }
}
