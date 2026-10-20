using UnityEngine;

/// <summary>
/// Adaptador de entrada Somatosensorial (Kinect + Machine Learning) para Ryu en el Modo Historia de SF3.
/// Implementa IFighterInput con detección geométrica de Pose Sostenida (0.5 segundos):
/// - Incluye un periodo de estabilización inicial (1.5s) cuando el Kinect detecta al jugador por primera vez
///   para evitar animaciones espontáneas al entrar en escena.
/// - Al mantener una postura física (puño, patada, agacharse, bloqueo) por 0.5 segundos, se dispara la animación.
/// - Mientras se mantenga dicha postura, la animación se repite constantemente en bucle.
/// - Al cambiar de posición física o volver a reposo (idle), el bucle de ataque se detiene inmediatamente.
/// </summary>
public class KinectFighterInput : MonoBehaviour, IFighterInput
{
    [Header("Receptor de Telemetría UDP")]
    [SerializeField] private KinectUDPReceiver receiver;

    [Header("Activación por Pose Sostenida (0.5 segundos)")]
    [Tooltip("Tiempo en segundos que se debe mantener la postura continua para activar el ataque (default: 0.5s).")]
    [Range(0.1f, 4.0f)]
    [SerializeField] private float poseHoldDurationRequired = 0.5f;

    [Tooltip("Umbral mínimo de certeza del clasificador postural para validar la pose (48%).")]
    [SerializeField] private float minConfidenceThreshold = 0.48f;

    [Tooltip("Tiempo de estabilización inicial (en segundos) al detectar un cuerpo para evitar animaciones espontáneas.")]
    [SerializeField] private float bodyWarmupGracePeriod = 1.5f;

    [Header("Auto-Spacing Asistido (Opcional con F2)")]
    [Tooltip("Desactivado por defecto para que Ryu no camine solo al iniciar la pelea. Activar con [F2].")]
    [SerializeField] private bool autoSpacingEnabled = false;
    [Tooltip("Transform del oponente (Ken) para calcular la distancia de combate.")]
    [SerializeField] private Transform opponent;
    [SerializeField] private float optimalDistanceMin = 0.90f;
    [SerializeField] private float optimalDistanceMax = 1.45f;

    [Header("HUD de Telemetría Somatosensorial")]
    [SerializeField] private bool showHUD = true;

    // Estados de seguimiento de pose sostenida y estabilización inicial
    [Header("Estado en Tiempo Real (Debug)")]
    [SerializeField] private string currentHeldAction = "idle";
    [SerializeField] private float currentHoldTimer = 0f;
    [SerializeField] private float bodyWarmupTimer = 0f;
    [SerializeField] private bool isCalibratingBody = true;
    [SerializeField] private bool isPoseActive = false;
    private bool jumpConsumed = false;

    // Caché de teclas de teclado (Fallback híbrido P2 / Ryu)
    private readonly KeyCode[] ryuLightPunchKeys = { KeyCode.Keypad1, KeyCode.Alpha7, KeyCode.B, KeyCode.J };
    private readonly KeyCode[] ryuHeavyPunchKeys = { KeyCode.Keypad2, KeyCode.Alpha8, KeyCode.N, KeyCode.K };
    private readonly KeyCode[] ryuLightKickKeys  = { KeyCode.Keypad4, KeyCode.Alpha9, KeyCode.M, KeyCode.L };
    private readonly KeyCode[] ryuHeavyKickKeys  = { KeyCode.Keypad5, KeyCode.Alpha0, KeyCode.Comma, KeyCode.O };

    private void Awake()
    {
        EnsureReceiver();
    }

