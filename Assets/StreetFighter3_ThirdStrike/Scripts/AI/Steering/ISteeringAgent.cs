using UnityEngine;

namespace StreetFighter3.AI.Steering
{
    /// <summary>
    /// Contrato que define una entidad física o cinemática capaz de recibir fuerzas de dirección (Steering Forces).
    /// </summary>
    public interface ISteeringAgent
    {
        Vector2 Position { get; }
        Vector2 Velocity { get; }
        float MaxSpeed { get; }
        float MaxForce { get; }
        Vector2 Forward { get; }
    }
}
