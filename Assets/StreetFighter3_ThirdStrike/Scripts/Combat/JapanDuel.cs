using UnityEngine;

// Self-contained two-player sandbox. Physics and overlap queries use Unity Physics2D.
public class JapanDuel : MonoBehaviour
{
    private DuelFighter ken, ryu;
    private float countdown;
    private float roundTimer = 99f;
    private string result;
    public float FloorY { get; private set; } = -0.32f;
    public bool IsPaused { get; private set; } = false;
    public bool Fighting => countdown <= 0 && result == null && !IsPaused;

    private AudioSource bgmSource;
    private AudioSource sfxSource;
    private AudioClip cursorSfx;
    private AudioClip confirmSfx;
    private int pauseSelectedIndex = 0;
    private readonly string[] pauseOptions = { "REANUDAR", "REINICIAR RONDA", "VOLVER AL MENÚ" };

    private void Start()
    {
        DuelRoster roster = Resources.Load<DuelRoster>("JapanDuelRoster");
        if (roster == null) { Debug.LogError("JapanDuelRoster missing."); enabled = false; return; }
        StageParallaxTester tester = GetComponent<StageParallaxTester>();
        if (tester != null) tester.enabled = false;
        bool isChinaStage = false;
        foreach (GameObject root in gameObject.scene.GetRootGameObjects())
        {
            if (!root.name.StartsWith("Stage_")) continue;
            if (root.name.Contains("China")) isChinaStage = true;
            Transform ground = root.transform.Find("Ground_Collider");
            if (ground == null) continue;
            BoxCollider2D floor = ground.GetComponent<BoxCollider2D>();
            if (floor != null) ground.position += Vector3.up * (FloorY - floor.bounds.max.y);
        }

        // BGM de Pelea (Suzaku Castle - Japón)
        AudioClip bgmClip = Resources.Load<AudioClip>(isChinaStage ? "Audio/BGM_China" : "Audio/BGM_Japan") ?? Resources.Load<AudioClip>("Audio/BGM_Japan");
        if (bgmClip != null)
        {
            bgmSource = gameObject.AddComponent<AudioSource>();
            bgmSource.clip = bgmClip;
            bgmSource.loop = true;
            bgmSource.volume = 0.55f;
            bgmSource.playOnAwake = true;
            bgmSource.Play();
        }

        cursorSfx = Resources.Load<AudioClip>("Audio/Menu_Cursor_Select");
        confirmSfx = Resources.Load<AudioClip>("Audio/Menu_Confirm_Start");
        sfxSource = gameObject.AddComponent<AudioSource>();

        ken = Create("Ken", roster.ken, true);
        ryu = Create("Ryu", roster.ryu, false);
        ken.opponent = ryu;
        ryu.opponent = ken;
        Restart();
    }

    private DuelFighter Create(string fighterName, DuelRoster.Motion[] motions, bool first)
    {
        GameObject root = new GameObject("Fighter_" + fighterName);
        UnityEngine.SceneManagement.SceneManager.MoveGameObjectToScene(root, gameObject.scene);
        DuelFighter fighter = root.AddComponent<DuelFighter>();
        fighter.Initialize(this, motions, first);
        return fighter;
    }

    public void Restart()
    {
        IsPaused = false;
        Time.timeScale = 1f;
        result = null;
        countdown = 0.5f;
        roundTimer = 99f;
        ken.ResetFighter(-1.35f);
        ryu.ResetFighter(1.35f);
    }

    public void TogglePause()
    {
        IsPaused = !IsPaused;
        Time.timeScale = IsPaused ? 0f : 1f;
        pauseSelectedIndex = 0;
        if (IsPaused && cursorSfx != null && sfxSource != null)
        {
            sfxSource.PlayOneShot(cursorSfx, 0.8f);
        }
    }

    public void ReturnToMainMenu()
    {
        Time.timeScale = 1f;
        UnityEngine.SceneManagement.SceneManager.LoadScene("MainMenu_Scene");
    }

    private void Update()
    {
        if (ken == null || ryu == null) return;

        // Toggle Pausa con Escape o P
        if (Input.GetKeyDown(KeyCode.Escape) || Input.GetKeyDown(KeyCode.P))
        {
            TogglePause();
        }

        if (IsPaused)
        {
            // Navegación en Menú de Pausa
            if (Input.GetKeyDown(KeyCode.W) || Input.GetKeyDown(KeyCode.UpArrow))
            {
                pauseSelectedIndex = (pauseSelectedIndex - 1 + pauseOptions.Length) % pauseOptions.Length;
                if (cursorSfx != null && sfxSource != null) sfxSource.PlayOneShot(cursorSfx, 0.7f);
            }
            else if (Input.GetKeyDown(KeyCode.S) || Input.GetKeyDown(KeyCode.DownArrow))
            {
                pauseSelectedIndex = (pauseSelectedIndex + 1) % pauseOptions.Length;
                if (cursorSfx != null && sfxSource != null) sfxSource.PlayOneShot(cursorSfx, 0.7f);
            }

            if (Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.Space) || Input.GetKeyDown(KeyCode.KeypadEnter))
            {
                ConfirmPauseOption(pauseSelectedIndex);
            }
            return;
        }

