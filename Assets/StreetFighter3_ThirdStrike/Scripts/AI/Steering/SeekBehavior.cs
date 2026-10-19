using UnityEngine;

namespace StreetFighter3.AI.Steering
{
    /// <summary>
    /// Implementación clásica del algoritmo de Persecución (Seeking) de Craig Reynolds.
    /// Calcula la aceleración vectorial hacia un objetivo móvil o estático.
    /// </summary>
    public class SeekBehavior : ISteeringBehavior
    {
        public string BehaviorName => "Seeking (Persecución)";

        public Vector2 TargetPosition { get; set; }
        public Transform TargetTransform { get; set; }
        public float ArrivalRadius { get; set; } = 15f; // Desaceleración suave al llegar si se desea

        public SeekBehavior() { }

        public SeekBehavior(Vector2 staticTarget)
        {
            TargetPosition = staticTarget;
        }

        public SeekBehavior(Transform targetTransform)
        {
            TargetTransform = targetTransform;
        }

        public Vector2 CalculateSteering(ISteeringAgent agent)
        {
            Vector2 target = TargetTransform != null 
                ? (Vector2)TargetTransform.position 
                : TargetPosition;

            Vector2 toTarget = target - agent.Position;
            float distance = toTarget.magnitude;

            if (distance < 0.001f)
            {
                return -agent.Velocity; // Frenado si ya está en el punto exacto
            }

            // Velocidad deseada hacia el objetivo
            Vector2 desiredVelocity = (toTarget / distance) * agent.MaxSpeed;

            // Suavizado de llegada opcional (Arrive blend)
            if (distance < ArrivalRadius && ArrivalRadius > 0.001f)
            {
                desiredVelocity *= (distance / ArrivalRadius);
            }

            // Fuerza de dirección = velocidad deseada - velocidad actual
            Vector2 steeringForce = desiredVelocity - agent.Velocity;

            // Limitar por la fuerza máxima del agente
            return Vector2.ClampMagnitude(steeringForce, agent.MaxForce);
        }
    }
}
