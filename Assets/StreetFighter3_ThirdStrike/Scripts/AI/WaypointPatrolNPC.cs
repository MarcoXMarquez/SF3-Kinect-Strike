using System.Collections;
using UnityEngine;
using StreetFighter3.Loading;

namespace Minigame.Waypoints
{
    public enum PatrolState
    {
        Patrolling,
        WaitingAtWaypoint,
        Alert,
        ChasingPlayer
    }

    [RequireComponent(typeof(SpriteRenderer))]
    public class WaypointPatrolNPC : MonoBehaviour
    {
        [Header("Ruta y Movimiento")]
        [SerializeField] private WaypointCircuit circuit;
        [SerializeField] private float moveSpeed = 3.2f;
        [SerializeField] private float chaseSpeed = 4.2f;
        [SerializeField] private float reachThreshold = 0.2f;
        [SerializeField] private float waitTimeAtWaypoint = 1.0f;

        [Header("Deteccion y Alerta")]
        [SerializeField] private float detectionRadius = 2.4f;
        [SerializeField] private float catchDistance = 0.85f;
        [SerializeField] private Transform targetPlayer;

        [Header("Animaciones por Cuadros")]
        [SerializeField] private Sprite[] idleFrames;
        [SerializeField] private Sprite[] walkFrames;
        [SerializeField] private Sprite[] alertFrames;

        [Header("Referencias")]
        [SerializeField] private SpriteRenderer spriteRenderer;
        [SerializeField] private SpriteFrameAnimator frameAnimator;

        private int currentWaypointIndex = 0;
        private int pingPongDirection = 1;
        private PatrolState currentState = PatrolState.Patrolling;
        private float waitTimer = 0f;
        private bool hasCaughtPlayer = false;
        private System.Action onPlayerCaughtCallback;

        public PatrolState CurrentState => currentState;
        public int CurrentWaypointIndex => currentWaypointIndex;
        public Transform TargetPlayer => targetPlayer;

        private void Awake()
        {
            if (spriteRenderer == null) spriteRenderer = GetComponent<SpriteRenderer>();
            if (frameAnimator == null)
            {
                frameAnimator = GetComponent<SpriteFrameAnimator>();
                if (frameAnimator == null) frameAnimator = gameObject.AddComponent<SpriteFrameAnimator>();
            }
        }

        private void Start()
        {
            if (circuit != null && circuit.WaypointCount > 0)
            {
                currentWaypointIndex = circuit.GetClosestWaypointIndex(transform.position);
                transform.position = circuit.GetPosition(currentWaypointIndex);
            }

            PlayWalkAnimation();
        }

        private void Update()
        {
            if (hasCaughtPlayer) return;

            // 1. Comprobar deteccion del jugador
            CheckPlayerProximity();

            // 2. Gestionar maquina de estados de patrulla
            switch (currentState)
            {
                case PatrolState.Patrolling:
                    ExecutePatrolMovement();
                    break;

                case PatrolState.WaitingAtWaypoint:
                    ExecuteWaitAtWaypoint();
                    break;

                case PatrolState.ChasingPlayer:
                    ExecuteChasePlayer();
                    break;
            }
        }

        private void ExecutePatrolMovement()
        {
            if (circuit == null || circuit.WaypointCount == 0) return;

            Vector3 targetPos = circuit.GetPosition(currentWaypointIndex);
            Vector3 currentPos = transform.position;
            Vector3 diff = targetPos - currentPos;
            diff.z = 0f;

            float dist = diff.magnitude;

            if (dist <= reachThreshold)
            {
                // Llegada al punto de referencia (Waypoint)
                transform.position = new Vector3(targetPos.x, targetPos.y, currentPos.z);
                currentState = PatrolState.WaitingAtWaypoint;
                waitTimer = waitTimeAtWaypoint;
                PlayIdleAnimation();
                return;
            }

            Vector3 moveDir = diff.normalized;
            transform.position += moveDir * (moveSpeed * Time.deltaTime);

            UpdateFacingDirection(moveDir.x);
        }

        private void ExecuteWaitAtWaypoint()
        {
            waitTimer -= Time.deltaTime;
            if (waitTimer <= 0f)
            {
                // Avanzar al siguiente nodo del circuito
                currentWaypointIndex = circuit.GetNextIndex(currentWaypointIndex, ref pingPongDirection);
                currentState = PatrolState.Patrolling;
                PlayWalkAnimation();
            }
        }

