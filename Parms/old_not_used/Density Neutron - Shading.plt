$ Density Neutron plot file withshading
$
$ Track Format
$                    --------Logarithmic Tracks--------  OverView       
$TRACK  Width  Grid  Grid Decades Left_Scale Minor_Grid  Track  Grid Lines
$
$ Curve Format
$CURVE Name   Left_Scale Right_Scale Backup Thickness Color Log/Lin Point_Plotting
$ Names that start with a '*' are curve Types
$ Left and Right scale values that start with * will use the curve default value
$
$ Grid and depth Format
$     Depth ---Grid Spacing--- User Defined ----------------Hard Copy--------------
$GRID Curve Heavy Medium Light   Spacing    Top Depth Bottom Depth Scale Grid Color
 $
$Recognised Colors are:
$  Aqua, Black, Blue, DkGray, Fuchsia, Gray, Green, Lime, LtGray,
$  Maroon, Navy, Olive, Purple, Red, Teal, White, Yellow
$
$
$ gr caliper track
TRACK    2.00   Yes   No     2    0.200          No       No       5
$CURVE Name   Left_Scale Right_Scale Backup Thickness Color Log/Lin Point_Plotting
CURVE  *GammaRay *         *         RBU        1     Green   LIN      Solid
CURVE  *Caliper  *         *         RBU        1     Blue    LIN      Solid
$ make depth track
TRACK    0.50    No   No     2    0.200          No       No       5
CURVE   *Index  0.0000     1.0000   NONE       1     Black   LIN      Solid
$ density neutron track
TRACK   4.00    Yes   No     4    0.200         Yes       No      10
CURVE  *Density  *         *         LBU        1     Red     LIN      Solid
CURVE  *Neutron  *         *         LBU        1     Green   LIN      Solid
CURVE  *Drho     *         *         NONE       1     Black   LIN      Solid
$ shade when Density curve is to the left of Neutron curve using YELLOW
SHADE *Density Curve *Neutron Curve Yellow
$ shade when Neutron curve is to the left of Density curve using GREEN
SHADE *Neutron Curve *Density Curve Green
$ OverView Track
TRACK    0.50    No   No     2    0.200          No      Yes       5
CURVE  *Index  0.0000     1.0000   NONE       1     Black   LIN      Solid
CURVE  *GammaRay *         *         RBU        1     Green   LIN      Solid
$ Grid and depths
GRID  *Index  100.00 10.00 2.00    FALSE      -999.000   -999.000    -1.00   DarkGray
PRINTOUT Clipboard
$ end of plot
