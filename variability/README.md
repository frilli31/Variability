### Variant Variability

```python
def compute_variant_variability(log: lg.EventLog) -> int:
    return len(set(tuple(event["concept:name"] for event in case) for case in log))
```

**Advantages**
- simplicity

**Disadvantages**
- doesn't consider size of log (big logs are penalized)
- doesn't consider how different are variants

### Edit Distance Variability
Compute the average edit distance (Levenshtein distance) between each pairs of traces.

**Advantages**
- take account of size of log
- consider how frequent are each variant

**Disadvantages**
- doesn't consider the length of each traces and the variance (logs with longest traces and high variance of length are penalized)


### My Variability
The average edit distance will be higher if the length of cases is higher, to
be able to compare the result with logs with a different average length we can 
divide each edit distance with the maximum edit distance between that cases 
(the length of the longest case involved).

**Advantages**
- gives a output between 0 and 1: immediately interpretable
- the number represents the percentage of portion of string that is equals
- resolve the problem of length of traces 

**Disadvantages**
- if the cases have much different length (e.g. 10 and 50) the measure of the 
distance is high and is mostly given by the difference of length, not by the 
real miss-match of characters
- In case of cycles in the model this error is relevant
- ABCABC and ABCXYZ have the same distance of ABCABC and ABC

### My Variability LZW
We try to solve the problem of cycles introducing a form of compression: the 
next time we find a sequence of activity we substitute that sequence with a 
single activity (as does LWZ compression algorithm).  
This mechanism allow us to penalize less in case of cycles because the fallowing 
iterations will produce a string with a shorter trace.  
This mechanism have the problem that penalize also traces that has an equal parts
in cycles (that is compressed) and a different part outside (non-compressed, in the
final percentage will have an higher impact).  
This mechanism significantly improves similarity in:
- L13.xes
- BPIChallenge2012.xes
- BPIChallenge2019.xes
    - Variants: 11973
    - Avg Edit Distance: 5.125463586773214
    - Avg Length: 6.33971970413214
    - My Variability: 0.3750578131941088
    - My Variability LZW: 0.4554336076013703

I haven't found any computable better measure.  
LZW can help identify the presence and the structure of cycles in models.    
I think LZW approach goes in the right direction because the idea of penalize less
lots of missing events rather than lots of wrong events is right, but a I think a 
more complicated 
approach can obtain better results (a measure more adherent to a possible model
that combine the traces) computing the distance in a different way of with different
pre/post operations, maybe including in some way swap

Problem still to be solved: 
- LZW can have different result for similar string
- LZW in some case can worse performances (ABCABC and ABCDBF)
- the parallel operation in the model is too penalized because there isn't 
    swap operation in Levenshtein_distance (It would te too computationally
    expensive) -> solve with Damerau-levenshtein enlarged to 3 values 
    (local-swaps)
