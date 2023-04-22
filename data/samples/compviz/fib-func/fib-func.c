int fib(int numTerms) 
{
  /* initialize first and second terms */
  int t1 = 0, t2 = 1;

  /* initialize the next term (3rd term) */
  int nextTerm = t1 + t2;

  /* Calculate the next "numTerms" terms */
  int counter;
  for (counter = 3; counter <= numTerms; ++counter) 
  {
    t1 = t2;
    t2 = nextTerm;
    nextTerm = t1 + t2;
  }

  return 0;
}
