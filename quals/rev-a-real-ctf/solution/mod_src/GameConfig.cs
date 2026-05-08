using UnityEngine;
using System.Collections.Generic;
using System.IO;

public class GameConfig {

	public float fixed_delta_time;
	public PlayerData player_data;
	public List<LevelData> levels = new();

	// --- Binary Load ---
	public static GameConfig LoadBinary(string path) {
		var config = new GameConfig();
		using (var fs = new FileStream(path, FileMode.Open, FileAccess.Read))
		using (var reader = new BinaryReader(fs)) {
			config.fixed_delta_time = reader.ReadSingle();
			config.player_data = PlayerData.ReadBinary(reader);

			int levelCount = reader.ReadInt32();
			config.levels = new List<LevelData>(levelCount);
			for (int i = 0; i < levelCount; i++)
				config.levels.Add(LevelData.ReadBinary(reader));
		}
		return config;
	}

	public class PlayerData {
		public float speed;
		public float gravity;
		public float jumpHeight;
		public float[] collider_size;

		private PlayerData() { }

		public static PlayerData ReadBinary(BinaryReader reader) {
			var data = new PlayerData();
			data.speed = reader.ReadSingle();
			data.gravity = reader.ReadSingle();
			data.jumpHeight = reader.ReadSingle();
			data.collider_size = readFloatArray(reader, 3);
			return data;
		}
	}

	public class LevelData {
		public ushort levelId;
		public BoxColliderData spawnArea;
		public BoxColliderData flagArea;
		public List<BoxColliderData> colliders;

		private LevelData() { }

		public static LevelData ReadBinary(BinaryReader reader) {
			LevelData level = new();

			level.levelId = reader.ReadUInt16();
			level.spawnArea = BoxColliderData.ReadBinary(reader);
			level.flagArea = BoxColliderData.ReadBinary(reader);

			level.colliders = new();
			int len = reader.ReadInt32();
			for (int i = 0; i < len; i++) {
				level.colliders.Add(BoxColliderData.ReadBinary(reader));
			}

			return level;
		}
	}

	public class BoxColliderData {
		public float[] position;
		public float[] rotation;
		public float[] size;

		private BoxColliderData() {
		}

		public static BoxColliderData ReadBinary(BinaryReader reader) {
			return new BoxColliderData {
				position = readFloatArray(reader, 3),
				rotation = readFloatArray(reader, 4),
				size = readFloatArray(reader, 3)
			};
		}
	}

	private static void writeFloatArray(BinaryWriter writer, float[] arr) {
		foreach (var f in arr)
			writer.Write(f);
	}

	private static float[] readFloatArray(BinaryReader reader, int len) {
		float[] arr = new float[len];
		for (int i = 0; i < len; i++)
			arr[i] = reader.ReadSingle();
		return arr;
	}
}