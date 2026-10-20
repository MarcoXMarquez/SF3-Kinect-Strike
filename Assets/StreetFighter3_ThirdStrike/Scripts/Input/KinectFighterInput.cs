using UnityEngine;

/// <summary>
/// Adaptador de entrada Somatosensorial (Kinect + Machine Learning) para Ryu en el Modo Historia de SF3.
/// Implementa IFighterInput conectándose al flujo UDP de test_live_kinect_classifier.py (puerto 5005),
/// con soporte para Auto-Spacing asistido y modo híbrido con teclado en paralelo (Fallback).
/// </summary>
public class KinectFighterInput : MonoBehaviour, IFighterInput
{
    [Header("Receptor de Telemetría UDP")]
    [SerializeField] private KinectUDPReceiver receiver;

    [Header("Auto-Spacing Asistido (Opción A)")]
    [Tooltip("El luchador ajusta suavemente su posición para mantenerse en rango óptimo de golpe.")]
    [SerializeField] private bool autoSpacingEnabled = true;
    [Tooltip("Transform del oponente (Ken) para calcular la distancia de combate.")]
    [SerializeField] private Transform opponent;
    [SerializeField] private float optimalDistanceMin = 0.90f;
    [SerializeField] private float optimalDistanceMax = 1.45f;

    [Header("Parámetros de Clasificación de Gestos")]
    [Tooltip("Umbral mínimo de certeza del modelo ML para registrar un ataque (20%).")]
    [SerializeField] private float minConfidenceThreshold = 0.20f;
    [Tooltip("Ventana de buffer para evitar spam de ataques durante la misma pose (segundos).")]
    [SerializeField] private float attackCooldownSeconds = 0.28f;

    [Header("HUD de Telemetría Somatosensorial")]
    [SerializeField] private bool showHUD = true;

    // Estados internos y temporizadores de gestos
    private string prevAction = "idle";
    private string lastTriggeredAttack = "";
    private float lastAttackTimestamp = -999f;
    private bool jumpConsumed = false;

    // Caché de teclas de teclado (Fallback híbrido P2 / Ryu)
    private readonly KeyCode[] ryuLightPunchKeys = { KeyCode.Keypad1, KeyCode.Alpha7, KeyCode.B, KeyCode.J };
    private readonly KeyCode[] ryuHeavyPunchKeys = { KeyCode.Keypad2, KeyCode.Alpha8, KeyCode.N, KeyCode.K };
    private readonly KeyCode[] ryuLightKickKeys  = { KeyCode.Keypad4, KeyCode.Alpha9, KeyCode.M, KeyCode.L };
    private readonly KeyCode[] ryuHeavyKickKeys   = { KeyCode.Keypad5, KeyCode.Alpha0, KeyCode.Comma, KeyCode.O };

    private void Awake()
    {
        EnsureReceiver();
    }

    private void Start()
    {
        EnsureReceiver();
        if (opponent == null)
        {
            // Intentar ubicar al oponente automáticamente si no fue asignado
            DuelFighter fighter = GetComponent<DuelFighter>();
            if (fighter != null && fighter.opponent != null)
            {
                opponent = fighter.opponent.transform;
            }
        }
    }

    public void SetOpponent(Transform targetOpponent)
    {
        opponent = targetOpponent;
    }

    public void SetAutoSpacing(bool enabled)
    {
        autoSpacingEnabled = enabled;
    }

    private void EnsureReceiver()
    {
        if (receiver == null)
        {
            receiver = KinectUDPReceiver.Instance;
            if (receiver == null)
            {
                receiver = FindFirstObjectByType<KinectUDPReceiver>();
                if (receiver == null)
                {
                    GameObject rxObj = new GameObject("[KinectUDPReceiver_Auto]");
                    receiver = rxObj.AddComponent<KinectUDPReceiver>();
                }
            }
        }
    }

    private void Update()
    {
        // Alternar visualización del HUD con [F1]
        if (Input.GetKeyDown(KeyCode.F1))
        {
            showHUD = !showHUD;
        }

        // Alternar Auto-Spacing con [F2]
        if (Input.GetKeyDown(KeyCode.F2))
        {
            autoSpacingEnabled = !autoSpacingEnabled;
        }

        // Reset del flag de salto cuando la acción ya no sea jump
        if (receiver != null && receiver.CurrentAction != "jump")
        {
            jumpConsumed = false;
        }

        if (receiver != null)
        {
            prevAction = receiver.CurrentAction;
        }
    }

    #region Implementación de IFighterInput

