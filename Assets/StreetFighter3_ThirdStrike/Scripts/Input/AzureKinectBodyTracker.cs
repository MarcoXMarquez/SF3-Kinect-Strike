using System;
using System.IO;
using System.Runtime.InteropServices;
using UnityEngine;
using Microsoft.Azure.Kinect.Sensor;
using Microsoft.Azure.Kinect.BodyTracking;

/// <summary>
/// Controlador principal de Azure Kinect DK para Unity.
/// Inicializa el sensor físico, ejecuta el Body Tracking SDK de 32 articulaciones
/// y reenvía las coordenadas 3D al adaptador IFighterInput (AzureKinectInput).
/// </summary>
public class AzureKinectBodyTracker : MonoBehaviour
{
    [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    private static extern bool SetDllDirectory(string lpPathName);

    [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    private static extern IntPtr LoadLibrary(string lpLibFileName);

    [Header("Conexión con Adaptador de Entrada")]
    [SerializeField] private AzureKinectInput targetInput;

    [Header("Configuración del Sensor")]
    [SerializeField] private DepthMode depthMode = DepthMode.NFOV_Unbinned;
    [SerializeField] private ColorResolution colorResolution = ColorResolution.Off;
    [SerializeField] private FPS cameraFps = FPS.FPS30;
    [SerializeField] private TrackerProcessingMode processingMode = TrackerProcessingMode.DirectML;

    [Header("Visualización de Diagnóstico")]
    [SerializeField] private bool drawGizmos = true;
    [SerializeField] private float jointGizmoRadius = 0.04f;
    [SerializeField] private Color skeletonColor = Color.cyan;

    private Device kinectDevice;
    private Tracker bodyTracker;
    private bool isInitialized = false;

    // Caché del último esqueleto detectado
    private Skeleton currentSkeleton;
    private bool hasValidBody = false;

    public bool IsInitialized => isInitialized;
    public bool HasDetectedBody => hasValidBody;

    private void Awake()
    {
        PreloadNativeLibraries();
    }

    private void PreloadNativeLibraries()
    {
        try
        {
            string sensorSdkBin = @"C:\Program Files\Azure Kinect SDK v1.4.1\sdk\windows-desktop\amd64\release\bin";
            string bodySdkBin = @"C:\Program Files\Azure Kinect Body Tracking SDK\sdk\windows-desktop\amd64\release\bin";
            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));

            // Priorizar carpetas oficiales del SDK y la raíz del proyecto para búsqueda de DLLs
            SetDllDirectory(sensorSdkBin);

            // Pre-cargar explícitamente depthengine_2_0.dll (crítico para que start_cameras funcione en Unity)
            if (Directory.Exists(sensorSdkBin))
            {
                LoadLibrary(Path.Combine(sensorSdkBin, "depthengine_2_0.dll"));
                LoadLibrary(Path.Combine(sensorSdkBin, "k4a.dll"));
            }

            if (Directory.Exists(bodySdkBin))
            {
                LoadLibrary(Path.Combine(bodySdkBin, "directml.dll"));
                LoadLibrary(Path.Combine(bodySdkBin, "onnxruntime.dll"));
                LoadLibrary(Path.Combine(bodySdkBin, "k4abt.dll"));
            }

            SetDllDirectory(projectRoot);
            Debug.Log("[AzureKinectBodyTracker] Librerías nativas de Azure Kinect pre-cargadas con éxito.");
        }
        catch (Exception ex)
        {
            Debug.LogWarning($"[AzureKinectBodyTracker] Advertencia al pre-cargar librerías nativas: {ex.Message}");
        }
    }

    private void Start()
    {
        if (targetInput == null)
        {
            targetInput = GetComponent<AzureKinectInput>();
        }

        InitializeKinect();
    }

