FROM ubuntu:22.04

WORKDIR /app

COPY verifier .
COPY flag.txt .

# Make sure the binary is executable
RUN chmod +x verifier

# Specify the command to run the binary
CMD ["./verifier"]
