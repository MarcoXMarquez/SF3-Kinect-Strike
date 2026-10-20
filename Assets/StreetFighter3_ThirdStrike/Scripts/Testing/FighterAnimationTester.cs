using UnityEngine;
using System.Collections;

/// <summary>
/// Probador interactivo de combate y máquina de estados para KINET STRIKE.
/// Soporta 2 Jugadores separados de forma independiente en el mismo teclado:
/// - Jugador 1 (P1): [W/A/S/D] Mover/Saltar/Agacharse | [J/K] Puños | [L/O] Patadas | [U/I/Y/T] Especiales | [P] Parry
/// - Jugador 2 (P2): [FLECHAS] Mover/Saltar/Agacharse | [Keypad 1/2 o B/N] Puños | [Keypad 4/5 o M/,] Patadas | [Keypad 7/8 o ./] Especiales | [RShift/Keypad 0] Parry
/// </summary>
public class FighterAnimationTester : MonoBehaviour
{
    [Header("Referencias")]
    [Tooltip("El componente Animator (en este objeto o en el hijo 'Visuals')")]
    public Animator animator;

    [Header("Configuración de Jugador")]
    [Tooltip("Falso = Jugador 1 (WASD). Verdadero = Jugador 2 (Flechas de dirección).")]
    public bool isPlayer2 = false;

    [Header("Estado Actual")]
    [SerializeField] private string currentAnimation = "idle_stance";
    [SerializeField] private bool isBusyWithAction = false;

    [Header("Locomoción Física")]
    [SerializeField] private float moveSpeed = 2.4f;
    [SerializeField] private float minX = -5.8f;
    [SerializeField] private float maxX = 5.8f;

    [Header("Instrucciones de Teclas en Play")]
    [TextArea(12, 16)]
    public string guiaControles =
        "=== CONTROLES DE COMBATE SEPARADOS ===\n" +
        "• JUGADOR 1: [W/A/S/D] Mover/Saltar | [J/K] Puños | [L/O] Patadas | [U/I/Y/T] Especiales | [P] Parry\n" +
        "• JUGADOR 2: [FLECHAS] Mover/Saltar | [Keypad 1/2 o B/N] Puños | [Keypad 4/5 o M/,] Patadas | [Keypad 7/8 o ./] Especiales | [RShift/Keypad 0] Parry\n" +
        "• [Escape] -> Volver al Menú Principal";

    private Coroutine actionCoroutine;
    private Rigidbody2D rb;

    void Awake()
    {
        if (animator == null)
        {
            animator = GetComponentInChildren<Animator>();
        }
        rb = GetComponent<Rigidbody2D>();

        // Auto-detección inteligente de Jugador 2 si no se especificó manualmente en el inspector
        if (!isPlayer2)
        {
            if (CompareTag("Enemy") || gameObject.name.ToLower().Contains("opponent") || transform.position.x > 0.5f)
            {
                isPlayer2 = true;
            }
        }
    }

    void Start()
    {
        PlayIdle();
    }

    void Update()
    {
        // Volver al Menú Principal con Escape
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            UnityEngine.SceneManagement.SceneManager.LoadScene("MainMenu_Scene");
            return;
        }

        // 1. Si está en medio de una acción activa, esperar a que finalice (o cancelar)
        if (isBusyWithAction)
        {
            bool cancelAction = !isPlayer2 
                ? Input.GetKeyDown(KeyCode.Space) 
                : (Input.GetKeyDown(KeyCode.KeypadEnter) || Input.GetKeyDown(KeyCode.Return));

            if (cancelAction)
            {
                if (actionCoroutine != null) StopCoroutine(actionCoroutine);
                isBusyWithAction = false;
                PlayIdle();
            }
            return;
        }

        bool rightPressed;
        bool leftPressed;
        bool jumpPressed;
        bool isCrouching;

