using UnityEngine;

public class FighterHitbox : MonoBehaviour
{
    public float damage = 10f;
    public float hitStunDuration = 0.2f;
    public bool isKnockdown = false;
    public AudioClip hitSound;

    void OnTriggerEnter2D(Collider2D other)
    {
        FighterHurtbox hurtbox = other.GetComponent<FighterHurtbox>();
        if (hurtbox != null && hurtbox.owner != transform.root.gameObject)
        {
            hurtbox.TakeHit(damage, hitStunDuration, isKnockdown, hitSound);
        }
    }
}

public class FighterHurtbox : MonoBehaviour
{
    public GameObject owner;
    public System.Action<float, float, bool, AudioClip> onHitReceived;

    public void TakeHit(float damage, float hitStun, bool knockdown, AudioClip sfx)
    {
        onHitReceived?.Invoke(damage, hitStun, knockdown, sfx);
    }
}
