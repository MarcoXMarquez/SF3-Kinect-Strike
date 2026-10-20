using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace SF3.NeonSiege.Editor
{
    public static class NeonSiegeBuilder
    {
        public const string Root = "Assets/StreetFighter3_ThirdStrike/Minigames/NeonSiege";
        public const string ScenePath = Root + "/NeonSiege.unity";
        private const string Source = "Assets/StreetFighter3_ThirdStrike/";
        private static NeonSiegeAssets data;

        [MenuItem("SF3 Tools/Neon Siege/Build Scene and Assets")]
        public static void Build()
        {
            AssetDatabase.Refresh();
            data = AssetDatabase.LoadAssetAtPath<NeonSiegeAssets>(Root + "/NeonSiegeAssets.asset");
            if (data == null)
            {
                data = ScriptableObject.CreateInstance<NeonSiegeAssets>();
                AssetDatabase.CreateAsset(data, Root + "/NeonSiegeAssets.asset");
            }
            foreach (var old in AssetDatabase.LoadAllAssetsAtPath(Root + "/NeonSiegeAssets.asset").OfType<Sprite>()) UnityEngine.Object.DestroyImmediate(old, true);
            data.background = SpriteAt(Source + "Stages/HongKong_Yun_Yang/yang-bg-layer1.png");
            data.spriteMaterial = AssetDatabase.LoadAssetAtPath<Material>(Source + "Materials/Stage_ChromaKey.mat");
            data.ryuIdle = Frames("Characters/02_Ryu/01_Movement/idle_stance");
            data.ryuCast = Frames("Characters/02_Ryu/03_Specials_Supers/fireball");
            data.ryuWin = Frames("Characters/02_Ryu/06_Intros_Victories/victory_pose_1");
            data.urienIdle = Frames("Characters/13_Urien/01_Movement/idle_stance");
            data.urienCast = Frames("Characters/13_Urien/03_Specials_Supers/metallicsphere");
            data.urienHit = Frames("Characters/13_Urien/04_Defense_Hit/hit_standing");
            data.remyIdle = Frames("Characters/20_Remy/01_Movement/idle_stance");
            data.remyCast = Frames("Characters/20_Remy/03_Specials_Supers/sonicboom");
            data.remyHit = Frames("Characters/20_Remy/04_Defense_Hit/hit_standing");
            data.displayFont = AssetDatabase.LoadAssetAtPath<Font>(Root + "/Fonts/Bangers-Regular.ttf");
            data.numberFont = AssetDatabase.LoadAssetAtPath<Font>(Root + "/Fonts/BarlowCondensed-BlackItalic.ttf");
            data.bodyFont = AssetDatabase.LoadAssetAtPath<Font>(Root + "/Fonts/Rajdhani-SemiBold.ttf");
            if (data.displayFont == null || data.numberFont == null || data.bodyFont == null) throw new Exception("Arcade fonts missing");
            data.blueShot = Frames("Effects/13_Hadouken_Energy_Aura_Blue");
            data.darkShot = Frames("Effects/14_Dark_Hadou_Aura_Purple");
            data.impact = Frames("Effects/08_Impact_Point_Burst");
            data.seal = Frames("Effects/13_Hadouken_Energy_Aura_Blue");
            data.music = Load<AudioClip>("Audio/BGM/04_China_Vox_ChunLi_Stage.mp3");
            data.cast = Load<AudioClip>("Audio/Voices/02_Ryu/02_Special_Hadouken.wav");
            data.hit = Load<AudioClip>("Audio/SFX/01_Combat_Hits/Hit_Impact_Fierce.wav");
            data.block = Load<AudioClip>("Audio/SFX/02_Defense_and_Parry/Guard_Block_Heavy.wav");
            data.win = Load<AudioClip>("Audio/SFX/03_Super_Arts_and_EX/EX_Special_Move_Chime.wav");
            EditorUtility.SetDirty(data);
            AssetDatabase.SaveAssets();
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var cameraRoot = new GameObject("Neon Siege / Game Camera");
            var camera = cameraRoot.AddComponent<Camera>();
            camera.orthographic = true; camera.orthographicSize = 5.625f;
            camera.transform.position = new Vector3(0, 0, -10);
            cameraRoot.tag = "MainCamera";
            cameraRoot.AddComponent<AudioListener>();
            cameraRoot.AddComponent<NeonSiegeGame>().assets = data;
            EditorSceneManager.SaveScene(scene, ScenePath);
            Debug.Log("NEON SIEGE BUILD PASS: scene, trimmed sprite catalog and audio ready.");
        }

        private static T Load<T>(string path) where T : UnityEngine.Object
        {
            T resource = AssetDatabase.LoadAssetAtPath<T>(Source + path);
            if (resource == null) throw new FileNotFoundException("Neon Siege resource missing: " + path);
            return resource;
        }

        private static Sprite SpriteAt(string path)
        {
            Sprite sprite = AssetDatabase.LoadAllAssetsAtPath(path).OfType<Sprite>().FirstOrDefault();
            if (sprite == null) throw new FileNotFoundException("Sprite missing: " + path);
            return sprite;
        }

        private static Sprite[] Frames(string folder)
        {
            string full = Source + folder;
            if (!Directory.Exists(full)) throw new DirectoryNotFoundException(full);
            var files = Directory.GetFiles(full, "*.png").OrderBy(path => int.TryParse(Path.GetFileNameWithoutExtension(path), out int number) ? number : int.MaxValue).ThenBy(path => path).ToArray();
            if (files.Length == 0) throw new Exception("Empty sprite sequence: " + full);
            Sprite[] frames = files.Select(path => Trim(path.Replace('\\', '/'))).Where(sprite => sprite != null).ToArray();
            if (frames.Length == 0) throw new Exception("No visible frames in " + full);
            return frames;
        }

        private static Sprite Trim(string path)
        {
            Sprite original = SpriteAt(path);
            var readable = new Texture2D(2, 2, TextureFormat.RGBA32, false);
            ImageConversion.LoadImage(readable, File.ReadAllBytes(path));
            Color32[] pixels = readable.GetPixels32();
            int minX = readable.width, minY = readable.height, maxX = 0, maxY = 0;
            for (int y = 0; y < readable.height; y++) for (int x = 0; x < readable.width; x++)
            {
                Color32 color = pixels[y * readable.width + x];
                if (color.a < 32 || (color.r > 220 && color.b > 220 && color.g < 40)) continue;
                minX = Mathf.Min(minX, x); minY = Mathf.Min(minY, y); maxX = Mathf.Max(maxX, x); maxY = Mathf.Max(maxY, y);
            }
            if (minX > maxX) { UnityEngine.Object.DestroyImmediate(readable); return null; }
            float sx = original.texture.width / (float)readable.width, sy = original.texture.height / (float)readable.height;
            var rect = new Rect(minX * sx, minY * sy, (maxX - minX + 1) * sx, (maxY - minY + 1) * sy);
            Sprite cropped = Sprite.Create(original.texture, rect, new Vector2(0.5f, 0), 100, 0, SpriteMeshType.FullRect);
            cropped.name = path.Substring(Source.Length).Replace('/', '_').Replace(".png", "");
            AssetDatabase.AddObjectToAsset(cropped, data);
            UnityEngine.Object.DestroyImmediate(readable);
            return cropped;
        }

        [MenuItem("SF3 Tools/Neon Siege/Build Windows Player")]
        public static void BuildWindows()
        {
            if (!File.Exists(ScenePath)) Build();
            Directory.CreateDirectory("Builds/NeonSiege_Arcade");
            string previousName = PlayerSettings.productName;
            try
            {
                PlayerSettings.productName = "Neon Siege";
                var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                    scenes = new[] { ScenePath }, locationPathName = "Builds/NeonSiege_Arcade/NeonSiege.exe",
                    target = BuildTarget.StandaloneWindows64, options = BuildOptions.None
                });
                if (report.summary.result != UnityEditor.Build.Reporting.BuildResult.Succeeded) throw new Exception("Neon Siege Windows build failed");
            }
            finally { PlayerSettings.productName = previousName; }
            Debug.Log("NEON SIEGE WINDOWS BUILD PASS");
        }
    }
}
