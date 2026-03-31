
filePath=$(dirname $0)
files=$(ls $filePath/*.dot)


for file in $files; do
    echo "dot -Tpng $file -o ${file%.*}.png"
    dot -Tpng $file -o ${file%.*}.png
done


cp ./2mm.1.kernel0.png ./2mm.1.kernel1.png ../../../../../results