using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

/// <summary>
/// Clasificador y comparador de poses calibradas en tiempo real para Azure Kinect.
/// Carga las poses capturadas desde calibrated_poses.json y calcula el porcentaje
/// de similitud biométrica con el cuerpo del jugador en cada frame.
/// </summary>
public class KinectPoseMatcher : MonoBehaviour
{
    [System.Serializable]
    public class PoseData
    {
        public string id;
        public string title;
        public float torsoYawDeg;
        public string leadArm;
        public Dictionary<string, Vector3> joints = new Dictionary<string, Vector3>();
    }

    [Header("Configuración de Calibración")]
    [Tooltip("Nombre del archivo JSON con las poses guardadas")]
    [SerializeField] private string jsonFileName = "calibrated_poses.json";

    [Tooltip("Umbral de similitud para considerar que la pose está activa (0 a 100%)")]
    [Range(60f, 95f)]
    [SerializeField] private float matchThresholdPercentage = 75f;

    [Tooltip("Tolerancia de distancia media por articulación en metros")]
    [SerializeField] private float maxDistanceToleranceMeters = 0.28f;

    [Header("Conexión con Ryu (Animaciones de Combate)")]
    [Tooltip("Controlador de pruebas de animación de Ryu")]
    [SerializeField] private FighterAnimationTester fighterTester;

    [Tooltip("Componente Animator de Ryu (en caso de no usar FighterAnimationTester)")]
    [SerializeField] private Animator fighterAnimator;

    [Tooltip("Tiempo de enfriamiento entre ataques automáticos para permitir que la animación termine")]
    [SerializeField] private float actionCooldownSeconds = 0.45f;

    public event System.Action<string, string> OnPoseActionTriggered;

    [Header("Visualización y Debug")]
    [SerializeField] private bool showHUD = true;
    [SerializeField] private bool drawGhostHologram = true;
    [SerializeField] private Color ghostColor = new Color(0f, 1f, 0.8f, 0.45f);

    private Dictionary<string, PoseData> loadedPoses = new Dictionary<string, PoseData>();
    private string bestMatchId = "Ninguna";
    private string bestMatchTitle = "Ninguna";
    private float bestMatchScore = 0f;

    // Caché de articulaciones en vivo relativas a la pelvis
    private Dictionary<string, Vector3> currentLiveJoints = new Dictionary<string, Vector3>();
    private bool hasLiveSkeleton = false;
    private float liveTorsoYaw = 0f;

    private float lastActionTriggerTime = 0f;
    private string lastTriggeredAnimation = "idle_stance";

    public string BestMatchId => bestMatchId;
    public float BestMatchScore => bestMatchScore;
    public string LastTriggeredAnimation => lastTriggeredAnimation;
    public bool IsMatching(string poseId) => bestMatchId == poseId && bestMatchScore >= matchThresholdPercentage;

    private void Awake()
    {
        LoadCalibratedPoses();
    }

    private void Start()
    {
        // Auto-detectar a Ryu en la escena si no se asignó en el Inspector
        if (fighterTester == null)
        {
            fighterTester = FindObjectOfType<FighterAnimationTester>();
        }
        if (fighterAnimator == null && fighterTester != null)
        {
            fighterAnimator = fighterTester.animator;
        }
        if (fighterAnimator == null)
        {
            fighterAnimator = FindObjectOfType<Animator>();
        }

        if (fighterTester != null || fighterAnimator != null)
        {
            Debug.Log("[KinectPoseMatcher] ✅ Conectado exitosamente con el Animator de Ryu.");
        }
        else
        {
            Debug.LogWarning("[KinectPoseMatcher] ⚠️ No se encontró Animator ni FighterAnimationTester en la escena.");
        }
    }

