using System;
using System.Linq;
using System.IO;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using System.Text.RegularExpressions;

class Solution
{
    static void Main(string[] args)
    {
        var resistDict = new Dictionary<string, int>();
        int N = int.Parse(Console.ReadLine());
        for (int i = 0; i < N; i++)
        {
            string[] inputs = Console.ReadLine().Split(' ');
            string name = inputs[0];
            int R = int.Parse(inputs[1]);
            resistDict.Add(name, R);
        }
        foreach(KeyValuePair<string,int> item in resistDict){
            Console.Error.WriteLine("Name={0}, Value={1}", item.Key, item.Value);
        }
        string circuit = Console.ReadLine();
        Console.Error.WriteLine("Starting Circuit is {0}", circuit);
        string converted = "";

        foreach (string chunk in circuit.Split(" ")){
            if(resistDict.ContainsKey(chunk)){
                converted += resistDict[chunk];
            }
            else{
                converted += chunk;
            }
            converted += " ";
        }
        Console.Error.WriteLine("Testing out the new string. {0}", converted);
        double Answer = Math.Round(Get_Circuit(converted),1);


        // Write an answer using Console.Error.WriteLine()
        // To debug: Console.Error.WriteLine("Debug messages...");

        Console.WriteLine(Answer.ToString("N1"));
    }

    private static double Get_Circuit(string Circuit){
        string[] circuitArray = Circuit.Split(" ");

        var series_filter = new Regex(@"\(\s((\w*\.*\w+\s)+)\)");
        var parallel_filter = new Regex(@"\[\s((\w*\.*\w+\s)+)\]");

        Match series_matches = series_filter.Match(Circuit); //will find an isolated series circuit
        Match parallel_matches = parallel_filter.Match(Circuit); //will find an isolated parallel circuit
        // Console.Error.WriteLine(Circuit);
        // foreach(var item in series_matches){
        //     Console.Error.WriteLine(item.Groups[1]);
        // }
        
        Console.Error.WriteLine("\nCurrent Circuit: {0}", Circuit);
        if (series_matches.Success){
            string series_result = series_matches.Groups[1].ToString();
            
            string series_equiv=Series_Calc(series_result);
            // Circuit = Regex.Replace(Circuit, series_filter.ToString(), series_equiv);
            Circuit = series_filter.Replace(Circuit, series_equiv,1);
            Console.Error.WriteLine("{0} is in series. Equivalent resistance is {1}", series_matches.Groups[1], series_equiv);
        }
        else if (parallel_matches.Success){
            string parallel_result = parallel_matches.Groups[1].ToString();
            string parallel_equiv=Parallel_Calc(parallel_result);
            // Circuit = Regex.Replace(Circuit, parallel_filter.ToString(), parallel_equiv);
            Circuit = parallel_filter.Replace(Circuit, parallel_equiv,1);
            Console.Error.WriteLine("{0} is in parallel. Equivalent resistance is {1}", parallel_matches.Groups[1],parallel_equiv);
        }
        if (!(series_matches.Success || parallel_matches.Success)){
            Console.Error.WriteLine("{0} is already reduced", Circuit);
            return Double.Parse(Circuit);
        }
        return Get_Circuit(Circuit);
    }
    private static string Series_Calc(string CircuitInput){
        var DeconstructedCircuit = CircuitInput.Split(" ");
        // Console.Error.WriteLine(DeconstructedCircuit);
        double result = 0;
        foreach (string item in DeconstructedCircuit){
            try{
                result += Double.Parse(item);
                // Console.Error.WriteLine("Our item is -{0}-\nOur result is {1}",item, result);
            }catch{}
        }
        return result.ToString();
    }
    private static string Parallel_Calc(string CircuitInput){
        var DeconstructedCircuit = CircuitInput.Split(" ");
        // Console.Error.WriteLine(DeconstructedCircuit);
        double result = 0;
        foreach (string item in DeconstructedCircuit){
            try{
                result += 1/Double.Parse(item);
                // Console.Error.WriteLine("Our item is -{0}-\nOur result is {1}",item, result);
            }catch(FormatException){}
        }
        result = 1/result;
        return result.ToString();
    }
}
