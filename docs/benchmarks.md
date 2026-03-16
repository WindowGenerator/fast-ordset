# benchmark_time.sh output

## Running

```bash
./scripts/benchmark_time.sh
```

## Example output (reference run)

Results from **Darwin arm64**, **Python 3.13.9**, **Apple M2 Pro**. Mean time per operation; lower is better. `fast_ordset` vs `ordered-set`.


| Group / scenario                      | fast_ordset | ordered_set | Winner / note               |
| ------------------------------------- | ----------- | ----------- | --------------------------- |
| **construction** empty                | 116 ns      | 118 ns      | ~tie                        |
| **construction** from list n=10k      | 278 µs      | 752 µs      | **fast_ordset ~2.7×**       |
| **add** n=10k                         | 761 µs      | 801 µs      | **fast_ordset ~1.05×**      |
| **contains** present (single) n=10k   | 78 ns       | 71 ns       | ordered_set slightly faster |
| **contains** absent (single) n=10k    | 62 ns       | 65 ns       | **fast_ordset** slightly    |
| **contains** 1000 lookups n=1k        | 49.6 µs     | 39.4 µs     | **ordered_set ~1.26×**      |
| **iteration** to list n=50k           | 1.24 ms     | 159 µs      | **ordered_set ~7.8×**       |
| **to_list** / list() n=10k            | 36 µs       | 32 µs       | ordered_set slightly        |
| **to_list** / list() n=50k            | 185 µs      | 158 µs      | ordered_set                 |
| **to_list** / list() n=100k           | 380 µs      | 318 µs      | ordered_set                 |
| **getitem** middle n=10k              | 59 ns       | 395 ns      | **fast_ordset ~6.7×**       |
| **getitem** 1000 accesses n=10k       | 30 µs       | 312 µs      | **fast_ordset ~10×**        |
| **remove** one (middle) n=10k         | 299 µs      | 1035 µs     | **fast_ordset ~3.5×**       |
| **pop** end n=10k                     | 305 µs      | 758 µs      | **fast_ordset ~2.5×**       |
| **pop** middle n=10k                  | 306 µs      | 779 µs      | **fast_ordset ~2.5×**       |
| **union** n=10k                       | 698 µs      | 1504 µs     | **fast_ordset ~2.2×**       |
| **update** n=10k                      | 739 µs      | 1470 µs     | **fast_ordset ~2×**         |
| **intersection** n=10k                | 656 µs      | 653 µs      | ~tie                        |
| **intersection_update** n=10k         | 1121 µs     | 1185 µs     | ~tie                        |
| **difference** n=10k                  | 605 µs      | 627 µs      | **fast_ordset** slightly    |
| **difference_update** n=10k           | 1040 µs     | 1221 µs     | **fast_ordset ~1.2×**       |
| **symmetric_difference** n=10k        | 1011 µs     | 3846 µs     | **fast_ordset ~3.8×**       |
| **symmetric_difference_update** n=10k | 1463 µs     | 1723 µs     | **fast_ordset ~1.2×**       |
| **copy** n=10k                        | 78 µs       | 736 µs      | **fast_ordset ~9.5×**       |


**Summary:** fast_ordset wins on construction from list, getitem, remove, pop, union/update, symmetric_difference, and copy. ordered_set wins on iteration-to-list and to_list (and many contains in a tight loop).