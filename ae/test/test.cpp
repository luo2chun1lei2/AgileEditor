#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void test_mem();
void test_print();
void my_print(const char *p);

/// main comment
int main()
{
	test_mem();
	test_print();
	
	return 0;
}

/// test for malloc and free.
void test_mem()
{
	char * p = (char *)malloc(4*8);
	
	p[3] = '0';
	
	free(p);
	
	p[4] = '1';
	
	free(p);
}

/** comment1 */
void my_print(const char *p)
{
	/* comment2 */
	printf("%s", p);
}

/// test for print and malloc.
void test_print()
{
	int v = 10;
	char *p = (char *)malloc(100);
	memset(p, 0, 100);

	if (v < 100) {
		sprintf(p, "%d is less than 100.\n", v);
	} else if(v < 1000) {
		sprintf(p, "%d is less than 1000.\n", v);
	} else {
		sprintf(p, "%d is more than 100.\n", v);
	}
	my_print(p);
}
