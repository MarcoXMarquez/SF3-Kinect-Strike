using UnityEngine;

/// <summary>
/// Adaptador de teclado para el sistema de entrada de Street Fighter III.
/// Permite jugar y testear el movimiento y ataques completos sin requerir hardware físico de Kinect.
/// </summary>
public class KeyboardFighterInput : MonoBehaviour, IFighterInput
{
    [Header("Teclas de Movimiento y Guardia")]
    [SerializeField] private KeyCode crouchKey = KeyCode.S;
    [SerializeField] private KeyCode crouchKeyAlt = KeyCode.DownArrow;
    [SerializeField] private KeyCode jumpKey = KeyCode.W;
    [SerializeField] private KeyCode jumpKeyAlt = KeyCode.UpArrow;
    [SerializeField] private KeyCode blockKey = KeyCode.L;

    [Header("Teclas de Ataque Clásicas")]
    [SerializeField] private KeyCode lightPunchKey = KeyCode.J;
    [SerializeField] private KeyCode heavyPunchKey = KeyCode.U;
    [SerializeField] private KeyCode lightKickKey = KeyCode.K;
    [SerializeField] private KeyCode heavyKickKey = KeyCode.I;

    [Header("Emulación de Gestos Kinect / Especiales")]
    [SerializeField] private KeyCode hadoukenKey = KeyCode.H;
    [SerializeField] private KeyCode shoryukenKey = KeyCode.Y;
    [SerializeField] private KeyCode parryKey = KeyCode.Space;

    public float GetHorizontalAxis()
    {
        return Input.GetAxisRaw("Horizontal");
    }

    public float GetHorizontalMove()
    {
        return GetHorizontalAxis();
    }

    public bool IsCrouching()
    {
        return Input.GetKey(crouchKey) || Input.GetKey(crouchKeyAlt);
    }

    public bool IsJumping()
    {
        return Input.GetKeyDown(jumpKey) || Input.GetKeyDown(jumpKeyAlt);
    }

    public bool IsBlocking()
    {
        return Input.GetKey(blockKey);
    }

    public bool WasLightPunchPressed()
    {
        return Input.GetKeyDown(lightPunchKey);
    }

    public bool WasHeavyPunchPressed()
    {
        return Input.GetKeyDown(heavyPunchKey);
    }

    public bool WasLightKickPressed()
    {
        return Input.GetKeyDown(lightKickKey);
    }

    public bool WasHeavyKickPressed()
    {
        return Input.GetKeyDown(heavyKickKey);
    }

    public bool WasHadoukenGestureDetected()
    {
        return Input.GetKeyDown(hadoukenKey);
    }

    public bool WasShoryukenGestureDetected()
    {
        return Input.GetKeyDown(shoryukenKey);
    }

    public bool WasParryStanceDetected()
    {
        return Input.GetKeyDown(parryKey);
    }

    public bool IsAttacking(out FighterAttackType attackType)
    {
        if (WasHadoukenGestureDetected())
        {
            attackType = FighterAttackType.Hadouken;
            return true;
        }

        if (WasShoryukenGestureDetected())
        {
            attackType = FighterAttackType.Shoryuken;
            return true;
        }

        if (WasHeavyPunchPressed())
        {
            attackType = FighterAttackType.HeavyPunch;
            return true;
        }

        if (WasLightPunchPressed())
        {
            attackType = FighterAttackType.LightPunch;
            return true;
        }

        if (WasHeavyKickPressed())
        {
            attackType = FighterAttackType.HeavyKick;
            return true;
        }

        if (WasLightKickPressed())
        {
            attackType = FighterAttackType.LightKick;
            return true;
        }

        attackType = FighterAttackType.None;
        return false;
    }
}
