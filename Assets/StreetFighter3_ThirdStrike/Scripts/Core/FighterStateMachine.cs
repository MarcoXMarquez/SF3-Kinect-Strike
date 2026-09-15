using UnityEngine;
using System.Collections;

/// <summary>
/// Estados de combate básicos para el ciclo de vida del luchador.
/// </summary>
public enum FighterState
{
    Idle,
    WalkForward,
    WalkBackward,
    Crouching,
    Jumping,
    AttackOneShot
}

/// <summary>
/// Máquina de estados desacoplada para luchadores de Street Fighter III (CPS-3).
/// Controla transiciones directas llamando a animator.Play() a 14 FPS sin usar flechas en Mecanim,
/// gestiona los inputs de combate y coordina con FighterPhysics.
/// </summary>
[RequireComponent(typeof(FighterPhysics))]
public class FighterStateMachine : MonoBehaviour
{
    [Header("Referencias")]
    [Tooltip("Controlador de física arcade determinista")]
    [SerializeField] private FighterPhysics fighterPhysics;

    [Tooltip("Animator ubicado en el GameObject hijo 'Visuals' o en este objeto")]
    [SerializeField] private Animator animator;

    [Header("Estado Actual (Lectura en tiempo real)")]
    [SerializeField] private FighterState currentState = FighterState.Idle;
    [SerializeField] private string currentAnimationName = "idle_stance";

    // Hashes precalculados para evitar Garbage Collection (GC) en runtime
    private readonly int hashIdle = Animator.StringToHash("idle_stance");
    private readonly int hashWalkForward = Animator.StringToHash("walk_forward");
    private readonly int hashWalkBackward = Animator.StringToHash("walk_backward");
    private readonly int hashCrouchIdle = Animator.StringToHash("crouch_idle");
    private readonly int hashJumpNeutral = Animator.StringToHash("jump_neutral");
    private readonly int hashJumpForward = Animator.StringToHash("jump_forward");
    private readonly int hashJumpBackward = Animator.StringToHash("jump_backward");
    private readonly int hashLightPunch = Animator.StringToHash("light_punch");
    private readonly int hashHeavyPunch = Animator.StringToHash("heavy_punch");
    private readonly int hashLightKick = Animator.StringToHash("light_kick");
    private readonly int hashHeavyKick = Animator.StringToHash("heavy_kick");
    private readonly int hashCrouchLightPunch = Animator.StringToHash("crouch_light_punch");
    private readonly int hashCrouchHeavyPunch = Animator.StringToHash("crouch_heavy_punch");
    private readonly int hashCrouchLightKick = Animator.StringToHash("crouch_light_kick");
    private readonly int hashCrouchHeavyKick = Animator.StringToHash("crouch_heavy_kick");
    private readonly int hashHadouken = Animator.StringToHash("fireball");

    private Coroutine attackCoroutine;

    // Propiedades públicas
    public FighterState CurrentState => currentState;
    public string CurrentAnimationName => currentAnimationName;

    private void Awake()
    {
        if (fighterPhysics == null)
        {
            fighterPhysics = GetComponent<FighterPhysics>();
        }

        if (animator == null)
        {
            // Busca primero en los hijos (GameObject hijo 'Visuals')
            animator = GetComponentInChildren<Animator>();
        }
    }

    private void OnEnable()
    {
        if (fighterPhysics != null)
        {
            fighterPhysics.OnLanded += HandleLanding;
        }
    }

    private void OnDisable()
    {
        if (fighterPhysics != null)
        {
            fighterPhysics.OnLanded -= HandleLanding;
        }
    }

    private void Start()
    {
        TransitionToState(FighterState.Idle, hashIdle, "idle_stance");
    }

