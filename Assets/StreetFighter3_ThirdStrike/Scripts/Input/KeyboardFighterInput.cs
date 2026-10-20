using UnityEngine;

/// <summary>
/// Adaptador de teclado para el sistema de entrada de KINET STRIKE.
/// Permite jugar y testear el combate para 2 Jugadores separados sin requerir hardware físico de Kinect.
/// </summary>
public class KeyboardFighterInput : MonoBehaviour, IFighterInput
{
    [Header("Configuración de Jugador")]
    [Tooltip("Falso = Jugador 1 (WASD). Verdadero = Jugador 2 (Flechas).")]
    [SerializeField] private bool isPlayer2 = false;

    [Header("Teclas de Movimiento y Guardia P1")]
    [SerializeField] private KeyCode crouchKeyP1 = KeyCode.S;
    [SerializeField] private KeyCode jumpKeyP1 = KeyCode.W;
    [SerializeField] private KeyCode leftKeyP1 = KeyCode.A;
    [SerializeField] private KeyCode rightKeyP1 = KeyCode.D;
    [SerializeField] private KeyCode blockKeyP1 = KeyCode.P;

    [Header("Teclas de Movimiento y Guardia P2")]
    [SerializeField] private KeyCode crouchKeyP2 = KeyCode.DownArrow;
    [SerializeField] private KeyCode jumpKeyP2 = KeyCode.UpArrow;
    [SerializeField] private KeyCode leftKeyP2 = KeyCode.LeftArrow;
    [SerializeField] private KeyCode rightKeyP2 = KeyCode.RightArrow;
    [SerializeField] private KeyCode blockKeyP2 = KeyCode.RightShift;

    [Header("Teclas de Ataque P1")]
    [SerializeField] private KeyCode lightPunchP1 = KeyCode.J;
    [SerializeField] private KeyCode heavyPunchP1 = KeyCode.K;
    [SerializeField] private KeyCode lightKickP1 = KeyCode.L;
    [SerializeField] private KeyCode heavyKickP1 = KeyCode.O;
    [SerializeField] private KeyCode hadoukenKeyP1 = KeyCode.U;
    [SerializeField] private KeyCode shoryukenKeyP1 = KeyCode.I;
    [SerializeField] private KeyCode parryKeyP1 = KeyCode.Space;

    [Header("Teclas de Ataque P2")]
    [SerializeField] private KeyCode lightPunchP2 = KeyCode.Keypad1;
    [SerializeField] private KeyCode heavyPunchP2 = KeyCode.Keypad2;
    [SerializeField] private KeyCode lightKickP2 = KeyCode.Keypad4;
    [SerializeField] private KeyCode heavyKickP2 = KeyCode.Keypad5;
    [SerializeField] private KeyCode hadoukenKeyP2 = KeyCode.Keypad7;
    [SerializeField] private KeyCode shoryukenKeyP2 = KeyCode.Keypad8;
    [SerializeField] private KeyCode parryKeyP2 = KeyCode.Keypad0;

    private void Awake()
    {
        if (!isPlayer2 && (CompareTag("Enemy") || gameObject.name.ToLower().Contains("opponent") || transform.position.x > 0.5f))
        {
            isPlayer2 = true;
        }
    }

    public float GetHorizontalAxis()
    {
        if (!isPlayer2)
        {
            return (Input.GetKey(rightKeyP1) ? 1f : 0f) - (Input.GetKey(leftKeyP1) ? 1f : 0f);
        }
        else
        {
            return (Input.GetKey(rightKeyP2) ? 1f : 0f) - (Input.GetKey(leftKeyP2) ? 1f : 0f);
        }
    }

    public float GetHorizontalMove()
    {
        return GetHorizontalAxis();
    }

    public bool IsCrouching()
    {
        return !isPlayer2 ? Input.GetKey(crouchKeyP1) : Input.GetKey(crouchKeyP2);
    }

    public bool IsJumping()
    {
        return !isPlayer2 ? Input.GetKeyDown(jumpKeyP1) : Input.GetKeyDown(jumpKeyP2);
    }

    public bool IsBlocking()
    {
        return !isPlayer2 ? Input.GetKey(blockKeyP1) : (Input.GetKey(blockKeyP2) || Input.GetKey(KeyCode.RightControl));
    }

    public bool WasLightPunchPressed()
    {
        return !isPlayer2 ? Input.GetKeyDown(lightPunchP1) : (Input.GetKeyDown(lightPunchP2) || Input.GetKeyDown(KeyCode.B));
    }

    public bool WasHeavyPunchPressed()
    {
        return !isPlayer2 ? Input.GetKeyDown(heavyPunchP1) : (Input.GetKeyDown(heavyPunchP2) || Input.GetKeyDown(KeyCode.N));
    }

    public bool WasLightKickPressed()
    {
        return !isPlayer2 ? Input.GetKeyDown(lightKickP1) : (Input.GetKeyDown(lightKickP2) || Input.GetKeyDown(KeyCode.M));
    }

    public bool WasHeavyKickPressed()
    {
        return !isPlayer2 ? Input.GetKeyDown(heavyKickP1) : (Input.GetKeyDown(heavyKickP2) || Input.GetKeyDown(KeyCode.Comma));
    }

    public bool WasHadoukenGestureDetected()
    {
        return !isPlayer2 ? Input.GetKeyDown(hadoukenKeyP1) : (Input.GetKeyDown(hadoukenKeyP2) || Input.GetKeyDown(KeyCode.Period));
    }

    public bool WasShoryukenGestureDetected()
    {
        return !isPlayer2 ? Input.GetKeyDown(shoryukenKeyP1) : (Input.GetKeyDown(shoryukenKeyP2) || Input.GetKeyDown(KeyCode.Slash));
    }

    public bool WasParryStanceDetected()
    {
        return !isPlayer2 ? Input.GetKeyDown(parryKeyP1) : (Input.GetKeyDown(parryKeyP2) || Input.GetKeyDown(KeyCode.Keypad0));
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
