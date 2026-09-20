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
    [SerializeField] private bool reviewMode = false;
    [SerializeField] private int reviewIndex = 0;

    private static readonly string[] reviewAnimations =
    {
        "crouch_down",
        "crouch_idle",
        "dash_backward",
        "dash_forward",
        "idle_stance",
        "jump_backward",
        "jump_forward",
        "jump_neutral",
        "walk_backward",
        "walk_forward",
        "back_medium_kick",
        "crouch_heavy_kick",
        "crouch_heavy_punch",
        "crouch_light_kick",
        "crouch_light_punch",
        "crouch_medium_kick",
        "crouch_medium_punch",
        "forward_heavy_kick",
        "forward_medium_kick",
        "heavy_kick",
        "heavy_punch",
        "heavy_punch_close",
        "jump_forward_heavy_kick",
        "jump_forward_medium_kick",
        "jump_heavy_kick",
        "jump_heavy_punch",
        "jump_light_kick",
        "jump_light_punch",
        "jump_medium_kick",
        "jump_medium_punch",
        "light_kick",
        "light_punch",
        "light_punch_close",
        "medium_kick",
        "medium_punch",
        "medium_punch_close",
        "fhkfake",
        "fireball",
        "flamingdp",
        "hurricane",
        "sf3kenhadouken2",
        "stance_lbx",
        "straight",
        "super_art_1",
        "super_art_2",
        "super_art_3",
        "super_art_3miss",
        "whats_this",
        "block_crouching",
        "block_high",
        "block_standing",
        "hit_crouching",
        "hit_electrocuted",
        "hit_standing",
        "knockdown_slam",
        "knockdown_twist",
        "parry_crouching",
        "parry_standing",
        "kneegrab",
        "throw_backward",
        "throw_forward",
        "throwmiss",
        "intro_1",
        "intro_2",
        "intro_3",
        "intro_4",
        "special_ryu_intro",
        "taunt",
        "taunt_red",
        "thumb",
        "victory_pose_1",
        "victory_pose_2",
        "defeat_chip_death",
        "defeat_timeout",
    };

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
        "• [Espacio]            -> Forzar reposo (idle_stance)\n" +
        "• [R]                  -> Modo revision 74 animaciones\n" +
        "• [N] / [B]            -> Siguiente / anterior animacion\n" +
        "• [Enter]              -> Repetir animacion actual";

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
        if (Input.GetKeyDown(KeyCode.R))
        {
            ToggleReviewMode();
        }

        if (reviewMode)
        {
            HandleReviewModeInput();
            return;
        }

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
            else if (HasState("flamingdp")) ExecuteOneShotAction("flamingdp");
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

    private void ToggleReviewMode()
    {
        reviewMode = !reviewMode;

        if (actionCoroutine != null)
        {
            StopCoroutine(actionCoroutine);
            actionCoroutine = null;
        }

        isBusyWithAction = false;

        if (reviewMode)
        {
            reviewIndex = Mathf.Clamp(reviewIndex, 0, reviewAnimations.Length - 1);
            PlayReviewAnimation();
        }
        else
        {
            PlayIdle();
        }
    }

    private void HandleReviewModeInput()
    {
        if (Input.GetKeyDown(KeyCode.N) || Input.GetKeyDown(KeyCode.PageDown) || Input.GetKeyDown(KeyCode.RightBracket))
        {
            MoveReviewIndex(1);
            return;
        }

        if (Input.GetKeyDown(KeyCode.B) || Input.GetKeyDown(KeyCode.PageUp) || Input.GetKeyDown(KeyCode.LeftBracket))
        {
            MoveReviewIndex(-1);
            return;
        }

        if (Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.KeypadEnter))
        {
            PlayReviewAnimation();
            return;
        }

        if (Input.GetKeyDown(KeyCode.Space))
        {
            reviewMode = false;
            PlayIdle();
        }
    }

    private void MoveReviewIndex(int direction)
    {
        reviewIndex += direction;

        if (reviewIndex < 0)
        {
            reviewIndex = reviewAnimations.Length - 1;
        }
        else if (reviewIndex >= reviewAnimations.Length)
        {
            reviewIndex = 0;
        }

        PlayReviewAnimation();
    }

    private void PlayReviewAnimation()
    {
        if (animator == null) return;

        string animName = reviewAnimations[reviewIndex];

        if (!HasState(animName))
        {
            Debug.LogWarning($"No existe el estado de animacion '{animName}' en {animator.name}.");
            currentAnimation = $"MISSING: {animName}";
            return;
        }

        currentAnimation = animName;
        animator.Play(animName, 0, 0f);
    }

    void OnGUI()
    {
        GUI.Box(new Rect(10, 10, 410, 385), "🥋 SF3 - Tester de Combate y Estados");
        
        string statusText = isBusyWithAction ? "<color=red>[EJECUTANDO ACCION]</color>" : "<color=green>[NEUTRAL / LIBRE]</color>";
        GUI.Label(new Rect(20, 35, 340, 25), $"<b>Estado:</b> {statusText}");
        GUI.Label(new Rect(20, 55, 340, 25), $"<b>Animacion:</b> <color=yellow>{currentAnimation}</color>");
        GUI.Label(new Rect(20, 75, 380, 20), $"Revision 74: {(reviewMode ? "ON" : "OFF")} ({reviewIndex + 1}/{reviewAnimations.Length})");

        GUI.Label(new Rect(20, 100, 380, 20), "• [R]                  : Entrar/salir revision de 74 animaciones");
        GUI.Label(new Rect(20, 120, 380, 20), "• [N] / [B]            : Siguiente / anterior");
        GUI.Label(new Rect(20, 140, 380, 20), "• [Enter]              : Repetir actual");
        GUI.Label(new Rect(20, 160, 380, 20), "• [Espacio]            : Salir revision y volver a idle");

        GUI.Label(new Rect(20, 195, 380, 20), "• [D] / [A] (Mantener) : Caminar Adelante / Atrás");
        GUI.Label(new Rect(20, 215, 380, 20), "• [S]       (Mantener) : Agacharse");
        GUI.Label(new Rect(20, 235, 380, 20), "• [W]                  : Saltar");
        GUI.Label(new Rect(20, 255, 380, 20), "• [J] / [K]            : Puño Débil / Fuerte");
        GUI.Label(new Rect(20, 275, 380, 20), "• [L] / [O]            : Patada Débil / Fuerte");
        GUI.Label(new Rect(20, 295, 380, 20), "• [U]                  : Hadouken (fireball)");
        GUI.Label(new Rect(20, 315, 380, 20), "• [I]                  : Shoryuken / flamingdp");
        GUI.Label(new Rect(20, 335, 380, 20), "• [Y]                  : Tatsumaki (hurricane)");
        GUI.Label(new Rect(20, 355, 380, 20), "• [T] / [P] / [H]      : Super / Parry / Hit");
    }
}
