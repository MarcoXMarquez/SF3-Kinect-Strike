using System.Collections.Generic;
using UnityEngine;

public class DuelFighter : MonoBehaviour
{
    public DuelFighter opponent;
    public int Health { get; private set; }
    private JapanDuel duel;
    private bool first, crouching, guarding, spentHit, finished;
    private Rigidbody2D body;
    private BoxCollider2D pushbox, attackBox;
    private readonly List<BoxCollider2D> hurtboxes = new List<BoxCollider2D>();
    private readonly Dictionary<string, Sprite[]> frames = new Dictionary<string, Sprite[]>();
    private readonly Collider2D[] contacts = new Collider2D[16];
    private SpriteRenderer visual;
    private string motion = "";
    private float motionTime, attackTime, stun, move;
    private int facing, attack = -1;
    private const float AttackDuration = 0.55f;
    private const float JumpSpeed = 7.5f;
    private static readonly KeyCode[] KenAttacks = { KeyCode.F, KeyCode.H, KeyCode.V, KeyCode.B };
    private static readonly KeyCode[] RyuAttacks = { KeyCode.Keypad1, KeyCode.Keypad2, KeyCode.Keypad4, KeyCode.Keypad5 };
    private static readonly KeyCode[] RyuAlternates = { KeyCode.Alpha7, KeyCode.Alpha8, KeyCode.Alpha9, KeyCode.Alpha0 };
    private bool Grounded => body.position.y <= duel.FloorY + 0.035f && body.linearVelocity.y <= 0.1f;

    public void Initialize(JapanDuel arena, DuelRoster.Motion[] motions, bool playerOne)
    {
        duel = arena;
        first = playerOne;
        foreach (var item in motions) frames[item.name] = item.frames;
        body = gameObject.AddComponent<Rigidbody2D>();
        body.gravityScale = 3;
        body.freezeRotation = true;
        body.collisionDetectionMode = CollisionDetectionMode2D.Continuous;
        body.interpolation = RigidbodyInterpolation2D.Interpolate;
        pushbox = gameObject.AddComponent<BoxCollider2D>();
        pushbox.size = new Vector2(0.38f, 0.9f);
        pushbox.offset = new Vector2(0, 0.46f);
        visual = new GameObject("Visuals").AddComponent<SpriteRenderer>();
        visual.transform.SetParent(transform, false);
        visual.sortingLayerName = "Fighters";
        visual.sortingOrder = 10;
        foreach (string region in new[] { "Head", "Torso", "Legs" })
        {
            var box = NewBox("Hurtbox_" + region);
            var hurt = box.gameObject.AddComponent<FighterHurtbox>();
            hurt.owner = gameObject;
            hurt.onHitReceived += ReceiveHit;
            hurtboxes.Add(box);
        }
        attackBox = NewBox("Hitbox_Attack");
        attackBox.enabled = false;
    }

    private BoxCollider2D NewBox(string boxName)
    {
        var child = new GameObject(boxName);
        child.transform.SetParent(transform, false);
        var box = child.AddComponent<BoxCollider2D>();
        box.isTrigger = true;
        return box;
    }

    public void ResetFighter(float x)
    {
        Health = 100;
        body.position = new Vector2(x, duel.FloorY + 0.02f);
        body.linearVelocity = Vector2.zero;
        facing = first ? 1 : -1;
        attack = -1;
        attackTime = 0;
        stun = 0;
        move = 0;
        finished = crouching = guarding = false;
        attackBox.enabled = false;
        foreach (var box in hurtboxes) box.enabled = true;
        Play("idle_stance", true);
        UpdateBoxes();
        Animate(true);
    }

    private void Update()
    {
        if (duel == null) return;
        motionTime += Time.deltaTime;
        stun = Mathf.Max(0, stun - Time.deltaTime);
        if (finished) { Animate(false); return; }
        if (!duel.Fighting) { move = 0; Animate(true); return; }
        if (attack < 0 && opponent != null) facing = opponent.transform.position.x >= transform.position.x ? 1 : -1;
        if (attack >= 0)
        {
            attackTime += Time.deltaTime;
            attackBox.enabled = !spentHit && attackTime >= 0.13f && attackTime <= 0.28f && stun <= 0;
            if (attackTime >= AttackDuration) { attack = -1; attackBox.enabled = false; }
        }
        if (stun <= 0 && attack < 0)
        {
            move = (Input.GetKey(first ? KeyCode.D : KeyCode.RightArrow) ? 1 : 0)
                - (Input.GetKey(first ? KeyCode.A : KeyCode.LeftArrow) ? 1 : 0);
            crouching = Grounded && Input.GetKey(first ? KeyCode.S : KeyCode.DownArrow);
            guarding = Grounded && Input.GetKey(first ? KeyCode.G : KeyCode.RightShift);
            if (Grounded && !crouching && !guarding && Input.GetKeyDown(first ? KeyCode.W : KeyCode.UpArrow))
                body.linearVelocity = new Vector2(body.linearVelocity.x, JumpSpeed);
            if (!guarding)
            {
                KeyCode[] keys = first ? KenAttacks : RyuAttacks;
                for (int i = 0; i < keys.Length; i++)
                    if (Input.GetKeyDown(keys[i]) || (!first && Input.GetKeyDown(RyuAlternates[i]))) { BeginAttack(i); break; }
            }
            if (attack < 0) Play(!Grounded ? "jump_neutral" : guarding ? "block_standing" : crouching ? "crouch_idle"
                : move == 0 ? "idle_stance" : move * facing > 0 ? "walk_forward" : "walk_backward");
        }
        Animate(attack < 0 && stun <= 0 && Grounded);
        UpdateBoxes();
    }