    private void Update()
    {
        // 1. Si está ocupado ejecutando un golpe o súper, esperar a que termine la animación
        if (currentState == FighterState.AttackOneShot)
        {
            // Opcional: cancelar con Espacio durante pruebas
            if (Input.GetKeyDown(KeyCode.Space))
            {
                CancelCurrentAction();
            }
            return;
        }

        // 2. Si está en el aire, la física controla el arco parabólico (Jump Commitment)
        if (currentState == FighterState.Jumping)
        {
            return;
        }

        // 3. Procesar ataques desde el suelo (de pie o agachado)
        if (ProcessAttackInputs())
        {
            return;
        }

        // 4. Procesar Salto
        if (Input.GetKeyDown(KeyCode.W))
        {
            ExecuteJump();
            return;
        }

        // 5. Procesar Agachado (mantener presionado S)
        bool isHoldingCrouch = Input.GetKey(KeyCode.S);

        if (isHoldingCrouch)
        {
            fighterPhysics.StopHorizontal();
            if (currentState != FighterState.Crouching)
            {
                TransitionToState(FighterState.Crouching, hashCrouchIdle, "crouch_idle");
            }
            return;
        }

        // 6. Procesar Locomoción Horizontal (D = Adelante, A = Atrás)
        if (Input.GetKey(KeyCode.D))
        {
            fighterPhysics.Move(1f);
            if (currentState != FighterState.WalkForward)
            {
                TransitionToState(FighterState.WalkForward, hashWalkForward, "walk_forward");
            }
        }
        else if (Input.GetKey(KeyCode.A))
        {
            fighterPhysics.Move(-1f);
            if (currentState != FighterState.WalkBackward)
            {
                TransitionToState(FighterState.WalkBackward, hashWalkBackward, "walk_backward");
            }
        }
        else
        {
            // Reposo total
            fighterPhysics.StopHorizontal();
            if (currentState != FighterState.Idle)
            {
                TransitionToState(FighterState.Idle, hashIdle, "idle_stance");
            }
        }
    }

    /// <summary>
    /// Evalúa la entrada de ataques por teclado. Devuelve true si se disparó un ataque.
    /// </summary>
    private bool ProcessAttackInputs()
    {
        bool isCrouching = Input.GetKey(KeyCode.S);

        // Puño Débil (J)
        if (Input.GetKeyDown(KeyCode.J))
        {
            if (isCrouching)
                ExecuteAttack("crouch_light_punch", hashCrouchLightPunch);
            else
                ExecuteAttack("light_punch", hashLightPunch);
            return true;
        }

        // Puño Fuerte (K)
        if (Input.GetKeyDown(KeyCode.K))
        {
            if (isCrouching)
                ExecuteAttack("crouch_heavy_punch", hashCrouchHeavyPunch);
            else
                ExecuteAttack("heavy_punch", hashHeavyPunch);
            return true;
        }

        // Patada Débil (L)
        if (Input.GetKeyDown(KeyCode.L))
        {
            if (isCrouching)
                ExecuteAttack("crouch_light_kick", hashCrouchLightKick);
            else
                ExecuteAttack("light_kick", hashLightKick);
            return true;
        }

        // Patada Fuerte (O)
        if (Input.GetKeyDown(KeyCode.O))
        {
            if (isCrouching)
                ExecuteAttack("crouch_heavy_kick", hashCrouchHeavyKick);
            else
                ExecuteAttack("heavy_kick", hashHeavyKick);
            return true;
        }

        // Especial Hadouken (U)
        if (Input.GetKeyDown(KeyCode.U))
        {
            ExecuteAttack("fireball", hashHadouken);
            return true;
        }

        return false;
    }

    /// <summary>
    /// Inicia el salto determinando dirección horizontal según las teclas presionadas en el frame de despegue.
    /// </summary>
    private void ExecuteJump()
    {
        float dir = 0f;
        int jumpAnimHash = hashJumpNeutral;
        string animName = "jump_neutral";

        if (Input.GetKey(KeyCode.D))
        {
            dir = 1f;
            jumpAnimHash = hashJumpForward;
            animName = "jump_forward";
        }
        else if (Input.GetKey(KeyCode.A))
        {
            dir = -1f;
            jumpAnimHash = hashJumpBackward;
            animName = "jump_backward";
        }

        fighterPhysics.Jump(dir);
        TransitionToState(FighterState.Jumping, jumpAnimHash, animName);
    }

