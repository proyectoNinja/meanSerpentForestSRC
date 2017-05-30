import sys
from fpdf import FPDF
import matplotlib.pyplot as plt

def getPlotAndSave(clusters):
    n_clusters=len(clusters)
    a=0
    for i in range(n_clusters):
        for group in clusters[i]:
            if (n_clusters<4):
                plt.subplot(1,3,i+1)
            elif (n_clusters<5):
                plt.subplot(2,2,i+1)
            elif (n_clusters<7):
                plt.subplot(2,3,i+1)
            elif(n_clusters<9):
                plt.subplot(2,4,i+1)
            elif(n_clusters==9):
                plt.subplot(3,3,i+1)
            elif(n_clusters==10):
                plt.subplot(2,5,i+1)
            elif(n_clusters<=16):
                plt.subplot(4,4,i+1)
            elif(n_clusters<=25):
                plt.subplot(5,5,i+1)
            elif(n_clusters<=36):
                plt.subplot(6,6,i+1)
            plt.plot(group)
            plt.axis([0,15,40,350])
    return plt.figure()
    plt.savefig(os.path.join(sys.argv[1]+'_graficas_'+sys.argv[2]+'_'+str(n_clusters)+'.png'))
    plt.show()
    return plt

def genParam(clusters,metodo):
    n=0
    tra=0
    for tramos in clusters:
        n+=1
        for tramo in tramos:
            tra+=1
    param=""
    param+="En este caso se ha optado por la tecnica de clustering conocida como "
    param+=metodo
    param+=", tras haber identificado hasta "
    param+=str(tra)
    param+=" tramos validos de cuatro horas, los hemos asociado en "
    param+=str(n)
    param+=" grupos, llamados clusters, distintos."
    return param


def toPDF(clusters,codes,metodo):
    pdf=FPDF('P','mm','A4')
    pdf.add_page()
    texto="A continuacion le mostraremos el analis que hemos realizado con los datos que nos ha entregado.\n"
    texto=texto+"Los resultados de estos analisis son el producto de la aplicacion de tecnicas de aprendizaje automatico. "
    texto+="Bajo ninguna circunstancia deberan sustituir a los consejo de su medico. "
    texto+="Ni la UCM, ni el grupo de investigacion se haran responsables del uso indevido que pueda hacerse con estos datos\n"
    titulo="Informe de los niveles de glucemia en tramos de cuatro horas"
    w = len(titulo) + 6
    pdf.set_x((210 - w) / 2)
    pdf.set_font('Times','B',16)
    pdf.cell(w,9,titulo,0,1,'C',0)
    pdf.ln()
    pdf.set_font('Times','',12)
    with open('Introduccion', 'rb') as fh:
            intro = fh.read().decode('utf-8')
    pdf.multi_cell(0,5,intro)
    pdf.ln()
    param=genParam(clusters,metodo)
    pdf.multi_cell(0,5,param)
    pdf.image(getPlotAndSave(clusters))
    pdf.output('../tuto.pdf','F')
