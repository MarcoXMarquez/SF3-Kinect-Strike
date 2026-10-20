using UnityEngine;

namespace SF3.NeonSiege
{
    public sealed class NeonSiegeAssets : ScriptableObject
    {
        public Sprite background;
        public Material spriteMaterial;
        public Sprite[] ryuIdle, ryuCast, ryuWin, urienIdle, urienCast, urienHit, remyIdle, remyCast, remyHit;
        public Font displayFont, numberFont, bodyFont;
        public Sprite[] blueShot, darkShot, impact, seal;
        public AudioClip music, cast, hit, block, win;
    }
}