    private void Start()
    {
        EnsureReceiver();
        if (opponent == null)
        {
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

    public void SetPoseHoldRequiredTime(float seconds)
    {
        poseHoldDurationRequired = Mathf.Clamp(seconds, 0.1f, 5.0f);
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
        // Atajos en tiempo de ejecución
        if (Input.GetKeyDown(KeyCode.F1)) showHUD = !showHUD;
        if (Input.GetKeyDown(KeyCode.F2)) autoSpacingEnabled = !autoSpacingEnabled;
        if (Input.GetKeyDown(KeyCode.F3)) poseHoldDurationRequired = Mathf.Max(0.1f, poseHoldDurationRequired - 0.1f);
        if (Input.GetKeyDown(KeyCode.F4)) poseHoldDurationRequired = Mathf.Min(4.0f, poseHoldDurationRequired + 0.1f);

        UpdatePoseHoldTracking();
    }

    /// <summary>
    /// Rastrea cuánto tiempo el jugador mantiene físicamente la misma posición.
    /// Incluye estabilización inicial (bodyWarmupGracePeriod) cuando el sensor recién detecta al jugador
    /// para evitar que dispare animaciones por su cuenta al inicio.
    /// </summary>
    private void UpdatePoseHoldTracking()
    {
        if (receiver == null || !receiver.IsConnected || !receiver.HasBody)
        {
            bodyWarmupTimer = 0f;
            isCalibratingBody = true;
            currentHeldAction = "idle";
            currentHoldTimer = 0f;
            isPoseActive = false;
            jumpConsumed = false;
            return;
        }

        // 1. Periodo de estabilización al detectar el cuerpo por primera vez
        if (bodyWarmupTimer < bodyWarmupGracePeriod)
        {
            bodyWarmupTimer += Time.deltaTime;
            isCalibratingBody = true;
            currentHeldAction = "idle";
            currentHoldTimer = 0f;
            isPoseActive = false;
            jumpConsumed = false;
            return;
        }

        isCalibratingBody = false;

        string detectedAction = receiver.CurrentAction;
        float conf = receiver.CurrentConfidence;

        // Si la confianza es menor al umbral, tratar como reposo (idle)
        if (conf < minConfidenceThreshold)
        {
            detectedAction = "idle";
        }

        // 2. Si la postura física cambia o regresa a reposo (idle)
        if (detectedAction != currentHeldAction)
        {
            currentHeldAction = detectedAction;
            currentHoldTimer = 0f;
            isPoseActive = false;
            jumpConsumed = false;
        }
        else
        {
            // Se mantiene la misma postura física continua
            if (detectedAction != "idle")
            {
                currentHoldTimer += Time.deltaTime;

                // Activar repetición en bucle al alcanzar el tiempo requerido (0.5s)
                if (currentHoldTimer >= poseHoldDurationRequired)
                {
                    isPoseActive = true;
                }
            }
            else
            {
                currentHoldTimer = 0f;
                isPoseActive = false;
                jumpConsumed = false;
            }
        }
    }

    #region Implementación de IFighterInput

    public float GetHorizontalAxis()
    {
        // 1. Prioridad: Teclado Fallback manual (Flechas)
        bool kbdRight = Input.GetKey(KeyCode.RightArrow);
        bool kbdLeft  = Input.GetKey(KeyCode.LeftArrow);
        if (kbdRight || kbdLeft)
        {
            return (kbdRight ? 1f : 0f) - (kbdLeft ? 1f : 0f);
        }

        // 2. Auto-Spacing Asistido (Solo si el usuario lo activa con [F2] y no está calibrando)
        if (autoSpacingEnabled && !isCalibratingBody && opponent != null)
        {
            if (IsCrouching() || IsBlocking())
            {
                return 0f;
            }

            float dx = opponent.position.x - transform.position.x;
            float absDist = Mathf.Abs(dx);
            float dir = Mathf.Sign(dx);

            if (absDist > optimalDistanceMax)
            {
                return dir * 1.0f;
            }
            if (absDist < optimalDistanceMin)
            {
                return -dir * 1.0f;
            }
            return 0f;
        }

        return 0f;
    }

    public float GetHorizontalMove()
    {
        return GetHorizontalAxis();
    }

    public bool IsCrouching()
    {
        bool kinectCrouch = !isCalibratingBody && isPoseActive && currentHeldAction == "crouch";
        bool kbdCrouch = Input.GetKey(KeyCode.DownArrow);
        return kinectCrouch || kbdCrouch;
    }

    public bool IsJumping()
    {
        bool kinectJump = false;
        if (!isCalibratingBody && isPoseActive && currentHeldAction == "jump" && !jumpConsumed)
        {
            kinectJump = true;
            jumpConsumed = true;
        }

        bool kbdJump = Input.GetKeyDown(KeyCode.UpArrow);
        return kinectJump || kbdJump;
    }

    public bool IsBlocking()
    {
        bool kinectBlock = !isCalibratingBody && isPoseActive && currentHeldAction == "block";
        bool kbdBlock = Input.GetKey(KeyCode.RightShift) || Input.GetKey(KeyCode.Keypad0);
        return kinectBlock || kbdBlock;
    }

    public bool WasLightPunchPressed()
    {
        // Se repite constantemente en bucle mientras la pose punch_left esté activa (>= 0.5s)
        bool gesture = !isCalibratingBody && isPoseActive && currentHeldAction == "punch_left";
        bool kbd = CheckKeyList(ryuLightPunchKeys);
        return gesture || kbd;
    }

    public bool WasHeavyPunchPressed()
    {
        // Se repite constantemente en bucle mientras la pose punch_right esté activa (>= 0.5s)
        bool gesture = !isCalibratingBody && isPoseActive && currentHeldAction == "punch_right";
        bool kbd = CheckKeyList(ryuHeavyPunchKeys);
        return gesture || kbd;
    }

    public bool WasLightKickPressed()
    {
        // Se repite constantemente en bucle mientras la pose kick_left esté activa (>= 0.5s)
        bool gesture = !isCalibratingBody && isPoseActive && currentHeldAction == "kick_left";
        bool kbd = CheckKeyList(ryuLightKickKeys);
        return gesture || kbd;
    }

    public bool WasHeavyKickPressed()
    {
        // Se repite constantemente en bucle mientras la pose kick_right esté activa (>= 0.5s)
        bool gesture = !isCalibratingBody && isPoseActive && currentHeldAction == "kick_right";
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

    #region Auxiliares de Teclado

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
        bool hasBody = (receiver != null && receiver.HasBody);
        float confidence = receiver != null ? receiver.CurrentConfidence : 0f;
        float distZ = receiver != null ? receiver.ZDistance : 0f;

        // Tarjeta lateral derecha CPS-3
        Rect hudRect = new Rect(650, 72, 290, 135);
        GUI.color = new Color(0.04f, 0.05f, 0.08f, 0.90f);
        GUI.DrawTexture(hudRect, Texture2D.whiteTexture);

        Color borderColor = !online
            ? new Color(0.8f, 0.4f, 0.2f, 1f)
            : isCalibratingBody
                ? new Color(0.3f, 0.8f, 1.0f, 1f)
                : isPoseActive
                    ? new Color(0.1f, 1.0f, 0.45f, 1f)
                    : currentHeldAction != "idle"
                        ? new Color(1.0f, 0.85f, 0.2f, 1f)
                        : new Color(0.4f, 0.75f, 1.0f, 1f);

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
        GUI.Label(new Rect(hudRect.x + 8, hudRect.y + 6, 275, 18), statusText, titleStyle);

        GUIStyle bodyStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 10,
            fontStyle = FontStyle.Normal
        };
        bodyStyle.normal.textColor = Color.white;

        string gestureLine = !online
            ? "Ejecuta: python Tools/test_live_kinect_classifier.py"
            : isCalibratingBody
                ? (hasBody ? $"Estabilizando esqueleto inicial... ({bodyWarmupTimer:F1}s)" : "Párate frente al Kinect (1.8m - 2.8m)")
                : $"Pose Detectada: {currentHeldAction.ToUpper()} ({confidence * 100:F0}%) | Z: {distZ:F2}m";
        GUI.Label(new Rect(hudRect.x + 8, hudRect.y + 26, 275, 16), gestureLine, bodyStyle);

        // Barra de progreso de pose sostenida o calibración
        float pct = isCalibratingBody
            ? Mathf.Clamp01(bodyWarmupTimer / Mathf.Max(0.1f, bodyWarmupGracePeriod))
            : Mathf.Clamp01(currentHoldTimer / Mathf.Max(0.1f, poseHoldDurationRequired));
        Rect barBg = new Rect(hudRect.x + 8, hudRect.y + 46, 274, 14);
        GUI.color = new Color(0.15f, 0.18f, 0.25f, 1f);
        GUI.DrawTexture(barBg, Texture2D.whiteTexture);

        Color barColor = isCalibratingBody
            ? new Color(0.2f, 0.75f, 1.0f, 1f)
            : isPoseActive
                ? new Color(0.1f, 0.95f, 0.4f, 1f)
                : new Color(1.0f, 0.75f, 0.15f, 1f);
        GUI.color = barColor;
        GUI.DrawTexture(new Rect(barBg.x, barBg.y, barBg.width * pct, barBg.height), Texture2D.whiteTexture);
        GUI.color = Color.white;

        string holdText = isCalibratingBody
            ? "Calibrando postura base (sin disparos falsos)..."
            : isPoseActive
                ? $"¡POSE FIJADA! REPITIENDO EN BUCLE ({currentHoldTimer:F1}s)"
                : currentHeldAction != "idle"
                    ? $"Manteniendo: {currentHoldTimer:F1}s / {poseHoldDurationRequired:F1}s ({pct * 100:F0}%)"
                    : $"Reposo: Mantén una pose por {poseHoldDurationRequired:F1}s para atacar";

        GUIStyle holdStyle = new GUIStyle(bodyStyle)
        {
            fontSize = 9,
            fontStyle = FontStyle.Bold
        };
        holdStyle.normal.textColor = isPoseActive ? new Color(0.2f, 1f, 0.5f) : (currentHeldAction != "idle" ? new Color(1f, 0.9f, 0.3f) : new Color(0.7f, 0.8f, 0.9f));
        GUI.Label(new Rect(hudRect.x + 8, hudRect.y + 64, 275, 16), holdText, holdStyle);

        string spacingLine = autoSpacingEnabled
            ? "Auto-Spacing: ON [F2]"
            : "Auto-Spacing: OFF [F2]";
        GUIStyle spacingStyle = new GUIStyle(bodyStyle);
        spacingStyle.normal.textColor = autoSpacingEnabled ? new Color(0.4f, 0.85f, 1f) : new Color(0.7f, 0.7f, 0.7f);
        GUI.Label(new Rect(hudRect.x + 8, hudRect.y + 82, 275, 16), spacingLine + " | Flechas: Mover", spacingStyle);

        GUIStyle hintStyle = new GUIStyle(bodyStyle)
        {
            fontSize = 8
        };
        hintStyle.normal.textColor = new Color(0.85f, 0.85f, 0.6f);
        GUI.Label(new Rect(hudRect.x + 8, hudRect.y + 100, 275, 14), "Cambiar de posición detiene el bucle al instante.", hintStyle);

        GUIStyle footerStyle = new GUIStyle(bodyStyle)
        {
            fontSize = 8
        };
        footerStyle.normal.textColor = new Color(0.6f, 0.65f, 0.75f);
        GUI.Label(new Rect(hudRect.x + 8, hudRect.y + 116, 275, 14), $"[F1] HUD | [F2] Auto-Walk | [F3/F4] Hold ({poseHoldDurationRequired:F1}s)", footerStyle);

        GUI.matrix = old;
    }

    #endregion
}
