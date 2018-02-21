#include <stdio.h>
#include <pigpio.h>

int main(int argc, char *argv[]) {
	if (gpioInitialise()<0) { printf("GPIO INIT FAIL\n"); return 1;}
	printf("Hello World\n");
	if(argc>1) {
		for(int x=1;x<argc;++x) {
			printf("Typing... %s%i\n",argv[x],x);
		}
	} else printf("No additional args\n");
	
	gpioTerminate();
}