    /// <summary>
    /// Carga y parsea el archivo calibrated_poses.json generado por la herramienta de Python.
    /// </summary>
    public void LoadCalibratedPoses()
    {
        loadedPoses.Clear();

        // Buscar en varias rutas posibles del proyecto
        string[] searchPaths = new string[]
        {
            Path.Combine(Application.dataPath, "StreetFighter3_ThirdStrike", "Scenes", jsonFileName),
            Path.Combine(Application.dataPath, "..", "Tools", jsonFileName),
            Path.Combine(Application.dataPath, jsonFileName)
        };

        string targetPath = null;
        foreach (string path in searchPaths)
        {
            if (File.Exists(path))
            {
                targetPath = path;
                break;
            }
        }

        if (string.IsNullOrEmpty(targetPath))
        {
            Debug.LogWarning($"[KinectPoseMatcher] ⚠️ No se encontró el archivo '{jsonFileName}'. Genera las poses primero con el script de Python.");
            return;
        }

        try
        {
            string jsonText = File.ReadAllText(targetPath);
            ParseCustomPosesJson(jsonText);
            Debug.Log($"[KinectPoseMatcher] ✅ Se cargaron {loadedPoses.Count} poses calibradas exitosamente desde: {targetPath}");
        }
        catch (Exception ex)
        {
            Debug.LogError($"[KinectPoseMatcher] Error al leer archivo de poses: {ex.Message}");
        }
    }

    /// <summary>
    /// Parser ligero y robusto de JSON sin requerir librerías externas.
    /// Lee secuencialmente línea por línea para evitar problemas de substring o cálculo de índices.
    /// </summary>
    private void ParseCustomPosesJson(string json)
    {
        string[] lines = json.Split(new[] { "\r\n", "\r", "\n" }, StringSplitOptions.None);

        PoseData currentPose = null;
        string currentJointName = null;
        float currX = 0f, currY = 0f, currZ = 0f;
        bool inJoints = false;

        foreach (string rawLine in lines)
        {
            string line = rawLine.Trim();
            if (string.IsNullOrEmpty(line)) continue;

            // Detectar el inicio de un bloque de pose por `"id": "VALOR"`
            if (line.StartsWith("\"id\":", StringComparison.OrdinalIgnoreCase))
            {
                int firstQuote = line.IndexOf('"', 5);
                if (firstQuote != -1)
                {
                    int secondQuote = line.IndexOf('"', firstQuote + 1);
                    if (secondQuote != -1)
                    {
                        string poseId = line.Substring(firstQuote + 1, secondQuote - firstQuote - 1).Trim();
                        currentPose = new PoseData();
                        currentPose.id = poseId;
                        currentPose.title = poseId;
                        loadedPoses[poseId] = currentPose;
                        inJoints = false;
                        currentJointName = null;
                    }
                }
                continue;
            }

            if (currentPose == null) continue;

            // Detectar título humano
            if (line.StartsWith("\"title\":", StringComparison.OrdinalIgnoreCase))
            {
                int firstQuote = line.IndexOf('"', 8);
                if (firstQuote != -1)
                {
                    int secondQuote = line.IndexOf('"', firstQuote + 1);
                    if (secondQuote != -1)
                    {
                        currentPose.title = line.Substring(firstQuote + 1, secondQuote - firstQuote - 1).Trim();
                    }
                }
                continue;
            }

            // Detectar el bloque de relative_joints
            if (line.Contains("\"relative_joints_"))
            {
                inJoints = true;
                continue;
            }

            if (inJoints)
            {
                // Si la línea define el inicio de una articulación: "left wrist": {
                if (line.EndsWith("{") && line.StartsWith("\""))
                {
                    int quote1 = line.IndexOf('"');
                    int quote2 = line.IndexOf('"', quote1 + 1);
                    if (quote1 != -1 && quote2 > quote1)
                    {
                        currentJointName = line.Substring(quote1 + 1, quote2 - quote1 - 1).Trim().ToLowerInvariant();
                        currX = currY = currZ = 0f;
                    }
                    continue;
                }

                if (!string.IsNullOrEmpty(currentJointName))
                {
                    if (line.StartsWith("\"x\":"))
                    {
                        currX = ParseFloatFromLine(line);
                    }
                    else if (line.StartsWith("\"y\":"))
                    {
                        currY = ParseFloatFromLine(line);
                    }
                    else if (line.StartsWith("\"z\":"))
                    {
                        currZ = ParseFloatFromLine(line);
                    }
                    else if (line.StartsWith("}") || line.StartsWith("},"))
                    {
                        // Guardar articulación convertida al sistema de Unity (X derecha, Y arriba, Z adelante)
                        // En Kinect SDK / Python: X derecha, Y abajo (negativo de Unity), Z profundidad
                        currentPose.joints[currentJointName] = new Vector3(currX, -currY, currZ);
                        currentJointName = null;
                    }
                }
            }
        }
    }

