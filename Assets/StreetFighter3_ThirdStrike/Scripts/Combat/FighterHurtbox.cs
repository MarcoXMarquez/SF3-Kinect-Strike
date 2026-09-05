using UnityEngine;
using System;

public class FighterHurtbox : MonoBehaviour
{
    [Header("Luchador Dueño")]
    [Tooltip("El GameObject raíz del luchador (para evitar que se golpee a sí mismo)")]
    public GameObject owner;

    [Header("Eventos de Combate")]
    public Action<float, float, bool, AudioClip> onHitReceived;

    public void TakeHit(float damage, float hitStun, bool knockdown, AudioClip sfx)
    {
        if (onHitReceived != null)
        {
            onHitReceived.Invoke(damage, hitStun, knockdown, sfx);
        }
    }
}
