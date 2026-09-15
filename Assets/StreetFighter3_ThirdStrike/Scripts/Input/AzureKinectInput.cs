using UnityEngine;

/// <summary>
/// Adaptador de entrada para Azure Kinect DK en Street Fighter III: 3rd Strike.
/// Procesa la cinemática de las 32 articulaciones (Joints) del Body Tracking SDK
/// y las traduce a comandos de IFighterInput para el luchador.
/// </summary>
public class AzureKinectInput : MonoBehaviour, IFighterInput
{
    [Header("Calibración y Umbrales Cinemáticos")]
    [Tooltip("Distancia mínima entre ambas muñecas para detectar preparación de Hadouken (metros)")]
    [SerializeField] private float hadoukenWristDistanceThreshold = 0.20f;

    [Tooltip("Velocidad mínima del vector hombro-muñeca para registrar un puñetazo (m/s)")]
    [SerializeField] private float punchVelocityThreshold = 2.2f;

    [Tooltip("Diferencia de altura entre rodilla y cadera para registrar agachado")]
    [SerializeField] private float crouchKneeDropThreshold = 0.15f;

    [Tooltip("Elevación del tobillo respecto al suelo para registrar patada (metros)")]
    [SerializeField] private float kickAnkleElevationThreshold = 0.25f;

    [Header("Rango Óptimo de Distancia al Sensor (Z en metros)")]
    [SerializeField] private float minDistanceZ = 1.5f;
    [SerializeField] private float maxDistanceZ = 3.5f;

    [Header("Depuración y Diagnóstico en Tiempo Real")]
    [Tooltip("Muestra logs descriptivos con métricas en la consola de Unity")]
    [SerializeField] private bool logDebugToConsole = true;

    [Tooltip("Muestra un cuadro de diagnóstico en la esquina de la pantalla")]
    [SerializeField] private bool showOnScreenDebugHUD = true;

    [Header("Clasificador de Poses Calibradas")]
    [Tooltip("Comparador opcional para activar ataques al encajar con poses del JSON")]
    [SerializeField] private KinectPoseMatcher poseMatcher;

    // Estados internos en caché para el frame actual
    private float horizontalAxis = 0f;
    private bool isCrouching = false;
    private bool isJumping = false;
    private bool isBlocking = false;

    private void Start()
    {
        if (poseMatcher == null)
        {
            poseMatcher = GetComponent<KinectPoseMatcher>();
        }
    }

    private bool lightPunchTriggered = false;
    private bool heavyPunchTriggered = false;
    private bool lightKickTriggered = false;
    private bool heavyKickTriggered = false;
    private bool hadoukenTriggered = false;
    private bool shoryukenTriggered = false;
    private bool parryTriggered = false;

    // Estados previos para detectar transiciones limpias
    private bool prevCrouching = false;
    private bool prevBlocking = false;
    private bool prevJumping = false;

    // Cooldowns para evitar spam de triggers en frames consecutivos
    private float lastPunchTime = 0f;
    private float lastKickTime = 0f;
    private float lastSpecialTime = 0f;
    private const float ACTION_COOLDOWN = 0.28f;

    // Métricas para visualización en pantalla
    private float currentZ = 0f;
    private float lastRightWristSpeed = 0f;
    private float lastLeftWristSpeed = 0f;
    private string lastActionDetected = "Ninguna";
    private float lastActionTimestamp = 0f;

    // Buffer temporal de posiciones previas para cálculo de velocidad v = (pos - prevPos) / dt
    private Vector3 prevRightWristPos;
    private Vector3 prevLeftWristPos;
    private float lastUpdateTime;

    public bool IsUserInOptimalRange(float userZ)
    {
        return userZ >= minDistanceZ && userZ <= maxDistanceZ;
    }

