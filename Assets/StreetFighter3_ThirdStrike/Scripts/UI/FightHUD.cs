using UnityEngine;

namespace StreetFighter3.UI
{
    /// <summary>
    /// HUD Arcade oficial de combate para KINET STRIKE.
    /// Renderiza barras de vida para P1 y P2, contador de tiempo de 99s,
    /// emblema de K.O. y animaciones de impacto con escala virtual 960x540.
    /// </summary>
    public class FightHUD : MonoBehaviour
    {
        public static FightHUD Instance { get; private set; }

        [Header("Datos de Combatientes")]
        [SerializeField] public string p1Name = "RYU";
        [SerializeField] public float p1MaxHealth = 100f;
        [SerializeField] public float p1CurrentHealth = 100f;

        [SerializeField] public string p2Name = "CHUN-LI";
        [SerializeField] public float p2MaxHealth = 100f;
        [SerializeField] public float p2CurrentHealth = 100f;

        [Header("Contador de Tiempo")]
        [SerializeField] public float roundDurationSeconds = 99f;
        [SerializeField] public bool timerRunning = true;
        private float currentRoundTime;

        [Header("Interpolación de Daño (Efecto CPS-3)")]
        private float p1DisplayHealth = 100f;
        private float p1RedHealth = 100f;
        private float p2DisplayHealth = 100f;
        private float p2RedHealth = 100f;

        [Header("Estado de la Ronda")]
        public bool isGameOver = false;
        public string matchResult = null;

        private Texture2D whiteTex;

        private void Awake()
        {
            Instance = this;
            currentRoundTime = roundDurationSeconds;
            p1CurrentHealth = p1MaxHealth;
            p2CurrentHealth = p2MaxHealth;
            p1DisplayHealth = p1RedHealth = p1MaxHealth;
            p2DisplayHealth = p2RedHealth = p2MaxHealth;

            whiteTex = Texture2D.whiteTexture;
        }

        private void Update()
        {
            // 1. Contador de Tiempo
            if (timerRunning && !isGameOver && currentRoundTime > 0f)
            {
                currentRoundTime -= Time.deltaTime;
                if (currentRoundTime <= 0f)
                {
                    currentRoundTime = 0f;
                    CheckTimeOver();
                }
            }

            // 2. Interpolación suave de barras de vida
            p1DisplayHealth = Mathf.MoveTowards(p1DisplayHealth, p1CurrentHealth, 80f * Time.deltaTime);
            p1RedHealth = Mathf.MoveTowards(p1RedHealth, p1DisplayHealth, 30f * Time.deltaTime);

            p2DisplayHealth = Mathf.MoveTowards(p2DisplayHealth, p2CurrentHealth, 80f * Time.deltaTime);
            p2RedHealth = Mathf.MoveTowards(p2RedHealth, p2DisplayHealth, 30f * Time.deltaTime);

            // 3. Comprobar KO
            if (!isGameOver)
            {
                if (p1CurrentHealth <= 0f && p2CurrentHealth <= 0f)
                {
                    TriggerGameOver("DOUBLE K.O.");
                }
                else if (p1CurrentHealth <= 0f)
                {
                    TriggerGameOver($"{p2Name} WINS!");
                }
                else if (p2CurrentHealth <= 0f)
                {
                    TriggerGameOver($"{p1Name} WINS!");
                }
            }
        }

        public void ApplyDamageToP1(float amount)
        {
            p1CurrentHealth = Mathf.Max(0f, p1CurrentHealth - amount);
        }

        public void ApplyDamageToP2(float amount)
        {
            p2CurrentHealth = Mathf.Max(0f, p2CurrentHealth - amount);
        }

        private void CheckTimeOver()
        {
            if (p1CurrentHealth == p2CurrentHealth)
            {
                TriggerGameOver("DRAW GAME");
            }
            else if (p1CurrentHealth > p2CurrentHealth)
            {
                TriggerGameOver($"{p1Name} WINS (TIME)");
            }
            else
            {
                TriggerGameOver($"{p2Name} WINS (TIME)");
            }
        }

        private void TriggerGameOver(string resultText)
        {
            isGameOver = true;
            timerRunning = false;
            matchResult = resultText;
        }

