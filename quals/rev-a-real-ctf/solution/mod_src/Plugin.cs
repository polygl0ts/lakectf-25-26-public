using BepInEx;
using BepInEx.Logging;
using System.IO;
using UnityEngine;
using UnityEngine.SceneManagement;
using static GameConfig;

namespace SolveMod;

[BepInPlugin(MyPluginInfo.PLUGIN_GUID, MyPluginInfo.PLUGIN_NAME, MyPluginInfo.PLUGIN_VERSION)]
public class Plugin : BaseUnityPlugin
{

    internal static ManualLogSource Log;

    void Awake() {
        Screen.fullScreen = false;

        Log = base.Logger;
		Logger.LogInfo("SolveMod Loaded");
        SceneManager.sceneLoaded += OnSceneLoaded;
    }

	private void OnSceneLoaded(Scene scene, LoadSceneMode mode) {
		Destroy(GameManager.Instance.level.gameObject);
        string filePath = Path.Combine(Application.dataPath, "../BepInEx/plugins/game_config.dat");
		Debug.Log($"Loading game config from {filePath}");
        LoadGameConfig(filePath);
	}

	private void OnDestroy()
	{
		SceneManager.sceneLoaded -= OnSceneLoaded;
	}

	private void LoadGameConfig(string path)
	{
		// Parse config
		GameConfig gameConfig = LoadBinary(path);

		if (gameConfig == null)
		{
			Debug.LogError("Failed to parse bin.");
			return;
		}

		// Create parent object
		GameObject levels = new GameObject("Custom Level");
		var i = gameConfig.levels.Count - 1;
		var level = LoadLevel(gameConfig.levels[i], $"Level {i}", levels.transform);
		level.levelId = 1;

		GameManager.Instance.level = level;

		Log.LogInfo($"Loaded custom level.");
    }

	public Level LoadLevel(LevelData levelData, string name, Transform parent)
	{
		GameObject levelGo = GameObject.CreatePrimitive(PrimitiveType.Cube);
		levelGo.name = name;
		levelGo.transform.parent = parent;

		var level = levelGo.AddComponent<Level>();

		level.spawnArea = CreateBoxCollider(levelData.spawnArea, "SpawnArea", levelGo.transform, 1);
		level.spawnArea.isTrigger = true;

		level.flagArea = CreateBoxCollider(levelData.flagArea, "FlagArea", levelGo.transform, 2);
		level.flagArea.isTrigger = true;

		for (int i = 0; i < levelData.colliders.Count; i++)
		{
			var colliderData = levelData.colliders[i];
			CreateBoxCollider(colliderData, $"Collider {i}", levelGo.transform);
		}

		return level;
	}

	private BoxCollider CreateBoxCollider(BoxColliderData colliderData, string name, Transform parent, int color = 0)
	{
		var child = GameObject.CreatePrimitive(PrimitiveType.Cube);
		child.name = name;
		child.transform.parent = parent;
		child.transform.SetPositionAndRotation(colliderData.position.ToVector3(), colliderData.rotation.ToQuaternion());
		child.transform.localScale = colliderData.size.ToVector3();

		Material[] colors = {
			Resources.Load<Material>("Materials/Green"),
			Resources.Load<Material>("Materials/Blue"),
			Resources.Load<Material>("Materials/Red")
		};

        Renderer rend = child.GetComponent<Renderer>();
        rend.material = colors[color];

		var bc = child.GetComponent<BoxCollider>();
		return bc;
	}
}
