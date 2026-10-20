using UnityEngine;

namespace Minigame.Waypoints
{
    public enum WaypointTraversalMode
    {
        Loop,
        PingPong,
        Random
    }

    public class WaypointCircuit : MonoBehaviour
    {
        [Header("Configuracion de Ruta")]
        [SerializeField] private WaypointTraversalMode traversalMode = WaypointTraversalMode.Loop;
        [SerializeField] private Transform[] customWaypoints;

        [Header("Visualizacion en Editor")]
        [SerializeField] private Color pathColor = new Color(0.2f, 0.8f, 1f, 0.9f);
        [SerializeField] private float nodeRadius = 0.3f;
        [SerializeField] private bool showGizmos = true;

        public WaypointTraversalMode TraversalMode => traversalMode;
        public int WaypointCount => GetWaypoints().Length;

        public Transform[] GetWaypoints()
        {
            if (customWaypoints != null && customWaypoints.Length > 0)
            {
                return customWaypoints;
            }

            int childCount = transform.childCount;
            Transform[] children = new Transform[childCount];
            for (int i = 0; i < childCount; i++)
            {
                children[i] = transform.GetChild(i);
            }
            return children;
        }

        public Vector3 GetPosition(int index)
        {
            Transform[] points = GetWaypoints();
            if (points == null || points.Length == 0) return transform.position;
            index = Mathf.Clamp(index, 0, points.Length - 1);
            return points[index] != null ? points[index].position : transform.position;
        }

        public int GetNextIndex(int currentIndex, ref int direction)
        {
            Transform[] points = GetWaypoints();
            int count = points.Length;
            if (count <= 1) return 0;

            switch (traversalMode)
            {
                case WaypointTraversalMode.Loop:
                    return (currentIndex + 1) % count;

                case WaypointTraversalMode.PingPong:
                    if (currentIndex + direction >= count)
                    {
                        direction = -1;
                    }
                    else if (currentIndex + direction < 0)
                    {
                        direction = 1;
                    }
                    return Mathf.Clamp(currentIndex + direction, 0, count - 1);

                case WaypointTraversalMode.Random:
                    if (count <= 1) return 0;
                    int next = currentIndex;
                    while (next == currentIndex)
                    {
                        next = Random.Range(0, count);
                    }
                    return next;

                default:
                    return (currentIndex + 1) % count;
            }
        }

        public int GetClosestWaypointIndex(Vector3 currentPosition)
        {
            Transform[] points = GetWaypoints();
            if (points == null || points.Length == 0) return 0;

            int closestIndex = 0;
            float minSqrDistance = float.MaxValue;

            for (int i = 0; i < points.Length; i++)
            {
                if (points[i] == null) continue;
                float sqrDist = (points[i].position - currentPosition).sqrMagnitude;
                if (sqrDist < minSqrDistance)
                {
                    minSqrDistance = sqrDist;
                    closestIndex = i;
                }
            }

            return closestIndex;
        }

        public void SetCustomWaypoints(Transform[] points, WaypointTraversalMode mode = WaypointTraversalMode.Loop)
        {
            customWaypoints = points;
            traversalMode = mode;
        }

        private void OnDrawGizmos()
        {
            if (!showGizmos) return;

            Transform[] points = GetWaypoints();
            if (points == null || points.Length == 0) return;

            Gizmos.color = pathColor;

            for (int i = 0; i < points.Length; i++)
            {
                if (points[i] == null) continue;

                Vector3 current = points[i].position;
                Gizmos.DrawWireSphere(current, nodeRadius);

                // Dibujar identificador del primer punto
                if (i == 0)
                {
                    Gizmos.color = Color.green;
                    Gizmos.DrawSphere(current, nodeRadius * 0.5f);
                    Gizmos.color = pathColor;
                }

                if (i < points.Length - 1 && points[i + 1] != null)
                {
                    Gizmos.DrawLine(current, points[i + 1].position);
                }
                else if (traversalMode == WaypointTraversalMode.Loop && points[0] != null)
                {
                    Gizmos.DrawLine(current, points[0].position);
                }
            }
        }
    }
}
