using UnityEngine;

namespace SF3.NeonSiege
{
    public sealed class SiegeProjectile : MonoBehaviour
    {
        public bool hostile;
        private NeonSiegeGame game;
        private Rigidbody2D body;
        private SpriteRenderer visual;
        private Sprite[] frames;
        private float age;
        private bool consumed;
        public Rigidbody2D Body => body;

        public void Setup(NeonSiegeGame owner, Vector2 position, Vector2 velocity, bool enemy)
        {
            game = owner; hostile = enemy;
            transform.position = position;
            frames = hostile ? game.Assets.darkShot : game.Assets.blueShot;
            visual = gameObject.AddComponent<SpriteRenderer>();
            visual.sharedMaterial = game.Assets.spriteMaterial;
            visual.sortingOrder = 22;
            visual.sprite = frames[0];
            transform.localScale = Vector3.one * 0.8f;
            body = gameObject.AddComponent<Rigidbody2D>();
            body.gravityScale = hostile ? 0 : 1;
            body.linearDamping = 0;
            body.angularDamping = 0;
            body.collisionDetectionMode = CollisionDetectionMode2D.Continuous;
            body.freezeRotation = true;
            body.linearVelocity = velocity;
            var collider = gameObject.AddComponent<CircleCollider2D>();
            collider.radius = SiegeBallistics.Radius / 0.8f;
            collider.isTrigger = true;
            var trail = gameObject.AddComponent<TrailRenderer>();
            trail.sharedMaterial = game.LineMaterial;
            trail.startWidth = 0.16f;
            trail.endWidth = 0;
            trail.time = 0.18f;
            trail.startColor = hostile ? new Color(1, 0.2f, 0.4f, 0.7f) : new Color(0.2f, 1, 1, 0.7f);
            trail.endColor = Color.clear;
            trail.sortingOrder = 21;
        }

        private void Update()
        {
            age += Time.deltaTime;
            visual.sprite = frames[(int)(age * 18) % frames.Length];
            visual.flipX = body.linearVelocity.x < 0;
            Vector2 p = body.position;
            if (age > 4.5f || p.y < -3.7f || p.y > 18 || p.x < -9.3f || p.x > 9.3f)
            {
                if (hostile && p.x < -6.8f) game.TakeDamage();
                Finish(false);
            }
        }

        private void OnTriggerEnter2D(Collider2D other)
        {
            if (consumed || !game.Playing) return;
            SiegeProjectile shot = other.GetComponent<SiegeProjectile>();
            if (shot != null && shot.hostile != hostile && !shot.consumed)
            {
                game.Intercept(transform.position);
                shot.Finish(true);
                Finish(true);
                return;
            }
            if (!hostile)
            {
                var target = other.GetComponent<SiegeTarget>();
                if (target != null && target.Alive) { target.Hit(transform.position); Finish(true); return; }
            }
            if (other.GetComponent<SiegeBarrier>() != null) { game.Blocked(transform.position); Finish(true); }
        }

        public void Finish(bool hit)
        {
            if (consumed) return;
            consumed = true;
            game.ProjectileFinished(this, hit);
            Destroy(gameObject);
        }
    }

    public sealed class SiegeBarrier : MonoBehaviour { }
}