        if (!isPlayer2)
        {
            // ==========================================
            // JUGADOR 1: EXCLUSIVAMENTE W, A, S, D
            // ==========================================
            rightPressed = Input.GetKey(KeyCode.D);
            leftPressed = Input.GetKey(KeyCode.A);
            jumpPressed = Input.GetKeyDown(KeyCode.W);
            isCrouching = Input.GetKey(KeyCode.S);

            // Puños P1 (J = Débil / Medio, K = Fuerte)
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

            // Patadas P1 (L = Débil, O = Fuerte / Media)
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

            // Movimientos especiales P1
            if (Input.GetKeyDown(KeyCode.U))
            {
                if (HasState("special_hadouken")) ExecuteOneShotAction("special_hadouken");
                else if (HasState("fireball")) ExecuteOneShotAction("fireball");
                else if (HasState("aegis")) ExecuteOneShotAction("aegis");
                return;
            }
            if (Input.GetKeyDown(KeyCode.I))
            {
                if (HasState("special_shoryuken")) ExecuteOneShotAction("special_shoryuken");
                else if (HasState("shoryuken")) ExecuteOneShotAction("shoryuken");
                else if (HasState("chariot_rush")) ExecuteOneShotAction("chariot_rush");
                return;
            }
            if (Input.GetKeyDown(KeyCode.Y))
            {
                if (HasState("hurricane")) ExecuteOneShotAction("hurricane");
                else if (HasState("halfcircle_forward_kick")) ExecuteOneShotAction("halfcircle_forward_kick");
                else if (HasState("chariot_rush")) ExecuteOneShotAction("chariot_rush");
                return;
            }
            if (Input.GetKeyDown(KeyCode.T))
            {
                if (HasState("super_art_2")) ExecuteOneShotAction("super_art_2");
                else if (HasState("denjin")) ExecuteOneShotAction("denjin");
                else if (HasState("cfesuper")) ExecuteOneShotAction("cfesuper");
                else if (HasState("aegis")) ExecuteOneShotAction("aegis");
                else if (HasState("taunt")) ExecuteOneShotAction("taunt");
                return;
            }

            // Defensa P1 (Parry P, Hit H)
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
        }
        else
        {
            // ==========================================
            // JUGADOR 2: EXCLUSIVAMENTE FLECHAS DE DIRECCIÓN
            // ==========================================
            rightPressed = Input.GetKey(KeyCode.RightArrow);
            leftPressed = Input.GetKey(KeyCode.LeftArrow);
            jumpPressed = Input.GetKeyDown(KeyCode.UpArrow);
            isCrouching = Input.GetKey(KeyCode.DownArrow);

            // Puños P2 (Keypad 1 o B = Débil, Keypad 2 o N = Fuerte)
            if (Input.GetKeyDown(KeyCode.Keypad1) || Input.GetKeyDown(KeyCode.B))
            {
                string anim = isCrouching ? "crouch_light_punch" : "light_punch";
                ExecuteOneShotAction(anim);
                return;
            }
            if (Input.GetKeyDown(KeyCode.Keypad2) || Input.GetKeyDown(KeyCode.N))
            {
                string anim = isCrouching ? "crouch_heavy_punch" : (HasState("heavy_punch") ? "heavy_punch" : "medium_punch");
                ExecuteOneShotAction(anim);
                return;
            }

            // Patadas P2 (Keypad 4 o M = Débil, Keypad 5 o Comma = Fuerte)
            if (Input.GetKeyDown(KeyCode.Keypad4) || Input.GetKeyDown(KeyCode.M))
            {
                string anim = isCrouching ? "crouch_light_kick" : "light_kick";
                ExecuteOneShotAction(anim);
                return;
            }
            if (Input.GetKeyDown(KeyCode.Keypad5) || Input.GetKeyDown(KeyCode.Comma))
            {
                string anim = isCrouching ? "crouch_heavy_kick" : (HasState("heavy_kick") ? "heavy_kick" : "medium_kick");
                ExecuteOneShotAction(anim);
                return;
            }

            // Especiales P2 (Keypad 7 o Period, Keypad 8 o Slash, Keypad 9 o Quote)
            if (Input.GetKeyDown(KeyCode.Keypad7) || Input.GetKeyDown(KeyCode.Period))
            {
                if (HasState("special_hadouken")) ExecuteOneShotAction("special_hadouken");
                else if (HasState("fireball")) ExecuteOneShotAction("fireball");
                else if (HasState("aegis")) ExecuteOneShotAction("aegis");
                return;
            }
            if (Input.GetKeyDown(KeyCode.Keypad8) || Input.GetKeyDown(KeyCode.Slash))
            {
                if (HasState("special_shoryuken")) ExecuteOneShotAction("special_shoryuken");
                else if (HasState("shoryuken")) ExecuteOneShotAction("shoryuken");
                else if (HasState("chariot_rush")) ExecuteOneShotAction("chariot_rush");
                return;
            }
            if (Input.GetKeyDown(KeyCode.Keypad9) || Input.GetKeyDown(KeyCode.Quote))
            {
                if (HasState("hurricane")) ExecuteOneShotAction("hurricane");
                else if (HasState("halfcircle_forward_kick")) ExecuteOneShotAction("halfcircle_forward_kick");
                else if (HasState("chariot_rush")) ExecuteOneShotAction("chariot_rush");
                return;
            }
            if (Input.GetKeyDown(KeyCode.KeypadPlus) || Input.GetKeyDown(KeyCode.Backslash))
            {
                if (HasState("super_art_2")) ExecuteOneShotAction("super_art_2");
                else if (HasState("denjin")) ExecuteOneShotAction("denjin");
                else if (HasState("cfesuper")) ExecuteOneShotAction("cfesuper");
                else if (HasState("aegis")) ExecuteOneShotAction("aegis");
                return;
            }

            // Defensa P2 (RightShift, RightControl o Keypad 0 = Parry, KeypadPeriod = Hit)
            if (Input.GetKeyDown(KeyCode.RightShift) || Input.GetKeyDown(KeyCode.RightControl) || Input.GetKeyDown(KeyCode.Keypad0))
            {
                if (HasState("parry_standing")) ExecuteOneShotAction("parry_standing");
                else if (HasState("parry_high")) ExecuteOneShotAction("parry_high");
                return;
            }
            if (Input.GetKeyDown(KeyCode.KeypadPeriod))
            {
                string anim = isCrouching ? "hit_crouching" : "hit_standing";
                ExecuteOneShotAction(anim);
                return;
            }
        }