    private float ParseFloatFromLine(string line)
    {
        int colonIdx = line.IndexOf(':');
        if (colonIdx < 0) return 0f;

        string numStr = line.Substring(colonIdx + 1).Trim().TrimEnd(',');
        if (float.TryParse(numStr, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float val))
        {
            return val;
        }
        return 0f;
    }

    /// <summary>
    /// Actualiza el comparador con el esqueleto en vivo del jugador.
    /// Invocado por AzureKinectBodyTracker o AzureKinectInput.
    /// </summary>
    public void EvaluateLiveSkeleton(
        Vector3 pelvis,
        Vector3 chest,
        Vector3 rShoulder,
        Vector3 rWrist,
        Vector3 lShoulder,
        Vector3 lWrist,
        Vector3 rKnee,
        Vector3 rAnkle,
        Vector3 lKnee,
        Vector3 lAnkle)
    {
        hasLiveSkeleton = true;

        // Normalizar relativas a la pelvis
        currentLiveJoints["pelvis"] = Vector3.zero;
        currentLiveJoints["neck"] = chest - pelvis;
        currentLiveJoints["spine - chest"] = chest - pelvis;
        currentLiveJoints["right shoulder"] = rShoulder - pelvis;
        currentLiveJoints["right wrist"] = rWrist - pelvis;
        currentLiveJoints["left shoulder"] = lShoulder - pelvis;
        currentLiveJoints["left wrist"] = lWrist - pelvis;
        currentLiveJoints["right knee"] = rKnee - pelvis;
        currentLiveJoints["right ankle"] = rAnkle - pelvis;
        currentLiveJoints["left knee"] = lKnee - pelvis;
        currentLiveJoints["left ankle"] = lAnkle - pelvis;

        // Calcular ángulo de torso
        float dx = rShoulder.x - lShoulder.x;
        float dz = rShoulder.z - lShoulder.z;
        liveTorsoYaw = Mathf.Atan2(dz, dx) * Mathf.Rad2Deg;

        // Comparar con todas las poses cargadas
        bestMatchScore = 0f;
        bestMatchId = "Ninguna";
        bestMatchTitle = "Ninguna";

        foreach (var kvp in loadedPoses)
        {
            PoseData refPose = kvp.Value;
            float score = CalculatePoseSimilarity(currentLiveJoints, refPose.joints);

            if (score > bestMatchScore)
            {
                bestMatchScore = score;
                bestMatchId = refPose.id;
                bestMatchTitle = refPose.title;
            }
        }

        // Disparar animación en Ryu si supera el umbral de similitud
        if (bestMatchScore >= matchThresholdPercentage && bestMatchId != "Ninguna")
        {
            string animName = GetAnimationForPoseId(bestMatchId);
            if (!string.IsNullOrEmpty(animName))
            {
                TriggerFighterAnimation(bestMatchId, animName);
            }
        }
    }

