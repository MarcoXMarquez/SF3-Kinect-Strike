using UnityEngine;

public class ParallaxBackground : MonoBehaviour
{
    [System.Serializable]
    public class ParallaxLayer
    {
        public Transform layerTransform;
        [Range(0f, 1f)]
        public float parallaxFactorX = 0.5f;
        [Range(0f, 1f)]
        public float parallaxFactorY = 0.1f;
        [HideInInspector]
        public Vector3 startPosition;
    }

    public Transform targetCamera;
    public ParallaxLayer[] layers;

    private Vector3 lastCameraPosition;

    void Start()
    {
        if (targetCamera == null && Camera.main != null)
        {
            targetCamera = Camera.main.transform;
        }

        if (targetCamera != null)
        {
            lastCameraPosition = targetCamera.position;
        }

        foreach (var layer in layers)
        {
            if (layer.layerTransform != null)
            {
                layer.startPosition = layer.layerTransform.position;
            }
        }
    }

    void LateUpdate()
    {
        if (targetCamera == null) return;

        Vector3 deltaMovement = targetCamera.position - lastCameraPosition;

        foreach (var layer in layers)
        {
            if (layer.layerTransform != null)
            {
                Vector3 newPos = layer.layerTransform.position;
                newPos.x += deltaMovement.x * layer.parallaxFactorX;
                newPos.y += deltaMovement.y * layer.parallaxFactorY;
                layer.layerTransform.position = newPos;
            }
        }

        lastCameraPosition = targetCamera.position;
    }
}
