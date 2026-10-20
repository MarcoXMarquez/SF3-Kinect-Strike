using System.Linq;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace SF3.NeonSiege
{
    public sealed partial class NeonSiegeGame
    {
        private Texture2D buttonTexture;
        private readonly Color ink = new Color(0.055f, 0.045f, 0.10f);
        private readonly Color blue = new Color(0.12f, 0.22f, 0.58f);

        private void OnGUI()
        {
            if (assets == null || cam == null) return;
            if (text == null)
            {
                text = new GUIStyle(GUI.skin.label) { wordWrap = true, richText = false, padding = new RectOffset() };
                button = new GUIStyle(GUIStyle.none);
                buttonTexture = new Texture2D(64, 24, TextureFormat.RGBA32, false) { filterMode = FilterMode.Point };
                var pixels = new Color[64 * 24];
                for (int y = 0; y < 24; y++) for (int x = 0; x < 64; x++)
                    pixels[y * 64 + x] = x >= (23 - y) / 3 && x < 64 - y / 3 ? Color.white : Color.clear;
                buttonTexture.SetPixels(pixels); buttonTexture.Apply();
            }
            Matrix4x4 old = GUI.matrix;
            GUI.matrix = Matrix4x4.TRS(new Vector3(viewport.x, Screen.height - viewport.yMax, 0), Quaternion.identity, Vector3.one * (viewport.width / 1280));
            if (state == Mode.Title || state == Mode.Briefing) DrawStory(); else DrawGame();
            GUI.matrix = old; GUI.color = GUI.backgroundColor = Color.white;
        }

        private void DrawStory()
        {
            Panel(new Rect(0, 0, 1280, 720), new Color(0.025f, 0.015f, 0.055f, 0.5f));
            Slant(new Rect(35, 38, 398, 41), coral);
            Type(new Rect(65, 42, 340, 30), "STREET FIGHTER III  /  SPECIAL MISSION", 22, Color.white, assets.numberFont);
            Arcade(new Rect(46, 105, 1060, 116), state == Mode.Title ? "NEON SIEGE" : "ROUND " + (Mission + 1), 100, gold, TextAnchor.UpperLeft, coral);
            Arcade(new Rect(57, 222, 870, 58), state == Mode.Title ? "LA ÚLTIMA SEÑAL" : Titles[Mission].ToUpperInvariant(), 42, Color.white);
            Type(new Rect(62, 300, 680, 148), Stories[state == Mode.Title ? 0 : Mission], 26, Color.white, assets.bodyFont);
            Slant(new Rect(55, 465, 590, 40), blue);
            Type(new Rect(82, 470, 550, 30), state == Mode.Title ? "CINCO ASALTOS. UNA CIUDAD POR RECUPERAR." : "OBJETIVO: DESPEJA LA AZOTEA Y CONSERVA LA SEÑAL.", 21, gold, assets.numberFont);
            
            if (Button(new Rect(55, 546, 320, 58), state == Mode.Title ? "EMPEZAR PARTIDA" : "¡A LUCHAR!", gold)) BeginMission(state == Mode.Title ? 0 : Mission);
            if (state == Mode.Title && Button(new Rect(390, 546, 300, 58), "VOLVER AL MENÚ", blue))
            {
                Time.timeScale = 1;
                SceneManager.LoadScene("MainMenu_Scene");
            }

            Type(new Rect(64, 652, 500, 30), "HONG KONG / MODO HISTORIA", 21, Color.white, assets.numberFont);
            Type(new Rect(840, 652, 360, 30), "RÉCORD  " + best, 25, gold, assets.numberFont, TextAnchor.UpperRight);
            Arcade(new Rect(937, 155, 280, 60), "URIEN", 52, gold, TextAnchor.MiddleCenter);
            Type(new Rect(905, 220, 330, 62), "El control de la ciudad\nse decide en los tejados.", 24, Color.white, assets.bodyFont, TextAnchor.MiddleCenter);
        }

        private void DrawGame()
        {
            int totalHp = targets.Sum(t => t.maxHealth), hp = targets.Sum(t => t.health);
            Panel(new Rect(0, 0, 1280, 98), new Color(0.04f, 0.035f, 0.075f, 0.9f));
            Slant(new Rect(18, 8, 135, 30), coral);
            Type(new Rect(38, 8, 100, 29), "1P  RYU", 25, Color.white, assets.numberFont);
            Type(new Rect(166, 10, 350, 27), "PUNTOS  " + Score, 23, gold, assets.numberFont);
            Arcade(new Rect(968, 4, 275, 36), Mission == 4 ? "URIEN" : "REMY / AEGIS", 28, Color.white, TextAnchor.UpperRight);
            LifeBar(new Rect(28, 41, 482, 23), Integrity / 4f, false);
            LifeBar(new Rect(770, 41, 482, 23), totalHp > 0 ? hp / (float)totalHp : 0, true);
            Arcade(new Rect(562, -1, 156, 76), Mathf.CeilToInt(Mathf.Max(0, remaining)).ToString(), 65, remaining < 15 ? coral : gold, TextAnchor.MiddleCenter);
            Type(new Rect(558, 72, 164, 22), "TIEMPO", 17, Color.white, assets.numberFont, TextAnchor.MiddleCenter);
            Type(new Rect(28, 69, 470, 25), "ROUND " + (Mission + 1) + " / " + Titles[Mission].ToUpperInvariant(), 20, Color.white, assets.numberFont);
            Type(new Rect(777, 69, 405, 25), "OBJETIVOS " + targets.Count(t => !t.Alive) + "/" + targets.Count + "     ENERGÍA " + Ammo + "/" + Ammunition[Mission], 21, gold, assets.numberFont, TextAnchor.UpperRight);
            if (Button(new Rect(1195, 68, 57, 27), "II", blue, "Pausa")) TogglePause();

            foreach (var target in targets.Where(t => t.Alive))
            {
                Vector3 p = cam.WorldToViewportPoint(target.NameAnchor);
                float x = p.x * 1280, y = (1 - p.y) * 720;
                bool closed = !target.OpenAt(MissionClock);
                Type(new Rect(x - 85, y - 34, 170, 28), target.callsign + (closed ? " · AEGIS" : ""), 21, closed ? mint : gold, assets.numberFont, TextAnchor.MiddleCenter, true);
                Panel(new Rect(x - 37, y - 5, 74, 7), ink);
                Panel(new Rect(x - 35, y - 3, 70f * target.health / target.maxHealth, 3), target.boss ? coral : gold);
            }
            if (Playing && Time.time < messageUntil)
                Arcade(new Rect(100, 113, 1080, 47), message, 33, gold, TextAnchor.MiddleCenter);
            foreach (var shot in projectiles.Where(p => p != null && !p.hostile && p.Body.position.y > 4.1f))
            {
                Vector3 p = cam.WorldToViewportPoint(shot.Body.position);
                float x = Mathf.Clamp(p.x * 1280, 90, 1190);
                Slant(new Rect(x - 66, 101, 132, 27), blue);
                Type(new Rect(x - 63, 101, 126, 25), "TIRO ALTO", 19, gold, assets.numberFont, TextAnchor.MiddleCenter);
            }

            Panel(new Rect(0, 611, 1280, 109), ink);
            Panel(new Rect(0, 611, 1280, 3), gold);
            Type(new Rect(27, 630, 278, 30), "POTENCIA  " + speed.ToString("F1") + " m/s", 23, Color.white, assets.numberFont);
            GUI.enabled = Playing;
            float nextSpeed = GUI.HorizontalSlider(new Rect(29, 672, 259, 22), speed, SiegeBallistics.MinSpeed, SiegeBallistics.MaxSpeed);
            if (Mathf.Abs(nextSpeed - speed) > 0.001f) { speed = nextSpeed; if (mouseOwnsAim) UpdateMouseAim(); }
            Type(new Rect(329, 630, 155, 28), "ÁNGULO", 21, gold, assets.numberFont);
            Arcade(new Rect(324, 659, 160, 37), angle.ToString("F1") + "°", 34, Color.white);
            Type(new Rect(503, 630, 310, 28), forecast, 21, mouseOwnsAim && !aimReachable ? coral : gold, assets.numberFont);
            Type(new Rect(504, 665, 280, 28), "VUELO  " + predictionTime.ToString("F2") + " s", 20, Color.white, assets.bodyFont);
            Type(new Rect(833, 624, 166, 24), "ARCO", 17, Color.white, assets.numberFont);
            if (Button(new Rect(826, 654, 81, 39), "BAJO", !highArc ? gold : blue)) { highArc = false; if (mouseOwnsAim) UpdateMouseAim(); }
            if (Button(new Rect(913, 654, 81, 39), "ALTO", highArc ? gold : blue)) { highArc = true; if (mouseOwnsAim) UpdateMouseAim(); }
            GUI.enabled = Playing && focus > 0;
            if (Button(new Rect(1021, 640, 231, 51), "FOCO  " + focus, gold, "Calcular un tiro")) Focus();
            GUI.enabled = true;

            if (Playing && mouseOwnsAim)
            {
                Vector3 p = cam.WorldToViewportPoint(aimPoint);
                float x = p.x * 1280, y = (1 - p.y) * 720;
                if (y > 105 && y < 600)
                {
                    Color color = aimReachable ? gold : coral;
                    Panel(new Rect(x - 13, y - 1, 8, 2), color); Panel(new Rect(x + 5, y - 1, 8, 2), color);
                    Panel(new Rect(x - 1, y - 13, 2, 8), color); Panel(new Rect(x - 1, y + 5, 2, 8), color);
                }
            }
            if (state != Mode.Play) DrawResult();
            if (!string.IsNullOrEmpty(GUI.tooltip))
                Type(new Rect(925, 588, 315, 24), GUI.tooltip, 19, Color.white, assets.bodyFont, TextAnchor.MiddleRight, true);
        }

        private void DrawResult()
        {
            Panel(new Rect(0, 99, 1280, 512), new Color(0.025f, 0.015f, 0.055f, 0.92f));
            string heading = state == Mode.Paused ? "PAUSA" : state == Mode.Failed ? "SEÑAL PERDIDA" : state == Mode.Complete ? "YOU WIN!" : "ROUND CLEAR!";
            Arcade(new Rect(130, 149, 1020, 90), heading, 76, state == Mode.Failed ? coral : gold, TextAnchor.MiddleCenter, coral);
            string body = state == Mode.Paused ? "La ciudad puede esperar un momento." : state == Mode.Failed ? failure
                : state == Mode.Complete ? "FIN DE CAMPAÑA · 5 DE 5 ASALTOS\nUrien ha caído. La señal vuelve y la evacuación está a salvo."
                : "Azotea despejada. El siguiente enlace ya está localizado.";
            Type(new Rect(230, 258, 820, 80), body, 27, Color.white, assets.bodyFont, TextAnchor.MiddleCenter);
            if (state == Mode.Clear || state == Mode.Complete)
            {
                Arcade(new Rect(200, 350, 880, 54), "RANGO " + (stars == 3 ? "S" : stars == 2 ? "A" : "B") + "    " + Score + " PUNTOS", 43, gold, TextAnchor.MiddleCenter);
                Type(new Rect(210, 410, 860, 29), hits + " ACIERTOS   ·   " + shots + " DISPAROS   ·   " + Ammo + " DE ENERGÍA RESTANTE", 23, Color.white, assets.numberFont, TextAnchor.MiddleCenter);
            }
            if (state == Mode.Paused)
            {
                Type(new Rect(305, 360, 195, 30), "VOLUMEN", 24, gold, assets.numberFont);
                volume = GUI.HorizontalSlider(new Rect(485, 374, 320, 22), volume, 0, 1); music.volume = volume * 0.3f;
                if (Button(new Rect(450, 420, 380, 46), "VOLVER AL COMBATE", gold)) { PlayerPrefs.SetFloat("NeonSiege.Volume", volume); TogglePause(); }
                if (Button(new Rect(450, 476, 380, 40), "VOLVER AL TÍTULO", blue)) { Time.timeScale = 1; Score = 0; ClearMission(); state = Mode.Title; music.UnPause(); }
                if (Button(new Rect(450, 526, 380, 40), "VOLVER AL MENÚ PRINCIPAL", coral)) { Time.timeScale = 1; SceneManager.LoadScene("MainMenu_Scene"); }
            }
            else
            {
                if (Button(new Rect(450, 465, 380, 50), state == Mode.Clear ? "SIGUIENTE ROUND" : state == Mode.Complete ? "FINALIZAR CAMPAÑA" : "REINTENTAR", gold))
                {
                    if (state == Mode.Clear) { Mission++; state = Mode.Briefing; ClearMission(); }
                    else if (state == Mode.Complete) ExitCompletedCampaign();
                    else Retry();
                }

                if (state == Mode.Failed || state == Mode.Complete)
                {
                    if (Button(new Rect(450, 525, 380, 40), "VOLVER AL MENÚ PRINCIPAL", blue))
                    {
                        Time.timeScale = 1;
                        SceneManager.LoadScene("MainMenu_Scene");
                    }
                }
            }
        }

        private void LifeBar(Rect rect, float fraction, bool reverse)
        {
            Panel(new Rect(rect.x - 2, rect.y - 2, rect.width + 4, rect.height + 4), Color.black);
            Panel(rect, new Color(0.4f, 0.08f, 0.09f));
            Rect fill = rect; fill.width *= Mathf.Clamp01(fraction);
            if (reverse) fill.x = rect.xMax - fill.width;
            Panel(fill, new Color(0.98f, 0.55f, 0.08f));
            fill.height = rect.height * 0.55f; Panel(fill, gold);
            Panel(new Rect(rect.x, rect.y, rect.width, 2), new Color(1, 0.95f, 0.6f));
            for (int i = 1; i < 4; i++) Panel(new Rect(rect.x + rect.width * i / 4, rect.y, 1, rect.height), new Color(0.1f, 0.06f, 0.05f, 0.5f));
        }

        private void Type(Rect rect, string value, int size, Color color, Font face, TextAnchor alignment = TextAnchor.UpperLeft, bool shadow = false)
        {
            text.font = face; text.fontSize = size; text.fontStyle = FontStyle.Normal; text.alignment = alignment;
            if (shadow) { text.normal.textColor = Color.black; GUI.Label(new Rect(rect.x + 2, rect.y + 2, rect.width, rect.height), value, text); }
            text.normal.textColor = color; GUI.Label(rect, value, text);
        }

        private void Arcade(Rect rect, string value, int size, Color color, TextAnchor alignment = TextAnchor.UpperLeft, Color? shadow = null)
        {
            text.font = assets.displayFont; text.fontSize = size; text.fontStyle = FontStyle.Normal; text.alignment = alignment;
            text.normal.textColor = shadow ?? Color.black;
            GUI.Label(new Rect(rect.x + 4, rect.y + 5, rect.width, rect.height), value, text);
            text.normal.textColor = Color.black;
            foreach (Vector2 offset in new[] { Vector2.left, Vector2.right, Vector2.up, Vector2.down })
                GUI.Label(new Rect(rect.x + offset.x * 2, rect.y + offset.y * 2, rect.width, rect.height), value, text);
            text.normal.textColor = color; GUI.Label(rect, value, text);
        }

        private void Slant(Rect rect, Color color) { GUI.color = color; GUI.DrawTexture(rect, buttonTexture); GUI.color = Color.white; }
        private bool Button(Rect rect, string value, Color color, string tooltip = "")
        {
            bool hover = rect.Contains(Event.current.mousePosition);
            Slant(new Rect(rect.x + 3, rect.y + 4, rect.width, rect.height), Color.black);
            Slant(rect, hover && GUI.enabled ? Color.Lerp(color, Color.white, 0.2f) : color);
            Type(new Rect(rect.x + 5, rect.y - 1, rect.width - 10, rect.height), value, rect.height < 32 ? 22 : 27, color == gold ? ink : Color.white, assets.numberFont, TextAnchor.MiddleCenter);
            return GUI.Button(rect, new GUIContent("", tooltip), button);
        }

        private static void Panel(Rect rect, Color color) { GUI.color = color; GUI.DrawTexture(rect, Texture2D.whiteTexture); GUI.color = Color.white; }
    }
}
