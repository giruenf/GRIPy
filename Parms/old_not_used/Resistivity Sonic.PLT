$ Resistivity sonic plot file
$
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
CURVE  *GammaRay *         *         RBU        1     Green   LIN      Solid
CURVE  *Caliper  *         *         RBU        1     Blue    LIN      Solid
CURVE  *SP       *         *         RBU        1     Black   LIN      Solid
$ make depth track
TRACK    0.50    No   No     2    0.200          No       No       5
CURVE   *Index  0.0000     1.0000   NONE       1     Black   LIN      Solid
$ resistivity track
TRACK    3.50   Yes   Yes    4    0.200          Yes      No       5
CURVE  *DeepRes  0.2000    2000.0000 RBU        1     Red     LOG      Solid
CURVE  *MedRes   0.2000    2000.0000 RBU        1     Fuchsia LOG      Solid
CURVE  *MicroRes 0.2000    2000.0000 RBU        1     Purple  LOG      Solid
$ sonic track
TRACK    2.50   Yes   No     4    0.200          Yes      No       5
CURVE  *Sonic    *         *         LBU        1     Blue    LIN      Solid
$ OverView Track
TRACK    0.50   No    No     2    0.200          No       Yes      5
CURVE  *Index  0.0000     1.0000   NONE       1     Black   LIN      Solid
CURVE  *GammaRay *         *         RBU        1     Green   LIN      Solid
$ Grid and depths
GRID  *Index  100.00 10.00 2.00    FALSE      -999.000   -999.000    -1.00   DarkGray
PRINTOUT Clipboard
$ end of plot
