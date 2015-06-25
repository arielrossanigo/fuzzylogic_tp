# -*- coding: utf-8 *-*
from Tkinter import *
import threading
from simulacion_pendulo import Pendulum
import math
import fuzzy


class PerpetualTimer(threading._Timer):

    def __init__(self, interval, function, name=None, daemon=False,
                    args=(), kwargs={}):
        super(PerpetualTimer, self).__init__(interval, function, args, kwargs)
        self.setName(name)
        self.setDaemon(daemon)

    def run(self):
        while True:
            self.finished.wait(self.interval)
            if self.finished.isSet():
                return
            self.function(*self.args, **self.kwargs)

    def stop(self, timeout=None):
        self.cancel()
        self.join(timeout)

    def callback(egg):
        egg.cook()


class ControladorPendulo(fuzzy.FuzzyAlgorithm):

    def set_program(self):
        return '''
universe = -300, 300, 0.5
implication_algotithm = MAMDANI

#phi Es el angulo del pendulo respecto del eje horizontal expresado en grados
phi.up_more_right = (0, 0)(30,1)(60, 0)
phi.up_right = (30, 0)(70, 1)(90, 0)
phi.up = (85, 0) (90, 1) (95, 0)
phi.up_left = (90, 0)(110, 1)(150, 0)
phi.up_more_left = (120, 0)(150, 1)(180, 0)

#dphi_dt es la velocidad angular del pendulo expresada en grados por segundo
dphi_dt.r_slow = (-300,0)(-150,1)(0, 0)
dphi_dt.stop = (-150,0)(0, 1)(150,0)
dphi_dt.l_slow = (0,0)(150,1)(300,0)

#a es la aceleracion que se debe aplicar al carro expresada en m/s2
a.left_fast = (-30, 0)(-20,1)(-10,0)
a.left_slow = (-10,0)(-5, 1)(0,0)
a.stop = (-5,0)(0, 1)(5,0)
a.right_slow = (0,0)(5,1)(10,0)
a.right_fast = (10,0)(20,1)(30,0)

#Si esta arriba frenado o llegando arriba despacio, freno
if  (phi is up AND dphi_dt is stop) OR
    (phi is up_right AND dphi_dt is l_slow) OR
    (phi is up_left AND dphi_dt is r_slow)
                                                then a is stop
ELSE

# si esta muy caido a la derecha hay que acelerar rapido
if phi is up_more_right then a is right_fast
ELSE
if phi is up_more_left then a is left_fast

else

#si esta poco caido hay que acelerar despacio
if phi is up_left AND dphi_dt is l_slow then a is left_slow
else
if phi is up_right AND dphi_dt is r_slow then a is right_slow

'''


class MuestraPendulo:

    def __init__(self, master):
        self.pendulo = Pendulum()
        self.pendulo.Phi = math.radians(45)
        self.controlador = ControladorPendulo()

        w = Canvas(master, width=800, height=400)
        self.w = w
        w.pack()

        #creamos el piso
        w.create_polygon(0, 270, 800, 270, 800, 300, 0, 300, fill='black')

        self.carga = w.create_oval(0, 0, 10, 10, fill='red')
        self.pivote = w.create_line(0, 0, 400, 300)  # x0, y0, x1, y1
        self.carro = w.create_polygon(0, 0, 70, 0, 70, 30, 0, 30, fill='blue')

        self.actualizar_puntos()
        self.posicionar_objetos()

        frame = Frame(master)
        frame.pack()

        self.iniciar = Button(frame, text="Iniciar", command=self.iniciar)
        self.iniciar.pack(side=LEFT)
        self.detener = Button(frame, text="Detener", command=self.detener)
        self.detener.pack(side=LEFT)
        self.paso = Button(frame, text="Paso", command=self.hacer_paso)
        self.paso.pack(side=LEFT)

        self.lx = StringVar()
        Label(frame, text="X: ").pack(side=LEFT)
        Label(frame, textvariable=self.lx).pack(side=LEFT)

        self.ldx = StringVar()
        Label(frame, text="dX: ").pack(side=LEFT)
        Label(frame, textvariable=self.ldx).pack(side=LEFT)

        self.lphi = StringVar()
        Label(frame, text="Phi: ").pack(side=LEFT)
        Label(frame, textvariable=self.lphi).pack(side=LEFT)

        self.ldphi = StringVar()
        Label(frame, text="dPhi: ").pack(side=LEFT)
        Label(frame, textvariable=self.ldphi).pack(side=LEFT)

        self.la = StringVar()
        Label(frame, text="Aceleracion: ").pack(side=LEFT)
        Label(frame, textvariable=self.la).pack(side=LEFT)

    def posicionar_objetos(self):
        cax, cay = self.pto_carga
        cox, coy = self.pto_carro
        self.w.coords(self.pivote, cax, cay, cox, coy - 15)
        self.w.coords(self.carga, cax - 15, cay - 15, cax + 15, cay + 15)
        self.w.coords(self.carro, cox - 35, coy, cox + 35, coy,
                                  cox + 35, coy - 30, cox - 35, coy - 30)

    def _coord(self, x, y):
        return (x + 400, 270 - y)

    def actualizar_puntos(self):
        escala = 100
        cox = self.pendulo.X * escala
        coy = 0

        phi = self.pendulo.Phi
        l = self.pendulo.l * escala

        cax = cox + l * math.cos(phi)
        cay = l * math.sin(phi)

        self.pto_carro = self._coord(cox, coy)
        self.pto_carga = self._coord(cax, cay)

    def hacer_paso(self):
        aceleracion = self.controlador.compute(
                               phi=int(math.degrees(self.pendulo.Phi)),
                               dphi_dt=int(math.degrees(self.pendulo.dPhi_dT)),
                               dx_dt=int(self.pendulo.dX_dT),
                               x=int(self.pendulo.X),
                               a=int(self.pendulo.a))
        self.lx.set("%6.2f" % self.pendulo.X)
        self.ldx.set("%6.2f" % self.pendulo.dX_dT)
        self.lphi.set("%6.2f" % math.degrees(self.pendulo.Phi))
        self.ldphi.set("%6.2f" % math.degrees(self.pendulo.dPhi_dT))
        self.la.set("%6.2f" % aceleracion)
        self.pendulo.a = aceleracion
        self.pendulo.doStep(0.01)
        self.actualizar_puntos()
        self.posicionar_objetos()

    def iniciar(self):
        print 'inicia'
        self.timer = PerpetualTimer(0.01, self.hacer_paso)
        self.timer.start()

    def detener(self):
        print 'detiene'
        self.timer.cancel()


if __name__ == '__main__':
    root = Tk()
    app = MuestraPendulo(root)
#    app.controlador.show_vars()
##    fuzzy.show_sets(app.controlador.vars['phi'].sets['zo'])
    root.mainloop()

