# Robocup Log Analyzer
Read robocup logs from games.
Evaluate statistics.
Save as JSON.


## Subfolders
- `analysing_tools/`
  - [`datamodel/`](./analysing_tools/datamodel)
      - data classes
  - [`parser/`](./analysing_tools/parser)
      - reading `*.rgc` and `*.rcl` files and generating the dataclasses
  - [`extraction/`](./analysing_tools/extraction)
      - calculation of additional base data from parsed data
  - [`analysis/`](./analysing_tools/analysis)
      - analyse the data model
  - [`constants/`](./analysing_tools/constants)
    - constants from the robocup game
- [`experiments/`](./experiments)
    - standalone experiments; other `main(...)` functions; 
- main.py
  - running without pushing things to the server
- RoboCup_main.py
  - the file that is called by the server
