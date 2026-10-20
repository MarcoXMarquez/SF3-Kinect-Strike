using UnityEngine;

namespace StreetFighter3.Loading
{
    /// <summary>
    /// Reproductor ligero de secuencias de frames de sprites a 14 FPS CPS-3 sin allocations de GC.
    /// Utilizado por el minijuego de carga y el minijuego de sigilo por waypoints.
    /// </summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public class SpriteFrameAnimator : MonoBehaviour
    {
        [SerializeField] private float frameRate = 14f;
        [SerializeField] private bool loop = true;

        private SpriteRenderer spriteRenderer;
        private Sprite[] currentFrames;
        private int currentFrameIndex = 0;
        private float frameTimer = 0f;
        private bool isPlaying = false;

        private void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
        }

        public void PlayAnimation(Sprite[] frames, bool shouldLoop = true)
        {
            if (frames == null || frames.Length == 0) return;

            // Si ya estamos reproduciendo la misma animación, no reiniciar innecesariamente
            if (currentFrames == frames && isPlaying && loop == shouldLoop) return;

            currentFrames = frames;
            loop = shouldLoop;
            currentFrameIndex = 0;
            frameTimer = 0f;
            isPlaying = true;

            if (spriteRenderer == null) spriteRenderer = GetComponent<SpriteRenderer>();
            if (spriteRenderer != null && currentFrames.Length > 0)
            {
                spriteRenderer.sprite = currentFrames[0];
            }
        }

        public void StopAnimation()
        {
            isPlaying = false;
        }

        private void Update()
        {
            if (!isPlaying || currentFrames == null || currentFrames.Length == 0) return;

            frameTimer += Time.deltaTime;
            float frameInterval = 1f / Mathf.Max(1f, frameRate);

            if (frameTimer >= frameInterval)
            {
                frameTimer -= frameInterval;
                currentFrameIndex++;

                if (currentFrameIndex >= currentFrames.Length)
                {
                    if (loop)
                    {
                        currentFrameIndex = 0;
                    }
                    else
                    {
                        currentFrameIndex = currentFrames.Length - 1;
                        isPlaying = false;
                    }
                }

                if (spriteRenderer != null)
                {
                    spriteRenderer.sprite = currentFrames[currentFrameIndex];
                }
            }
        }
    }
}
