Shader "Custom/RinneganPortal2D"
{
    Properties
    {
        [PerRendererData] _MainTex ("Sprite Texture", 2D) = "white" {}
        _Color ("Tint", Color) = (1,1,1,1)
        _VoidColor ("Void Core Color", Color) = (0.04, 0.0, 0.09, 1.0)
        _InnerColor ("Rinnegan Violet Color", Color) = (0.52, 0.08, 0.92, 1.0)
        _OuterColor ("Aura Magenta Color", Color) = (0.82, 0.25, 1.0, 1.0)
        _GlowColor ("Lightning Flare Color", Color) = (0.95, 0.75, 1.0, 1.0)
        _LockedTint ("Locked Dark Tint", Color) = (0.4, 0.1, 0.2, 1.0)
        _RotationSpeed ("Vortex Speed", Float) = 3.5
        _RingFrequency ("Rinnegan Ring Frequency", Float) = 32.0
        _RingSpeed ("Ring Pulse Speed", Float) = 4.0
        _ArmCount ("Vortex Arms", Float) = 3.0
        _SwirlTension ("Swirl Tension", Float) = 14.0
        _IsUnlocked ("Is Unlocked", Range(0, 1)) = 0.0
    }

    SubShader
    {
        Tags
        {
            "Queue"="Transparent"
            "IgnoreProjector"="True"
            "RenderType"="Transparent"
            "PreviewType"="Plane"
            "CanUseSpriteAtlas"="True"
        }

        Cull Off
        Lighting Off
        ZWrite Off
        Blend SrcAlpha OneMinusSrcAlpha

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma target 2.0
            #include "UnityCG.cginc"

            struct appdata_t
            {
                float4 vertex   : POSITION;
                float4 color    : COLOR;
                float2 texcoord : TEXCOORD0;
            };

            struct v2f
            {
                float4 vertex   : SV_POSITION;
                fixed4 color    : COLOR;
                float2 texcoord : TEXCOORD0;
            };

            fixed4 _Color;
            fixed4 _VoidColor;
            fixed4 _InnerColor;
            fixed4 _OuterColor;
            fixed4 _GlowColor;
            fixed4 _LockedTint;
            float _RotationSpeed;
            float _RingFrequency;
            float _RingSpeed;
            float _ArmCount;
            float _SwirlTension;
            float _IsUnlocked;
            sampler2D _MainTex;

            v2f vert(appdata_t IN)
            {
                v2f OUT;
                OUT.vertex = UnityObjectToClipPos(IN.vertex);
                OUT.texcoord = IN.texcoord;
                OUT.color = IN.color * _Color;
                return OUT;
            }

            fixed4 frag(v2f IN) : SV_Target
            {
                // Centrar UV de -0.5 a 0.5
                float2 uv = IN.texcoord - float2(0.5, 0.5);
                float dist = length(uv);

                // Mascara circular suave para que nunca haya bordes cuadrados
                float circleAlpha = smoothstep(0.5, 0.36, dist);
                if (circleAlpha <= 0.001) discard;

                float angle = atan2(uv.y, uv.x);

                // Modulacion segun estado de desbloqueo
                float speedMult = lerp(0.4, 1.4, _IsUnlocked);
                float energyMult = lerp(0.35, 1.0, _IsUnlocked);

                // 1. Espiral / Vortice dimensional (Ame-no-tejikara)
                float spiralAngle = angle + (dist * _SwirlTension) - (_Time.y * _RotationSpeed * speedMult);
                float vortex = sin(spiralAngle * _ArmCount);
                vortex = smoothstep(-0.3, 0.85, vortex);

                // 2. Ondas concentricas caracteristicas del Rinnegan
                float rings = sin(dist * _RingFrequency - (_Time.y * _RingSpeed * speedMult));
                float ringIntensity = smoothstep(0.45, 0.95, rings) * 0.45;

                // 3. Nucleo del Vacio (Singularidad / Agujero dimensional)
                float coreMask = smoothstep(0.06, 0.28, dist);

                // 4. Composicion de color
                fixed4 baseColor = lerp(_VoidColor, _InnerColor, coreMask);
                fixed4 auraColor = lerp(baseColor, _OuterColor, vortex * 0.7);
                fixed4 flareColor = lerp(auraColor, _GlowColor, ringIntensity * energyMult);

                // Si esta bloqueado, atenuar y tenyir a tono purpura oscuro latente
                if (_IsUnlocked < 0.5)
                {
                    flareColor = lerp(flareColor * _LockedTint, _VoidColor, 0.35);
                    // Pulsacion sutil de advertencia
                    float pulse = sin(_Time.y * 2.5) * 0.15 + 0.85;
                    flareColor *= pulse;
                }
                else
                {
                    // Relampagos / destellos dimensionales cuando esta activo
                    float flarePulse = sin(_Time.y * 7.0 + angle * 2.0) * 0.2 + 0.8;
                    flareColor += _GlowColor * (flarePulse * 0.25 * (1.0 - dist * 1.5));
                }

                fixed4 finalColor = flareColor * IN.color;
                finalColor.a = circleAlpha * IN.color.a;

                return finalColor;
            }
            ENDCG
        }
    }
    Fallback "Sprites/Default"
}