        countdown = Mathf.Max(0, countdown - Time.deltaTime);
        if (Fighting && roundTimer > 0f)
        {
            roundTimer -= Time.deltaTime;
            if (roundTimer <= 0f && result == null)
            {
                roundTimer = 0f;
                result = ken.Health == ryu.Health ? "DRAW GAME" : (ken.Health > ryu.Health ? "KEN WINS" : "RYU WINS");
                ken.EndRound(ken.Health > ryu.Health);
                ryu.EndRound(ryu.Health > ken.Health);
            }
        }
        if (Input.GetKeyDown(KeyCode.Return) && !IsPaused) Restart();
        if (result == null && (ken.Health <= 0 || ryu.Health <= 0))
        {
            result = ken.Health == ryu.Health ? "DOUBLE K.O." : ken.Health > 0 ? "KEN WINS" : "RYU WINS";
            ken.EndRound(ken.Health > 0);
            ryu.EndRound(ryu.Health > 0);
        }
    }

    private void ConfirmPauseOption(int index)
    {
        if (confirmSfx != null && sfxSource != null) sfxSource.PlayOneShot(confirmSfx, 0.8f);

        switch (index)
        {
            case 0: // Reanudar
                TogglePause();
                break;
            case 1: // Reiniciar Ronda
                Restart();
                break;
            case 2: // Volver al Menú
                ReturnToMainMenu();
                break;
        }
    }

    private void OnGUI()
    {
        if (ken == null || ryu == null) return;
        float scale = Mathf.Min(Screen.width / 960f, Screen.height / 540f);
        Matrix4x4 old = GUI.matrix;
        GUI.matrix = Matrix4x4.TRS(new Vector3((Screen.width - 960 * scale) / 2, 0), Quaternion.identity, Vector3.one * scale);
        GUIStyle label = new GUIStyle(GUI.skin.label) { fontSize = 22, fontStyle = FontStyle.Bold };

        if (IsPaused)
        {
            // Fondo oscuro semitransparente completo
            GUI.color = new Color(0.02f, 0.03f, 0.06f, 0.85f);
            GUI.DrawTexture(new Rect(0, 0, 960, 540), Texture2D.whiteTexture);

            // Marco central del Menú de Pausa
            GUI.color = new Color(0.08f, 0.10f, 0.16f, 0.95f);
            GUI.DrawTexture(new Rect(280, 95, 400, 340), Texture2D.whiteTexture);

            // Borde dorado
            GUI.color = new Color(1f, 0.82f, 0.15f, 0.9f);
            GUI.DrawTexture(new Rect(280, 95, 400, 4), Texture2D.whiteTexture);
            GUI.DrawTexture(new Rect(280, 431, 400, 4), Texture2D.whiteTexture);
            GUI.DrawTexture(new Rect(280, 95, 4, 340), Texture2D.whiteTexture);
            GUI.DrawTexture(new Rect(676, 95, 4, 340), Texture2D.whiteTexture);

            // Título
            GUIStyle pauseTitleStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 32,
                fontStyle = FontStyle.Bold,
                alignment = TextAnchor.MiddleCenter
            };
            pauseTitleStyle.normal.textColor = new Color(1f, 0.85f, 0.2f);
            GUI.Label(new Rect(280, 115, 400, 45), "— PAUSA —", pauseTitleStyle);

            // Opciones
            GUIStyle optionStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 20,
                fontStyle = FontStyle.Bold,
                alignment = TextAnchor.MiddleCenter
            };

            for (int i = 0; i < pauseOptions.Length; i++)
            {
                bool isSel = (i == pauseSelectedIndex);
                optionStyle.normal.textColor = isSel ? new Color(1f, 0.9f, 0.2f) : new Color(0.75f, 0.8f, 0.85f);

                Rect optRect = new Rect(300, 180 + i * 65, 360, 48);
                if (isSel)
                {
                    GUI.color = new Color(0.2f, 0.25f, 0.35f, 0.75f);
                    GUI.DrawTexture(optRect, Texture2D.whiteTexture);
                }

                string prefix = isSel ? ">>  " : "    ";
                string suffix = isSel ? "  <<" : "";
                if (GUI.Button(optRect, prefix + pauseOptions[i] + suffix, optionStyle))
                {
                    pauseSelectedIndex = i;
                    ConfirmPauseOption(i);
                }
            }

            // Pie de página de ayuda
            GUIStyle hintStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 13,
                fontStyle = FontStyle.Normal,
                alignment = TextAnchor.MiddleCenter
            };
            hintStyle.normal.textColor = new Color(0.6f, 0.65f, 0.75f);
            GUI.Label(new Rect(280, 390, 400, 30), "[W/S/Flechas]: Navegar | [ENTER]: Elegir | [ESC/P]: Reanudar", hintStyle);

            GUI.color = Color.white;
            GUI.matrix = old;
            return;
        }

        GUI.color = new Color(0.04f, 0.04f, 0.04f, 0.85f);
        GUI.DrawTexture(new Rect(20, 8, 400, 61), Texture2D.whiteTexture);
        GUI.DrawTexture(new Rect(540, 8, 400, 61), Texture2D.whiteTexture);
        GUI.color = Color.white;
        Bar(new Rect(30, 42, 380, 19), ken.Health, new Color(0.95f, 0.25f, 0.2f));
        Bar(new Rect(550, 42, 380, 19), ryu.Health, new Color(0.2f, 0.8f, 0.8f));

        // Caja Central del Contador de Tiempo (99s)
        Rect timerBox = new Rect(436, 12, 88, 54);
        GUI.color = new Color(0.04f, 0.05f, 0.09f, 0.95f);
        GUI.DrawTexture(timerBox, Texture2D.whiteTexture);
        GUI.color = new Color(0.95f, 0.78f, 0.2f, 1f);
        GUI.DrawTexture(new Rect(timerBox.x, timerBox.y, timerBox.width, 2), Texture2D.whiteTexture);
        GUI.DrawTexture(new Rect(timerBox.x, timerBox.y + timerBox.height - 2, timerBox.width, 2), Texture2D.whiteTexture);
        GUI.DrawTexture(new Rect(timerBox.x, timerBox.y, 2, timerBox.height), Texture2D.whiteTexture);
        GUI.DrawTexture(new Rect(timerBox.x + timerBox.width - 2, timerBox.y, 2, timerBox.height), Texture2D.whiteTexture);
        GUI.color = Color.white;

        int secLeft = Mathf.CeilToInt(roundTimer);
        GUIStyle tStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 32,
            fontStyle = FontStyle.Bold,
            alignment = TextAnchor.MiddleCenter
        };
        tStyle.normal.textColor = secLeft <= 15 ? new Color(1f, 0.22f, 0.2f) : new Color(1f, 0.88f, 0.15f);
        GUI.Label(timerBox, secLeft.ToString("D2"), tStyle);
        GUI.Label(new Rect(30, 12, 300, 30), "KEN   " + ken.Health, label);
        label.alignment = TextAnchor.UpperRight;
        GUI.Label(new Rect(630, 12, 300, 30), "RYU   " + ryu.Health, label);
        label.alignment = TextAnchor.MiddleCenter;
        label.fontSize = 30;
        if (result != null || countdown > 0)
        {
            GUI.color = new Color(0.04f, 0.04f, 0.04f, 0.85f);
            GUI.DrawTexture(new Rect(270, 80, 420, 60), Texture2D.whiteTexture);
            GUI.color = Color.white;
        }
        GUI.Label(new Rect(270, 80, 420, 60), result ?? (countdown > 0 ? "READY" : ""), label);
        if (result != null && GUI.Button(new Rect(410, 145, 140, 36), "Revancha")) Restart();

        // Banner informativo de controles en vivo
        GUI.color = new Color(0.04f, 0.05f, 0.08f, 0.85f);
        GUI.DrawTexture(new Rect(80, 498, 800, 34), Texture2D.whiteTexture);
        GUI.color = Color.white;
        GUIStyle controlHint = new GUIStyle(GUI.skin.label)
        {
            fontSize = 12,
            fontStyle = FontStyle.Bold,
            alignment = TextAnchor.MiddleCenter
        };
        controlHint.normal.textColor = new Color(1f, 0.92f, 0.4f);
        GUI.Label(new Rect(80, 498, 800, 34), "P1 (KEN): [WASD / Flechas] Mover/Saltar | [J / F] Puño D | [K / H] Puño F | [L / V] Patada D | [O / B] Patada F | [ESC] Pausa", controlHint);

        GUI.matrix = old;
    }

    private static void Bar(Rect rect, int health, Color color)
    {
        GUI.color = new Color(0.08f, 0.08f, 0.08f, 0.9f);
        GUI.DrawTexture(rect, Texture2D.whiteTexture);
        rect.width *= health / 100f;
        GUI.color = color;
        GUI.DrawTexture(rect, Texture2D.whiteTexture);
        GUI.color = Color.white;
    }

    private void OnDestroy()
    {
        if (ken != null) Destroy(ken.gameObject);
        if (ryu != null) Destroy(ryu.gameObject);
    }
}
