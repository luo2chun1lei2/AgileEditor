#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/** comment1 */
void my_print(const char *p)
{
	printf(p); /// comment2
}

/// main comment
int main()
{
	int v = 10;
	char *p = (char *)malloc(100);
	memset(p, 0, 100);

	if (v < 100) {
		sprintf(p, "%d is less than 100.\n", v);
	} else {
		sprintf(p, "%d is more than 100.\n", v);
	}
	my_print(p);

	return 0;
}