    private void BeginAttack(int index)
    {
        attack = index;
        attackTime = 0;
        spentHit = false;
        string prefix = !Grounded ? "jump_" : crouching ? "crouch_" : "";
        Play(prefix + new[] { "light_punch", "heavy_punch", "light_kick", "heavy_kick" }[index], true);
    }

    private void FixedUpdate()
    {
        if (body == null) return;
        float speed = duel.Fighting && !finished && stun <= 0 && attack < 0 && !crouching && !guarding ? move * 1.7f : 0;
        body.linearVelocity = new Vector2(speed, body.linearVelocity.y);
        if (body.position.x < -3.7f || body.position.x > 3.7f)
            body.position = new Vector2(Mathf.Clamp(body.position.x, -3.7f, 3.7f), body.position.y);
        if (body.position.y < duel.FloorY - 2) body.position = new Vector2(body.position.x, duel.FloorY + 0.1f);
        if (!attackBox.enabled || spentHit || !duel.Fighting) return;
        Physics2D.SyncTransforms();
        var filter = new ContactFilter2D { useTriggers = true };
        int count = attackBox.Overlap(filter, contacts);
        for (int i = 0; i < count; i++)
        {
            var hurt = contacts[i].GetComponent<FighterHurtbox>();
            if (hurt == null || opponent == null || hurt.owner != opponent.gameObject) continue;
            spentHit = true;
            hurt.TakeHit(attack % 2 == 0 ? 7 : 12, attack % 2 == 0 ? 0.18f : 0.3f, false, null);
            attackBox.enabled = false;
            break;
        }
    }

    private void ReceiveHit(float damage, float duration, bool knockdown, AudioClip sound)
    {
        if (!duel.Fighting || finished || Health <= 0) return;
        bool blocked = guarding && Grounded && stun <= 0 && opponent != null
            && (opponent.transform.position.x - transform.position.x) * facing >= 0;
        Health = Mathf.Max(0, Health - (blocked ? 0 : Mathf.RoundToInt(damage)));
        stun = blocked ? 0.12f : duration;
        attack = -1;
        attackBox.enabled = false;
        move = 0;
        Play(blocked ? "block_standing" : "hit_standing", true);
        visual.color = blocked ? new Color(0.4f, 0.9f, 1) : new Color(1, 0.55f, 0.55f);
    }

    public void EndRound(bool won)
    {
        finished = true;
        attack = -1;
        move = 0;
        attackBox.enabled = false;
        foreach (var box in hurtboxes) box.enabled = false;
        Play(won ? "victory_pose_1" : "defeat_timeout", true);
    }

    private void Play(string name, bool restart = false)
    {
        if (motion == name && !restart) return;
        motion = frames.ContainsKey(name) ? name : "idle_stance";
        motionTime = 0;
    }

    private void Animate(bool loop)
    {
        if (!frames.TryGetValue(motion, out Sprite[] sequence) || sequence.Length == 0) return;
        int index = (int)(motionTime * 14);
        if (attack >= 0) index = (int)(Mathf.Clamp01(attackTime / AttackDuration) * sequence.Length);
        else if (motion == "jump_neutral") index = (int)(Mathf.Clamp01((JumpSpeed - body.linearVelocity.y) / (2 * JumpSpeed)) * (sequence.Length - 1));
        loop &= motion == "idle_stance" || motion == "walk_forward" || motion == "walk_backward";
        visual.sprite = sequence[loop ? index % sequence.Length : Mathf.Min(index, sequence.Length - 1)];
        if (visual.sprite == null) return;
        visual.flipX = facing < 0;
        Bounds bounds = visual.sprite.bounds;
        visual.transform.localPosition = new Vector3(-bounds.center.x * facing, -bounds.min.y, 0);
        if (stun <= 0) visual.color = Color.white;
    }

    private void UpdateBoxes()
    {
        float height = crouching ? 0.6f : 1f;
        float lean = attack >= 0 ? facing * 0.06f : 0;
        for (int i = 0; i < hurtboxes.Count; i++)
        {
            hurtboxes[i].size = new Vector2(i == 0 ? 0.25f : 0.36f, height / 3);
            hurtboxes[i].offset = new Vector2(lean, height * (5 - i * 2) / 6);
        }
        pushbox.size = new Vector2(0.38f, height * 0.9f);
        pushbox.offset = new Vector2(0, height * 0.45f + 0.01f);
        bool kick = attack >= 2;
        float extension = Mathf.Sin(Mathf.Clamp01(attackTime / 0.28f) * Mathf.PI * 0.5f);
        attackBox.size = new Vector2(kick ? 0.55f : 0.4f, kick ? 0.26f : 0.22f);
        attackBox.offset = new Vector2(facing * (0.22f + extension * (kick ? 0.43f : 0.3f)), height * (kick ? 0.42f : 0.78f));
    }

    private void OnDrawGizmosSelected()
    {
        Gizmos.color = Color.green;
        foreach (var box in hurtboxes) if (box != null && box.enabled) Gizmos.DrawWireCube(box.bounds.center, box.bounds.size);
        Gizmos.color = Color.red;
        if (attackBox != null && attackBox.enabled) Gizmos.DrawWireCube(attackBox.bounds.center, attackBox.bounds.size);
    }
}
