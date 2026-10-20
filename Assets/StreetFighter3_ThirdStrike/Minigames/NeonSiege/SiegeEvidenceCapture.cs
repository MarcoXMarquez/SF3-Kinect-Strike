using System;
using System.Collections;
using System.IO;
using UnityEngine;

namespace SF3.NeonSiege
{
    // Explicit rendering check; never attached without the evidence command flag.
    public sealed class SiegeEvidenceCapture : MonoBehaviour
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Install()
        {
            if (Array.IndexOf(Environment.GetCommandLineArgs(), "--neon-siege-evidence") < 0) return;
            if (Application.isBatchMode) { Debug.LogError("Evidence requires a rendered player window."); Application.Quit(2); return; }
            new GameObject("Neon Siege rendering verification").AddComponent<SiegeEvidenceCapture>();
        }

        private IEnumerator Start()
        {
            Screen.SetResolution(1280, 720, FullScreenMode.Windowed);
            Application.runInBackground = true;
            AudioListener.volume = 0;
            string folder = Path.Combine(Application.dataPath, "..", "Evidence");
            Directory.CreateDirectory(folder);
            yield return new WaitForSeconds(0.6f);
            var game = FindFirstObjectByType<NeonSiegeGame>();
            if (game == null) { Application.Quit(1); yield break; }
            ScreenCapture.CaptureScreenshot(Path.Combine(folder, "01_title.png"));
            yield return new WaitForSeconds(0.4f);
            game.BeginMission(2);
            yield return new WaitForSeconds(0.2f);
            ScreenCapture.CaptureScreenshot(Path.Combine(folder, "02_cover_mission.png"));
            yield return new WaitForSeconds(0.3f);
            game.BeginMission(4);
            yield return new WaitForSeconds(0.2f);
            ScreenCapture.CaptureScreenshot(Path.Combine(folder, "03_urien.png"));
            yield return new WaitForSeconds(0.3f);
            game.Launch(SiegeBallistics.Velocity(40, 12));
            yield return new WaitForSeconds(0.2f);
            ScreenCapture.CaptureScreenshot(Path.Combine(folder, "04_energy_projectile.png"));
            yield return new WaitForSeconds(0.3f);
            game.TogglePause();
            yield return new WaitForSecondsRealtime(0.2f);
            ScreenCapture.CaptureScreenshot(Path.Combine(folder, "05_pause.png"));
            yield return new WaitForSecondsRealtime(0.5f);
            game.TogglePause();
            foreach (var target in game.Targets)
            {
                target.shieldPeriod = 0;
                while (target.Alive) target.Hit(target.transform.position);
            }
            yield return new WaitForSecondsRealtime(0.5f);
            ScreenCapture.CaptureScreenshot(Path.Combine(folder, "06_campaign_complete.png"));
            yield return new WaitForSecondsRealtime(0.5f);
            Debug.Log("NEON SIEGE RENDER CAPTURE PASS: " + folder);
            Application.Quit(0);
        }
    }
}
