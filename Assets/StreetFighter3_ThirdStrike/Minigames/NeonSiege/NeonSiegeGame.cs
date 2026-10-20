using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace SF3.NeonSiege
{
    [DefaultExecutionOrder(-100)]
    public sealed partial class NeonSiegeGame : MonoBehaviour
    {
        public NeonSiegeAssets assets;
        public NeonSiegeAssets Assets => assets;
        public Material LineMaterial { get; private set; }
        public Sprite SolidSprite => white;
        public float MissionClock { get; private set; }
        public bool Playing => state == Mode.Play;
        public int Mission { get; private set; }
        public int Score { get; private set; }
        public int Ammo { get; private set; }
        public int Integrity { get; private set; }
        public float AimAngle => angle;
        public float LaunchSpeed => speed;
        public int InitialFocus => Mission < 2 ? 2 : 1;
        public IReadOnlyList<SiegeTarget> Targets => targets;
        public Vector2 Muzzle => new Vector2(-6.65f, -1.92f);
        public Vector2 PlayerPosition => ryu.transform.position;
        public enum Mode { Title, Briefing, Play, Paused, Clear, Failed, Complete }
        public Mode State => state;
        private Mode state;
        private readonly List<SiegeTarget> targets = new List<SiegeTarget>();
        private readonly List<SiegeProjectile> projectiles = new List<SiegeProjectile>();
        private readonly List<GameObject> barriers = new List<GameObject>();
        private readonly List<GameObject> owned = new List<GameObject>();
        private Camera cam;
        private SiegeActor ryu, titleRival;
        private AudioSource music, audioFx;
        private LineRenderer path, marker;
        private Sprite white;
        private SpriteRenderer flash;
        private Font font;
        private GUIStyle text, button;
        private float angle = 36, speed = 13.8f, cooldown, remaining, nextEnemy, messageUntil, predictionTime;
        private float desiredAngle = 36, aimDamping;
        private bool mouseOwnsAim, aimReachable = true, highArc, attackWarned;
        private Vector2 lastMouse, aimPoint;
        private float volume = 0.65f, flashUntil;
        private int combo, hits, shots, focus, startScore, best, stars;
        private string message = "", failure = "", forecast = "";
        private readonly Color mint = new Color(0.35f, 0.72f, 1), coral = new Color(0.95f, 0.19f, 0.18f), gold = new Color(1, 0.79f, 0.12f);
        private Vector2 predictedPoint;
        private Rect viewport;
        private static readonly string[] Titles = { "La última señal", "Cazadores de neón", "Línea de ruptura", "El pulso de Aegis", "Amanecer sobre Hong Kong" };
        private static readonly string[] Stories = {
            "Hong Kong, 23:47. La red del distrito acaba de caer. Mientras Yun y Yang sacan a los vecinos de las calles, Ryu descubre quién controla los repetidores: Urien. El primer paso es abrir una ruta entre los tejados.",
            "Remy espera sobre los ascensores de carga. Sus disparos cubren los accesos al transmisor. Ryu tendrá que anticipar sus movimientos y acertar antes de que lleguen los refuerzos.",
            "Los refuerzos han cerrado la azotea con barreras de acero. Los ascensores siguen funcionando al otro lado. Un tiro con suficiente potencia puede superar la cobertura; un arco alto abre otra ruta.",
            "El último enlace está protegido por Aegis. Los paneles eléctricos detienen los golpes, pero se apagan entre descargas. Remy aprovecha esas pausas para devolver el fuego.",
            "Medianoche. Urien protege el núcleo del transmisor. Abajo, la evacuación se ha detenido. Ryu debe romper los dos enlaces y vencer a Urien antes de que sus esferas alcancen la calle."
        };
        private static readonly int[] Ammunition = { 6, 7, 9, 10, 15 };
        private static readonly float[] Deadlines = { 55, 65, 80, 80, 95 };

        private void Start()
        {
            if (assets == null) { Debug.LogError("Neon Siege assets missing"); enabled = false; return; }
            Time.timeScale = 1;
            cam = GetComponent<Camera>();
            cam.orthographic = true;
            cam.orthographicSize = 5.625f;
            cam.transform.position = new Vector3(0, 0, -10);
            cam.backgroundColor = new Color(0.025f, 0.035f, 0.055f);
            font = assets.bodyFont;
            best = PlayerPrefs.GetInt("NeonSiege.Best", 0);
            volume = PlayerPrefs.GetFloat("NeonSiege.Volume", 0.65f);
            CreateVisuals();
            audioFx = gameObject.AddComponent<AudioSource>();
            music = gameObject.AddComponent<AudioSource>();
            music.clip = assets.music; music.loop = true; music.volume = volume * 0.3f; music.Play();
            ryu = Actor("Ryu", new Vector2(-7.3f, -3.22f), assets.ryuIdle, false, 1.7f);
            titleRival = Actor("Urien / title rival", new Vector2(5.8f, -3.22f), assets.urienIdle, true, 3.1f);
            state = Mode.Title;
            FitViewport();
        }

        private void CreateVisuals()
        {
            LineMaterial = new Material(Shader.Find("Sprites/Default"));
            white = Sprite.Create(Texture2D.whiteTexture, new Rect(0, 0, 1, 1), Vector2.one * 0.5f, 1);
            var bg = new GameObject("Hong Kong / original stage"); owned.Add(bg);
            var renderer = bg.AddComponent<SpriteRenderer>();
            renderer.sprite = assets.background; renderer.sharedMaterial = assets.spriteMaterial;
            renderer.sortingOrder = -20;
            renderer.color = new Color(0.92f, 0.92f, 1);
            bg.transform.position = new Vector3(0, 1.9f, 0);
            bg.transform.localScale = new Vector3(20 / renderer.sprite.bounds.size.x, 11.4f / renderer.sprite.bounds.size.y, 1);
            RectVisual("Roof ledge", new Vector2(0, -3.52f), new Vector2(20, 0.18f), new Color(0.08f, 0.11f, 0.15f), 1);
            RectVisual("Roof trim", new Vector2(0, -3.41f), new Vector2(20, 0.035f), new Color(0.58f, 0.61f, 0.7f), 2);
            path = NewLine("Predicted trajectory", mint, 0.032f, 16);
            marker = NewLine("Future impact", gold, 0.035f, 18);
            flash = RectVisual("Impact flash", Vector2.zero, Vector2.one * 24, Color.clear, 80);
        }

        private LineRenderer NewLine(string label, Color color, float width, int order)
        {
            var root = new GameObject(label); owned.Add(root);
            var line = root.AddComponent<LineRenderer>();
            line.sharedMaterial = LineMaterial; line.startWidth = line.endWidth = width;
            line.startColor = line.endColor = color; line.sortingOrder = order;
            line.positionCount = 0;
            return line;
        }

        private SpriteRenderer RectVisual(string label, Vector2 position, Vector2 size, Color color, int order)
        {
            var root = new GameObject(label); owned.Add(root);
            root.transform.position = position; root.transform.localScale = size;
            var renderer = root.AddComponent<SpriteRenderer>();
            renderer.sprite = white; renderer.color = color; renderer.sortingOrder = order;
            return renderer;
        }

        private SiegeActor Actor(string name, Vector2 position, Sprite[] idle, bool flip, float scale)
        {
            var root = new GameObject(name); owned.Add(root); root.transform.position = position;
            var actor = root.AddComponent<SiegeActor>(); actor.Setup(assets, idle, flip, scale); return actor;
        }

        public void BeginMission(int index)
        {
            Time.timeScale = 1;
            ClearMission();
            Mission = Mathf.Clamp(index, 0, 4);
            startScore = Score;
            MissionClock = 0; remaining = Deadlines[Mission]; Ammo = Ammunition[Mission]; Integrity = 4;
            shots = hits = combo = 0; focus = InitialFocus; cooldown = 0; nextEnemy = Mission == 4 ? 5.5f : 9;
            attackWarned = false; mouseOwnsAim = false; highArc = false; aimReachable = true;
            angle = desiredAngle = 36; speed = 13.8f; aimDamping = 0; lastMouse = Input.mousePosition;
            ryu.Play(assets.ryuIdle, 0);
            switch (Mission)
            {
                case 0:
                    Target(new Vector2(-0.8f, -1.9f)); Target(new Vector2(3.3f, -0.5f)); Target(new Vector2(6.9f, -1.8f)); break;
                case 1:
                    Target(new Vector2(0.5f, -0.9f), new Vector2(1.2f, 0.5f), 1.7f, 2);
                    Target(new Vector2(5.8f, -0.6f), new Vector2(1.1f, 0.45f), 1.8f, 2); break;
                case 2:
                    Barrier(new Vector2(-1.4f, -2.2f), new Vector2(0.7f, 2.4f));
                    Target(new Vector2(2.5f, -1.4f), new Vector2(0.3f, 0.45f), 1.2f, 2);
                    Target(new Vector2(5.5f, -0.1f), new Vector2(0.65f, 0.35f), 1.5f, 3); break;
                case 3:
                    Target(new Vector2(0.1f, -0.5f), new Vector2(0.5f, 0.9f), 1.1f, 2, 3.8f);
                    Target(new Vector2(5.9f, -1.1f), new Vector2(1, 0.4f), 1.4f, 3, 4.3f); break;
                case 4:
                    Target(new Vector2(-0.1f, -0.6f), new Vector2(0, 0.6f), 1.3f, 2);
                    Target(new Vector2(3.5f, 1.4f), new Vector2(0.8f, 0), 1.2f, 2);
                    Target(new Vector2(6.7f, -1.4f), new Vector2(0.6f, 0.35f), 1.1f, 5, 4.6f, true); break;
            }
            state = Mode.Play;
            titleRival.gameObject.SetActive(false);
            Notify("ROUND " + (Mission + 1) + "   FIGHT!", 2);
            Physics2D.SyncTransforms();
        }

        private void Target(Vector2 position, Vector2 movement = default, float frequency = 0, int health = 1, float shield = 0, bool boss = false)
        {
            var root = new GameObject(boss ? "Urien / Aegis core" : "Aegis guardian");
            var target = root.AddComponent<SiegeTarget>();
            target.Setup(this, position, movement, frequency, health, shield, boss, targets.Count + 1); targets.Add(target);
        }

        private void Barrier(Vector2 position, Vector2 size)
        {
            var visual = RectVisual("Steel barrier", position, size, new Color(0.17f, 0.19f, 0.25f), 10);
            barriers.Add(visual.gameObject);
            var box = visual.gameObject.AddComponent<BoxCollider2D>(); box.size = Vector2.one;
            visual.gameObject.AddComponent<SiegeBarrier>();
            var edge = RectVisual("Barrier steel cap", position + Vector2.up * size.y / 2, new Vector2(size.x + 0.08f, 0.09f), gold, 11);
            barriers.Add(edge.gameObject);
            for (int i = 0; i < 2; i++)
            {
                var rim = RectVisual("Steel beam edge", position + Vector2.right * (i == 0 ? -size.x / 2 : size.x / 2), new Vector2(0.06f, size.y), new Color(0.46f, 0.49f, 0.56f), 11);
                barriers.Add(rim.gameObject);
            }
            for (int i = 0; i < 4; i++)
            {
                var rib = RectVisual("Steel cross brace", position + Vector2.up * (-size.y / 2 + (i + 0.5f) * size.y / 4), new Vector2(size.x - 0.08f, 0.04f), new Color(0.32f, 0.35f, 0.43f), 11);
                rib.transform.rotation = Quaternion.Euler(0, 0, i % 2 == 0 ? 30 : -30); barriers.Add(rib.gameObject);
            }
        }

        private void ClearMission()
        {
            foreach (var projectile in projectiles.ToArray()) if (projectile != null) { projectile.gameObject.SetActive(false); Destroy(projectile.gameObject); }
            projectiles.Clear();
            foreach (var target in targets) if (target != null) { target.gameObject.SetActive(false); Destroy(target.gameObject); }
            targets.Clear();
            foreach (var barrier in barriers) if (barrier != null) { barrier.SetActive(false); Destroy(barrier); owned.Remove(barrier); }
            barriers.Clear();
        }

        private void FitViewport()
        {
            float ratio = Screen.width / (float)Mathf.Max(Screen.height, 1);
            cam.rect = ratio > 16f / 9 ? new Rect((1 - (16f / 9) / ratio) / 2, 0, (16f / 9) / ratio, 1)
                : new Rect(0, (1 - ratio / (16f / 9)) / 2, 1, ratio / (16f / 9));
            viewport = cam.pixelRect;
        }

        private void Update()
        {
            if (cam == null) return;
            FitViewport();
            titleRival.gameObject.SetActive(state == Mode.Title || state == Mode.Briefing);
            flash.color = Time.unscaledTime < flashUntil ? new Color(1, 0.3f, 0.35f, 0.12f) : Color.clear;
            if (Input.GetKeyDown(KeyCode.Escape) || Input.GetKeyDown(KeyCode.P)) TogglePause();
            if (!Playing) { path.positionCount = marker.positionCount = 0; return; }
            remaining -= Time.deltaTime; cooldown -= Time.deltaTime;
            Vector2 mouse = Input.mousePosition;
            float mouseY = (Screen.height - mouse.y - (Screen.height - viewport.yMax)) / viewport.height * 720;
            bool inField = viewport.Contains(mouse) && mouseY > 100 && mouseY < 602;
            if (inField && (mouse - lastMouse).sqrMagnitude > 0.1f)
            {
                mouseOwnsAim = true;
                aimPoint = cam.ScreenToWorldPoint(mouse);
            }
            lastMouse = mouse;
            float change = Input.GetKey(KeyCode.W) ? 4 * Time.deltaTime : Input.GetKey(KeyCode.S) ? -4 * Time.deltaTime : 0;
            if (inField) change += Input.mouseScrollDelta.y * 0.3f;
            speed = Mathf.Clamp(speed + change, SiegeBallistics.MinSpeed, SiegeBallistics.MaxSpeed);
            if (Input.GetKeyDown(KeyCode.Tab)) ToggleArc();
            if (mouseOwnsAim) UpdateMouseAim();
            if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.D))
            {
                mouseOwnsAim = false; aimReachable = true;
                desiredAngle = Mathf.Clamp(desiredAngle + (Input.GetKey(KeyCode.A) ? 1 : -1) * 30 * Time.deltaTime, 8, 78);
            }
            angle = Mathf.SmoothDampAngle(angle, desiredAngle, ref aimDamping, 0.045f, 720, Time.deltaTime);
            if (Input.GetKeyDown(KeyCode.F)) Focus();
            Predict();
            if ((inField && Input.GetMouseButtonDown(0)) || Input.GetKeyDown(KeyCode.Space)) FireAimedShot();
            if (remaining <= 0) Fail("Se agotó el tiempo. El transmisor sigue en manos de Urien.");
            else if (Ammo == 0 && !projectiles.Any(p => p != null && !p.hostile)) Fail("Ryu se quedó sin energía antes de despejar la azotea.");
        }

        public bool AimAtWorld(Vector2 position, bool useHighArc = false)
        {
            aimPoint = position; highArc = useHighArc; mouseOwnsAim = true;
            UpdateMouseAim();
            angle = desiredAngle; aimDamping = 0;
            return aimReachable;
        }

        private void UpdateMouseAim()
        {
            aimReachable = SiegeBallistics.AimAt(Muzzle, aimPoint, speed, highArc, out Vector2 velocity);
            if (aimReachable) desiredAngle = Mathf.Atan2(velocity.y, velocity.x) * Mathf.Rad2Deg;
            else desiredAngle = Mathf.Clamp(Mathf.Atan2((aimPoint - Muzzle).y, (aimPoint - Muzzle).x) * Mathf.Rad2Deg + 15, 8, 78);
        }

        public void ToggleArc() { highArc = !highArc; if (mouseOwnsAim) UpdateMouseAim(); }

        public bool FireAimedShot()
        {
            // Smoothing is visual; a fast pointer-and-click must use the requested arc.
            angle = desiredAngle; aimDamping = 0;
            Predict();
            return Launch(SiegeBallistics.Velocity(angle, speed));
        }

        private void FixedUpdate()
        {
            if (!Playing) return;
            MissionClock += Time.fixedDeltaTime;
            if (Mission >= 3 && MissionClock >= nextEnemy - 0.7f && !attackWarned)
            {
                attackWarned = true;
                var attacker = targets.Where(t => t.Alive).OrderByDescending(t => t.boss).ThenByDescending(t => t.origin.x).FirstOrDefault();
                if (attacker != null) { attacker.Cast(); Notify("¡CONTRAATAQUE!", 0.7f); }
            }
            if (Mission >= 3 && MissionClock >= nextEnemy)
            {
                nextEnemy += Mission == 4 ? 6.2f : 10;
                attackWarned = false;
                var attacker = targets.Where(t => t.Alive).OrderByDescending(t => t.boss).ThenByDescending(t => t.origin.x).FirstOrDefault();
                if (attacker != null)
                {
                    SpawnProjectile(attacker.PositionAt(MissionClock), new Vector2(-4.2f, 0), true);
                }
            }
        }

        public bool Launch(Vector2 velocity)
        {
            if (!Playing || Ammo <= 0 || cooldown > 0 || projectiles.Any(p => p != null && !p.hostile)) return false;
            Ammo--; shots++; cooldown = 0.5f;
            SpawnProjectile(Muzzle, velocity, false);
            ryu.Play(assets.ryuCast, 0.48f);
            Sound(assets.cast, 0.65f);
            return true;
        }

        private void SpawnProjectile(Vector2 position, Vector2 velocity, bool enemy)
        {
            var root = new GameObject(enemy ? "Hostile sphere" : "Ballistic Hadouken");
            var projectile = root.AddComponent<SiegeProjectile>();
            projectile.Setup(this, position, velocity, enemy); projectiles.Add(projectile);
        }

        public void ProjectileFinished(SiegeProjectile projectile, bool hit)
        {
            projectiles.Remove(projectile);
            if (!projectile.hostile && !hit && Playing) { combo = 0; Notify("DISPARO PERDIDO", 1.2f); }
        }

        public void HitTarget(SiegeTarget target, Vector2 point)
        {
            hits++; combo++;
            int gained = 150 + Mathf.Min(combo, 5) * 40 + (!target.Alive ? 150 : 0);
            Score += gained;
            Burst(point, mint); Sound(assets.hit);
            Notify("+" + gained + "   /   RACHA " + combo, 1.5f);
            if (targets.All(t => !t.Alive)) CompleteMission();
        }

        public void Blocked(Vector2 position) { combo = 0; Burst(position, coral); Sound(assets.block); Notify("AEGIS / IMPACTO BLOQUEADO", 1.2f); }
        public void Intercept(Vector2 position) { Score += 200; Burst(position, gold); Sound(assets.hit); Notify("¡INTERCEPCIÓN! +200", 1.5f); }
        public void TakeDamage()
        {
            if (!Playing) return;
            Integrity--; combo = 0; flashUntil = Time.unscaledTime + 0.18f;
            Sound(assets.block); Notify("¡LA EVACUACIÓN ESTÁ EN PELIGRO!", 1.5f);
            if (Integrity <= 0) Fail("Los contraataques han cerrado la ruta de evacuación.");
        }

        private void CompleteMission()
        {
            stars = hits == shots && focus == InitialFocus ? 3 : hits >= shots * 0.65f ? 2 : 1;
            Score += Ammo * 60 + Mathf.CeilToInt(Mathf.Max(remaining, 0)) * 8 + Integrity * 100;
            state = Mission == 4 ? Mode.Complete : Mode.Clear;
            foreach (var projectile in projectiles.ToArray())
                if (projectile != null) projectile.Finish(true);
            ryu.Play(assets.ryuWin, 1.2f, true); Sound(assets.win);
            path.positionCount = marker.positionCount = 0;
            if (state == Mode.Complete && Score > best) { best = Score; PlayerPrefs.SetInt("NeonSiege.Best", best); PlayerPrefs.Save(); }
        }

        private void Fail(string reason)
        {
            if (!Playing) return;
            failure = reason; state = Mode.Failed;
            path.positionCount = marker.positionCount = 0;
        }

        public void TogglePause()
        {
            if (state != Mode.Play && state != Mode.Paused) return;
            state = state == Mode.Play ? Mode.Paused : Mode.Play;
            Time.timeScale = state == Mode.Paused ? 0 : 1;
            if (state == Mode.Paused) music.Pause(); else music.UnPause();
        }

        public void Retry()
        {
            if (state == Mode.Complete) return;
            Score = startScore;
            BeginMission(Mission);
            music.UnPause();
        }

        public void ExitCompletedCampaign()
        {
            if (state != Mode.Complete) return;
            PlayerPrefs.Save();
            Time.timeScale = 1;
            UnityEngine.SceneManagement.SceneManager.LoadScene("MainMenu_Scene");
        }

        public bool FindSolution(SiegeTarget target, out Vector2 velocity, out float time)
        {
            // Future target position and shield phase are evaluated at arrival, not now.
            for (int i = 24; i < 185; i++)
            {
                time = i * SiegeBallistics.StepTime;
                if (!target.OpenAt(MissionClock + time)) continue;
                if (!SiegeBallistics.Solve(Muzzle, target.PositionAt(MissionClock + time), time, out velocity)) continue;
                if (Forecast(velocity, out _, out _, out var hitTarget) == 1 && hitTarget == target) return true;
            }
            velocity = Vector2.zero; time = 0; return false;
        }

        public void Focus()
        {
            if (!Playing || focus <= 0) return;
            foreach (var target in targets.Where(t => t.Alive))
                if (FindSolution(target, out Vector2 velocity, out _))
                {
                    focus--; Score = Mathf.Max(startScore, Score - 75);
                    speed = velocity.magnitude; angle = desiredAngle = Mathf.Atan2(velocity.y, velocity.x) * Mathf.Rad2Deg;
                    mouseOwnsAim = false; aimReachable = true; aimDamping = 0;
                    Notify("TIRO CALCULADO", 1.2f); Predict(); return;
                }
            Notify("SIN VENTANA DE TIRO. ESPERA EL SIGUIENTE MOVIMIENTO.", 1.5f);
        }

        public int Forecast(Vector2 velocity, out Vector2 point, out float time, out SiegeTarget target, List<Vector3> points = null)
        {
            Vector2 position = Muzzle;
            point = position; target = null; time = 0;
            points?.Add(position);
            for (int i = 1; i <= 190; i++)
            {
                Vector2 previous = position;
                SiegeBallistics.Step(ref position, ref velocity, SiegeBallistics.StepTime);
                time = i * SiegeBallistics.StepTime;
                if (i % 2 == 0) points?.Add(position);
                point = position;
                foreach (var barrier in barriers)
                {
                    if (barrier == null) continue;
                    var collider = barrier.GetComponent<BoxCollider2D>();
                    if (collider == null) continue;
                    Bounds b = collider.bounds; b.Expand(SiegeBallistics.Radius * 2);
                    if (b.IntersectRay(new Ray(previous, (position - previous).normalized), out float distance) && distance <= (position - previous).magnitude) return -1;
                }
                foreach (var shot in projectiles)
                {
                    if (shot == null || !shot.hostile) continue;
                    Vector2 oldShot = shot.Body.position + shot.Body.linearVelocity * (time - SiegeBallistics.StepTime);
                    Vector2 newShot = shot.Body.position + shot.Body.linearVelocity * time;
                    if (SiegeBallistics.SegmentCircle(previous - oldShot, position - newShot, Vector2.zero, SiegeBallistics.Radius * 2)) return 2;
                }
                foreach (var t in targets)
                {
                    if (!t.Alive) continue;
                    Vector2 oldTarget = t.PositionAt(MissionClock + time - SiegeBallistics.StepTime);
                    Vector2 newTarget = t.PositionAt(MissionClock + time);
                    if (!SiegeBallistics.SegmentCircle(previous - oldTarget, position - newTarget, Vector2.zero, SiegeBallistics.Radius + SiegeTarget.Radius - 0.07f)) continue;
                    target = t;
                    return t.OpenAt(MissionClock + time) ? 1 : -1;
                }
                if (position.y < -3.7f || position.y > 18 || position.x > 9.3f) return 0;
            }
            return 0;
        }

        private void Predict()
        {
            var points = new List<Vector3>();
            int result = Forecast(SiegeBallistics.Velocity(angle, speed), out predictedPoint, out predictionTime, out var target, points);
            path.positionCount = points.Count; path.SetPositions(points.ToArray());
            Color color = result > 0 ? gold : result < 0 ? coral : new Color(1, 1, 1, 0.65f);
            path.startColor = color; path.endColor = new Color(color.r, color.g, color.b, 0.15f);
            marker.positionCount = 5;
            marker.SetPositions(new[] { (Vector3)predictedPoint + Vector3.left * 0.13f, (Vector3)predictedPoint + Vector3.right * 0.13f,
                (Vector3)predictedPoint, (Vector3)predictedPoint + Vector3.up * 0.13f, (Vector3)predictedPoint + Vector3.down * 0.13f });
            marker.startColor = marker.endColor = color;
            forecast = mouseOwnsAim && !aimReachable ? "AUMENTA LA POTENCIA" : result == 2 ? "INTERCEPCIÓN" : result > 0 ? "TIRO ALCANZABLE" : result < 0 ? "COBERTURA EN LA RUTA" : "SIN BLANCO EN LA RUTA";
        }

        private void Burst(Vector2 position, Color color)
        {
            var burst = new GameObject("Impact animation");
            burst.transform.position = position + Vector2.down * 0.25f;
            var animation = burst.AddComponent<SiegeActor>();
            animation.Setup(assets, assets.impact, false, 1.1f);
            animation.Renderer.sortingOrder = 24;
            animation.Play(assets.impact, 0.3f, true);
            Destroy(burst, 0.32f);
            for (int i = 0; i < 8; i++)
            {
                var spark = RectVisual("Energy spark", position, Vector2.one * Random.Range(0.04f, 0.1f), color, 25);
                var effect = spark.gameObject.AddComponent<SiegeSpark>();
                effect.velocity = Random.insideUnitCircle.normalized * Random.Range(1.3f, 3.8f);
                owned.Remove(spark.gameObject);
            }
        }

        private void Notify(string value, float duration) { message = value; messageUntil = Time.time + duration; }
        private void Sound(AudioClip clip, float gain = 1) { if (clip != null) audioFx.PlayOneShot(clip, volume * gain); }


        private void OnDestroy()
        {
            Time.timeScale = 1;
            ClearMission();
            foreach (var root in owned) if (root != null) Destroy(root);
            if (LineMaterial != null) Destroy(LineMaterial);
            if (white != null) Destroy(white);
            if (buttonTexture != null) Destroy(buttonTexture);
        }
    }

    public sealed class SiegeSpark : MonoBehaviour
    {
        public Vector2 velocity;
        private float life = 0.4f;
        private void Update()
        {
            life -= Time.deltaTime;
            transform.position += (Vector3)velocity * Time.deltaTime;
            transform.localScale *= Mathf.Exp(-5 * Time.deltaTime);
            if (life <= 0) Destroy(gameObject);
        }
    }
}