    private void InitializeKinect()
    {
        try
        {
            int deviceCount = Device.GetInstalledCount();
            if (deviceCount == 0)
            {
                Debug.LogWarning("[AzureKinectBodyTracker] ⚠️ No se detectó ningún Azure Kinect conectado por USB 3.0.");
                return;
            }

            // 1. Abrir el primer dispositivo disponible
            Debug.Log("[AzureKinectBodyTracker] Abriendo dispositivo Azure Kinect index 0...");
            kinectDevice = Device.Open(0);
            Debug.Log($"[AzureKinectBodyTracker] Dispositivo abierto exitosamente (Serial: {kinectDevice.SerialNum}).");

            DeviceConfiguration deviceConfig = new DeviceConfiguration
            {
                CameraFPS = cameraFps,
                ColorResolution = colorResolution,
                DepthMode = depthMode,
                SynchronizedImagesOnly = false,
                WiredSyncMode = WiredSyncMode.Standalone
            };

            Debug.Log("[AzureKinectBodyTracker] Iniciando cámaras del sensor...");
            kinectDevice.StartCameras(deviceConfig);
            Debug.Log("[AzureKinectBodyTracker] Cámaras iniciadas a 30 FPS.");

            // 2. Obtener calibración
            Calibration calibration = kinectDevice.GetCalibration(deviceConfig.DepthMode, deviceConfig.ColorResolution);

            // 3. Iniciar Body Tracker con modelo ONNX explícito
            string bodySdkBin = @"C:\Program Files\Azure Kinect Body Tracking SDK\sdk\windows-desktop\amd64\release\bin";
            string projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));

            // Priorizar modelo Lite (optimizado para 30 FPS en tiempo real)
            string modelToUse = Path.Combine(projectRoot, "dnn_model_2_0_lite_op11.onnx");
            if (!File.Exists(modelToUse))
            {
                modelToUse = Path.Combine(bodySdkBin, "dnn_model_2_0_lite_op11.onnx");
            }
            if (!File.Exists(modelToUse))
            {
                modelToUse = Path.Combine(projectRoot, "dnn_model_2_0_op11.onnx");
            }
            if (!File.Exists(modelToUse))
            {
                modelToUse = Path.Combine(bodySdkBin, "dnn_model_2_0_op11.onnx");
            }

            Debug.Log($"[AzureKinectBodyTracker] Ruta del modelo ONNX para articulaciones: {modelToUse}");

            TrackerConfiguration trackerConfig = new TrackerConfiguration
            {
                ModelPath = modelToUse,
                SensorOrientation = SensorOrientation.Default
            };

            TrackerProcessingMode[] modesToTry = new TrackerProcessingMode[]
            {
                processingMode,
                TrackerProcessingMode.DirectML,
                TrackerProcessingMode.Cuda,
                TrackerProcessingMode.Cpu
            };

            bool trackerCreated = false;
            foreach (TrackerProcessingMode mode in modesToTry)
            {
                try
                {
                    trackerConfig.ProcessingMode = mode;
                    Debug.Log($"[AzureKinectBodyTracker] Intentando inicializar Body Tracker en modo: {mode}...");
                    bodyTracker = Tracker.Create(calibration, trackerConfig);
                    Debug.Log($"[AzureKinectBodyTracker] ✅ Body Tracker creado exitosamente en modo: {mode}!");
                    trackerCreated = true;
                    break;
                }
                catch (Exception ex)
                {
                    Debug.LogWarning($"[AzureKinectBodyTracker] Modo {mode} falló: {ex.Message}");
                }
            }

            if (!trackerCreated)
            {
                throw new Exception("No fue posible inicializar el Body Tracker en ningún modo (DirectML, Cuda, Cpu).");
            }