    public float GetHorizontalAxis()
    {
        // 1. Prioridad: Teclado Fallback manual (Flechas o WASD)
        bool kbdRight = Input.GetKey(KeyCode.RightArrow) || Input.GetKey(KeyCode.D);
        bool kbdLeft  = Input.GetKey(KeyCode.LeftArrow)  || Input.GetKey(KeyCode.A);
        if (kbdRight || kbdLeft)
        {
            return (kbdRight ? 1f : 0f) - (kbdLeft ? 1f : 0f);
        }

        // 2. Auto-Spacing Asistido (Opción A)
        if (autoSpacingEnabled && opponent != null)
        {
            // Si el jugador está agachado o bloqueando, se queda firme en su postura
            if (IsCrouching() || IsBlocking())
            {
                return 0f;
            }

            float dx = opponent.position.x - transform.position.x;
            float absDist = Mathf.Abs(dx);
            float dir = Mathf.Sign(dx);

            if (absDist > optimalDistanceMax)
            {
                return dir * 1.0f; // Avanzar suavemente hacia el oponente
            }
            if (absDist < optimalDistanceMin)
            {
                return -dir * 1.0f; // Retroceder ligeramente para recuperar distancia de guardia
            }
            return 0f; // En distancia óptima de golpe
        }

        return 0f;
    }

    public float GetHorizontalMove()
    {
        return GetHorizontalAxis();
    }

    public bool IsCrouching()
    {
        bool kinectCrouch = (receiver != null && receiver.IsConnected && receiver.HasBody &&
                             receiver.CurrentAction == "crouch" && receiver.CurrentConfidence >= minConfidenceThreshold);

        bool kbdCrouch = Input.GetKey(KeyCode.DownArrow) || Input.GetKey(KeyCode.S);
        return kinectCrouch || kbdCrouch;
    }

    public bool IsJumping()
    {
        bool kinectJump = false;
        if (receiver != null && receiver.IsConnected && receiver.HasBody &&
            receiver.CurrentAction == "jump" && receiver.CurrentConfidence >= minConfidenceThreshold)
        {
            if (!jumpConsumed)
            {
                kinectJump = true;
                jumpConsumed = true;
            }
        }

        bool kbdJump = Input.GetKeyDown(KeyCode.UpArrow) || Input.GetKeyDown(KeyCode.W);
        return kinectJump || kbdJump;
    }

    public bool IsBlocking()
    {
        bool kinectBlock = (receiver != null && receiver.IsConnected && receiver.HasBody &&
                            receiver.CurrentAction == "block" && receiver.CurrentConfidence >= minConfidenceThreshold);

        bool kbdBlock = Input.GetKey(KeyCode.RightShift) || Input.GetKey(KeyCode.Keypad0) ||
                        Input.GetKey(KeyCode.G) || Input.GetKey(KeyCode.P);

        return kinectBlock || kbdBlock;
    }

    public bool WasLightPunchPressed()
    {
        bool gesture = EvaluateAttackTrigger("punch_left");
        bool kbd = CheckKeyList(ryuLightPunchKeys);
        return gesture || kbd;
    }

    public bool WasHeavyPunchPressed()
    {
        bool gesture = EvaluateAttackTrigger("punch_right");
        bool kbd = CheckKeyList(ryuHeavyPunchKeys);
        return gesture || kbd;
    }

    public bool WasLightKickPressed()
    {
        bool gesture = EvaluateAttackTrigger("kick_left");
        bool kbd = CheckKeyList(ryuLightKickKeys);
        return gesture || kbd;
    }

    public bool WasHeavyKickPressed()
    {
        bool gesture = EvaluateAttackTrigger("kick_right");
        bool kbd = CheckKeyList(ryuHeavyKickKeys);
        return gesture || kbd;
    }

    public bool IsAttacking(out FighterAttackType attackType)
    {
        if (WasLightPunchPressed()) { attackType = FighterAttackType.LightPunch; return true; }
        if (WasHeavyPunchPressed()) { attackType = FighterAttackType.HeavyPunch; return true; }
        if (WasLightKickPressed())  { attackType = FighterAttackType.LightKick;  return true; }
        if (WasHeavyKickPressed())  { attackType = FighterAttackType.HeavyKick;  return true; }

        attackType = FighterAttackType.None;
        return false;
    }

    public bool WasHadoukenGestureDetected() => false;
    public bool WasShoryukenGestureDetected() => false;
    public bool WasParryStanceDetected() => false;

    #endregion

    #region Evaluación de Disparo de Ataques

    private bool EvaluateAttackTrigger(string targetAction)
    {
        if (receiver == null || !receiver.IsConnected || !receiver.HasBody)
        {
            return false;
        }

        if (receiver.CurrentAction != targetAction || receiver.CurrentConfidence < minConfidenceThreshold)
        {
            return false;
        }

        float now = Time.time;
        bool isNewAction = (targetAction != lastTriggeredAttack);
        bool cooldownExpired = (now - lastAttackTimestamp) >= attackCooldownSeconds;

        if (isNewAction || cooldownExpired)
        {
            lastAttackTimestamp = now;
            lastTriggeredAttack = targetAction;
            return true;
        }

        return false;
    }

