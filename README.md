# Structure2pdf
Creates a PDF out of a structure in find . format.

E.g., 
/a/b/c
/a/c/d

creates
a - b - c
  | c - d
  
  
Example:
./structure2pdf.py -f core-git.txt -d 4 -i product -e "components|tools|api" -o outputname
