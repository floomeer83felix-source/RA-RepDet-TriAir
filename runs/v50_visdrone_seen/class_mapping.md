# V50 Class Mapping

The frozen target is four-wheel road-vehicle detection: car, van, truck, and bus map to one foreground class. This matches the existing project mapping used for DroneVehicle; pedestrian, people, bicycle, tricycle, awning-tricycle, and motor remain non-target categories.

| YOLO ID | original ID | name | mapping |
|---:|---:|---|---|
| 0 | 1 | pedestrian | background/non-target |
| 1 | 2 | people | background/non-target |
| 2 | 3 | bicycle | background/non-target |
| 3 | 4 | car | vehicle |
| 4 | 5 | van | vehicle |
| 5 | 6 | truck | vehicle |
| 6 | 7 | tricycle | background/non-target |
| 7 | 8 | awning-tricycle | background/non-target |
| 8 | 9 | bus | vehicle |
| 9 | 10 | motor | background/non-target |

Original score=0/category=0 regions are restored from linked source annotations as COCO crowd/ignore regions. Truncation and occlusion flags are preserved but do not remove valid vehicle boxes.
