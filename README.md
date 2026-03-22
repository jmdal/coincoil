Design files for an electromagnetic coilgun currently in development.

The intention for the coilgun is to be able to shoot coins, specifically the Filipino 1-peso coin (the new one, not the old) at a decent speed.

This repo contains simulations and simulation code, as well as some design files. Results are excluded; file size and count is far larger than the dev files.

Primary test results, as well as some design deliberation documents, can be found [here (Spreadsheet)](https://docs.google.com/spreadsheets/d/1q969p90pQs-uu_K9dNQ5dfCKq3uF5XSzDFNZLuAj6OA/edit?usp=sharing) and [here (Older design files)](https://drive.google.com/drive/folders/1uCv4Be62ojAWk9Jn0AJoW_bbN4CBgA6p?usp=sharing)


## Simulation Details
2 primary simulation apps are currently used, [LTSpice](https://www.analog.com/en/resources/design-tools-and-calculators/ltspice-simulator.html) and [FEMM](https://www.femm.info/)
More tests will be done in the future; future iterations may use different apps and software.
A considered contender for other software is [FreeCAD](https://www.freecad.org/) and its inbuilt ELMER electromagnetics solver to replace FEMM so that the 3d-model and CAD files that will be used as primary coilgun design can be modified and simulated directly rather than being abstracted.

[Python](https://www.python.org/) is used as a cross-controller between all the simulations (see pyscripts folder, such files are named "fullsim"); take data from initial parameters, feed initial data into electric simulation, take sim data and further feed into magnetics simulation, then post-process and report data in a .csv file to be integrated into a larger spreadsheet (see results spreadsheet). By use of iterables, thousands of test cases can be batch-tested without manual intervention.

## Prototype Details
Details on physical prototypes will be placed in a Google Doc soon to come; this will begin once equipment is acquired and the first prototypes are assembled. Design files for creating such prototypes will continue to be placed and updated in this repository. Check back every once in a while to see updates.

## Miscellaneous Details
Don't mind the stated 45%+ "Action Game Script" listed on the repo; I have no clue why it says that but it's most likely reading the .asc files that were used for LTSpice. In reality, as of writing the project is around 90%+ Python and the rest was some Lua used in scripts for FEMM before switching to the PyFEMM interface.
