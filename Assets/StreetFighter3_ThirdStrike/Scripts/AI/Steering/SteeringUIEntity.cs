using UnityEngine;
using UnityEngine.UI;

namespace StreetFighter3.AI.Steering
{
    /// <summary>
    /// Componente MonoBehaviour para entidades UI (RectTransform) que se desplazan
    /// mediante algoritmos de Steering Behaviors (Wander o Seek).
    /// </summary>
    [RequireComponent(typeof(RectTransform))]
    public class SteeringUIEntity : MonoBehaviour, ISteeringAgent
    {
        [Header("Cinemática")]
        [SerializeField] private float maxSpeed = 160f;
        [SerializeField] private float maxForce = 220f;
        [SerializeField] private Vector2 currentVelocity = Vector2.zero;
        [SerializeField] private bool autoFlipX = true;

        [Header("Límites del Área de Juego (UI)")]
        [SerializeField] private Vector2 boundsMin = new Vector2(-420f, -220f);
        [SerializeField] private Vector2 boundsMax = new Vector2(420f, 220f);

        private RectTransform rectTransform;
        private Image image;
        private ISteeringBehavior currentBehavior;

        public Vector2 Position => rectTransform != null ? rectTransform.anchoredPosition : Vector2.zero;
        public Vector2 Velocity => currentVelocity;
        public float MaxSpeed => maxSpeed;
        public float MaxForce => maxForce;
        public Vector2 Forward => currentVelocity.sqrMagnitude > 0.001f ? currentVelocity.normalized : Vector2.right;

        public ISteeringBehavior CurrentBehavior => currentBehavior;

        private void Awake()
        {
            rectTransform = GetComponent<RectTransform>();
            image = GetComponent<Image>();
            if (currentVelocity == Vector2.zero)
            {
                // Velocidad inicial aleatoria
                float startAngle = Random.Range(0f, Mathf.PI * 2f);
                currentVelocity = new Vector2(Mathf.Cos(startAngle), Mathf.Sin(startAngle)) * (maxSpeed * 0.5f);
            }
        }

        public void SetBehavior(ISteeringBehavior behavior)
        {
            currentBehavior = behavior;
        }

        public void SetBounds(Vector2 min, Vector2 max)
        {
            boundsMin = min;
            boundsMax = max;
        }

        public void SetSpeedAndForce(float speed, float force)
        {
            maxSpeed = speed;
            maxForce = force;
        }

        public void SetColor(Color color)
        {
            if (image == null) image = GetComponent<Image>();
            if (image != null) image.color = color;
        }

        public void SetSprite(Sprite sprite)
        {
            if (image == null) image = GetComponent<Image>();
            if (image != null) image.sprite = sprite;
        }

        private void Update()
        {
            if (rectTransform == null) return;

            float dt = Time.deltaTime;
            if (dt <= 0f) return;

            // 1. Calcular aceleración de dirección mediante el comportamiento activo
            Vector2 steering = Vector2.zero;
            if (currentBehavior != null)
            {
                steering = currentBehavior.CalculateSteering(this);
            }

            // 2. Integración de velocidad de Euler
            currentVelocity += steering * dt;
            currentVelocity = Vector2.ClampMagnitude(currentVelocity, maxSpeed);

            // 3. Integración de posición
            Vector2 pos = rectTransform.anchoredPosition + currentVelocity * dt;

            // 4. Rebote elástico suave contra los bordes del área del minijuego
            if (pos.x < boundsMin.x)
            {
                pos.x = boundsMin.x;
                currentVelocity.x = Mathf.Abs(currentVelocity.x) * 0.9f;
            }
            else if (pos.x > boundsMax.x)
            {
                pos.x = boundsMax.x;
                currentVelocity.x = -Mathf.Abs(currentVelocity.x) * 0.9f;
            }

            if (pos.y < boundsMin.y)
            {
                pos.y = boundsMin.y;
                currentVelocity.y = Mathf.Abs(currentVelocity.y) * 0.9f;
            }
            else if (pos.y > boundsMax.y)
            {
                pos.y = boundsMax.y;
                currentVelocity.y = -Mathf.Abs(currentVelocity.y) * 0.9f;
            }

            rectTransform.anchoredPosition = pos;

            // 5. Orientación / Flip horizontal según dirección
            if (autoFlipX && Mathf.Abs(currentVelocity.x) > 0.1f)
            {
                Vector3 scale = rectTransform.localScale;
                scale.x = (currentVelocity.x < 0) ? -Mathf.Abs(scale.x) : Mathf.Abs(scale.x);
                rectTransform.localScale = scale;
            }
        }
    }
}