    /// <summary>
    /// Método receptor invocado cuando el SDK de Azure Kinect entrega un nuevo frame de articulaciones.
    /// </summary>
    public void ProcessSkeletonData(
        Vector3 pelvis,
        Vector3 chest,
        Vector3 rightShoulder,
        Vector3 rightWrist,
        Vector3 leftShoulder,
        Vector3 leftWrist,
        Vector3 rightKnee,
        Vector3 rightAnkle,
        Vector3 leftKnee,
        Vector3 leftAnkle)
    {
        float dt = Time.time - lastUpdateTime;
        if (dt <= 0.0001f) dt = Time.deltaTime;

        currentZ = pelvis.z;

        // Evaluar clasificador de poses calibradas en tiempo real (si está presente)
        if (poseMatcher != null)
        {
            poseMatcher.EvaluateLiveSkeleton(
                pelvis, chest, rightShoulder, rightWrist, leftShoulder, leftWrist,
                rightKnee, rightAnkle, leftKnee, leftAnkle);
        }

        // 1. Análisis de Postura Sagital (Orientación de perfil para combate 2D)
        float dx = rightShoulder.x - leftShoulder.x;
        float dz = rightShoulder.z - leftShoulder.z;
        float torsoYawDeg = Mathf.Atan2(dz, dx) * Mathf.Rad2Deg;
        bool isSagittalStance = Mathf.Abs(torsoYawDeg) > 20f;

        string leadArm = "Frontal";
        if (leftShoulder.z < rightShoulder.z - 0.05f) leadArm = "Izquierda (Ortodoxa)";
        else if (rightShoulder.z < leftShoulder.z - 0.05f) leadArm = "Derecha (Zurda)";

        // 2. Cálculo de velocidad de extensión de muñecas hacia el plano sagital (Z en metros/segundo)
        Vector3 rightWristVel = (rightWrist - prevRightWristPos) / dt;
        Vector3 leftWristVel = (leftWrist - prevLeftWristPos) / dt;
        lastRightWristSpeed = rightWristVel.z;
        lastLeftWristSpeed = leftWristVel.z;

        // 3. Movimiento horizontal: posición de la pelvis relativa al centro del sensor (eje X)
        horizontalAxis = Mathf.Clamp(pelvis.x * 2.0f, -1f, 1f);
        if (Mathf.Abs(horizontalAxis) < 0.2f) horizontalAxis = 0f; // Deadzone

        // 4. Postura de agachado: compresión de cadera respecto a rodillas
        float avgKneeY = (rightKnee.y + leftKnee.y) * 0.5f;
        isCrouching = (pelvis.y - avgKneeY) < crouchKneeDropThreshold;

        if (isCrouching != prevCrouching)
        {
            if (isCrouching) LogAction("🧘 [Kinect] Postura: ¡AGACHADO! (Crouch)");
            else LogAction("🧍 [Kinect] Postura: De pie (Stand)");
            prevCrouching = isCrouching;
        }

        // 5. Salto: elevación súbita de la pelvis
        isJumping = pelvis.y > 1.15f; // Calibrado según altura base del usuario
        if (isJumping && !prevJumping)
        {
            LogAction($"🦘 [Kinect] ¡SALTO DETECTADO! (Altura Pelvis: {pelvis.y:F2}m)");
        }
        prevJumping = isJumping;

        // 6. Guardia / Bloqueo Sagital: antebrazos protegiendo la línea sagital del cuerpo
        float wristDist = Vector3.Distance(rightWrist, leftWrist);
        float chestDistRight = Vector3.Distance(rightWrist, chest);
        float chestDistLeft = Vector3.Distance(leftWrist, chest);
        isBlocking = wristDist < 0.28f && chestDistRight < 0.38f && chestDistLeft < 0.38f;

        if (isBlocking != prevBlocking)
        {
            if (isBlocking)
            {
                string guardType = isSagittalStance ? $"GUARDIA SAGITAL (Perfil {torsoYawDeg:F0}° - {leadArm})" : "GUARDIA FRONTAL";
                LogAction($"🛡️ [Kinect] Postura: ¡{guardType}!");
            }
            prevBlocking = isBlocking;
        }

        // 7. Gesto de Hadouken: ambas manos proyectadas hacia adelante tras converger
        if (Time.time - lastSpecialTime > ACTION_COOLDOWN)
        {
            if (wristDist < hadoukenWristDistanceThreshold && rightWristVel.z > punchVelocityThreshold)
            {
                hadoukenTriggered = true;
                lastSpecialTime = Time.time;
                LogAction($"🔥 [Kinect] ¡¡¡HADOUKEN DETECTADO!!! (Distancia muñecas: {wristDist:F2}m, Vel: {rightWristVel.z:F1} m/s)");
            }
        }

        // 8. Detección de Puñetazos Sagitales (Jab adelantado vs Cross con rotación)
        if (!hadoukenTriggered && Time.time - lastPunchTime > ACTION_COOLDOWN)
        {
            if (leadArm.StartsWith("Izquierda"))
            {
                if (leftWristVel.z > punchVelocityThreshold)
                {
                    lightPunchTriggered = true;
                    lastPunchTime = Time.time;
                    LogAction($"🥊 [Kinect] ¡JAB SAGITAL (LP - Mano Adelantada Izq)! (Vel: {leftWristVel.z:F1} m/s)");
                }
                else if (rightWristVel.z > punchVelocityThreshold)
                {
                    heavyPunchTriggered = true;
                    lastPunchTime = Time.time;
                    LogAction($"💥 [Kinect] ¡CROSS SAGITAL (HP - Mano Atrasada Der)! (Vel: {rightWristVel.z:F1} m/s)");
                }
            }
            else if (leadArm.StartsWith("Derecha"))
            {
                if (rightWristVel.z > punchVelocityThreshold)
                {
                    lightPunchTriggered = true;
                    lastPunchTime = Time.time;
                    LogAction($"🥊 [Kinect] ¡JAB SAGITAL (LP - Mano Adelantada Der)! (Vel: {rightWristVel.z:F1} m/s)");
                }
                else if (leftWristVel.z > punchVelocityThreshold)
                {
                    heavyPunchTriggered = true;
                    lastPunchTime = Time.time;
                    LogAction($"💥 [Kinect] ¡CROSS SAGITAL (HP - Mano Atrasada Izq)! (Vel: {leftWristVel.z:F1} m/s)");
                }
            }
            else // Postura neutra frontal
            {
                if (rightWristVel.z > punchVelocityThreshold)
                {
                    heavyPunchTriggered = true;
                    lastPunchTime = Time.time;
                    LogAction($"🥊 [Kinect] ¡PUÑETAZO DERECHO (HP)! (Vel: {rightWristVel.z:F1} m/s)");
                }
                else if (leftWristVel.z > punchVelocityThreshold)
                {
                    lightPunchTriggered = true;
                    lastPunchTime = Time.time;
                    LogAction($"🥊 [Kinect] ¡PUÑETAZO IZQUIERDO (LP)! (Vel: {leftWristVel.z:F1} m/s)");
                }
            }
        }

        // 9. Detección de Patadas Sagitales por elevación y avance
        if (Time.time - lastKickTime > ACTION_COOLDOWN)
        {
            if (rightAnkle.y > kickAnkleElevationThreshold)
            {
                heavyKickTriggered = true;
                lastKickTime = Time.time;
                LogAction($"🦶 [Kinect] ¡PATADA SAGITAL DERECHA (HK)! (Elevación tobillo: {rightAnkle.y:F2}m)");
            }
            else if (leftAnkle.y > kickAnkleElevationThreshold)
            {
                lightKickTriggered = true;
                lastKickTime = Time.time;
                LogAction($"🦶 [Kinect] ¡PATADA SAGITAL IZQUIERDA (LK)! (Elevación tobillo: {leftAnkle.y:F2}m)");
            }
        }

        // Guardar posiciones para el siguiente frame
        prevRightWristPos = rightWrist;
        prevLeftWristPos = leftWrist;
        lastUpdateTime = Time.time;
    }