    private static bool CheckKeyList(KeyCode[] keys)
    {
        if (keys == null) return false;
        for (int i = 0; i < keys.Length; i++)
        {
            if (Input.GetKeyDown(keys[i])) return true;
        }
        return false;
    }

    #endregion

    #region Telemetría Somatosensorial en Pantalla (OnGUI)

    private void OnGUI()
    {
        if (!showHUD) return;

        float scale = Mathf.Min(Screen.width / 960f, Screen.height / 540f);
        Matrix4x4 old = GUI.matrix;
        GUI.matrix = Matrix4x4.TRS(new Vector3((Screen.width - 960 * scale) / 2, 0), Quaternion.identity, Vector3.one * scale);

        bool online = (receiver != null && receiver.IsConnected);
        string currentAction = receiver != null ? receiver.CurrentAction : "none";
        float confidence = receiver != null ? receiver.CurrentConfidence : 0f;
        float distZ = receiver != null ? receiver.ZDistance : 0f;

        // Tarjeta lateral derecha CPS-3
        Rect hudRect = new Rect(670, 72, 270, 115);
        GUI.color = new Color(0.04f, 0.05f, 0.08f, 0.88f);
        GUI.DrawTexture(hudRect, Texture2D.whiteTexture);

        // Borde superior de color dinámico (Verde si online, Ámbar si offline)
        Color borderColor = online ? new Color(0.1f, 0.95f, 0.45f, 1f) : new Color(1f, 0.65f, 0.15f, 1f);
        GUI.color = borderColor;
        GUI.DrawTexture(new Rect(hudRect.x, hudRect.y, hudRect.width, 3), Texture2D.whiteTexture);
        GUI.DrawTexture(new Rect(hudRect.x, hudRect.y + hudRect.height - 2, hudRect.width, 2), Texture2D.whiteTexture);
        GUI.DrawTexture(new Rect(hudRect.x, hudRect.y, 2, hudRect.height), Texture2D.whiteTexture);
        GUI.DrawTexture(new Rect(hudRect.x + hudRect.width - 2, hudRect.y, 2, hudRect.height), Texture2D.whiteTexture);
        GUI.color = Color.white;

        GUIStyle titleStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 11,
            fontStyle = FontStyle.Bold
        };
        titleStyle.normal.textColor = borderColor;
        string statusText = online ? "● KINECT STRIKE: ONLINE (UDP 5005)" : "○ KINECT STRIKE: ESPERANDO PYTHON...";
        GUI.Label(new Rect(hudRect.x + 8, hudRect.y + 6, 255, 18), statusText, titleStyle);

        GUIStyle bodyStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 10,
            fontStyle = FontStyle.Normal
        };
        bodyStyle.normal.textColor = Color.white;

        string gestureLine = online
            ? $"Gesto ML: {currentAction.ToUpper()} ({confidence * 100:F0}%) | Z: {distZ:F2}m"
            : "Ejecuta: python Tools/test_live_kinect_classifier.py";
        GUI.Label(new Rect(hudRect.x + 8, hudRect.y + 28, 255, 16), gestureLine, bodyStyle);

        string spacingLine = autoSpacingEnabled
            ? "Auto-Spacing: ON (Distancia Asistida)"
            : "Auto-Spacing: OFF (Control Manual)";
        GUIStyle spacingStyle = new GUIStyle(bodyStyle);
        spacingStyle.normal.textColor = autoSpacingEnabled ? new Color(0.4f, 0.85f, 1f) : new Color(0.7f, 0.7f, 0.7f);
        GUI.Label(new Rect(hudRect.x + 8, hudRect.y + 48, 255, 16), spacingLine, spacingStyle);

        GUIStyle kbdStyle = new GUIStyle(bodyStyle);
        kbdStyle.normal.textColor = new Color(1f, 0.88f, 0.35f);
        GUI.Label(new Rect(hudRect.x + 8, hudRect.y + 68, 255, 16), "Teclado Fallback: ACTIVO [Flechas / NumPad]", kbdStyle);

        GUIStyle footerStyle = new GUIStyle(bodyStyle)
        {
            fontSize = 9
        };
        footerStyle.normal.textColor = new Color(0.6f, 0.65f, 0.75f);
        GUI.Label(new Rect(hudRect.x + 8, hudRect.y + 90, 255, 16), "[F1] Ocultar Telemetría | [F2] Toggle Spacing", footerStyle);

        GUI.matrix = old;
    }

    #endregion
}
