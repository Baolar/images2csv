from PIL import Image
import os
import sys
import pyocr
import random
import csv
from tqdm import tqdm
from time import sleep
from pdf2image import convert_from_path
import codecs
# a image translate to string

def image2str(image, tool):
    return tool.image_to_string(image)

def pdf2images(pdf):
    pdf_name = pdf.split('.')[0]
   
    folder = os.path.exists(pdf_name)
    
    if not folder:                   
        os.makedirs(pdf_name)           

    pages = convert_from_path(pdf)

    cnt = 1
    for page in pages:
        page.save(pdf_name + '/' + str(cnt) + '.jpg', 'JPEG')
        cnt += 1

def pdf2str(pdf, tool):
    pdf_name = pdf.split('.')[0]
    pages = convert_from_path(pdf)
    tran_str = ""
    for i in tqdm(range(1, len(pages) + 1)):
        tran_str += image2str(pages[i-1], tool)
        
    return tran_str

# filepath is a dir contained several pdfs doc.
# the function will translate them to txt and put them into filepath_output folder
    
def pdfs2txt(inputfolder):
    pdfs = os.listdir(inputfolder)
    
    for pdf in pdfs:
        print(pdf)
    print('INPUT PATH: ' + os.path.abspath(inputfolder) + '    Found ' + str(len(pdfs)) + ' File(s)!')

    outputfolder = inputfolder + "_out"
    outputfolder_exist = os.path.exists(outputfolder)

    if not outputfolder_exist:                   
        os.makedirs(outputfolder)      

    tool = pyocr.get_available_tools()[0]
    tot = len(pdfs)
    for i in range(tot):
        pdfpath = inputfolder + '/' + pdfs[i]
        print('[' + str(i+1) + '/' + str(tot) + '] ' + str(pdfs[i]))
        tran_str = pdf2str(pdfpath, tool)
        tran_str = str_modify(tran_str) # 处理空格和换行

        with open(outputfolder + '/' + pdfs[i].split('.')[0] + '.txt',"w") as f:
            f.write(tran_str) 
    
    print('OUPUT PATH: ' + os.path.abspath(outputfolder) + ' ' + str(len(pdfs)) + ' File(s)')

def str_modify(s):
    if len(s) < 3:
        return s
    
    ans = str(s[:2])

    for i in range(2, len(s)):
        if (s[i] == '\n' or s[i] == ' ') and (s[i-1] == '\n' or s[i-1] == ' ') and (s[i-2] == '\n' or s[i-2] == ' '):
            continue

        ans += s[i]
    
    return ans

def str_modify2(s):
    if len(s) < 3:
        return s
    
    ans = str(s[:1])

    for i in range(1, len(s)):
        # print(str(ord(s[i])) +  "   " + s[i])
        if s[i] == ' ' and s[i-1] == ' ':
            continue
        
        if s[i] == '\n':
            ans += ' '
        else:
            ans += s[i]
    
    return ans

def main(inputfolder):
    outputfile = inputfolder + "_out.csv"
    tool = pyocr.get_available_tools()[0]
    image_names = os.listdir(inputfolder)
    tot = len(image_names)

    for i in range(len(image_names)):
        os.rename(inputfolder + "/" + image_names[i], inputfolder + "/" + str(i + 1) + "_" + str(int(random.random() * 1000000)) + "_tmp." + image_names[i].split('.')[-1])

    image_names = os.listdir(inputfolder)
    tot = len(image_names)

    print(tot)

    with codecs.open(outputfile, 'w', 'utf_8_sig') as csvfile:
        writer = csv.writer(csvfile)

        for i in tqdm(range(1, tot + 1)):
            imagepath = inputfolder + "/" + image_names[i-1] 
            txt = str_modify2(image2str(Image.open(imagepath), tool))
            writer.writerow([str(i), txt, txt])

            os.rename(imagepath, inputfolder + "/" + str(i) + "." + image_names[i-1].split(".")[-1])
    
if __name__ == "__main__":
    path = sys.argv[1]
    main(path)
