using UnityEngine;
using UnityEditor;

public class SF3AutoSpriteImporter : AssetPostprocessor
{
    void OnPreprocessTexture()
    {
        // Solo aplica a los assets dentro de StreetFighter3_ThirdStrike
        if (assetPath.Contains("StreetFighter3_ThirdStrike"))
        {
            TextureImporter textureImporter = (TextureImporter)assetImporter;
            
            TextureImporterSettings settings = new TextureImporterSettings();
            textureImporter.ReadTextureSettings(settings);

            textureImporter.textureType = TextureImporterType.Sprite;
            textureImporter.spriteImportMode = SpriteImportMode.Single;
            textureImporter.spritePixelsPerUnit = 100;
            textureImporter.filterMode = FilterMode.Point;
            textureImporter.textureCompression = TextureImporterCompression.Uncompressed;
            textureImporter.alphaIsTransparency = true;

            // Si el usuario establecio un Custom pivot, NUNCA sobreescribirlo
            if (settings.spriteAlignment == (int)SpriteAlignment.Custom)
            {
                return;
            }

            // Solo aplicar valores por defecto en primera importacion o si no ha sido personalizado
            if (assetImporter.importSettingsMissing)
            {
                if (assetPath.Contains("Characters"))
                {
                    settings.spriteAlignment = (int)SpriteAlignment.BottomCenter;
                    settings.spritePivot = new Vector2(0.5f, 0.0f);
                }
                else if (assetPath.Contains("Stages"))
                {
                    settings.spriteAlignment = (int)SpriteAlignment.Center;
                    settings.spritePivot = new Vector2(0.5f, 0.5f);
                }
                textureImporter.SetTextureSettings(settings);
            }
        }
    }
}
