using UnityEngine;
using System;

/// <summary>
/// Controlador de física determinista arcade para luchadores (CPS-3).
/// Gestiona la velocidad horizontal, el salto parabólico con inercia fija (Jump Commitment)
/// y la detección precisa de suelo en Y = 0.
/// </summary>
[RequireComponent(typeof(Rigidbody2D))]
public class FighterPhysics : MonoBehaviour
{
    [Header("Parámetros de Movimiento Horizontal")]
    [Tooltip("Velocidad de caminata hacia adelante (unidades/segundo)")]
    [SerializeField] private float walkForwardSpeed = 3.4f;

    [Tooltip("Velocidad de caminata hacia atrás (unidades/segundo)")]
    [SerializeField] private float walkBackwardSpeed = 2.8f;

    [Header("Parámetros de Salto Arcade (CPS-3)")]
    [Tooltip("Velocidad vertical inicial del salto (Vy impulso)")]
    [SerializeField] private float jumpVerticalVelocity = 8.5f;

    [Tooltip("Velocidad horizontal fija al saltar adelante/atrás (Jump Arc Commitment)")]
    [SerializeField] private float jumpHorizontalVelocity = 3.2f;

    [Tooltip("Aceleración gravitatoria arcade (alta para caída rápida y responsiva)")]
    [SerializeField] private float gravityScale = 22.0f;

    [Header("Línea de Suelo")]
    [Tooltip("Cota Y exacta que representa el nivel del piso")]
    [SerializeField] private float groundLevelY = 0.0f;

    [Tooltip("Activar si se desea detección mediante Raycast contra una capa de suelo física")]
    [SerializeField] private bool useRaycastGroundCheck = false;

    [SerializeField] private LayerMask groundLayer;
    [SerializeField] private float groundCheckDistance = 0.1f;

    // Componentes cacheados
    private Rigidbody2D rb;

    // Estado físico interno
    private Vector2 currentVelocity;
    private bool isGrounded = true;
    private bool isJumpCommitted = false;

    // Eventos para la máquina de estados
    public event Action OnLanded;
    public event Action OnJumpStarted;

    // Propiedades públicas
    public bool IsGrounded => isGrounded;
    public Vector2 Velocity => currentVelocity;
    public float GroundLevelY => groundLevelY;

    private void Awake()
    {
        if (rb == null)
        {
            rb = GetComponent<Rigidbody2D>();
        }

        // Configuración defensiva de Rigidbody2D para juego de peleas
        rb.bodyType = RigidbodyType2D.Dynamic;
        rb.gravityScale = 0f; // Gravedad controlada matemáticamente por este script
        rb.constraints = RigidbodyConstraints2D.FreezeRotation;
        rb.collisionDetectionMode = CollisionDetectionMode2D.Continuous;
    }

    private void Start()
    {
        // Ajustar a la línea de suelo al iniciar si está por debajo
        if (transform.position.y < groundLevelY)
        {
            Vector3 pos = transform.position;
            pos.y = groundLevelY;
            transform.position = pos;
        }
    }

    private void FixedUpdate()
    {
        if (!isGrounded)
        {
            // 1. Integración de gravedad: Vy(t) = Vy - (g * dt)
            currentVelocity.y -= gravityScale * Time.fixedDeltaTime;

            // 2. Detección de aterrizaje cuando el personaje desciende
            if (currentVelocity.y <= 0f)
            {
                bool reachedGround = false;

                if (useRaycastGroundCheck)
                {
                    RaycastHit2D hit = Physics2D.Raycast(transform.position, Vector2.down, groundCheckDistance, groundLayer);
                    if (hit.collider != null)
                    {
                        reachedGround = true;
                    }
                }
                else if (transform.position.y <= groundLevelY)
                {
                    reachedGround = true;
                }

                if (reachedGround)
                {
                    Land();
                    return;
                }
            }
        }

        // 3. Aplicar velocidad calculada al Rigidbody2D (linearVelocity en Unity 6)
        rb.linearVelocity = currentVelocity;
    }

    /// <summary>
    /// Aplica velocidad horizontal en el suelo.
    /// </summary>
    /// <param name="direction">+1 para adelante, -1 para atrás, 0 para detenerse</param>
    public void Move(float direction)
    {
        if (!isGrounded || isJumpCommitted) return;

        if (direction > 0.01f)
        {
            currentVelocity.x = walkForwardSpeed;
        }
        else if (direction < -0.01f)
        {
            currentVelocity.x = -walkBackwardSpeed;
        }
        else
        {
            currentVelocity.x = 0f;
        }
    }

    /// <summary>
    /// Detiene en seco la inercia horizontal al soltar las teclas en el suelo.
    /// </summary>
    public void StopHorizontal()
    {
        if (isGrounded)
        {
            currentVelocity.x = 0f;
            rb.linearVelocity = new Vector2(0f, rb.linearVelocity.y);
        }
    }

    /// <summary>
    /// Ejecuta el impulso de salto con física parabólica y compromiso de inercia aérea.
    /// </summary>
    /// <param name="horizontalDirection">0 = vertical, +1 = adelante, -1 = atrás</param>
    public void Jump(float horizontalDirection)
    {
        if (!isGrounded) return;

        isGrounded = false;
        isJumpCommitted = true;

        // Impulso vertical instantáneo
        currentVelocity.y = jumpVerticalVelocity;

        // Inercia horizontal bloqueada durante todo el arco de vuelo
        if (horizontalDirection > 0.01f)
        {
            currentVelocity.x = jumpHorizontalVelocity;
        }
        else if (horizontalDirection < -0.01f)
        {
            currentVelocity.x = -jumpHorizontalVelocity;
        }
        else
        {
            currentVelocity.x = 0f;
        }

        rb.linearVelocity = currentVelocity;
        OnJumpStarted?.Invoke();
    }

    /// <summary>
    /// Aterriza en el suelo: clava posición exacta y resetea velocidades.
    /// </summary>
    private void Land()
    {
        isGrounded = true;
        isJumpCommitted = false;
        currentVelocity = Vector2.zero;
        rb.linearVelocity = Vector2.zero;

        // Clavar Y en la línea de suelo para evitar oscilaciones sub-pixel
        Vector3 pos = transform.position;
        pos.y = groundLevelY;
        transform.position = pos;

        OnLanded?.Invoke();
    }

    /// <summary>
    /// Permite reubicar al personaje inmediatamente en una coordenada dada.
    /// </summary>
    public void Teleport(Vector2 targetPosition)
    {
        transform.position = new Vector3(targetPosition.x, targetPosition.y, transform.position.z);
        currentVelocity = Vector2.zero;
        rb.linearVelocity = Vector2.zero;
    }
}
