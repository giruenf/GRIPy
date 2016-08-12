TRACK    1.25 Yes No     2    0.200 No No     5 Yes 
CURVE   *GammaRay       0.0000     150.0000   RBU  2 Green LIN Solid Yes 
CURVE         *SP    -200.0000     200.0000  WRAP  1 Black LIN Solid Yes 
SHADE *GammaRay 0. *GammaRay Curve  Yes Variable *Vcl No  No No  1. 0. 256 1 Yes  Earth.pal :>:Clay
ZONES Cutoff     0.0000     1.0000 Clear Yes 
TOPS Cutoff Purple FALSE
ORDER  GridLines Pictures Images VDL VertLines Waveform Shading Curves PointPip Tadpoles Zones Numerics DIPImage
TRACK    0.40 No No     2    0.200 No No     5 Yes 
CURVE       *Index      0.0000       1.0000  NONE  1 Black LIN Solid Yes 
CURVE        *TVD       0.0000       1.0000  NONE  1 Red LIN Solid Yes 
ORDER  GridLines Pictures Images VDL VertLines Waveform Shading Curves PointPip Tadpoles Zones Numerics DIPImage
TRACK    1.25 Yes Yes     2    0.200 Yes No     5 Yes 
CURVE    *DeepRes       0.2000      20.0000   RBU  2 Red LOG Solid Yes 
CURVE     *MedRes       0.2000      20.0000   RBU  1 Fuchsia LOG Solid Yes 
CURVE   *MicroRes       0.2000      20.0000   RBU  1 Purple LOG Solid Yes 
TOPS Cutoff Purple FALSE
ORDER  GridLines Pictures Images VDL VertLines Waveform Shading Curves PointPip Tadpoles Zones Numerics DIPImage
TRACK    0.30 No No     2    0.200 No No     5 Yes 
CURVE    *Caliper       6.0000      16.0000   RBU  1 DkGray LIN Mirror Yes 
ORDER  GridLines Pictures Images VDL VertLines Waveform Shading Curves PointPip Tadpoles Zones Numerics DIPImage
TRACK    1.25 Yes No     4    0.200 Yes No     5 Yes 
CURVE    *Density       1.9500       2.9500  WRAP  1 Red LIN Solid Yes 
CURVE    *Neutron       0.4500      -0.1500  WRAP  1 Green LIN Solid Yes 
CURVE       *Drho      -1.0000       0.2500  WRAP  1 Black LIN Solid Yes 
CURVE      *Sonic     140.0000      40.0000   LBU  2 Fuchsia LIN Solid Yes 
SHADE *Density Curve *Neutron Curve  Yes Yellow :>:Sand
SHADE *Neutron Curve *Density Curve  Yes Green :>:Shale
TOPS Cutoff Purple FALSE
ORDER  GridLines Pictures Images VDL VertLines Waveform Shading Curves PointPip Tadpoles Zones Numerics DIPImage
TRACK    1.25 Yes No     4    0.200 Yes No     5 Yes 
CURVE       *Temp     100.0000     300.0000  NONE  1 Blue LIN Solid Yes 
CURVE    *RhoMatx       2.5000       3.0000  NONE  1 Purple LIN Solid Yes 
CURVE     *CoreGD       2.5000       3.0000  NONE  1 Maroon LIN Circle Yes 
TOPS Cutoff Purple FALSE
ORDER  GridLines Pictures Images VDL VertLines Waveform Shading Curves PointPip Tadpoles Zones Numerics DIPImage
TRACK    0.30 No No     2    0.200 No No     5 Yes 
CURVE    *ResFlag       0.0000       3.0000  NONE  1 Black LIN BSolid Yes 
CURVE    *PayFlag       3.0000       0.0000  NONE  1 Red LIN BSolid Yes 
SHADE *ResFlag 0. *ResFlag Curve  Yes Black :>:Res
SHADE *PayFlag Curve *PayFlag 0.  Yes Red :>:Pay
ORDER  GridLines Pictures Images VDL VertLines Waveform Shading Curves PointPip Tadpoles Zones Numerics DIPImage
TRACK    1.25 Yes No     4    0.200 Yes No     5 Yes 
CURVE         *Sw       1.0000       0.0000  NONE  2 Green LIN Solid Yes 
SHADE *Sw 1. *Sw Curve  Yes Red :>:Hydrocarbon
TOPS Cutoff Purple FALSE
ORDER  GridLines Pictures Images VDL VertLines Waveform Shading Curves PointPip Tadpoles Zones Numerics DIPImage
TRACK    1.25 Yes No     4    0.200 Yes No     5 Yes 
CURVE       *PhiT       0.5000       0.0000  NONE  1 Navy LIN Solid Yes 
CURVE        *Phi       0.5000       0.0000  NONE  2 Blue LIN Solid Yes 
CURVE        *BVW       0.5000       0.0000  NONE  1 Red LIN Solid No 
CURVE    *CorePhi       0.5000       0.0000  NONE  1 Black LIN Circle Yes 
SHADE *Phi Curve *BVW Curve  Yes Red :>:Hydrocarbon
TOPS Cutoff Purple FALSE
ORDER  GridLines Pictures Images VDL VertLines Waveform Shading Curves PointPip Tadpoles Zones Numerics DIPImage
TRACK    1.25 Yes No     4    0.200 Yes No     5 Yes 
CURVE        *Vcl       0.0000       1.0000  NONE  1 Green LIN Cumulative Yes 
CURVE       *Vsilt      0.0000       1.0000  NONE  1 Green LIN Cumulative Yes 
CURVE        *Phi       1.0000       0.0000  NONE  1 Blue LIN Solid Yes 
SHADE  *Vcl 0.  *Vcl Curve  Yes Clay :>:Clay
SHADE  *Vcl Curve *Vsilt Curve  Yes Silt :>:Silt
SHADE  *Vsilt Curve *Phi Curve  Yes Sandstone :>:Sand
SHADE *Phi Curve *Phi 0.  Yes Blank :>:Porosity
TOPS Cutoff Purple FALSE
ORDER  GridLines Pictures Images VDL VertLines Waveform Shading Curves PointPip Tadpoles Zones Numerics DIPImage
TRACK    1.25 Yes Yes     5    0.100 Yes No     5 Yes 
CURVE   *CorePerm       0.1000   10000.0000  NONE  1 Navy LOG Circle Yes 
CURVE       *Perm       0.1000   10000.0000  NONE  1 Blue LOG Solid Yes 
TOPS Cutoff Purple FALSE
ORDER  GridLines Pictures Images VDL VertLines Waveform Shading Curves PointPip Tadpoles Zones Numerics DIPImage
TRACK    0.50 No No     2    0.200 No Yes     5 Yes 
CURVE       *Index      0.0000       1.0000  NONE  1 Black LIN Solid Yes 
CURVE   *GammaRay       0.0000     150.0000   RBU  1 Green LIN Solid Yes 
ORDER  GridLines Pictures Images VDL VertLines Waveform Shading Curves PointPip Tadpoles Zones Numerics DIPImage
GRID *Index  100.00  10.00   2.00 FALSE      -999.000   -999.000    -1.00   DarkGray
PRINTOUT Clipboard
