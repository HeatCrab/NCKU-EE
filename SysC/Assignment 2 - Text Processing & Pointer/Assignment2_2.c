#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <memory_size>\n", argv[0]);
        return 1;
    }

    int memory_size = atoi(argv[1]);

    if (memory_size <= 0) {
        printf("Error: Memory size must be positive\n");
        return 1;
    }

    void *allocated_memory = malloc(memory_size);
    if (allocated_memory == NULL) {
        printf("Error: Memory allocation failed\n");
        return 1;
    }

    /* Fill memory with 'A' to 'Z' then '1' to '9' using char pointer */
    char *char_ptr = (char *)allocated_memory;

    for (int i = 0; i < memory_size; i++) {
        int pos = i % 35;
        if (pos < 26) {
            char_ptr[i] = 'A' + pos;
        } else {
            char_ptr[i] = '1' + (pos - 26);
        }
    }

    printf("Generated string: ");
    fwrite(char_ptr, 1, memory_size, stdout);
    printf("\n\n");

    /* Print memory as integers (value : value-1) using int pointer */
    int *int_ptr = (int *)allocated_memory;
    int num_integers = memory_size / sizeof(int);
    int i = 0;

    printf("Memory content as integers (value : value-1):\n");
    while (i < num_integers) {
        if ((i + 1) * sizeof(int) <= memory_size) {
            int value = int_ptr[i];
            printf("%d : %d\n", value, value - 1);
        } else {
            break;
        }
        i++;
    }

    free(allocated_memory);

    return 0;
}