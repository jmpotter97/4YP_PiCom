#include <stdio.h>
// INCLUDE PIGPIO

int main(int argc, char *argv[]) {
	printf("Hello World\n");
	if(argc>1) {
		for(int x=1;x<argc;x=x+1) {
			char* Str = "" + argv[1][x];
			printf("Typing... %s\n",Str);
		}
	} else printf("No additional args/n");
}
