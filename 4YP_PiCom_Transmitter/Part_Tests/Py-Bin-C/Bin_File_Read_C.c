#include <stdio.h>
#include <stdlib.h>

int main(int argc, char* argv[]) {

    FILE *file;
    long size;
    size_t size_32int = sizeof(uint32_t);
    char* path;
    if(argc>1) path = argv[1];
    else path = "data.bin";

    file = fopen(path, "rb");
    fseek (file , 0 , SEEK_END);
    size = ftell(file);
    printf("Size of file: %i\n",size);
    rewind (file);

    uint32_t* transmit_data = calloc(size/size_32int, size_32int);
    fread(transmit_data, size_32int, size/size_32int, file);

    fclose(file);

    for(int i = 0; i<256; i++) {
        printf("%i\n", transmit_data[i]);
    }

    return 0;
}