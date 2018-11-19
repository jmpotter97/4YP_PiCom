#include <stdio.h>
#include <stdlib.h> // for int = atoi(char), malloc

int main(int argc, char *argv[]) {
	
    int* receive_data_mask = calloc(10, sizeof(int));
    *receive_data_mask = 0;
	free(receive_data_mask);
	printf("YAY");
	
}
