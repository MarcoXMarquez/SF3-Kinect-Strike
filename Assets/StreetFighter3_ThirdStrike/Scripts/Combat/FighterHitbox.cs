using UnityEngine;

public class FighterHitbox : MonoBehaviour
{
    [Header("Propiedades del Golpe")]
    public float damage = 10f;
    public float hitStunDuration = 0.2f;
    public bool isKnockdown = false;
    public AudioClip hitSound;

    private void OnTriggerEnter2D(Collider2D other)
    {
        FighterHurtbox hurtbox = other.GetComponent<FighterHurtbox>();
        if (hurtbox != null)
        {
            // Evitar autogolpes si el owner es el mismo personaje raíz
            GameObject rootObj = transform.root.gameObject;
            if (hurtbox.owner != null && hurtbox.owner == rootObj)
            {
                return;
            }

            hurtbox.TakeHit(damage, hitStunDuration, isKnockdown, hitSound);
        }
    }
}
