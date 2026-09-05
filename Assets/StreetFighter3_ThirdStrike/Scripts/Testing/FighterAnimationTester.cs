using UnityEngine;
using System.Collections;

/// <summary>
/// Probador interactivo de combate y maquina de estados para Street Fighter III.
/// Permite probar golpes con retorno automatico a reposo (idle) y locomocion fluida con teclado.
/// </summary>
public class FighterAnimationTester : MonoBehaviour
{
    [Header("Referencias")]
    [Tooltip("El componente Animator (en este objeto o en el hijo 'Visuals')")]
    public Animator animator;

    [Header("Estado Actual")]
    [SerializeField] private string currentAnimation = "idle_stance";
    [SerializeField] private bool isBusyWithAction = false;

    [Header("Instrucciones de Teclas en Play")]
    [TextArea(12, 16)]
    public string guiaControles =
        "=== CONTROLES DE PRUEBA EN VIVO ===\n" +
        "• [D] / [A] (Mantener) -> Caminar adelante / atras\n" +
        "• [S]       (Mantener) -> Agacharse (crouch_idle)\n" +
        "• [W]                  -> Saltar (jump_neutral)\n" +
        "• [J] / [K]            -> Puño Débil / Fuerte (de pie o agachado)\n" +
        "• [L] / [O]            -> Patada Débil / Fuerte (de pie o agachado)\n" +
        "• [U]                  -> Hadouken (fireball)\n" +
        "• [I]                  -> Shoryuken (shoryuken)\n" +
        "• [Y]                  -> Tatsumaki (hurricane)\n" +
        "• [T]                  -> Super Art (super_art_2 / denjin)\n" +
        "• [P] / [H]            -> Parry / Recibir Golpe\n" +
        "• [Espacio]            -> Forzar reposo (idle_stance)";

    private Coroutine actionCoroutine;

    void Awake()
    {
        if (animator == null)
        {
            animator = GetComponentInChildren<Animator>();
        }
    }

    void Start()
    {
        PlayIdle();
    }

    void Update()
    {
        // 1. Si está en medio de una acción activa, esperar a que finalice (o cancelar con Espacio)
        if (isBusyWithAction)
        {
            if (Input.GetKeyDown(KeyCode.Space))
            {
                if (actionCoroutine != null) StopCoroutine(actionCoroutine);
                isBusyWithAction = false;
                PlayIdle();
            }
            return;
        }

        bool isCrouching = Input.GetKey(KeyCode.S);

        // 2. Puños (J = Débil / Medio, K = Fuerte)
        if (Input.GetKeyDown(KeyCode.J))
        {
            string anim = isCrouching ? "crouch_light_punch" : "light_punch";
            ExecuteOneShotAction(anim);
            return;
        }
        if (Input.GetKeyDown(KeyCode.K))
        {
            string anim = isCrouching ? "crouch_heavy_punch" : (HasState("heavy_punch") ? "heavy_punch" : "medium_punch");
            ExecuteOneShotAction(anim);
            return;
        }

        // 3. Patadas (L = Débil, O = Fuerte / Media)
        if (Input.GetKeyDown(KeyCode.L))
        {
            string anim = isCrouching ? "crouch_light_kick" : "light_kick";
            ExecuteOneShotAction(anim);
            return;
        }
        if (Input.GetKeyDown(KeyCode.O))
        {
            string anim = isCrouching ? "crouch_heavy_kick" : (HasState("heavy_kick") ? "heavy_kick" : "medium_kick");
            ExecuteOneShotAction(anim);
            return;
        }

        // 4. Movimientos especiales y Súpers
        if (Input.GetKeyDown(KeyCode.U))
        {
            if (HasState("special_hadouken")) ExecuteOneShotAction("special_hadouken");
            else if (HasState("fireball")) ExecuteOneShotAction("fireball");
            return;
        }
        if (Input.GetKeyDown(KeyCode.I))
        {
            if (HasState("special_shoryuken")) ExecuteOneShotAction("special_shoryuken");
            else if (HasState("shoryuken")) ExecuteOneShotAction("shoryuken");
            return;
        }
        if (Input.GetKeyDown(KeyCode.Y))
        {
            if (HasState("hurricane")) ExecuteOneShotAction("hurricane");
            else if (HasState("halfcircle_forward_kick")) ExecuteOneShotAction("halfcircle_forward_kick");
            return;
        }
        if (Input.GetKeyDown(KeyCode.T))
        {
            if (HasState("super_art_2")) ExecuteOneShotAction("super_art_2");
            else if (HasState("denjin")) ExecuteOneShotAction("denjin");
            else if (HasState("taunt")) ExecuteOneShotAction("taunt");
            return;
        }

        // 5. Defensa y Reacciones (Parry, Hit)
        if (Input.GetKeyDown(KeyCode.P))
        {
            if (HasState("parry_standing")) ExecuteOneShotAction("parry_standing");
            else if (HasState("parry_high")) ExecuteOneShotAction("parry_high");
            return;
        }
        if (Input.GetKeyDown(KeyCode.H))
        {
            string anim = isCrouching ? "hit_crouching" : "hit_standing";
            ExecuteOneShotAction(anim);
            return;
        }

        // 6. Salto simple
        if (Input.GetKeyDown(KeyCode.W))
        {
            if (Input.GetKey(KeyCode.D)) ExecuteOneShotAction("jump_forward");
            else if (Input.GetKey(KeyCode.A)) ExecuteOneShotAction("jump_backward");
            else ExecuteOneShotAction("jump_neutral");
            return;
        }

        // 7. Locomoción continua (Mantener presionada la tecla)
        if (Input.GetKey(KeyCode.D))
        {
            if (currentAnimation != "walk_forward") PlayLoop("walk_forward");
        }
        else if (Input.GetKey(KeyCode.A))
        {
            if (currentAnimation != "walk_backward") PlayLoop("walk_backward");
        }
        else if (isCrouching)
        {
            if (currentAnimation != "crouch_idle") PlayLoop("crouch_idle");
        }
        else
        {
            if (currentAnimation != "idle_stance") PlayIdle();
        }
    }

