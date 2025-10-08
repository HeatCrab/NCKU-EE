#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

/* Count lines, alphanumeric chars, uppercase letters, and words */
void count_file_statistics(const char *filename, int *lines,
                          int *characters, int *uppercase, int *words) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        printf("Error: Cannot open file %s\n", filename);
        exit(1);
    }
    
    *lines = 0;
    *characters = 0;
    *uppercase = 0;
    *words = 0;
    
    int ch;
    int in_word = 0;
    
    while ((ch = fgetc(file)) != EOF) {
        if (ch == '\n') {
            (*lines)++;
            in_word = 0;
        }
        
        if (isalnum(ch)) {
            (*characters)++;
            
            if (isupper(ch)) {
                (*uppercase)++;
            }
            
            if (!in_word) {
                (*words)++;
                in_word = 1;
            }
        } else if (ch == ' ' || ch == '\n' || ch == '\t') {
            in_word = 0;
        }
    }
    
    if (*lines == 0 || ch != '\n') {
        (*lines)++;
    }

    fclose(file);
}

/* Convert text to uppercase and write to "UPPER" file */
void convert_to_uppercase(const char *filename) {
    FILE *input_file = fopen(filename, "r");
    if (input_file == NULL) {
        printf("Error: Cannot open input file %s\n", filename);
        exit(1);
    }

    FILE *output_file = fopen("UPPER", "w");
    if (output_file == NULL) {
        printf("Error: Cannot create output file UPPER\n");
        fclose(input_file);
        exit(1);
    }
    
    int ch;
    while ((ch = fgetc(input_file)) != EOF) {
        fputc(toupper(ch), output_file);
    }
    
    fclose(input_file);
    fclose(output_file);

    printf("Uppercase conversion completed. Output saved to 'UPPER' file.\n");
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <filename>\n", argv[0]);
        return 1;
    }

    const char *filename = argv[1];
    int lines, characters, uppercase, words;

    count_file_statistics(filename, &lines, &characters, &uppercase, &words);

    printf("File: %s\n", filename);
    printf("Lines: %d\n", lines);
    printf("Characters (alphanumeric): %d\n", characters);
    printf("Uppercase letters: %d\n", uppercase);
    printf("Words: %d\n", words);
    printf("\n");

    convert_to_uppercase(filename);

    return 0;
}