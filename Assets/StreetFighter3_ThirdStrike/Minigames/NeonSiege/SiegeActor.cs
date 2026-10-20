using UnityEngine;

namespace SF3.NeonSiege
{
    public sealed class SiegeActor : MonoBehaviour
    {
        private SpriteRenderer visual;
        private Sprite[] idle, playing;
        private float clock, hold;
        private bool permanent;
        public SpriteRenderer Renderer => visual;
        public bool FacingLeft => transform.localScale.x < 0;

        public void Setup(NeonSiegeAssets assets, Sprite[] idleFrames, bool flip, float height)
        {
            idle = idleFrames;
            visual = gameObject.AddComponent<SpriteRenderer>();
            visual.sharedMaterial = assets.spriteMaterial;
            visual.sortingOrder = 15;
            transform.localScale = Vector3.one * height;
            FaceLeft(flip);
            Play(idle, 0, false);
        }

        public void FaceLeft(bool left)
        {
            // The shared chroma-key shader does not implement SpriteRenderer.flipX.
            Vector3 scale = transform.localScale;
            scale.x = Mathf.Abs(scale.x) * (left ? -1 : 1);
            transform.localScale = scale;
        }

        public void Play(Sprite[] frames, float duration, bool keep = false)
        {
            playing = frames == null || frames.Length == 0 ? idle : frames;
            hold = duration;
            clock = 0;
            permanent = keep;
            Draw();
        }

        private void Update()
        {
            clock += Time.deltaTime;
            if (!permanent && hold > 0 && clock >= hold) Play(idle, 0);
            Draw();
        }

        private void Draw()
        {
            if (playing == null || playing.Length == 0) return;
            int frame = (int)(clock * 12);
            if (hold > 0) frame = Mathf.FloorToInt(clock / hold * playing.Length);
            visual.sprite = playing[hold == 0 && !permanent ? frame % playing.Length : Mathf.Min(frame, playing.Length - 1)];
        }
    }
}