    /// <summary>
    /// Ejecuta una animación de ataque/reacción y regresa automáticamente al estado neutral.
    /// </summary>
    private void ExecuteOneShotAction(string animName)
    {
        if (animator == null) return;

        if (actionCoroutine != null)
        {
            StopCoroutine(actionCoroutine);
        }

        actionCoroutine = StartCoroutine(ActionRoutine(animName));
    }

    private IEnumerator ActionRoutine(string animName)
    {
        isBusyWithAction = true;
        currentAnimation = animName;

        animator.Play(animName, 0, 0f);

        // Esperar un frame para que el Animator actualice su estado
        yield return null;

        AnimatorStateInfo stateInfo = animator.GetCurrentAnimatorStateInfo(0);
        float clipDuration = stateInfo.length;

        // Fallback por si la duración reportada no está lista
        if (clipDuration <= 0.05f)
        {
            clipDuration = 0.4f;
        }

        yield return new WaitForSeconds(clipDuration);

        isBusyWithAction = false;
        
        // Si sigue agachado, regresar a crouch_idle, si no a idle_stance
        if (Input.GetKey(KeyCode.S))
        {
            PlayLoop("crouch_idle");
        }
        else
        {
            PlayIdle();
        }
    }

    private void PlayLoop(string animName)
    {
        if (animator == null) return;
        currentAnimation = animName;
        animator.Play(animName, 0, 0f);
    }

    private void PlayIdle()
    {
        if (animator == null) return;
        currentAnimation = "idle_stance";
        animator.Play("idle_stance", 0, 0f);
    }

    private bool HasState(string stateName)
    {
        if (animator == null || animator.runtimeAnimatorController == null) return false;
        return animator.HasState(0, Animator.StringToHash(stateName));
    }

    void OnGUI()
    {
        GUI.Box(new Rect(10, 10, 360, 320), "🥋 SF3 - Tester de Combate y Estados");
        
        string statusText = isBusyWithAction ? "<color=red>[EJECUTANDO ACCION]</color>" : "<color=green>[NEUTRAL / LIBRE]</color>";
        GUI.Label(new Rect(20, 35, 340, 25), $"<b>Estado:</b> {statusText}");
        GUI.Label(new Rect(20, 55, 340, 25), $"<b>Animacion:</b> <color=yellow>{currentAnimation}</color>");

        GUI.Label(new Rect(20, 85, 340, 20), "• [D] / [A] (Mantener) : Caminar Adelante / Atrás");
        GUI.Label(new Rect(20, 105, 340, 20), "• [S]       (Mantener) : Agacharse");
        GUI.Label(new Rect(20, 125, 340, 20), "• [W]                  : Saltar");
        GUI.Label(new Rect(20, 145, 340, 20), "• [J] / [K]            : Puño Débil / Fuerte");
        GUI.Label(new Rect(20, 165, 340, 20), "• [L] / [O]            : Patada Débil / Fuerte");
        GUI.Label(new Rect(20, 185, 340, 20), "• [U]                  : Hadouken (fireball)");
        GUI.Label(new Rect(20, 205, 340, 20), "• [I]                  : Shoryuken (shoryuken)");
        GUI.Label(new Rect(20, 225, 340, 20), "• [Y]                  : Tatsumaki (hurricane)");
        GUI.Label(new Rect(20, 245, 340, 20), "• [T]                  : Super Art 2 / Denjin");
        GUI.Label(new Rect(20, 265, 340, 20), "• [P] / [H]            : Parry / Recibir Golpe");
        GUI.Label(new Rect(20, 285, 340, 20), "• [Espacio]            : Forzar Cancel a Idle");
    }
}
