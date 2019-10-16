# Super Smart Bros

## Build and upload library example

```bash
pio ci -c configs/platformio-example.ini --build-dir /tmp/piobuild --keep-build-dir lib/DummyLib/examples/dummyExample.cpp

# Or for the debug build:
pio ci -c configs/platformio-example-debug.ini --build-dir /tmp/piobuild --keep-build-dir lib/DummyLib/examples/dummyExample.cpp
```