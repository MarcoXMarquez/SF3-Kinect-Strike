using UnityEngine;

/// <summary>
/// Cicla secuencialmente un conjunto de Sprites a una tasa de cuadros CPS-3 (14 FPS por defecto).
/// Diseñado para dar vida a props y personajes del fondo (mercado de China, toldos, espectadores).
/// </summary>
[RequireComponent(typeof(SpriteRenderer))]
public class AnimatedSpriteProp : MonoBehaviour
{
    [Header("Configuración de Animación")]
    [SerializeField] private Sprite[] frames;
    [SerializeField] private float frameRate = 14f;
    [SerializeField] private bool loop = true;
    [SerializeField] private bool randomStartFrame = true;

    private SpriteRenderer spriteRenderer;
    private float timer;
    private int currentFrame;

    public Sprite[] Frames
    {
        get => frames;
        set => frames = value;
    }

    public float FrameRate
    {
        get => frameRate;
        set => frameRate = value;
    }

    private void Awake()
    {
        spriteRenderer = GetComponent<SpriteRenderer>();
        if (frames != null && frames.Length > 0 && randomStartFrame)
        {
            currentFrame = Random.Range(0, frames.Length);
            spriteRenderer.sprite = frames[currentFrame];
        }
    }

    private void Update()
    {
        if (frames == null || frames.Length <= 1) return;

        timer += Time.deltaTime;
        float interval = 1f / Mathf.Max(frameRate, 1f);

        if (timer >= interval)
        {
            timer -= interval;
            currentFrame++;

            if (currentFrame >= frames.Length)
            {
                if (loop)
                {
                    currentFrame = 0;
                }
                else
                {
                    currentFrame = frames.Length - 1;
                    enabled = false;
                    return;
                }
            }

            spriteRenderer.sprite = frames[currentFrame];
        }
    }
}
