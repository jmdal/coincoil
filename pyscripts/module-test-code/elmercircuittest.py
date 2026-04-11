import sys
from elmer_circuitbuilder import *                                                 # STEP 1
# -------------------------------------------------------------------------------

def main(argv=None):

    # name output file - do not remove                                             # STEP 2
    output_file = "pyscripts/module-test-code/output/coiltest.definition"

    # initialize circuits: number of circuits - do not remove                      # STEP 3
    c = number_of_circuits(1)

    # reference/ground node needed - do not remove.                                # STEP 4
    c[1].ref_node = 1

    # ----------------------- Electrical Network Definition ---------------------  # STEP 5

    # Components
    I1 = I("I1", 1, 2, 2742)
    Com1 = ElmerComponent("Coil1", 2, 1, 1, ["Coil"])

    Com1.is3D()
    Com1.stranded(1,0)
    Com1.isClosed()

    # Define coil type: massive, stranded, foil

    # Define dimension related features if needed (closed, open)

    # store components in array components = [comp1, comp2,...] - do not remove    # STEP 6
    c[1].components.append([I1,Com1])                                 

    # ---------------------------------------------------------------------------

    # generate elmer circuit.definitions - do not remove / do not edit             # STEP 7
    generate_elmer_circuits(c, output_file)                              

    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
