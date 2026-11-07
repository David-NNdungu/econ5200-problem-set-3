# The Rollout That Looked Like It Worked

I used difference-in-differences to evaluate a simulated workforce training rollout. I started by reproducing Card and Krueger’s estimate of +2.75 full-time-equivalent jobs per restaurant. Then I simulated a county-year panel where regional workforce boards adopted training at different times and the effect grew the longer counties had been in the program.

The agency’s two-way fixed-effects estimate was 4.46, below the smallest true effect of 5.00. When I broke down the estimate, I found that comparisons using already-treated counties as controls received 48.55% of the weight.

Using only counties that were untreated at the time of each comparison, I estimated an average effect of 10.48, close to the simulated true average of 10.66. I also ran a board-level wild cluster bootstrap. It gave a p-value of 0.133 for the agency’s estimate, which was above the 5% significance threshold.

- [Notebook and results](Econ_5200_PS3.ipynb)
- [Difference-in-differences toolkit](src/did_toolkit.py)
- [Phase 4 AI appendix](ai-appendix.md)
