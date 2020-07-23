// This code was created by pygmsh vunknown.
SetFactory("OpenCASCADE");
Mesh.CharacteristicLengthMin = 0.001;
Mesh.CharacteristicLengthMax = 0.01;
vol0 = newv;
Box(vol0) = {-0.284, -0.15, -0.125, 0.568, 0.3, 0.25};
vol1 = newv;
Cylinder(vol1) = {-0.05, 0.0, 0.075, 0, 0, 0.05, 0.00025};
vol2 = newv;
Cylinder(vol2) = {0.05, 0.0, 0.075, 0, 0, 0.05, 0.00025};
bo1[] = BooleanFragments{ Volume{vol0}; Delete; } { Volume{vol1};Volume{vol2}; Delete;};