            isInitialized = true;
            Debug.Log("[AzureKinectBodyTracker] ✅ Sistema Kinect 100% operativo en Unity.");
        }
        catch (Exception ex)
        {
            Debug.LogError($"[AzureKinectBodyTracker] Error crítico al inicializar Azure Kinect: {ex.Message}");
            // Liberar el dispositivo para no bloquear el puerto USB
            ShutdownKinect();
        }
    }

    private void Update()
    {
        if (!isInitialized || kinectDevice == null || bodyTracker == null) return;

        try
        {
            // Capturar frame del sensor
            using (Capture capture = kinectDevice.GetCapture())
            {
                if (capture != null)
                {
                    bodyTracker.EnqueueCapture(capture);
                }
            }

            // Extraer resultado del Body Tracking sin bloquear el hilo de renderizado
            using (Microsoft.Azure.Kinect.BodyTracking.Frame frame = bodyTracker.PopResult(TimeSpan.Zero, throwOnTimeout: false))
            {
                if (frame != null && frame.NumberOfBodies > 0)
                {
                    // Seleccionar el cuerpo principal (Jugador 1)
                    Body body = frame.GetBody(0);
                    currentSkeleton = body.Skeleton;
                    hasValidBody = true;

                    // Convertir las articulaciones clave a espacio métrico de Unity
                    Vector3 pelvis = ToUnityVector(currentSkeleton.GetJoint(JointId.Pelvis).Position);
                    Vector3 chest = ToUnityVector(currentSkeleton.GetJoint(JointId.SpineChest).Position);
                    Vector3 rShoulder = ToUnityVector(currentSkeleton.GetJoint(JointId.ShoulderRight).Position);
                    Vector3 rWrist = ToUnityVector(currentSkeleton.GetJoint(JointId.WristRight).Position);
                    Vector3 lShoulder = ToUnityVector(currentSkeleton.GetJoint(JointId.ShoulderLeft).Position);
                    Vector3 lWrist = ToUnityVector(currentSkeleton.GetJoint(JointId.WristLeft).Position);
                    Vector3 rKnee = ToUnityVector(currentSkeleton.GetJoint(JointId.KneeRight).Position);
                    Vector3 rAnkle = ToUnityVector(currentSkeleton.GetJoint(JointId.AnkleRight).Position);
                    Vector3 lKnee = ToUnityVector(currentSkeleton.GetJoint(JointId.KneeLeft).Position);
                    Vector3 lAnkle = ToUnityVector(currentSkeleton.GetJoint(JointId.AnkleLeft).Position);

                    // Notificar al adaptador de combate IFighterInput
                    if (targetInput != null)
                    {
                        targetInput.ProcessSkeletonData(
                            pelvis, chest, rShoulder, rWrist, lShoulder, lWrist,
                            rKnee, rAnkle, lKnee, lAnkle);
                    }
                }
                else
                {
                    hasValidBody = false;
                }
            }
        }
        catch (Exception)
        {
            // Manejo de caídas ocasionales de frame
        }
    }

    /// <summary>
    /// Convierte coordenadas de milímetros de Azure Kinect a metros en el sistema de coordenadas de Unity.
    /// Kinect: X derecha, Y abajo, Z adelante.
    /// Unity:  X derecha, Y arriba, Z adelante.
    /// </summary>
    private Vector3 ToUnityVector(System.Numerics.Vector3 positionInMm)
    {
        return new Vector3(positionInMm.X * 0.001f, -positionInMm.Y * 0.001f, positionInMm.Z * 0.001f);
    }

    private void OnDisable()
    {
        ShutdownKinect();
    }

    private void OnDestroy()
    {
        ShutdownKinect();
    }

    private void OnApplicationQuit()
    {
        ShutdownKinect();
    }

    private void ShutdownKinect()
    {
        if (bodyTracker != null)
        {
            bodyTracker.Dispose();
            bodyTracker = null;
        }

        if (kinectDevice != null)
        {
            try
            {
                kinectDevice.StopCameras();
            }
            catch { }

            try
            {
                kinectDevice.Dispose();
            }
            catch { }

            kinectDevice = null;
        }

        isInitialized = false;
        hasValidBody = false;
    }

    private void OnDrawGizmos()
    {
        if (!drawGizmos || !hasValidBody) return;

        Gizmos.color = skeletonColor;
        for (int i = 0; i < (int)JointId.Count; i++)
        {
            Vector3 pos = ToUnityVector(currentSkeleton.GetJoint((JointId)i).Position);
            Gizmos.DrawSphere(transform.position + pos, jointGizmoRadius);
        }
    }
}
