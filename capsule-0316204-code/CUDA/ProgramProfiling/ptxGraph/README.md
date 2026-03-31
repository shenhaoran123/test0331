# Build ptxGraph

## Extenal

cmake 3.0.0+

g++ with c++11

graphviz package

## Command

Build with `./build.sh`

Use `./ptxGraph -h` or `./ptxGraph --help` for help information.

```
Generate Dynamic/Static Ptx Graph
Usage:
  ptxGraph [OPTION...]

      --pf arg   Ptx file path; string (required)
      --dynamic  Generate Dynamic Ptx Graph
      --static   Generate Static Ptx Graph
      --pr       Pr SDC Flag
      --df arg   Read Dynamic Ptx_File from File
  -h, --help     help
```

Use `--dynamic` or `--static` to select ptx graph type.

Use `--pf fileName` to choose ptx file.

Use `--pr` to announce if there is prSDC at the end of input line.

Use `--df dynamicFileList` to read dynamic ptx fileName from a file.

Use `--dw dynamicWeightFile` to read dynamic ptx file's weight from a dile.

For example: `./ptxGraph --pf ./examples/2Dconv/id_1-ptx.txt --pr --dynamic` for dynamic ptxGraph with prSDC.

Therefore `./ptxGraph --pf ./examples/static/kmeans.1.sm_35.ptx --static --df ./examples/static/kmeans.1.sm_35.ptx.list --dw ./examples/static/RDIStid-threadcount.txt` for static ptxGraph where *.list stored dynamic fileNames.

You can use `dot -Tpng test.dot -o test.png` to fransform the Graph. And `draw.sh` in `./dot/` can transform all dot file in the directory.
