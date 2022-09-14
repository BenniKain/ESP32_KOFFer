def minify(f):
    myfile = open(f, "r")
    cssfile=""
    for line in myfile.readlines():
        cssfile += line
    cssfile.replace(" ","")
    cssfile.replace("\t", "")
    cssfile.replace("\n", "")
    myfile.close()
    myfile = open("src/html_css/minified.css", "w")
    myfile.write(cssfile)
    myfile.close()

minify("src/html_css/base.css")


