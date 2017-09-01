$ 3 tracks blank
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
$  
TRACK    2.00   Yes   No     2    0.200          No       No       5
$ make depth track
TRACK    0.50    No   No     2    0.200          No       No       5
CURVE   *Index  0.0000     1.0000   NONE       1     Black   LIN      Solid
$  
TRACK   2.00    Yes   No     4    0.200         Yes       No      5
$  
TRACK   2.00    Yes   No     4    0.200         Yes       No      5
$ OverView Track
TRACK    0.50    No   No     2    0.200          No      Yes       5
CURVE  *Index  0.0000     1.0000   NONE       1     Black   LIN      Solid
CURVE  *GammaRay *         *         RBU        1     Green   LIN      Solid
$ Grid and depths
GRID  *Index  100.00 10.00 2.00    FALSE      -999.000   -999.000    -1.00   DarkGray
PRINTOUT Clipboard
$ end of plot
