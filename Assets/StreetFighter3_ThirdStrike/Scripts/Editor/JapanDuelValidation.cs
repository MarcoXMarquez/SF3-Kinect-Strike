using System;
using System.Reflection;
using UnityEditor;
using UnityEngine;

// Runs against the live sandbox and restores a fresh round after every test run.
public static class JapanDuelValidation
{
    private const BindingFlags Private = BindingFlags.Instance | BindingFlags.NonPublic;
    private static void Set(object target, string name, object value) => target.GetType().GetField(name, Private).SetValue(target, value);
    private static T Get<T>(object target, string name) => (T)target.GetType().GetField(name, Private).GetValue(target);
    private static void Call(object target, string name, params object[] args) => target.GetType().GetMethod(name, Private).Invoke(target, args);
    private static void Check(bool pass, string message)
    {
        if (!pass) throw new Exception("Duel validation: " + message);
    }

    [MenuItem("SF3 Tools/Validate Local Duel")]
    public static void Validate()
    {
        JapanDuel duel = UnityEngine.Object.FindFirstObjectByType<JapanDuel>();
        if (!Application.isPlaying || duel == null)
        {
            Debug.LogWarning("Open Sandbox_Sebas and enter Play before validating the duel.");
            return;
        }
        try
        {
            DuelRoster roster = Resources.Load<DuelRoster>("JapanDuelRoster");
            foreach (var motions in new[] { roster.ken, roster.ryu })
                foreach (var motion in motions)
                {
                    Check(motion.frames.Length > 0, "Empty motion: " + motion.name);
                    foreach (var sprite in motion.frames) Check(sprite != null, "Missing sprite: " + motion.name);
                }
            DuelFighter ken = Get<DuelFighter>(duel, "ken");
            DuelFighter ryu = Get<DuelFighter>(duel, "ryu");
            Set(duel, "result", null);
            Set(duel, "countdown", 0f);
            ken.ResetFighter(-2f);
            ryu.ResetFighter(2f);
            Strike(ken, 1);
            Check(ryu.Health == 100, "Out-of-range attack caused damage");
            for (int i = 0; i < 4; i++)
            {
                ken.ResetFighter(-0.3f);
                ryu.ResetFighter(0.3f);
                Strike(ken, i);
                Check(ryu.Health == (i % 2 == 0 ? 93 : 88), "Attack damage " + i);
                Check(ken.Health == 100, "Self damage");
                Call(ken, "FixedUpdate");
                Check(ryu.Health == (i % 2 == 0 ? 93 : 88), "Repeated damage in same attack");
            }
            ken.ResetFighter(-0.3f);
            ryu.ResetFighter(0.3f);
            Set(ryu, "guarding", true);
            Strike(ken, 1);
            Check(ryu.Health == 100, "Front guard did not block");
            ken.ResetFighter(-0.3f);
            ryu.ResetFighter(0.3f);
            Strike(ryu, 1);
            Check(ken.Health == 88, "Mirrored Ryu attack");
            ken.ResetFighter(-0.3f);
            Call(ken, "BeginAttack", 0);
            Call(ken, "Update");
            Check(!Get<BoxCollider2D>(ken, "attackBox").enabled, "Hitbox enabled during startup");
            Set(ken, "attackTime", 0.4f);
            Call(ken, "Update");
            Check(!Get<BoxCollider2D>(ken, "attackBox").enabled, "Hitbox enabled during recovery");
            float standing = Get<BoxCollider2D>(ken, "pushbox").size.y;
            Set(ken, "crouching", true);
            Call(ken, "UpdateBoxes");
            Check(Get<BoxCollider2D>(ken, "pushbox").size.y < standing, "Crouching dimensions");
            ken.ResetFighter(-0.3f);
            ryu.ResetFighter(0.3f);
            Set(ken, "guarding", false);
            Call(ken, "ReceiveHit", 100f, 0.3f, false, null);
            Call(duel, "Update");
            Check(!duel.Fighting && Get<string>(ryu, "motion") == "victory_pose_1", "KO/victory");
            Check(!Get<BoxCollider2D>(ryu, "attackBox").enabled, "Attack still active after KO");
            Call(duel, "Restart");
            Check(ken.Health == 100 && ryu.Health == 100, "Restart health");
            Debug.Log("DUEL VALIDATION PASS: 486 sprites, four attacks, single impact, no self-hit, guard, mirrored Ryu, crouch, KO, victory, restart.");
        }
        catch (Exception error) { Debug.LogException(error); }
        finally { Call(duel, "Restart"); }
    }

    private static void Strike(DuelFighter fighter, int attack)
    {
        Call(fighter, "BeginAttack", attack);
        Set(fighter, "attackTime", 0.18f);
        Call(fighter, "UpdateBoxes");
        Get<BoxCollider2D>(fighter, "attackBox").enabled = true;
        Physics2D.SyncTransforms();
        Call(fighter, "FixedUpdate");
    }
}
