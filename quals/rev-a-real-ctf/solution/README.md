The idea of this challenge is to play the secret level contained in the verifier but not on the user's build.
The player must first discover that a secret level exists, then figure out how to extract it from the binary ELF file, and finally play through the level.

Instructions to solve the challenge:
1. Extract the game_config from the verifier which contains the secret level
2. Load the secret level into the game*
3. Play the level, then save the replay and send it to the verifier

*The game is shipped with BepInEx already installed. This is a mod loader allowing to add custom C# code easily. You can use dnSpy on `A_REAL_CTF_Data/Manager/Assembly-CSharp.dll` to understand how each class of the game works.
Note that it's absolutely not mandatory to use BepInEx to solve the challenge. One could directly patch `A_REAL_CTF_Data/level0` with the good level, modify `A_REAL_CTF_Data/Manager/Assembly-CSharp.dll` or even just reimplement a new game with the correct physics.

Detailed instructions:
1. Run `game_config_extractor.py`, it will extract the `game_config.dat` from the verifier app.
2. Add `SolveMod.dll` and `game_config.dat` inside the `BepInEx/plugins` folder of the game build.
3. Simply play the patched level

Note: The verifier isn't prefect and may reject even legitimate replays, you may need to retry several times step 3.