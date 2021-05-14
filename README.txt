========================
rmc6f_stuff
========================

contains:

-----------------
dist_calc_coord
-----------------
Function for calculating distances between two atoms. It takes three
parameters in order:
    -   Atomic coordinate 1 in RMC6F internal form.
    -   Atomic coordinate 2 in RMC6F internal form.
    -   Lattice vector.
Here, assuming the crystallographic fractional coordination of a certain
atoms is a, the corresponding RMC6F internal coordinate will be 
(2 * a - 1).
-------------------------------------------------------------------------

-----------------
RMC6FReader
-----------------
Class concerning reading in RMC6F configuration. The initializer of the
class will be default read in the specified (as the parameter when
declaring an instance of the class) configuration.

Namespace:
    -   atomsCoord, list containing atomic crystallographic coordinates.
    -   atomsCoordInt, list containing atomic coordinates in RMC6F
        internal form (see explanation above).
    -   atomsEle, list containing atomic element symbols.
    -   atomsLine, list containing as it says.
    -   atomTypes, atom types present.
    -   numAtomEachType, number of each type of atom.
    -   numTypeAtom, number of atomic types.
=========================================================================

========================
bulk_stuff
========================

contains:

-----------------
BulkStuff
-----------------
Class containing methods to process bulk RMC6F configuration.

    contains:

    -----------------
    bulk_to_shells
    -----------------
    Method to generate spherical shells from a random center from the
    specified RMC6F configuration. It takes an instance of RMC6FReader
    class as argument. The purpose of such a method is to compare with
    the corresponding analysis for a nanoparticle model.
=========================================================================

========================
nano_stuff
========================

contains:

-----------------
NanoStuff
-----------------
Class containing methods to process RMC6F configuration of
nanoparticle(s).

    contains:

    -----------------
    cent_rad_config
    -----------------
    Method to configure the center and radius of the given nanoparticle
    model in RMC6F format. It takes an instance of RMC6FReader class as
    argument.

    Namespace:
        -   centPos, list containing the center position of the
            nanoparticle in crystallographic coordinate.
        -   centPosInt, list containing the center position of the
            nanoparticle in RMC6F internal form (see explanation above).
    ---------------------------------------------------------------------
    
    -----------------
    np_to_shells
    -----------------
    Method divide the specified nanoparticle into shells. It takes an
    instance of RMC6FReader class as argument.
=========================================================================

============================
Yuanpeng Zhang @ Jun-21-2019
NIST & ORNL
============================
