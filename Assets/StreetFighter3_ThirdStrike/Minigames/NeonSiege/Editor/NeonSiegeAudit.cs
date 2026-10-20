using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace SF3.NeonSiege.Editor
{
    [InitializeOnLoad]
    public static class NeonSiegeAudit
    {
        [Serializable] private sealed class Report
        {
            public bool passed;
            public float physicsError;
            public string failure;
            public List<string> missions = new List<string>();
            public int shots;
            public int hits;
            public bool pause, retry, shotLock, defeat;
            public bool cursorAim, spanishFonts;
            public bool campaignEnding, enemyFacing, namesAboveSprites;
            public int levelThreePhaseCases;
            public List<string> levelThreeRoutes = new List<string>();
        }
        private static NeonSiegeGame game;
        private static Report report;
        private static double began, nextAction;
        private static bool initialized;
        private static int lastHealth;
        private static readonly string Output = "Builds/NeonSiegeAudit.json";

        static NeonSiegeAudit()
        {
            EditorApplication.playModeStateChanged += Changed;
        }

        public static void BuildAndValidate()
        {
            NeonSiegeBuilder.Build();
            SessionState.SetBool("NeonSiege.Audit", true);
            EditorApplication.isPlaying = true;
        }

        public static void BuildValidateRelease()
        {
            SessionState.SetBool("NeonSiege.BuildRelease", true);
            BuildAndValidate();
        }

        [MenuItem("SF3 Tools/Neon Siege/Validate Campaign in Play")]
        public static void ValidatePlay()
        {
            if (!EditorApplication.isPlaying) { Debug.LogWarning("Enter Play in NeonSiege first."); return; }
            Begin();
        }

        private static void Changed(PlayModeStateChange change)
        {
            if (change == PlayModeStateChange.EnteredPlayMode && SessionState.GetBool("NeonSiege.Audit", false))
                EditorApplication.delayCall += Begin;
        }

        private static void Begin()
        {
            game = UnityEngine.Object.FindFirstObjectByType<NeonSiegeGame>();
            report = new Report(); initialized = false;
            began = EditorApplication.timeSinceStartup;
            EditorApplication.update -= Tick;
            EditorApplication.update += Tick;
        }

        private static void Require(bool condition, string message) { if (!condition) throw new Exception(message); }

        private static void Tick()
        {
            try
            {
                if (game == null || game.Assets == null) return;
                if (!initialized)
                {
                    if (game.State != NeonSiegeGame.Mode.Title) return;
                    initialized = true;
                    ValidatePhysics();
                    ValidateLevelThree();
                    game.BeginMission(0);
                    game.TogglePause(); Require(game.State == NeonSiegeGame.Mode.Paused && Time.timeScale == 0, "Pause failed");
                    game.TogglePause(); report.pause = true;
                    int ammo = game.Ammo;
                    Require(game.Launch(SiegeBallistics.Velocity(30, 10)), "Initial shot rejected");
                    Require(!game.Launch(SiegeBallistics.Velocity(30, 10)) && game.Ammo == ammo - 1, "Shot lock failed");
                    report.shotLock = true;
                    game.Retry(); Require(game.Ammo == ammo && game.Score == 0, "Retry did not restore round");
                    report.retry = true;
                    for (int i = 0; i < 4; i++) game.TakeDamage();
                    Require(game.State == NeonSiegeGame.Mode.Failed, "Defeat did not stop the mission");
                    game.Retry(); report.defeat = true;
                    lastHealth = game.Targets.Sum(t => t.health);
                    Time.timeScale = 4;
                    nextAction = EditorApplication.timeSinceStartup + 0.5;
                }
                if (EditorApplication.timeSinceStartup - began > 190) throw new Exception("Campaign audit timeout");
                int currentHealth = game.Targets.Sum(t => t.health);
                report.hits += Mathf.Max(0, lastHealth - currentHealth);
                lastHealth = currentHealth;
                if (game.State == NeonSiegeGame.Mode.Failed) throw new Exception("Campaign failed in mission " + (game.Mission + 1) + ", ammo=" + game.Ammo + ", integrity=" + game.Integrity);
                if (game.State == NeonSiegeGame.Mode.Clear || game.State == NeonSiegeGame.Mode.Complete)
                {
                    report.missions.Add("Mission " + (game.Mission + 1) + ": all targets defeated, score=" + game.Score + ", ammo=" + game.Ammo + ", integrity=" + game.Integrity);
                    if (game.State == NeonSiegeGame.Mode.Complete)
                    {
                        int finalScore = game.Score;
                        game.Retry();
                        game.TogglePause();
                        game.TakeDamage();
                        Require(game.Mission == 4 && game.State == NeonSiegeGame.Mode.Complete && !game.Playing && game.Score == finalScore, "Final campaign state was restarted or changed");
                        Require(!game.Launch(SiegeBallistics.Velocity(30, 14)), "Shot accepted after campaign ending");
                        report.campaignEnding = true;
                        Finish(true, null); return;
                    }
                    game.BeginMission(game.Mission + 1); Time.timeScale = 4;
                    lastHealth = game.Targets.Sum(t => t.health);
                    nextAction = EditorApplication.timeSinceStartup + 0.2;
                }
                if (EditorApplication.timeSinceStartup < nextAction || !game.Playing) return;
                foreach (var target in game.Targets.Where(t => t.Alive))
                {
                    Require(target.FacingRyu, "Enemy is not facing Ryu: " + target.callsign);
                    var visual = target.GetComponentInChildren<SiegeActor>().Renderer;
                    Require(target.NameAnchor.y > visual.bounds.max.y + 0.2f, "Enemy name overlaps sprite");
                }
                report.enemyFacing = report.namesAboveSprites = true;
                nextAction = EditorApplication.timeSinceStartup + 0.035;
                foreach (var target in game.Targets.Where(t => t.Alive).OrderByDescending(t => t.boss))
                {
                    if (!game.FindSolution(target, out Vector2 velocity, out _)) continue;
                    if (game.Launch(velocity)) report.shots++;
                    break;
                }
            }
            catch (Exception error) { Finish(false, error.ToString()); }
        }

        private static void ValidatePhysics()
        {
            Require(Mathf.Abs(Physics2D.gravity.y - SiegeBallistics.Gravity) < 0.001f && Mathf.Abs(Time.fixedDeltaTime - 0.02f) < 0.001f, "Project physics differs from prediction constants");
            Scene scene = SceneManager.CreateScene("NeonSiege isolated physics test", new CreateSceneParameters(LocalPhysicsMode.Physics2D));
            var root = new GameObject("Prediction reference body");
            SceneManager.MoveGameObjectToScene(root, scene);
            var body = root.AddComponent<Rigidbody2D>(); body.gravityScale = 1; body.linearDamping = 0;
            Vector2 origin = new Vector2(-6.65f, -1.92f), velocity = SiegeBallistics.Velocity(42, 12);
            body.position = origin; body.linearVelocity = velocity;
            for (int i = 0; i < 85; i++) scene.GetPhysicsScene2D().Simulate(0.02f);
            report.physicsError = Vector2.Distance(body.position, SiegeBallistics.Position(origin, velocity, 1.7f));
            Require(report.physicsError < 0.02f, "Prediction drift: " + report.physicsError);
            SceneManager.UnloadSceneAsync(scene);
            foreach (var frames in new[] { game.Assets.ryuIdle, game.Assets.ryuCast, game.Assets.urienIdle, game.Assets.remyIdle, game.Assets.blueShot, game.Assets.darkShot })
                Require(frames.Length > 0 && frames.All(sprite => sprite != null), "Missing animation sprites");
            foreach (var font in new[] { game.Assets.displayFont, game.Assets.numberFont, game.Assets.bodyFont })
                Require(font != null && font.HasCharacter('ñ') && font.HasCharacter('á'), "Font lacks Spanish glyphs");
            report.spanishFonts = true;
        }

        private static void ValidateLevelThree()
        {
            game.BeginMission(2);
            var cursor = new Vector2(4.3f, -0.25f);
            Require(game.AimAtWorld(cursor), "Mouse cannot aim at a reachable point");
            Vector2 velocity = SiegeBallistics.Velocity(game.AimAngle, game.LaunchSpeed);
            float error = float.MaxValue;
            for (int i = 1; i <= 150; i++) error = Mathf.Min(error, Vector2.Distance(cursor, SiegeBallistics.Position(game.Muzzle, velocity, i * 0.02f)));
            Require(error < 0.2f, "Mouse aim misses cursor by " + error);
            report.cursorAim = true;
            foreach (var selected in game.Targets)
            {
                foreach (float phaseTime in new[] { 0f, 0.7f, 1.4f, 2.1f, 2.8f, 3.5f, 4.2f, 4.9f })
                {
                    foreach (var t in game.Targets) t.health = t == selected ? t.maxHealth : 0;
                    float oldPhase = selected.phase;
                    selected.phase += phaseTime * selected.frequency;
                    bool found = false;
                    float foundPower = 0, foundAngle = 0;
                    foreach (float power in new[] { 13.8f, 15f, 16.5f, 18f })
                    {
                        if (found) break;
                        for (int i = 20; i < 145 && !found; i += 2)
                        {
                            foreach (bool high in new[] { false, true })
                            {
                                Vector2 point = selected.PositionAt(i * 0.02f);
                                if (!SiegeBallistics.AimAt(game.Muzzle, point, power, high, out var shot)) continue;
                                if (game.Forecast(shot, out _, out _, out var hit) != 1 || hit != selected) continue;
                                found = true; foundPower = power; foundAngle = Mathf.Atan2(shot.y, shot.x) * Mathf.Rad2Deg; break;
                            }
                        }
                    }
                    selected.phase = oldPhase;
                    Require(found, "Level 3 target unreachable with manual aim, target x=" + selected.origin.x + ", phase time=" + phaseTime);
                    report.levelThreePhaseCases++;
                    report.levelThreeRoutes.Add("x=" + selected.origin.x + ", phase=" + phaseTime + ", speed=" + foundPower + ", angle=" + foundAngle.ToString("F1"));
                }
            }
        }

        private static void Finish(bool success, string error)
        {
            EditorApplication.update -= Tick;
            report.passed = success; report.failure = error;
            Directory.CreateDirectory("Builds");
            File.WriteAllText(Output, JsonUtility.ToJson(report, true));
            SessionState.SetBool("NeonSiege.Audit", false);
            Time.timeScale = 1;
            if (success) Debug.Log("NEON SIEGE CAMPAIGN PASS: all five missions completed with physical projectiles and moving targets. " + Output);
            else Debug.LogError("NEON SIEGE AUDIT FAILED: " + error);
            if (success && SessionState.GetBool("NeonSiege.BuildRelease", false))
            {
                SessionState.SetBool("NeonSiege.BuildRelease", false);
                EditorApplication.isPlaying = false;
                EditorApplication.delayCall += Release;
                return;
            }
            if (Application.isBatchMode) EditorApplication.Exit(success ? 0 : 1);
        }

        private static void Release()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode) { EditorApplication.delayCall += Release; return; }
            try { NeonSiegeBuilder.BuildWindows(); if (Application.isBatchMode) EditorApplication.Exit(0); }
            catch (Exception error) { Debug.LogException(error); if (Application.isBatchMode) EditorApplication.Exit(1); }
        }
    }
}
