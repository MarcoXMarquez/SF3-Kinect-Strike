using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

/// <summary>
/// Estructura del paquete de telemetría transmitido por test_live_kinect_classifier.py
/// vía UDP (puerto 5005 por defecto).
/// </summary>
[Serializable]
public struct KinectGesturePacket
{
    public string action;
    public int action_id;
    public float confidence;
    public bool has_body;
    public double timestamp;
    public float z_distance;
}

/// <summary>
/// Receptor UDP no bloqueante y thread-safe para la clasificación de gestos de Kinect en tiempo real.
/// Permite desacoplar el modelo de Machine Learning en Python del ciclo de renderizado de Unity.
/// </summary>
public class KinectUDPReceiver : MonoBehaviour
{
    public static KinectUDPReceiver Instance { get; private set; }

    [Header("Configuración de Red UDP")]
    [Tooltip("Puerto local donde se escucharán los datagramas de test_live_kinect_classifier.py")]
    [SerializeField] private int listenPort = 5005;

    [Header("Estado de Conexión")]
    [SerializeField] private bool isConnected = false;
    [SerializeField] private string latestAction = "idle";
    [SerializeField] private float latestConfidence = 1.0f;
    [SerializeField] private bool bodyDetected = false;
    [SerializeField] private float playerDistanceZ = 0f;
    [SerializeField] private int totalPacketsReceived = 0;

    private UdpClient udpClient;
    private IPEndPoint remoteEndPoint;
    private float lastPacketTime = -999f;
    private KinectGesturePacket latestPacket;

    public bool IsConnected => (Time.time - lastPacketTime) < 1.6f;
    public string CurrentAction => latestPacket.action ?? "idle";
    public int CurrentActionId => latestPacket.action_id;
    public float CurrentConfidence => latestPacket.confidence;
    public bool HasBody => latestPacket.has_body;
    public float ZDistance => latestPacket.z_distance;
    public double Timestamp => latestPacket.timestamp;
    public int TotalPackets => totalPacketsReceived;

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
        InitializeSocket();
    }

    private void InitializeSocket()
    {
        try
        {
            remoteEndPoint = new IPEndPoint(IPAddress.Any, 0);
            udpClient = new UdpClient(listenPort);
            udpClient.Client.Blocking = false;
            udpClient.Client.ReceiveTimeout = 100;
            Debug.Log($"[KinectUDPReceiver] Escuchando datagramas UDP en el puerto {listenPort}...");
        }
        catch (SocketException ex)
        {
            Debug.LogWarning($"[KinectUDPReceiver] Puerto {listenPort} ya en uso o no disponible ({ex.SocketErrorCode}): {ex.Message}");
        }
        catch (Exception ex)
        {
            Debug.LogError($"[KinectUDPReceiver] Error inicializando socket UDP: {ex.Message}");
        }
    }

    private void Update()
    {
        if (udpClient == null) return;

        // Drenar el buffer de red y conservar el paquete más reciente para minimizar latencia
        while (udpClient.Available > 0)
        {
            try
            {
                byte[] rawData = udpClient.Receive(ref remoteEndPoint);
                if (rawData != null && rawData.Length > 0)
                {
                    string json = Encoding.UTF8.GetString(rawData);
                    KinectGesturePacket pkt = JsonUtility.FromJson<KinectGesturePacket>(json);

                    latestPacket = pkt;
                    latestAction = pkt.action;
                    latestConfidence = pkt.confidence;
                    bodyDetected = pkt.has_body;
                    playerDistanceZ = pkt.z_distance;
                    lastPacketTime = Time.time;
                    totalPacketsReceived++;
                }
            }
            catch (SocketException)
            {
                // No hay más datos disponibles en el buffer no bloqueante
                break;
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[KinectUDPReceiver] Excepción al procesar datagrama: {ex.Message}");
                break;
            }
        }

        isConnected = IsConnected;
    }

    private void OnDestroy()
    {
        CloseSocket();
        if (Instance == this) Instance = null;
    }

    private void OnApplicationQuit()
    {
        CloseSocket();
    }

    private void CloseSocket()
    {
        if (udpClient != null)
        {
            try
            {
                udpClient.Close();
                udpClient.Dispose();
            }
            catch (Exception)
            {
                // Ignorar en cierre
            }
            udpClient = null;
        }
    }
}
