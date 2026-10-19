using UnityEngine;

namespace StreetFighter3.AI.Steering
{
    /// <summary>
    /// Implementación del algoritmo de Merodeo (Wandering) de Craig Reynolds.
    /// Proyecta un círculo virtual hacia adelante del agente y calcula desplazamientos
    /// angulares suaves para producir una trayectoria orgánica y natural sin sacudidas.
    /// </summary>
    public class WanderBehavior : ISteeringBehavior
    {
        public string BehaviorName => "Wandering (Merodeo)";

        public float CircleRadius { get; set; } = 40f;
        public float CircleDistance { get; set; } = 70f;
        public float AngleChangeRate { get; set; } = 35f * Mathf.Deg2Rad; // Variación angular máxima por frame

        private float currentWanderAngle;

        public WanderBehavior()
        {
            currentWanderAngle = Random.Range(0f, Mathf.PI * 2f);
        }

        public WanderBehavior(float radius, float distance, float angleRateDegrees = 30f)
        {
            CircleRadius = radius;
            CircleDistance = distance;
            AngleChangeRate = angleRateDegrees * Mathf.Deg2Rad;
            currentWanderAngle = Random.Range(0f, Mathf.PI * 2f);
        }

        public Vector2 CalculateSteering(ISteeringAgent agent)
        {
            // 1. Centro del círculo proyectado adelante según la dirección actual
            Vector2 forward = agent.Forward;
            if (forward.sqrMagnitude < 0.001f)
            {
                forward = Vector2.right;
            }

            Vector2 circleCenter = agent.Position + forward * CircleDistance;

            // 2. Modificar el ángulo de merodeo aleatoriamente en un rango controlado
            currentWanderAngle += Random.Range(-AngleChangeRate, AngleChangeRate);

            // 3. Desplazamiento sobre la circunferencia
            Vector2 displacement = new Vector2(
                Mathf.Cos(currentWanderAngle),
                Mathf.Sin(currentWanderAngle)
            ) * CircleRadius;

            // 4. Punto objetivo en la circunferencia
            Vector2 wanderTarget = circleCenter + displacement;

            // 5. Fuerza de dirección hacia el punto proyectado
            Vector2 toTarget = wanderTarget - agent.Position;
            Vector2 desiredVelocity = toTarget.normalized * agent.MaxSpeed;
            Vector2 steeringForce = desiredVelocity - agent.Velocity;

            return Vector2.ClampMagnitude(steeringForce, agent.MaxForce);
        }
    }
}