        public void ResetRound()
        {
            p1CurrentHealth = p1MaxHealth;
            p2CurrentHealth = p2MaxHealth;
            p1DisplayHealth = p1RedHealth = p1MaxHealth;
            p2DisplayHealth = p2RedHealth = p2MaxHealth;
            currentRoundTime = roundDurationSeconds;
            isGameOver = false;
            timerRunning = true;
            matchResult = null;
        }

        private void OnGUI()
        {
            // Matriz de resolución virtual arcade fija 960x540
            float scale = Mathf.Min(Screen.width / 960f, Screen.height / 540f);
            Matrix4x4 oldMatrix = GUI.matrix;
            GUI.matrix = Matrix4x4.TRS(
                new Vector3((Screen.width - 960f * scale) / 2f, (Screen.height - 540f * scale) / 2f, 0f),
                Quaternion.identity,
                Vector3.one * scale);

            // ==========================================
            // 1. MARCOS DE BARRAS DE VIDA (FONDO OSCURO)
            // ==========================================
            const float barWidth = 380f;
            const float barHeight = 22f;
            const float barTop = 38f;

            // Fondo barra P1 (Izquierda)
            DrawRect(new Rect(38, barTop - 4, barWidth + 8, barHeight + 8), new Color(0.06f, 0.08f, 0.12f, 0.95f));
            DrawRectBorder(new Rect(38, barTop - 4, barWidth + 8, barHeight + 8), new Color(0.85f, 0.72f, 0.25f, 0.9f), 2);

            // Fondo barra P2 (Derecha)
            DrawRect(new Rect(534, barTop - 4, barWidth + 8, barHeight + 8), new Color(0.06f, 0.08f, 0.12f, 0.95f));
            DrawRectBorder(new Rect(534, barTop - 4, barWidth + 8, barHeight + 8), new Color(0.85f, 0.72f, 0.25f, 0.9f), 2);

            // ==========================================
            // 2. BARRAS DE VIDA DINÁMICAS (P1 y P2)
            // ==========================================
            // P1: Llena de derecha a izquierda (ancla a la derecha del bloque)
            float p1Ratio = Mathf.Clamp01(p1DisplayHealth / p1MaxHealth);
            float p1RedRatio = Mathf.Clamp01(p1RedHealth / p1MaxHealth);

            // P1 Barra roja de daño retrasado
            float p1RedW = barWidth * p1RedRatio;
            DrawRect(new Rect(42 + (barWidth - p1RedW), barTop, p1RedW, barHeight), new Color(0.85f, 0.18f, 0.15f, 0.9f));
            // P1 Barra amarilla/dorada de vida actual
            float p1ActW = barWidth * p1Ratio;
            DrawRect(new Rect(42 + (barWidth - p1ActW), barTop, p1ActW, barHeight), new Color(0.96f, 0.78f, 0.15f, 1f));
            // P1 Brillo superior
            DrawRect(new Rect(42 + (barWidth - p1ActW), barTop, p1ActW, barHeight * 0.45f), new Color(1f, 0.95f, 0.55f, 0.75f));

            // P2: Llena de izquierda a derecha
            float p2Ratio = Mathf.Clamp01(p2DisplayHealth / p2MaxHealth);
            float p2RedRatio = Mathf.Clamp01(p2RedHealth / p2MaxHealth);

            // P2 Barra roja de daño retrasado
            float p2RedW = barWidth * p2RedRatio;
            DrawRect(new Rect(538, barTop, p2RedW, barHeight), new Color(0.85f, 0.18f, 0.15f, 0.9f));
            // P2 Barra amarilla/dorada de vida actual
            float p2ActW = barWidth * p2Ratio;
            DrawRect(new Rect(538, barTop, p2ActW, barHeight), new Color(0.96f, 0.78f, 0.15f, 1f));
            // P2 Brillo superior
            DrawRect(new Rect(538, barTop, p2ActW, barHeight * 0.45f), new Color(1f, 0.95f, 0.55f, 0.75f));

            // ==========================================
            // 3. NOMBRES DE LUCHADORES
            // ==========================================
            GUIStyle nameStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 18,
                fontStyle = FontStyle.Bold
            };

