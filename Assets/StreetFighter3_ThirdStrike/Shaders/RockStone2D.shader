Shader "Custom/RockStone2D"
{
    Properties
    {
        [PerRendererData] _MainTex ("Sprite Texture", 2D) = "white" {}
        _Color ("Tint", Color) = (1,1,1,1)
        _BaseRockColor ("Base Rock Color", Color) = (0.28, 0.30, 0.35, 1.0)
        _HighlightRockColor ("Highlight Color", Color) = (0.42, 0.46, 0.52, 1.0)
        _CrackColor ("Crack / Shadow Color", Color) = (0.12, 0.13, 0.16, 1.0)
        _Scale ("Pattern Scale", Float) = 6.0
        _CrackIntensity ("Crack Intensity", Range(0, 1)) = 0.65
        _EdgeDarkness ("Edge Bevel Darkness", Range(0, 1)) = 0.4
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
                float2 worldPos : TEXCOORD1;
            };

            fixed4 _Color;
            fixed4 _BaseRockColor;
            fixed4 _HighlightRockColor;
            fixed4 _CrackColor;
            float _Scale;
            float _CrackIntensity;
            float _EdgeDarkness;
            sampler2D _MainTex;

            v2f vert(appdata_t IN)
            {
                v2f OUT;
                OUT.vertex = UnityObjectToClipPos(IN.vertex);
                OUT.texcoord = IN.texcoord;
                OUT.worldPos = mul(unity_ObjectToWorld, IN.vertex).xy;
                OUT.color = IN.color * _Color;
                return OUT;
            }

            float hash21(float2 p)
            {
                p = frac(p * float2(234.34, 435.345));
                p += dot(p, p + 34.23);
                return frac(p.x * p.y);
            }

            float noise(float2 p)
            {
                float2 i = floor(p);
                float2 f = frac(p);
                f = f * f * (3.0 - 2.0 * f);

                float a = hash21(i);
                float b = hash21(i + float2(1.0, 0.0));
                float c = hash21(i + float2(0.0, 1.0));
                float d = hash21(i + float2(1.0, 1.0));

                return lerp(lerp(a, b, f.x), lerp(c, d, f.x), f.y);
            }

            float voronoi(float2 uv)
            {
                float2 g = floor(uv);
                float2 f = frac(uv);
                float minDist = 1.0;
                for (int y = -1; y <= 1; y++)
                {
                    for (int x = -1; x <= 1; x++)
                    {
                        float2 lattice = float2(x, y);
                        float2 offset = float2(hash21(g + lattice), hash21(g + lattice + float2(13.1, 7.3)));
                        float d = distance(lattice + offset, f);
                        minDist = min(minDist, d);
                    }
                }
                return minDist;
            }

            fixed4 frag(v2f IN) : SV_Target
            {
                fixed4 spriteTex = tex2D(_MainTex, IN.texcoord);

                float2 rockUV = IN.texcoord * _Scale;

                float n = noise(rockUV * 2.0) * 0.5 + noise(rockUV * 5.0) * 0.25;
                float v = voronoi(rockUV);

                float crack = smoothstep(0.08, 0.0, abs(v - 0.45)) * _CrackIntensity;

                fixed4 stoneCol = lerp(_BaseRockColor, _HighlightRockColor, n);
                stoneCol = lerp(stoneCol, _CrackColor, crack);

                float edgeX = min(IN.texcoord.x, 1.0 - IN.texcoord.x);
                float edgeY = min(IN.texcoord.y, 1.0 - IN.texcoord.y);
                float edgeDist = min(edgeX, edgeY);
                float edgeShadow = smoothstep(0.0, 0.12, edgeDist);
                stoneCol = lerp(_CrackColor, stoneCol, edgeShadow * (1.0 - _EdgeDarkness * 0.5));

                float topHighlight = smoothstep(0.85, 0.98, IN.texcoord.y) * 0.3;
                stoneCol += _HighlightRockColor * topHighlight;

                fixed4 finalCol = stoneCol * IN.color;
                finalCol.a = spriteTex.a * IN.color.a;

                return finalCol;
            }
            ENDCG
        }
    }
    Fallback "Sprites/Default"
}