    /// <summary>
    /// Callback invocado por FighterPhysics al tocar el suelo tras un salto.
    /// </summary>
    private void HandleLanding()
    {
        if (Input.GetKey(KeyCode.S))
        {
            TransitionToState(FighterState.Crouching, hashCrouchIdle, "crouch_idle");
        }
        else if (Input.GetKey(KeyCode.D))
        {
            TransitionToState(FighterState.WalkForward, hashWalkForward, "walk_forward");
        }
        else if (Input.GetKey(KeyCode.A))
        {
            TransitionToState(FighterState.WalkBackward, hashWalkBackward, "walk_backward");
        }
        else
        {
            TransitionToState(FighterState.Idle, hashIdle, "idle_stance");
        }
    }

    /// <summary>
    /// Dispara un ataque One-Shot desacoplado y gestiona el retorno automático al finalizar.
    /// </summary>
    private void ExecuteAttack(string animName, int animHash)
    {
        fighterPhysics.StopHorizontal();

        if (attackCoroutine != null)
        {
            StopCoroutine(attackCoroutine);
        }

        attackCoroutine = StartCoroutine(AttackRoutine(animName, animHash));
    }

    private IEnumerator AttackRoutine(string animName, int animHash)
    {
        currentState = FighterState.AttackOneShot;
        currentAnimationName = animName;

        PlayAnimation(animHash);

        // Esperar 1 frame para que Mecanim registre el estado y exponga la duración real del clip
        yield return null;

        float duration = 0.35f;
        if (animator != null)
        {
            AnimatorStateInfo stateInfo = animator.GetCurrentAnimatorStateInfo(0);
            if (stateInfo.length > 0.05f)
            {
                duration = stateInfo.length;
            }
        }

        yield return new WaitForSeconds(duration);

        // Retorno automático: si sigue manteniendo agachado, volver a crouch; si no, a idle
        if (Input.GetKey(KeyCode.S))
        {
            TransitionToState(FighterState.Crouching, hashCrouchIdle, "crouch_idle");
        }
        else
        {
            TransitionToState(FighterState.Idle, hashIdle, "idle_stance");
        }
    }

    private void CancelCurrentAction()
    {
        if (attackCoroutine != null)
        {
            StopCoroutine(attackCoroutine);
        }
        TransitionToState(FighterState.Idle, hashIdle, "idle_stance");
    }

    /// <summary>
    /// Transición limpia de estado con disparo instantáneo de animación sin transiciones con flechas.
    /// </summary>
    private void TransitionToState(FighterState newState, int animHash, string animName)
    {
        currentState = newState;
        currentAnimationName = animName;
        PlayAnimation(animHash);
    }

    private void PlayAnimation(int animHash)
    {
        if (animator != null)
        {
            animator.Play(animHash, 0, 0f);
        }
    }

    private void OnGUI()
    {
        // HUD de depuración para probar el estado y la física en modo Play
        GUI.Box(new Rect(10, 10, 360, 260), "🥋 SF3 - Core Fighter State Machine");

        GUI.Label(new Rect(20, 35, 340, 22), $"<b>Estado:</b> <color=cyan>{currentState}</color>");
        GUI.Label(new Rect(20, 55, 340, 22), $"<b>Animación:</b> <color=yellow>{currentAnimationName}</color>");
        GUI.Label(new Rect(20, 75, 340, 22), $"<b>Suelo (Grounded):</b> {(fighterPhysics.IsGrounded ? "<color=green>SÍ</color>" : "<color=red>EN EL AIRE</color>")}");
        GUI.Label(new Rect(20, 95, 340, 22), $"<b>Velocidad:</b> {fighterPhysics.Velocity}");

        GUI.Label(new Rect(20, 125, 340, 20), "• [D] / [A] : Caminar Adelante / Atrás");
        GUI.Label(new Rect(20, 145, 340, 20), "• [S] (Mantener) : Agacharse");
        GUI.Label(new Rect(20, 165, 340, 20), "• [W] (+ D / A)  : Salto Parabólico CPS-3");
        GUI.Label(new Rect(20, 185, 340, 20), "• [J] / [K]      : Puño Débil / Fuerte");
        GUI.Label(new Rect(20, 205, 340, 20), "• [L] / [O]      : Patada Débil / Fuerte");
        GUI.Label(new Rect(20, 225, 340, 20), "• [U]            : Hadouken (fireball)");
    }
}