        // 6. Salto simple
        if (jumpPressed)
        {
            if (rb != null && Mathf.Abs(rb.linearVelocity.y) < 0.1f)
            {
                float horiz = rightPressed ? 1.6f : (leftPressed ? -1.6f : 0f);
                rb.linearVelocity = new Vector2(horiz, 7.2f);
            }
            if (rightPressed) ExecuteOneShotAction("jump_forward");
            else if (leftPressed) ExecuteOneShotAction("jump_backward");
            else ExecuteOneShotAction("jump_neutral");
            return;
        }

        // 7. Locomoción continua con desplazamiento físico en escena
        if (rightPressed && !leftPressed && !isCrouching)
        {
            transform.position += Vector3.right * (moveSpeed * Time.deltaTime);
            if (currentAnimation != "walk_forward") PlayLoop("walk_forward");
        }
        else if (leftPressed && !rightPressed && !isCrouching)
        {
            transform.position += Vector3.left * (moveSpeed * Time.deltaTime);
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

        // Delimitar posición dentro de los bordes del escenario
        Vector3 clampedPos = transform.position;
        clampedPos.x = Mathf.Clamp(clampedPos.x, minX, maxX);
        transform.position = clampedPos;
    }

    /// <summary>
    /// Retorna si el luchador está ocupado ejecutando una animación activa de ataque.
    /// </summary>
    public bool IsBusyWithAction() => isBusyWithAction;

    /// <summary>
    /// Ejecuta una animación de ataque/reacción y regresa automáticamente al estado neutral.
    /// </summary>
    public void ExecuteOneShotAction(string animName)
    {
        if (animator == null) return;

        if (actionCoroutine != null)
        {
            StopCoroutine(actionCoroutine);
        }

        actionCoroutine = StartCoroutine(ActionRoutine(animName));
        CheckHitOnOpponent(animName);
    }

