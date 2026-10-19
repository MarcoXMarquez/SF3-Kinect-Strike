using UnityEngine;

namespace StreetFighter3.AI.Steering
{
    /// <summary>
    /// Contrato para cualquier algoritmo de comportamiento de dirección (Reynolds Steering Behavior).
    /// </summary>
    public interface ISteeringBehavior
    {
        string BehaviorName { get; }
        Vector2 CalculateSteering(ISteeringAgent agent);
    }
}