    /// <summary>
    /// Mapea el ID de la pose calibrada al nombre del estado de animación correspondiente en el Animator de Ryu.
    /// </summary>
    public string GetAnimationForPoseId(string poseId)
    {
        if (string.IsNullOrEmpty(poseId)) return null;

        // Si el poseId coincide directamente con un estado del Animator de Ryu (los 51 estados mapeados)
        if (fighterAnimator != null && fighterAnimator.HasState(0, Animator.StringToHash(poseId)))
        {
            return poseId;
        }

        switch (poseId)
        {
            // Puños Ligeros (LP)
            case "PUNCH_LIGHT_LEFT":
            case "JAB_LIGHT_PUNCH":
                return "light_punch";

            case "PUNCH_LIGHT_RIGHT":
                return "light_punch_close";

            // Puños Fuertes (HP)
            case "PUNCH_HEAVY_LEFT":
            case "CROSS_HEAVY_PUNCH":
                return "heavy_punch";

            case "PUNCH_HEAVY_RIGHT":
                return "forward_heavy_punch";

            // Patadas Ligeras (LK)
            case "KICK_LIGHT_LEFT":
            case "KICK_LIGHT":
                return "light_kick";

            case "KICK_LIGHT_RIGHT":
                return "medium_kick";

            // Patadas Fuertes (HK)
            case "KICK_HEAVY_LEFT":
            case "KICK_HEAVY":
                return "heavy_kick";

            case "KICK_HEAVY_RIGHT":
                return "heavy_kick";

            // Patadas Frontales / Empuje
            case "KICK_PUSH_LEFT":
                return "medium_kick_close";

            case "KICK_PUSH_RIGHT":
                return "heavy_kick";

            // Movimientos Especiales
            case "HADOUKEN":
                return "fireball";

            case "SHORYUKEN_RIGHT":
            case "SHORYUKEN_LEFT":
            case "SHORYUKEN":
                return "shoryuken";

            // Defensa y Bloqueos
            case "PARRY_LEFT":
            case "PARRY_RIGHT":
            case "PARRY_BLOCK":
                return "parry_standing";

            // Guardias (Reposo dinámico)
            case "GUARD_LEFT":
            case "GUARD_RIGHT":
            case "GUARD_BASE":
            case "GUARD_ORTHODOX":
            case "GUARD_SOUTHPAW":
                return "idle_stance";

            // Movilidad
            case "CROUCH":
                return "crouch_idle";

            case "JUMP":
                return "jump_neutral";

            default:
                return null;
        }
    }

    /// <summary>
    /// Activa la animación en el luchador (Ryu), respetando cooldowns y estados de combate.
    /// </summary>
    private void TriggerFighterAnimation(string poseId, string animName)
    {
        // 1. Posturas continuas de guardia o agachado
        if (animName == "idle_stance" || animName == "crouch_idle")
        {
            if (fighterTester != null)
            {
                if (!fighterTester.IsBusyWithAction())
                {
                    fighterTester.PlayLoop(animName);
                }
            }
            else if (fighterAnimator != null)
            {
                fighterAnimator.Play(animName, 0, 0f);
            }
            lastTriggeredAnimation = animName;
            return;
        }

        // 2. Acciones one-shot (ataques, patadas, especiales, parry, salto)
        if (Time.time < lastActionTriggerTime + actionCooldownSeconds)
        {
            return;
        }

        if (fighterTester != null)
        {
            if (fighterTester.IsBusyWithAction()) return;

            lastActionTriggerTime = Time.time;
            lastTriggeredAnimation = animName;
            fighterTester.ExecuteOneShotAction(animName);
            OnPoseActionTriggered?.Invoke(poseId, animName);
            Debug.Log($"[KinectPoseMatcher] 🥋 Pose '{poseId}' activó animación '{animName}' en Ryu!");
        }
        else if (fighterAnimator != null)
        {
            lastActionTriggerTime = Time.time;
            lastTriggeredAnimation = animName;
            fighterAnimator.Play(animName, 0, 0f);
            OnPoseActionTriggered?.Invoke(poseId, animName);
            Debug.Log($"[KinectPoseMatcher] 🥋 Pose '{poseId}' activó animación '{animName}' en Ryu Animator!");
        }
    }

