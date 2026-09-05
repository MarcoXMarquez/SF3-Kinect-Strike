using UnityEngine;

public class SF3SoundManager : MonoBehaviour
{
    public static SF3SoundManager Instance { get; private set; }

    [Header("Audio Sources")]
    public AudioSource bgmSource;
    public AudioSource sfxSource;
    public AudioSource voiceSource;

    [Header("Signature SF3 Sounds")]
    public AudioClip parrySound;
    public AudioClip superFlashSound;
    public AudioClip blockSound;
    public AudioClip lightHitSound;
    public AudioClip heavyHitSound;

    void Awake()
    {
        if (Instance == null) Instance = this;
        else Destroy(gameObject);
    }

    public void PlaySFX(AudioClip clip, float volume = 1f)
    {
        if (clip != null && sfxSource != null)
        {
            sfxSource.PlayOneShot(clip, volume);
        }
    }

    public void PlayVoice(AudioClip clip, float volume = 1f)
    {
        if (clip != null && voiceSource != null)
        {
            voiceSource.PlayOneShot(clip, volume);
        }
    }

    public void PlayParry()
    {
        PlaySFX(parrySound);
    }

    public void PlaySuperFlash()
    {
        PlaySFX(superFlashSound);
    }
}
