#include <ctype.h>
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/prctl.h>
#include <time.h>
#include <unistd.h>

#define PRISONERS 100
#define MAX_ATTEMPTS 50

static int verbose = 0;

static int drawers[PRISONERS] = {
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
    31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
    41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
    51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
    61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
    71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
    81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
    91, 92, 93, 94, 95, 96, 97, 98, 99, 100
};

static void rstrip(char *s) {
    size_t len = s ? strlen(s) : 0;
    while (len && (s[len - 1] == '\n' || s[len - 1] == '\r')) {
        s[--len] = '\0';
    }
}

static unsigned int seed_rng(void) {
    unsigned int seed = (unsigned int)time(NULL);
    FILE *ur = fopen("/dev/urandom", "rb");
    if (ur) {
        if (fread(&seed, sizeof(seed), 1, ur) != 1) {
            seed ^= (unsigned int)getpid();
        }
        fclose(ur);
    }
    return seed;
}

static void shuffle_drawers(void) {
    srand(seed_rng());
    for (int i = PRISONERS - 1; i > 0; --i) {
        int j = rand() % (i + 1);
        int tmp = drawers[i];
        drawers[i] = drawers[j];
        drawers[j] = tmp;
    }
}

static int read_script(int prisoner, char *out_path, size_t out_sz) {
    char tmpl[] = "/tmp/playerXXXXXX";
    int fd = mkstemp(tmpl);
    if (fd < 0) {
        perror("mkstemp");
        return -1;
    }
    FILE *f = fdopen(fd, "w");
    if (!f) {
        perror("fdopen");
        close(fd);
        unlink(tmpl);
        return -1;
    }

    printf("Provide Python script for player %d (end with string 'EOF' on its own line):\n", prisoner);
    fflush(stdout);

    char *line = NULL;
    size_t cap = 0;
    ssize_t got;
    int ok = 0;
    while ((got = getline(&line, &cap, stdin)) != -1) {
        rstrip(line);
        if (strcmp(line, "EOF") == 0) {
            ok = 1;
            break;
        }
        fputs(line, f);
        fputc('\n', f);
    }
    free(line);

    if (!ok) {
        fprintf(stderr, "EOF marker missing.\n");
        fclose(f);
        unlink(tmpl);
        return -1;
    }

    fflush(f);
    fclose(f);
    snprintf(out_path, out_sz, "%s", tmpl);
    return 0;
}

static int parse_choice(const char *resp) {
    if (!resp || !resp[0]) {
        return -1;
    }
    char *end = NULL;
    long val = strtol(resp, &end, 10);
    while (end && *end && isspace((unsigned char)*end)) {
        ++end;
    }
    if (!end || *end != '\0') {
        return -1;
    }
    if (val < 1 || val > PRISONERS) {
        return -1;
    }
    return (int)val;
}

static void clean_child(pid_t pid) {
    kill(pid, SIGTERM);
    waitpid(pid, NULL, 0);
}

static int run_prisoner(int prisoner, const char *script_path) {
    int to_child[2], from_child[2];
    if (pipe(to_child) < 0 || pipe(from_child) < 0) {
        perror("pipe");
        return -1;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        close(to_child[0]);
        close(to_child[1]);
        close(from_child[0]);
        close(from_child[1]);
        return -1;
    }

    if (pid == 0) {
        dup2(to_child[0], STDIN_FILENO);
        dup2(from_child[1], STDOUT_FILENO);
        dup2(from_child[1], STDERR_FILENO);
        close(to_child[0]);
        close(to_child[1]);
        close(from_child[0]);
        close(from_child[1]);
        execlp("python3", "python3", "-u", script_path, (char *)NULL);
        _exit(1);
    }

    close(to_child[0]);
    close(from_child[1]);
    FILE *child_in = fdopen(to_child[1], "w");
    FILE *child_out = fdopen(from_child[0], "r");
    if (!child_in || !child_out) {
        perror("fdopen");
        if (child_in) fclose(child_in);
        if (child_out) fclose(child_out);
        clean_child(pid);
        return -1;
    }

    char resp[128];
    for (int attempts = MAX_ATTEMPTS; attempts > 0; --attempts) {
        char prompt[128];
        snprintf(prompt, sizeof(prompt),
                 "You are player number %d. You have %d attempts left. Which box do you want to open?",
                 prisoner, attempts);
        printf("%s\n", prompt);
        fflush(stdout);

        fprintf(child_in, "%s\n", prompt);
        fflush(child_in);

        if (!fgets(resp, sizeof(resp), child_out)) {
            printf("Python script terminated early.\n");
            fclose(child_in);
            fclose(child_out);
            clean_child(pid);
            return -1;
        }
        rstrip(resp);
        if (verbose) {
            printf("[python %d] %s\n", prisoner, resp);
        }
        int choice = parse_choice(resp);
        if (choice < 1) {
            printf("Invalid response from Python. Quitting.\n");
            fclose(child_in);
            fclose(child_out);
            clean_child(pid);
            return -1;
        }

        int found = drawers[choice - 1];
        printf("The box %d contains number %d.\n", choice, found);
        fprintf(child_in, "FOUND %d\n", found);
        fflush(child_in);
        if (found == prisoner) {
            printf("Player %d succeeded.\n", prisoner);
            fclose(child_in);
            fclose(child_out);
            clean_child(pid);
            return 0;
        }
    }

    printf("Player %d failed after %d attempts.\n", prisoner, MAX_ATTEMPTS);
    fclose(child_in);
    fclose(child_out);
    clean_child(pid);
    return -1;
}

int main(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "-v") == 0) {
        verbose = 1;
    } else if (argc != 1) {
        fprintf(stderr, "Usage: %s [-v]\n", argv[0]);
        return 1;
    }
    if (prctl(PR_SET_DUMPABLE, 0) != 0) {
        perror("prctl");
        return 1;
    }
    const char *env_flag = getenv("FLAG");
    if (!env_flag) {
        fprintf(stderr, "FLAG environment variable not set.\n");
        return 1;
    }
    char flag_buf[4096];
    size_t flag_len = 0;
    while (flag_len + 1 < sizeof(flag_buf) && env_flag[flag_len]) {
        flag_buf[flag_len] = env_flag[flag_len];
        ++flag_len;
    }
    flag_buf[flag_len] = '\0';
    unsetenv("FLAG");

    shuffle_drawers();
    for (int p = 1; p <= PRISONERS; ++p) {
        char script_path[64];
        if (read_script(p, script_path, sizeof(script_path)) != 0) {
            return 1;
        }
        int res = run_prisoner(p, script_path);
        unlink(script_path);
        if (res != 0) {
            return 1;
        }
    }

    printf("All players succeeded! Flag:\n");
    fwrite(flag_buf, 1, flag_len, stdout);
    putchar('\n');
    return 0;
}