    private void LogAction(string message)
    {
        lastActionDetected = message;
        lastActionTimestamp = Time.time;

        if (logDebugToConsole)
        {
            Debug.Log($"<color=#00FFCC><b>{message}</b></color>");
        }
    }

    private void LateUpdate()
    {
        // Consumir triggers tras procesar el frame
        lightPunchTriggered = false;
        heavyPunchTriggered = false;
        lightKickTriggered = false;
        heavyKickTriggered = false;
        hadoukenTriggered = false;
        shoryukenTriggered = false;
        parryTriggered = false;
    }

    private void OnGUI()
    {
        if (!showOnScreenDebugHUD) return;

        GUILayout.BeginArea(new Rect(15, 15, 380, 200), GUI.skin.box);
        GUILayout.Label("<b>🎮 SF3 - AZURE KINECT DIAGNOSTICS</b>");

        bool inRange = IsUserInOptimalRange(currentZ);
        string rangeStatus = inRange ? "<color=green>ÓPTIMA (OK)</color>" : "<color=red>FUERA DE RANGO</color>";
        GUILayout.Label($"Distancia al sensor (Z): {currentZ:F2}m | Rango: {rangeStatus}");
        GUILayout.Label($"Eje Horizontal: {horizontalAxis:F2} | Agachado: {isCrouching} | Guardia: {isBlocking}");
        GUILayout.Label($"Velocidad Muñeca Der: {lastRightWristSpeed:F1} m/s | Izq: {lastLeftWristSpeed:F1} m/s");

        GUILayout.Space(5);
        if (Time.time - lastActionTimestamp < 1.5f)
        {
            GUILayout.Label($"<b>Última Acción:</b> <color=yellow>{lastActionDetected}</color>");
        }
        else
        {
            GUILayout.Label("<b>Última Acción:</b> Esperando movimiento...");
        }

        GUILayout.EndArea();
    }

    // --- Implementación de la Interfaz IFighterInput ---

    public float GetHorizontalAxis() => horizontalAxis;
    public float GetHorizontalMove() => horizontalAxis;
    public bool IsCrouching() => isCrouching;
    public bool IsJumping() => isJumping;
    public bool IsBlocking() => isBlocking;

    public bool WasLightPunchPressed() => lightPunchTriggered;
    public bool WasHeavyPunchPressed() => heavyPunchTriggered;
    public bool WasLightKickPressed() => lightKickTriggered;
    public bool WasHeavyKickPressed() => heavyKickTriggered;
    public bool WasHadoukenGestureDetected() => hadoukenTriggered;
    public bool WasShoryukenGestureDetected() => shoryukenTriggered;
    public bool WasParryStanceDetected() => parryTriggered;

    public bool IsAttacking(out FighterAttackType attackType)
    {
        if (hadoukenTriggered)
        {
            attackType = FighterAttackType.Hadouken;
            return true;
        }
        if (shoryukenTriggered)
        {
            attackType = FighterAttackType.Shoryuken;
            return true;
        }
        if (heavyPunchTriggered)
        {
            attackType = FighterAttackType.HeavyPunch;
            return true;
        }
        if (lightPunchTriggered)
        {
            attackType = FighterAttackType.LightPunch;
            return true;
        }
        if (heavyKickTriggered)
        {
            attackType = FighterAttackType.HeavyKick;
            return true;
        }
        if (lightKickTriggered)
        {
            attackType = FighterAttackType.LightKick;
            return true;
        }

        attackType = FighterAttackType.None;
        return false;
    }
}
