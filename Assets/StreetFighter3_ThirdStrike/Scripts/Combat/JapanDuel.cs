using UnityEngine;

// Self-contained two-player sandbox. Physics and overlap queries use Unity Physics2D.
public class JapanDuel : MonoBehaviour
{
    private DuelFighter ken, ryu;
    private float countdown;
    private string result;
    public float FloorY { get; private set; } = -0.32f;
    public bool Fighting => countdown <= 0 && result == null;

    private void Start()
    {
        DuelRoster roster = Resources.Load<DuelRoster>("JapanDuelRoster");
        if (roster == null) { Debug.LogError("JapanDuelRoster missing."); enabled = false; return; }
        StageParallaxTester tester = GetComponent<StageParallaxTester>();
        if (tester != null) tester.enabled = false;
        foreach (GameObject root in gameObject.scene.GetRootGameObjects())
        {
            if (root.name != "Stage_Japan") continue;
            Transform ground = root.transform.Find("Ground_Collider");
            if (ground == null) continue;
            BoxCollider2D floor = ground.GetComponent<BoxCollider2D>();
            if (floor != null) ground.position += Vector3.up * (FloorY - floor.bounds.max.y);
        }
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

    private void Restart()
    {
        result = null;
        countdown = 2f;
        ken.ResetFighter(-1.35f);
        ryu.ResetFighter(1.35f);
    }

    private void Update()
    {
        if (ken == null || ryu == null) return;
        countdown = Mathf.Max(0, countdown - Time.deltaTime);
        if (Input.GetKeyDown(KeyCode.Return)) Restart();
        if (result == null && (ken.Health <= 0 || ryu.Health <= 0))
        {
            result = ken.Health == ryu.Health ? "DOUBLE K.O." : ken.Health > 0 ? "KEN WINS" : "RYU WINS";
            ken.EndRound(ken.Health > 0);
            ryu.EndRound(ryu.Health > 0);
        }
    }

    private void OnGUI()
    {
        if (ken == null || ryu == null) return;
        float scale = Mathf.Min(Screen.width / 960f, Screen.height / 540f);
        Matrix4x4 old = GUI.matrix;
        GUI.matrix = Matrix4x4.TRS(new Vector3((Screen.width - 960 * scale) / 2, 0), Quaternion.identity, Vector3.one * scale);
        GUIStyle label = new GUIStyle(GUI.skin.label) { fontSize = 22, fontStyle = FontStyle.Bold };
        GUI.color = new Color(0.04f, 0.04f, 0.04f, 0.85f);
        GUI.DrawTexture(new Rect(20, 8, 400, 61), Texture2D.whiteTexture);
        GUI.DrawTexture(new Rect(540, 8, 400, 61), Texture2D.whiteTexture);
        GUI.color = Color.white;
        Bar(new Rect(30, 42, 380, 19), ken.Health, new Color(0.95f, 0.25f, 0.2f));
        Bar(new Rect(550, 42, 380, 19), ryu.Health, new Color(0.2f, 0.8f, 0.8f));
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
