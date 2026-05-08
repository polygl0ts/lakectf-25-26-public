savedcmd_furrow.mod := printf '%s\n'   furrow.o | awk '!x[$$0]++ { print("./"$$0) }' > furrow.mod
