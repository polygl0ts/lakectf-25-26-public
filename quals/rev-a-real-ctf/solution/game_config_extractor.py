input_file = "../verifier"
output_file = "game_config.dat"
check_file = "../verifier_src/game_config.dat"

# The offset and the length can be found at the beginning of the function verifier::game_config::load in the verifier ELF.
# Be careful: decompilers usually display addresses and not raw file offsets
offset = 0x2e1f6
length = 0x374

# Extract and save
with open(input_file, "rb") as f_in:
    f_in.seek(offset)                  # move to the start position
    game_config = f_in.read(length)     # read the selected bytes

with open(output_file, "wb") as f_out:
    f_out.write(game_config)

print(f"Extracted {len(game_config)} bytes into {output_file}")

with open(check_file, "rb") as f_check:
    check_data = f_check.read()
    if game_config == check_data:
        print("Check passed: extracted game configuration the check file.")
    else:
        print("Check failed: wrong game configuration data.")