    private void CheckHitOnOpponent(string animName)
    {
        if (animName == "hit_standing" || animName == "hit_crouching")
        {
            if (!isPlayer2) StreetFighter3.UI.FightHUD.Instance?.ApplyDamageToP1(10f);
            else StreetFighter3.UI.FightHUD.Instance?.ApplyDamageToP2(10f);
            return;
        }

        bool isAttack = animName.Contains("punch") || animName.Contains("kick") ||
                        animName.Contains("fireball") || animName.Contains("shoryuken") ||
                        animName.Contains("hurricane") || animName.Contains("super") ||
                        animName.Contains("denjin") || animName.Contains("aegis") ||
                        animName.Contains("chariot");

        if (!isAttack || StreetFighter3.UI.FightHUD.Instance == null) return;

        foreach (var go in UnityEngine.SceneManagement.SceneManager.GetActiveScene().GetRootGameObjects())
        {
            if (go != gameObject && go.name.StartsWith("Fighter_"))
            {
                float dist = Mathf.Abs(transform.position.x - go.transform.position.x);
                if (dist < 2.3f)
                {
                    float dmg = 8f;
                    if (animName.Contains("heavy")) dmg = 14f;
                    else if (animName.Contains("fireball") || animName.Contains("shoryuken") || animName.Contains("hurricane")) dmg = 18f;
                    else if (animName.Contains("super") || animName.Contains("denjin") || animName.Contains("aegis")) dmg = 26f;

                    if (!isPlayer2)
                        StreetFighter3.UI.FightHUD.Instance.ApplyDamageToP2(dmg);
                    else
                        StreetFighter3.UI.FightHUD.Instance.ApplyDamageToP1(dmg);
                    break;
                }
            }
        }
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

        // Fallback y acotamiento de duración para máxima responsividad arcade
        if (clipDuration <= 0.05f)
        {
            clipDuration = 0.4f;
        }
        else
        {
            // Acotar a máximo 1.25 segundos para evitar bloqueos largos en animaciones extendidas
            clipDuration = Mathf.Clamp(clipDuration, 0.25f, 1.25f);
        }

        float elapsed = 0f;
        while (elapsed < clipDuration)
        {
            elapsed += Time.deltaTime;
            // Permitir combo/cancelación fluida tras el impacto inicial (0.25s) si se pulsa otro ataque
            if (elapsed > 0.25f)
            {
                if (!isPlayer2)
                {
                    if (Input.GetKeyDown(KeyCode.J) || Input.GetKeyDown(KeyCode.K) ||
                        Input.GetKeyDown(KeyCode.L) || Input.GetKeyDown(KeyCode.O) ||
                        Input.GetKeyDown(KeyCode.U) || Input.GetKeyDown(KeyCode.I))
                    {
                        break;
                    }
                }
                else
                {
                    if (Input.GetKeyDown(KeyCode.Keypad1) || Input.GetKeyDown(KeyCode.Keypad2) ||
                        Input.GetKeyDown(KeyCode.B) || Input.GetKeyDown(KeyCode.N) ||
                        Input.GetKeyDown(KeyCode.Keypad4) || Input.GetKeyDown(KeyCode.Keypad5))
                    {
                        break;
                    }
                }
            }
            yield return null;
        }

        isBusyWithAction = false;
        
        // Si sigue agachado, regresar a crouch_idle, si no a idle_stance
        bool stillCrouching = !isPlayer2 ? Input.GetKey(KeyCode.S) : Input.GetKey(KeyCode.DownArrow);
        if (stillCrouching)
        {
            PlayLoop("crouch_idle");
        }
        else
        {
            PlayIdle();
        }
    }

    public void PlayLoop(string animName)
    {
        if (animator == null) return;
        currentAnimation = animName;
        animator.Play(animName, 0, 0f);
    }

    public void PlayIdle()
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
        // Solo dibujar el banner una vez (desde el Jugador 1)
        if (isPlayer2) return;

        float scale = Mathf.Min(Screen.width / 960f, Screen.height / 540f);
        Matrix4x4 old = GUI.matrix;
        GUI.matrix = Matrix4x4.TRS(
            new Vector3((Screen.width - 960f * scale) / 2f, (Screen.height - 540f * scale) / 2f, 0f),
            Quaternion.identity,
            Vector3.one * scale);

        GUI.color = new Color(0.04f, 0.05f, 0.08f, 0.88f);
        GUI.DrawTexture(new Rect(50, 498, 860, 36), Texture2D.whiteTexture);
        GUI.color = Color.white;

        GUIStyle style = new GUIStyle(GUI.skin.label)
        {
            fontSize = 11,
            fontStyle = FontStyle.Bold,
            alignment = TextAnchor.MiddleCenter
        };
        style.normal.textColor = new Color(1f, 0.92f, 0.4f);

        GUI.Label(new Rect(50, 499, 860, 34), 
            "P1: [WASD] Mover | [J/K] Puños | [L/O] Patadas | [U/I] Especiales   ||   P2: [FLECHAS] Mover | [Keypad 1-5 o B,N,M,,] Golpes | [ESC] Menú", style);

        GUI.matrix = old;
    }
}
