int perfect(int test)
{
     /* Utility counter and sum */
     int counter = 1;
     int sum = 0;

     /* Count from 0 to test, adding all divisors of test to the sum */
     while (counter < test)
     {
          if (test % counter == 0)
               sum = sum + counter;
          counter++;
     }

     /* If the sum == counter, this is a perfect number */
     return (sum == counter);
}
