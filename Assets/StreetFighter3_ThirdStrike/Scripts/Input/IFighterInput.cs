using UnityEngine;

/// <summary>
/// Tipos de ataque admitidos por el sistema de combate de SF3.
/// </summary>
public enum FighterAttackType
{
    None,
    LightPunch,
    HeavyPunch,
    LightKick,
    HeavyKick,
    Hadouken,
    Shoryuken,
    Tatsumaki,
    SuperArt
}

/// <summary>
/// Contrato de entrada desacoplado para cualquier entidad que controle a un luchador.
/// Ni la máquina de estados ni las animaciones dependen de si el jugador usa teclado, mando o Azure Kinect.
/// </summary>
public interface IFighterInput
{
    /// <summary>
    /// Eje horizontal (-1 = atrás/izquierda, 0 = neutral, 1 = adelante/derecha).
    /// </summary>
    float GetHorizontalAxis();

    /// <summary>
    /// Alias de compatibilidad para movimiento horizontal.
    /// </summary>
    float GetHorizontalMove();

    /// <summary>
    /// Retorna true si el jugador está agachado.
    /// </summary>
    bool IsCrouching();

    /// <summary>
    /// Retorna true si se solicita salto en este frame.
    /// </summary>
    bool IsJumping();

    /// <summary>
    /// Retorna true si el jugador mantiene la postura de guardia/bloqueo.
    /// </summary>
    bool IsBlocking();

    /// <summary>
    /// Retorna true si se ejecuta cualquier ataque, extrayendo el tipo específico.
    /// </summary>
    bool IsAttacking(out FighterAttackType attackType);

    // --- Comandos de botones o gestos individuales ---
    bool WasLightPunchPressed();
    bool WasHeavyPunchPressed();
    bool WasLightKickPressed();
    bool WasHeavyKickPressed();

    // --- Gestos de Kinect / Movimientos especiales ---
    bool WasHadoukenGestureDetected();
    bool WasShoryukenGestureDetected();
    bool WasParryStanceDetected();
}