    /// <summary>
    /// Calcula similitud porcentual (0 a 100%) entre el esqueleto actual y una pose de referencia.
    /// </summary>
    private float CalculatePoseSimilarity(Dictionary<string, Vector3> live, Dictionary<string, Vector3> reference)
    {
        float totalDist = 0f;
        int evaluatedCount = 0;

        // Articulaciones críticas con mayor peso para fighting games
        string[] criticalJoints = new string[]
        {
            "right wrist", "left wrist", "right shoulder", "left shoulder",
            "right ankle", "left ankle", "right knee", "left knee", "neck", "spine - chest"
        };

        foreach (string jointKey in criticalJoints)
        {
            if (live.ContainsKey(jointKey) && reference.ContainsKey(jointKey))
            {
                float dist = Vector3.Distance(live[jointKey], reference[jointKey]);

                // Las muñecas y tobillos tienen doble ponderación
                if (jointKey.Contains("wrist") || jointKey.Contains("ankle"))
                {
                    totalDist += dist * 1.5f;
                    evaluatedCount += 2;
                }
                else
                {
                    totalDist += dist;
                    evaluatedCount++;
                }
            }
        }

        if (evaluatedCount == 0) return 0f;

        float avgDistance = totalDist / evaluatedCount;
        float similarityRatio = Mathf.Clamp01(1.0f - (avgDistance / maxDistanceToleranceMeters));
        return similarityRatio * 100f;
    }

    private void OnGUI()
    {
        if (!showHUD) return;

        GUILayout.BeginArea(new Rect(15, 225, 410, 265), GUI.skin.box);
        GUILayout.Label("<b>🥋 SF3 - CLASIFICADOR DE POSES & RYU</b>");

        if (loadedPoses.Count == 0)
        {
            GUILayout.Label("<color=yellow>⚠️ No hay poses cargadas. Presiona Recargar.</color>");
            if (GUILayout.Button("Recargar calibrated_poses.json"))
            {
                LoadCalibratedPoses();
            }
            GUILayout.EndArea();
            return;
        }

        GUILayout.Label($"Poses Calibradas en Memoria: <b>{loadedPoses.Count}</b>");

        bool isHit = bestMatchScore >= matchThresholdPercentage;
        string scoreColor = isHit ? "lime" : (bestMatchScore > 50f ? "yellow" : "white");

        GUILayout.Label($"Pose Más Cercana: <color={scoreColor}><b>{bestMatchTitle}</b></color>");
        GUILayout.Label($"Similitud Biométrica: <color={scoreColor}><b>{bestMatchScore:F1}%</b></color> (Umbral: {matchThresholdPercentage}%)");
        GUILayout.Label($"Animación Ryu Activa: <color=cyan><b>{lastTriggeredAnimation}</b></color>");

        // Barra de coincidencia
        Rect barRect = GUILayoutUtility.GetRect(350, 18);
        GUI.Box(barRect, "");
        float fillW = (barRect.width * (bestMatchScore / 100f));
        Color originalColor = GUI.color;
        GUI.color = isHit ? Color.green : Color.yellow;
        GUI.Box(new Rect(barRect.x, barRect.y, fillW, barRect.height), "");
        GUI.color = originalColor;

        if (isHit)
        {
            GUILayout.Label($"<color=lime><b>⚡ ¡ACCIÓN DISPARADA: {bestMatchId}!</b></color>");
        }
        else
        {
            GUILayout.Label("<color=grey>Adopta una pose calibrada para activar...</color>");
        }

        GUILayout.EndArea();
    }

    private void OnDrawGizmos()
    {
        if (!drawGhostHologram || !hasLiveSkeleton) return;

        // Dibujar holograma fantasma de la pose calibrada más cercana para que el usuario encaje en ella
        if (loadedPoses.ContainsKey(bestMatchId))
        {
            PoseData bestPose = loadedPoses[bestMatchId];
            Gizmos.color = bestMatchScore >= matchThresholdPercentage ? Color.green : ghostColor;

            foreach (var kvp in bestPose.joints)
            {
                Vector3 worldPos = transform.position + kvp.Value;
                Gizmos.DrawWireSphere(worldPos, 0.05f);
            }
        }
    }
}