            // Nombre P1 (Alineado a la izquierda)
            nameStyle.alignment = TextAnchor.MiddleLeft;
            nameStyle.normal.textColor = Color.black;
            GUI.Label(new Rect(44, 15, 300, 22), p1Name, nameStyle);
            nameStyle.normal.textColor = new Color(1f, 0.92f, 0.45f);
            GUI.Label(new Rect(42, 14, 300, 22), p1Name, nameStyle);

            // Nombre P2 (Alineado a la derecha)
            nameStyle.alignment = TextAnchor.MiddleRight;
            nameStyle.normal.textColor = Color.black;
            GUI.Label(new Rect(616, 15, 300, 22), p2Name, nameStyle);
            nameStyle.normal.textColor = new Color(1f, 0.92f, 0.45f);
            GUI.Label(new Rect(614, 14, 300, 22), p2Name, nameStyle);

            // ==========================================
            // 4. CONTADOR DE TIEMPO DE 99s (CENTRAL)
            // ==========================================
            Rect timerBox = new Rect(436, 18, 88, 56);
            // Marco oscuro con borde dorado
            DrawRect(timerBox, new Color(0.04f, 0.05f, 0.09f, 0.96f));
            DrawRectBorder(timerBox, new Color(0.95f, 0.78f, 0.2f, 1f), 3);

            int secondsLeft = Mathf.CeilToInt(currentRoundTime);
            GUIStyle timerStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 34,
                fontStyle = FontStyle.Bold,
                alignment = TextAnchor.MiddleCenter
            };

            // Sombra
            timerStyle.normal.textColor = Color.black;
            GUI.Label(new Rect(timerBox.x + 2, timerBox.y + 2, timerBox.width, timerBox.height), secondsLeft.ToString("D2"), timerStyle);
            // Color de dígitos (Alerta roja si quedan menos de 15 segundos)
            timerStyle.normal.textColor = (secondsLeft <= 15) ? new Color(1f, 0.22f, 0.2f) : new Color(1f, 0.88f, 0.15f);
            GUI.Label(timerBox, secondsLeft.ToString("D2"), timerStyle);

            // Emblema K.O. en el centro
            GUIStyle koStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 13,
                fontStyle = FontStyle.Bold,
                alignment = TextAnchor.MiddleCenter
            };
            koStyle.normal.textColor = new Color(0.85f, 0.15f, 0.15f);
            GUI.Label(new Rect(436, 76, 88, 18), "— K.O. —", koStyle);

            // ==========================================
            // 5. MENSAJE DE FIN DE COMBATE (GAME OVER)
            // ==========================================
            if (isGameOver && !string.IsNullOrEmpty(matchResult))
            {
                DrawRect(new Rect(230, 180, 500, 120), new Color(0.04f, 0.05f, 0.08f, 0.92f));
                DrawRectBorder(new Rect(230, 180, 500, 120), new Color(0.95f, 0.8f, 0.2f, 1f), 3);

                GUIStyle resultStyle = new GUIStyle(GUI.skin.label)
                {
                    fontSize = 32,
                    fontStyle = FontStyle.Bold,
                    alignment = TextAnchor.MiddleCenter
                };
                resultStyle.normal.textColor = new Color(1f, 0.9f, 0.25f);
                GUI.Label(new Rect(230, 195, 500, 45), matchResult, resultStyle);

                if (GUI.Button(new Rect(380, 248, 200, 38), "REVANCHA (REINICIAR)"))
                {
                    ResetRound();
                }
            }

            GUI.matrix = oldMatrix;
        }

        private void DrawRect(Rect rect, Color color)
        {
            GUI.color = color;
            GUI.DrawTexture(rect, whiteTex);
            GUI.color = Color.white;
        }

        private void DrawRectBorder(Rect rect, Color color, float thickness)
        {
            // Borde Superior
            DrawRect(new Rect(rect.x, rect.y, rect.width, thickness), color);
            // Borde Inferior
            DrawRect(new Rect(rect.x, rect.y + rect.height - thickness, rect.width, thickness), color);
            // Borde Izquierdo
            DrawRect(new Rect(rect.x, rect.y, thickness, rect.height), color);
            // Borde Derecho
            DrawRect(new Rect(rect.x + rect.width - thickness, rect.y, thickness, rect.height), color);
        }
    }
}
