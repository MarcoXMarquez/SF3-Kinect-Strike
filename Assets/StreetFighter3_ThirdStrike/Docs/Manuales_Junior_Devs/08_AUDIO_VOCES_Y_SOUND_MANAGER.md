# 🔊 Guía 08: Audio, Voces y Sound Manager
## Integración de Sonidos, Música y Voces Verificadas por IA

En el paquete tienes más de 500 archivos de audio de alta calidad, clasificados y listos para Unity:
* **`Audio/BGM/`:** 14 temas musicales de escenarios en MP3.
* **`Audio/SFX/`:** Efectos de golpes ligeros, medios y pesados, bloqueo y el icónico sonido de Parry.
* **`Audio/Voices/`:** 485 clips de voces donde cada archivo coincide 100% con lo que dice (*01_Special_Shoryuken.wav*, *02_Special_Hadouken.wav*, *Final_Round.wav*, etc.).

---

### 📍 Paso 1: Configurar el SoundManager en la Escena
Para no tener componentes de audio desordenados por todos lados, usamos el patrón **Singleton**: un único objeto central que gestiona todos los sonidos del juego.

1. En la ventana **Hierarchy**, haz clic derecho ➔ **Create Empty**.
2. Nómbralo: **`SoundManager`**.
3. Añade dos componentes **Audio Source**:
   * Clic en **Add Component** ➔ **`Audio Source`** (este será para la música BGM):
     * **Play On Awake:** Marcado.
     * **Loop:** **MARCADO [X]** (para que la música de la pelea nunca se detenga).
     * **Volume:** `0.6`.
   * Clic en **Add Component** ➔ **`Audio Source`** (este será para los efectos SFX y voces):
     * **Play On Awake:** Desmarcado.
     * **Loop:** Desmarcado.
     * **Volume:** `1.0`.
4. Añade el script incluido: `Assets/StreetFighter3_ThirdStrike/Scripts/Audio/SF3SoundManager.cs`.

---

### 📍 Paso 2: Asignar la Música de Fondo (BGM)
1. En el primer Audio Source de `SoundManager`, busca el campo **AudioClip**.
2. Ve a `Assets/StreetFighter3_ThirdStrike/Audio/BGM/` en tu ventana Project.
3. Arrastra el tema que quieras usar (por ejemplo: `08_Kobu_Ryu_Stage.mp3` o `02_China_Vox_ChunLi.mp3`) al campo **AudioClip**.
4. ¡Al darle Play al juego, la música comenzará a sonar en bucle continuo!

---

### 💻 Cómo Reproducir Efectos y Voces desde Código C#
Gracias al script `SF3SoundManager.cs`, cualquier programador puede hacer sonar un efecto con una sola línea limpia:

```csharp
// 1. Reproducir el icónico Parry de Street Fighter III:
SF3SoundManager.Instance.PlayParry();

// 2. Reproducir sonido de super art:
SF3SoundManager.Instance.PlaySuperFlash();

// 3. Reproducir un golpe o efecto específico:
public AudioClip hitSFX;
SF3SoundManager.Instance.PlaySFX(hitSFX);

// 4. Reproducir la voz de un ataque:
public AudioClip hadoukenVoice;
SF3SoundManager.Instance.PlayVoice(hadoukenVoice);
```
