using System;
using UnityEngine;

public class DuelRoster : ScriptableObject
{
    [Serializable]
    public class Motion
    {
        public string name;
        public Sprite[] frames;
    }

    public Motion[] ken;
    public Motion[] ryu;
}