        private void ExecuteChasePlayer()
        {
            if (targetPlayer == null)
            {
                ReturnToPatrol();
                return;
            }

            Vector3 playerPos = targetPlayer.position;
            Vector3 currentPos = transform.position;
            Vector3 diff = playerPos - currentPos;
            diff.z = 0f;

            float dist = diff.magnitude;

            if (dist <= catchDistance)
            {
                TriggerCatchPlayer();
                return;
            }

            // Si el jugador se aleja demasiado, retomar ruta de waypoints
            if (dist > detectionRadius * 1.5f)
            {
                ReturnToPatrol();
                return;
            }

            Vector3 moveDir = diff.normalized;
            transform.position += moveDir * (chaseSpeed * Time.deltaTime);

            UpdateFacingDirection(moveDir.x);
        }

        private void CheckPlayerProximity()
        {
            if (targetPlayer == null) return;

            float dist = Vector2.Distance(transform.position, targetPlayer.position);

            if (dist <= catchDistance)
            {
                TriggerCatchPlayer();
                return;
            }

            if (dist <= detectionRadius && currentState != PatrolState.ChasingPlayer)
            {
                currentState = PatrolState.ChasingPlayer;
                PlayAlertOrWalkAnimation();
            }
        }

        private void ReturnToPatrol()
        {
            if (circuit != null)
            {
                currentWaypointIndex = circuit.GetClosestWaypointIndex(transform.position);
            }
            currentState = PatrolState.Patrolling;
            PlayWalkAnimation();
        }

        private void TriggerCatchPlayer()
        {
            if (hasCaughtPlayer) return;
            hasCaughtPlayer = true;
            currentState = PatrolState.Alert;

            PlayIdleAnimation();
            onPlayerCaughtCallback?.Invoke();
        }

        private void UpdateFacingDirection(float horizontalDir)
        {
            if (spriteRenderer == null) return;

            if (horizontalDir > 0.05f)
            {
                spriteRenderer.flipX = false;
            }
            else if (horizontalDir < -0.05f)
            {
                spriteRenderer.flipX = true;
            }
        }

        public void SetCircuit(WaypointCircuit newCircuit)
        {
            circuit = newCircuit;
            if (circuit != null && circuit.WaypointCount > 0)
            {
                currentWaypointIndex = 0;
            }
        }

        public void SetTargetPlayer(Transform player)
        {
            targetPlayer = player;
        }

        public void SetAnimationFrames(Sprite[] idle, Sprite[] walk, Sprite[] alert = null)
        {
            idleFrames = idle;
            walkFrames = walk;
            alertFrames = alert;
        }

        public void SetOnPlayerCaughtCallback(System.Action callback)
        {
            onPlayerCaughtCallback = callback;
        }

        public void ResetToWaypoint(int waypointIndex = 0)
        {
            hasCaughtPlayer = false;
            currentWaypointIndex = waypointIndex;
            if (circuit != null && circuit.WaypointCount > 0)
            {
                transform.position = circuit.GetPosition(currentWaypointIndex);
            }
            currentState = PatrolState.Patrolling;
            PlayWalkAnimation();
        }

        private void PlayIdleAnimation()
        {
            if (frameAnimator != null && idleFrames != null && idleFrames.Length > 0)
            {
                frameAnimator.PlayAnimation(idleFrames, true);
            }
        }

        private void PlayWalkAnimation()
        {
            if (frameAnimator != null && walkFrames != null && walkFrames.Length > 0)
            {
                frameAnimator.PlayAnimation(walkFrames, true);
            }
        }

        private void PlayAlertOrWalkAnimation()
        {
            if (frameAnimator != null)
            {
                if (alertFrames != null && alertFrames.Length > 0)
                {
                    frameAnimator.PlayAnimation(alertFrames, true);
                }
                else if (walkFrames != null && walkFrames.Length > 0)
                {
                    frameAnimator.PlayAnimation(walkFrames, true);
                }
            }
        }

        private void OnDrawGizmosSelected()
        {
            // Radio de alerta
            Gizmos.color = new Color(1f, 0.9f, 0.1f, 0.4f);
            Gizmos.DrawWireSphere(transform.position, detectionRadius);

            // Radio de captura
            Gizmos.color = new Color(1f, 0.2f, 0.2f, 0.8f);
            Gizmos.DrawWireSphere(transform.position, catchDistance);

            // Linea hacia el waypoint activo
            if (circuit != null && circuit.WaypointCount > 0)
            {
                Gizmos.color = Color.magenta;
                Gizmos.DrawLine(transform.position, circuit.GetPosition(currentWaypointIndex));
            }
        }
    }
}
