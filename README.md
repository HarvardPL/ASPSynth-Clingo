# ASPSynth-Clingo

This repo contains ASPSynth-Clingo, the best-performing Datalog synthesis tool from the POPL'23 paper "From SMT to ASP: Solver-Based Approaches to Solving Datalog Synthesis-as-Rule-Selection Problems" by Aaron Bembenek, Michael Greenberg, and Stephen Chong (available [here](https://dl.acm.org/doi/abs/10.1145/3571200)).

It also contains the benchmarks we used, which, as described in the paper, are based on benchmarks from prior work.

The only dependencies are Python and the answer set programming (ASP) solver [Clingo](https://potassco.org/clingo/) (the `clingo` binary needs to be on your path).

You run ASPSynth-Clingo on a benchmark directory:

```shell
python src/aspsynth-clingo benchmarks/regular/scc
```

The output is a little messy, but (towards the end) contains the answer set of `rule` facts that corresponds to the solution to the synthesis problem.

If you run ASPSynth-Clingo on large problems and specify a minimization criterion (# of premises or # of rules), you might want to increase the number of threads used to search for a solution:

```
python src/aspsynth-clingo benchmarks/scale/scc-100x-100 --minimize rules --parallelism 8
```

(We used 32 threads on the scaling benchmarks in our evaluation.)

The additional tools described in the paper are available in the official paper artifact (available [here](https://zenodo.org/records/7150677)).