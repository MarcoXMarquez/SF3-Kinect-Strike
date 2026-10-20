using UnityEngine;

namespace SF3.NeonSiege
{
    public sealed class SiegeTarget : MonoBehaviour
    {
        public Vector2 origin, travel;
        public float frequency, phase, shieldPeriod;
        public int health, maxHealth;
        public bool boss;
        public string callsign;
        public const float Radius = 0.55f;
        private NeonSiegeGame game;
        private Rigidbody2D body;
        private SpriteRenderer shield;
        private SiegeActor actor;
        private GameObject rails;
        private float hurtUntil;
        public bool Alive => health > 0;
        public Vector3 NameAnchor => new Vector3(actor.Renderer.bounds.center.x, actor.Renderer.bounds.max.y + 0.28f, 0);
        public bool FacingRyu => actor.FacingLeft == (game.PlayerPosition.x < transform.position.x);

        public Vector2 PositionAt(float time) => origin + travel * Mathf.Sin(time * frequency + phase);
        public bool OpenAt(float time) => shieldPeriod <= 0 || Mathf.Repeat(time + phase, shieldPeriod) > shieldPeriod * 0.45f;

        public void Setup(NeonSiegeGame owner, Vector2 position, Vector2 amplitude, float rate, int hp, float shield, bool isBoss, int number)
        {
            game = owner; origin = position; travel = amplitude; frequency = rate;
            phase = number * 0.7f; health = maxHealth = hp; shieldPeriod = shield; boss = isBoss;
            callsign = boss ? "URIEN" : "REMY";
            body = gameObject.AddComponent<Rigidbody2D>();
            body.bodyType = RigidbodyType2D.Kinematic;
            body.position = PositionAt(0);
            var sensor = gameObject.AddComponent<CircleCollider2D>();
            sensor.isTrigger = true;
            sensor.radius = Radius;
            this.shield = Piece("Aegis electric panel", new Vector2(-0.57f, 0.15f), new Vector2(0.1f, 1.55f), new Color(0.25f, 0.6f, 1, 0.9f), 18);
            var model = new GameObject("Guardian");
            model.transform.SetParent(transform, false);
            model.transform.localPosition = new Vector3(0, -0.55f, 0);
            actor = model.AddComponent<SiegeActor>();
            actor.Setup(game.Assets, boss ? game.Assets.urienIdle : game.Assets.remyIdle, true, boss ? 1.55f : 1.25f);
            Piece("Steel deck", new Vector2(0, -0.64f), new Vector2(1.5f, 0.17f), new Color(0.23f, 0.26f, 0.33f), 14);
            Piece("Deck highlight", new Vector2(0, -0.55f), new Vector2(1.56f, 0.045f), new Color(0.72f, 0.74f, 0.79f), 16);
            Piece("Deck shadow", new Vector2(0, -0.77f), new Vector2(1.25f, 0.08f), new Color(0.07f, 0.08f, 0.11f), 13);
            for (int i = 0; i < 5; i++)
            {
                var stripe = Piece("Hazard marking", new Vector2(-0.56f + i * 0.28f, -0.64f), new Vector2(0.12f, 0.15f), new Color(0.95f, 0.7f, 0.15f), 15);
                stripe.transform.localRotation = Quaternion.Euler(0, 0, -22);
            }
            rails = new GameObject("Freight lift rails");
            float bottom = -3.4f, top = Mathf.Max(origin.y + Mathf.Abs(travel.y) - 0.55f, bottom + 0.1f);
            for (int i = 0; i < 2; i++)
            {
                var post = new GameObject("Steel lift guide"); post.transform.SetParent(rails.transform, false);
                post.transform.position = new Vector3(origin.x + (i == 0 ? -0.46f : 0.46f), (bottom + top) / 2, 0);
                post.transform.localScale = new Vector3(0.08f, top - bottom, 1);
                var renderer = post.AddComponent<SpriteRenderer>(); renderer.sprite = game.SolidSprite;
                renderer.color = new Color(0.17f, 0.19f, 0.25f, 0.7f); renderer.sortingOrder = 3;
            }
        }

        private SpriteRenderer Piece(string label, Vector2 offset, Vector2 size, Color color, int order)
        {
            var root = new GameObject(label); root.transform.SetParent(transform, false);
            root.transform.localPosition = offset; root.transform.localScale = size;
            var renderer = root.AddComponent<SpriteRenderer>(); renderer.sprite = game.SolidSprite;
            renderer.color = color; renderer.sortingOrder = order; return renderer;
        }

        private void FixedUpdate()
        {
            if (game == null || !game.Playing || !Alive) return;
            body.MovePosition(PositionAt(game.MissionClock));
        }

        private void Update()
        {
            if (shield == null) return;
            actor.FaceLeft(game.PlayerPosition.x < transform.position.x);
            shield.enabled = Alive && !OpenAt(game.MissionClock);
            shield.color = new Color(0.35f, 0.65f, 1, 0.6f + 0.3f * Mathf.Abs(Mathf.Sin(Time.time * 28)));
            actor.Renderer.color = Time.time < hurtUntil ? new Color(1, 0.55f, 0.45f) : Color.white;
        }

        public void Hit(Vector2 point)
        {
            if (!Alive || !game.Playing) return;
            if (!OpenAt(game.MissionClock)) { game.Blocked(point); return; }
            health--;
            hurtUntil = Time.time + 0.12f;
            actor.Play(boss ? game.Assets.urienHit : game.Assets.remyHit, 0.25f);
            game.HitTarget(this, point);
            if (!Alive) { actor.gameObject.SetActive(false); shield.enabled = false; GetComponent<CircleCollider2D>().enabled = false; }
        }

        public void Cast() { if (Alive) actor.Play(boss ? game.Assets.urienCast : game.Assets.remyCast, 0.65f); }
        private void OnDestroy() { if (rails != null) Destroy(rails); }
    }
}
