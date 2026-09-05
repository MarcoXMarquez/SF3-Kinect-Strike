using UnityEngine;

public class FighterCombatColliders : MonoBehaviour
{
    [Header("Referencias a Colisionadores")]
    [Tooltip("Asignar el hijo Hitbox_Root que contiene el BoxCollider2D Trigger")]
    public GameObject hitboxObject;

    [Header("Audio y Efectos")]
    public AudioClip attackVoiceClip;

    // Llamado por el Animation Event en el frame de impacto
    public void EnableHitbox()
    {
        if (hitboxObject != null)
        {
            hitboxObject.SetActive(true);
        }
    }

    // Llamado por el Animation Event cuando el golpe termina
    public void DisableHitbox()
    {
        if (hitboxObject != null)
        {
            hitboxObject.SetActive(false);
        }
    }

    // Reproduce la voz del personaje en el momento del impacto
    public void PlayAttackVoice()
    {
        if (attackVoiceClip != null)
        {
            SF3SoundManager.Instance.PlayVoice(attackVoiceClip);
        }
    }
}
