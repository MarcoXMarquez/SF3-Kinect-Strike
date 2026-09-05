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
            textureImporter.textureType = TextureImporterType.Sprite;
            textureImporter.spriteImportMode = SpriteImportMode.Single;
            textureImporter.spritePixelsPerUnit = 100;
            textureImporter.filterMode = FilterMode.Point;
            textureImporter.textureCompression = TextureImporterCompression.Uncompressed;
            textureImporter.alphaIsTransparency = true;

            TextureImporterSettings settings = new TextureImporterSettings();
            textureImporter.ReadTextureSettings(settings);

            // Para personajes, el pivot recomendado es Bottom (pies en el suelo)
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
