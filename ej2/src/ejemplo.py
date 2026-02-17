
import pdfplumber


my_pdf = pdfplumber.open("C:/Users/loren/Desktop/FP2/ej2/data/departamentos.pdf")
im = my_pdf.pages[0].to_image(resolution=150).draw_rects(my_pdf.pages[0].extract_words())
im.show()