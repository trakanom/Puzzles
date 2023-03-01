using System;
using System.Linq;
using System.IO;
using System.Text;
using System.Collections;
using System.Collections.Generic;

class Solution
{


    public static int[] CalculateAnswer(int TargetValue, int[] MaximumsArray)
    {
        var N = MaximumsArray.Length;
        var X = new int[N];
        Array.Sort(MaximumsArray);
        //maximum budget for participant. Make sure X[i] <= V[i] for all i<N.
        int ProposedValue;
        int ProposedRemainder;
        int Debt = TargetValue;
        for (int i=0; i< N; i++){
            
            ProposedValue = Debt/(N-i);
            ProposedRemainder =  (i <= Math.Abs(Debt%(N-i)) ? (Debt%(N-i))/(N-i) : 0);
            X[i] = Math.Min(MaximumsArray[i], ProposedValue+ProposedRemainder);
            Debt -= X[i];
            Console.Error.WriteLine("X[i]: {0}, V: {1}, R: {2}, Max: {3} ",X[i], ProposedValue, ProposedRemainder, MaximumsArray[i]);
        }
        Array.Sort(X);
        Console.Error.WriteLine("Sum: {0}, Avg: {1}",X.Sum(),X.Average());
        return X;
    }
    public static string GetAnswer(int TargetValue, int[] MaximumsArray)
    {
        /*
            Algorithm Entry.
            Stringifies the answer array or returns DefaultResponse if impossible.
        */
        const string DefaultResponse = "IMPOSSIBLE";
        if (MaximumsArray.Sum() < TargetValue)
        {
            return DefaultResponse; //Early return if impossible.
        }
        var Answer = new StringBuilder();
        Answer.Append(StringifyAnswer(CalculateAnswer(TargetValue, MaximumsArray)));
        return Answer.ToString();
    }
    public static string StringifyAnswer(int[] answer_list){
        //builds a string that separates the contents with a new line.
        //python equivalent: "\n".join([answer for answer in answer_list])
        Array.Sort(answer_list);
        var solution = new StringBuilder();
        for(int i=0; i<answer_list.Length; i++){
            solution.Append(answer_list[i]);
            if (i+1 <= answer_list.Length){
                solution.Append("\n");
            }
        }
        return solution.ToString();
    }
    public static void Main(string[] args)
    {
        int N = int.Parse(Console.ReadLine()); //number of participants
        int C = int.Parse(Console.ReadLine()); //cost of gift. Our target value.
        int[] V = new int[N]; //budgets
        int[] X = new int[N]; //solution storage. 
        for (int i = 0; i < N; i++) //iterating through the participants.
        {
            V[i] = int.Parse(Console.ReadLine());
        }

        Console.WriteLine(GetAnswer(C, V)); // "IMPOSSIBLE" if not possible, else the sequence separated by new lines.
    }
}
