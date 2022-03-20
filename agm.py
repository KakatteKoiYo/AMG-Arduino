import re, os
import time
import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
from xml.etree import ElementTree

programa_version = "1.0"

AP = RATIO_SEL = HALL_SEL = LOWER_BURDEN = LO_ZIN_SKY = LO_ZIN_EARTH = EFS_G4 = EFS_G1_2 = IMEI = SIM = CSQ = "?" 
RAM = FLASH = HALL1 = HALL2 = HALL_LPF = IMEAS = ESFX = VCAP = CapCharge = TP ="?"
puerto = "?"

mensajeInicio = """Antes de presionar "Reboot" para comenzar:
-Asegúrese de que el puerto seleccionado es el correcto.
-Que el Arduino esté conectado a la unidad y ésta tenga firmware de debug.
-Que la fuente esté encendia.
-Si va a leer voltaje, AP debe estar activo para leer señales +5V y -5V.
Y muy importante: conecte correctamente el cable al conector J8 
Si está mal conectado en J8 el Arduino podría dañarse.
"""

tiempoEnvio = 0.005


window = tk.Tk()
window.title("Arduino AGM GUI Tester V1.0")
window.geometry("1100x620")
window.resizable(False, False)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def buscarActualizacion():
    try:
        ruta = "//Mxgdld0nsifsn03/gdl_te_vol_1/TE_Customers/Aclara/Aclara_RF/Aplicaciones de Pruebas/updateverify.xml"
        carpeta = "//Mxgdld0nsifsn03/gdl_te_vol_1/TE_Customers/Aclara/Aclara_RF/Aplicaciones de Pruebas"
        xmlupdate = ElementTree.parse(ruta)
        version = xmlupdate.getroot()[3][0].text.strip()
        nombreapp = xmlupdate.getroot()[3][1].text.strip()
        print(nombreapp)

        if  version != programa_version:
            
            mensaje_pregunta = messagebox.askokcancel("Actualización disponible",
            """Hay una actualización disponible en:
            """+carpeta+"""\nPuede copiar la nueva versión (V"""+version+ """) y borrar esta (V"""+programa_version+""") ¿Abrir carpeta?\n Dudas: Daniel_Romo@jabil.com""")
            if mensaje_pregunta == True:
                try:
                    carpeta = os.path.realpath(carpeta)
                    os.startfile(carpeta)
                except:
                    messagebox.showinfo(title="ERROR", message="Hubo un error al tratar de abrir la carpeta. Intente abrirla manualmente")
            
    except Exception as e:
        print(e)

def iniciar():
    global campoEstatus, campoRespuesta, comandosSimplesFrame, comandosRadioFrame, btnRadioSalir, pruebasFrame, pinesFrame, campoValores, btnRadio
    global selPuertoList, btnReboot, campoValores2, voltajesFrame, btnTestV
    global vcValue, _3v3Value, _3v3AValue, XCVRValue, _1v5Value, _5v0Value, _N5v0Value


    fuenteBtn = ("Arial", 10)

    btnPady = 5
    btnPadx = 5
    

    ####  Frame para los botones de comandos simples. ###

    comandosSimplesFrame = tk.Frame(window, bg = "azure")
    comandosSimplesFrame.pack(fill = "y", side = tk.LEFT, padx = btnPadx)

    btnAP = tk.Button(comandosSimplesFrame, text = "AP", command = lambda: commandAP(), font = fuenteBtn, width = 15)
    btnAP.pack(pady = btnPady)

    btnFPGA = tk.Button(comandosSimplesFrame, text = "Reiniciar FPGA", command = lambda: reiniciarFPGA(), font = fuenteBtn, width = 15)
    btnFPGA.pack(pady = btnPady)

    btnOn = tk.Button(comandosSimplesFrame, text = "Encender LED ", command = lambda: enviarComandoSimple("flash on"), font = fuenteBtn, width = 15)
    btnOn.pack(pady = btnPady)

    btnOff = tk.Button(comandosSimplesFrame, text = "Apagar LED", command = lambda : enviarComandoSimple("flash off"), font = fuenteBtn, width = 15)
    btnOff.pack(pady = btnPady)

    btnReboot = tk.Button(comandosSimplesFrame, text = "Reboot", command = lambda : reiniciar(), font = fuenteBtn, width = 15)
    btnReboot.pack(pady = btnPady)


    ####  Frame para los botones de radio. ###

    radioFrame = tk.Frame(window, bg = "aliceblue")
    radioFrame.pack(fill = "y", side = tk.LEFT)

    btnRadio = tk.Button(radioFrame, text = "Radio", command = lambda : radioIniciar(), font = fuenteBtn, width = 10)
    btnRadio.pack(pady = btnPady, padx = btnPadx)
    
    comandosRadioFrame = tk.Frame(radioFrame, bg = "aliceblue")
    comandosRadioFrame.pack(pady = btnPady)


    btnIMEI = tk.Button(comandosRadioFrame, text = "IMEI", command = lambda : radioComandos("AT+GSN", opcion = 1), font = fuenteBtn, width = 10, state = "disabled")
    btnIMEI.pack(side = tk.LEFT, padx = btnPadx)

    btnSIM = tk.Button(comandosRadioFrame, text = "SIM", command = lambda : radioComandos("AT+ICCID", opcion = 2), font = fuenteBtn, width = 10, state = "disabled")
    btnSIM.pack(side = tk.LEFT, padx = btnPadx)

    btnAntena = tk.Button(comandosRadioFrame, text = "Señal Ant", command = lambda : radioComandos("AT+CSQ", opcion = 3), font = fuenteBtn, width = 10, state = "disabled")
    btnAntena.pack(side = tk.LEFT, padx = btnPadx)
    print(btnAntena.cget("bg"))

    btnRadioSalir = tk.Button(radioFrame, text = "Salir de modo radio", command = lambda : salirRadio(), font = fuenteBtn, state = "disabled")
    btnRadioSalir.pack(pady = btnPady)

    ####  Frame para los botones de pruebas ###

    pruebasFrame = tk.Frame(window, bg = "azure")
    pruebasFrame.pack(fill = "y", side = tk.LEFT, padx = btnPadx)

    btnMTR = tk.Button(pruebasFrame, text = "Prueba RAM", command = lambda : enviarComandoSimple("MT RAM", 20, 1, 1), font = fuenteBtn, width = 13)
    btnMTR.pack(pady = btnPady)

    btnMTF = tk.Button(pruebasFrame, text = "Prueba FLASH", command = lambda : enviarComandoSimple("MT FLASH", 20, 1, 1), font = fuenteBtn, width = 13)
    btnMTF.pack(pady = btnPady)

    btnHall1 = tk.Button(pruebasFrame, text = "Prueba Hall1", command = lambda : hallTest(1), font = fuenteBtn, width = 13)
    btnHall1.pack(pady = btnPady)

    btnHall2 = tk.Button(pruebasFrame, text = "Prueba Hall2", command = lambda : hallTest(2), font = fuenteBtn, width = 13)
    btnHall2.pack(pady = btnPady)

    btnLPF = tk.Button(pruebasFrame, text = "Prueba Hall1 LPF", command = lambda : specialTest("IH1", 1), font = fuenteBtn, width = 13)
    btnLPF.pack(pady = btnPady)

    btnIMEAS = tk.Button(pruebasFrame, text = "Prueba IMEAS", command = lambda : specialTest("IM", 2), font = fuenteBtn, width = 13)
    btnIMEAS.pack(pady = btnPady)

    btnESFX = tk.Button(pruebasFrame, text = "Prueba ESFX", command = lambda : specialTest("EF", 3), font = fuenteBtn, width = 13)
    btnESFX.pack(pady = btnPady)

    btnVCAP = tk.Button(pruebasFrame, text = "Prueba VCAP", command = lambda : specialTest("VC", 4), font = fuenteBtn, width = 13)
    btnVCAP.pack(pady = btnPady)

    btnCC = tk.Button(pruebasFrame, text = "Prueba Carga", command = lambda : specialTest("CC", 5), font = fuenteBtn, width = 13)
    btnCC.pack(pady = btnPady)

    btnTP = tk.Button(pruebasFrame, text = "Prueba Temp", command = lambda : specialTest("TP", 6), font = fuenteBtn, width = 13)
    btnTP.pack(pady = btnPady)


    ####  Frame para los botones para habilitar/deshabilitar pines ###

    pinesFrame = tk.Frame(window, bg = "aliceblue")
    pinesFrame.pack(fill = "both", side = tk.LEFT, padx = btnPadx)


    primeraFrame = tk.Frame(pinesFrame)
    primeraFrame.pack(pady = 10)

    fila1Frame = tk.Frame(primeraFrame)
    fila1Frame.pack()

    btnRatioSel1 = tk.Button(fila1Frame, text = "RATIO_SEL high", command = lambda : cambiarEstadoNodo("P5.7 1", 0, "RATIO_SEL"), font = fuenteBtn, width = 19)
    btnRatioSel1.pack(side = tk.LEFT, padx = btnPadx)

    btnHallSel1 = tk.Button(fila1Frame, text = "HALL_SEL high", command = lambda : cambiarEstadoNodo("P2.2 1", 1, "HALL_SEL"), font =  fuenteBtn, width = 19)
    btnHallSel1.pack(side = tk.LEFT, padx = btnPadx)

    btnLB1 = tk.Button(fila1Frame, text = "LOWER_BURDEN high", command = lambda : cambiarEstadoNodo("P1.7 1", 2, "LOWER_BURDEN"), font =  fuenteBtn, width = 19)
    btnLB1.pack(side = tk.LEFT, padx = btnPadx)

    fila2Frame = tk.Frame(primeraFrame)
    fila2Frame.pack()

    btnRatioSel0 = tk.Button(fila2Frame, text = "RATIO_SEL low", command = lambda : cambiarEstadoNodo("P5.7 0", 0, "RATIO_SEL"), font = fuenteBtn, width = 19)
    btnRatioSel0.pack(side = tk.LEFT, padx = btnPadx)

    btnHallSel0 = tk.Button(fila2Frame, text = "HALL_SEL low", command = lambda : cambiarEstadoNodo("P2.2 0", 1, "HALL_SEL"), font =  fuenteBtn, width = 19)
    btnHallSel0.pack(side = tk.LEFT, padx = btnPadx)

    btnLB0 = tk.Button(fila2Frame, text = "LOWER_BURDEN low", command = lambda : cambiarEstadoNodo("P1.7 0", 2, "LOWER_BURDEN"), font =  fuenteBtn, width = 19)
    btnLB0.pack(side = tk.LEFT, padx = btnPadx)

    
    segundaFrame = tk.Frame(pinesFrame)
    segundaFrame.pack(pady = 10)

    fila3Frame = tk.Frame(segundaFrame)
    fila3Frame.pack()

    btnLZS1 = tk.Button(fila3Frame, text = "LO_ZIN_SKY high", command = lambda : cambiarEstadoNodo("P4.6 1", 3, "LO_ZIN_SKY", 1), font = fuenteBtn, width = 19)
    btnLZS1.pack(side = tk.LEFT, padx = btnPadx)

    btnLZE1 = tk.Button(fila3Frame, text = "LO_ZIN_EARTH high", command = lambda : cambiarEstadoNodo("P4.7 1", 4, "LO_ZIN_EARTH", 1), font =  fuenteBtn, width = 19)
    btnLZE1.pack(side = tk.LEFT, padx = btnPadx)

    btnEFS121 = tk.Button(fila3Frame, text = "EFS_G1/2 high", command = lambda : cambiarEstadoNodo("P4.4 1", 5, "EFS_G1/2", 1), font =  fuenteBtn, width = 19)
    btnEFS121.pack(side = tk.LEFT, padx = btnPadx)

    fila4Frame = tk.Frame(segundaFrame)
    fila4Frame.pack()

    btnLZS0 = tk.Button(fila4Frame, text = "LO_ZIN_SKY low", command = lambda : cambiarEstadoNodo("P4.6 0", 3, "LO_ZIN_SKY", 1), font = fuenteBtn, width = 19)
    btnLZS0.pack(side = tk.LEFT, padx = btnPadx)

    btnLZE0 = tk.Button(fila4Frame, text = "LO_ZIN_EARTH low", command = lambda : cambiarEstadoNodo("P4.7 0", 4, "LO_ZIN_EARTH", 1), font =  fuenteBtn, width = 19)
    btnLZE0.pack(side = tk.LEFT, padx = btnPadx)

    btnEFS120 = tk.Button(fila4Frame, text = "EFS_G1/2 low", command = lambda : cambiarEstadoNodo("P4.4 0", 5, "EFS_G1/2", 1), font =  fuenteBtn, width = 19)
    btnEFS120.pack(side = tk.LEFT, padx = btnPadx)
    
    terceraFrame = tk.Frame(pinesFrame)
    terceraFrame.place(y = 155, x=0)
    
    fila5Frame = tk.Frame(terceraFrame)
    fila5Frame.pack()

    btnEFSG41 = tk.Button(fila5Frame, text = "EFS_G4 high", command = lambda : cambiarEstadoNodo("P4.5 1", 6, "EFS_G4", 1), font = fuenteBtn, width = 19)
    btnEFSG41.pack(side = tk.LEFT, padx = btnPadx)


    fila6Frame = tk.Frame(terceraFrame)
    fila6Frame.pack()

    btnEFSG40 = tk.Button(fila6Frame, text = "EFS_G4 low", command = lambda : cambiarEstadoNodo("P4.5 0", 6, "EFS_G4", 1), font = fuenteBtn, width = 19)
    btnEFSG40.pack(side = tk.LEFT, padx = btnPadx)


    respuestaFrame = tk.Frame(window, bg = "azure")
    respuestaFrame.place(x = 0, y = 380)

 
    labelRespuesta = tk.Label(respuestaFrame, text = "Respuesta", font = ("Arial", 15), bg = "azure")
    labelRespuesta.pack()
    campoEstatus = tk.Text(respuestaFrame, width = 57, height = 1, font = ("Arial", 17))
    campoEstatus.pack()
    campoRespuesta = tk.Text(respuestaFrame, width = 67, height = 7, font = ("Arial", 15))
    campoRespuesta.pack()
    campoRespuesta.insert(tk.INSERT, mensajeInicio)


    campoValores = tk.Text(window, width = 24, height = 28, font = ("Arial", 10))
    campoValores.place(x = 750, y = 155)

    campoValores2 = tk.Text(window, width = 24, height = 28, font = ("Arial", 10))
    campoValores2.place(x = 920, y = 155)

    puertoSelFrame = tk.Frame(window)
    puertoSelFrame.place(x = 140, y = 200)

    labelPuerto = tk.Label(puertoSelFrame, text = "--Seleccione un puerto--")
    labelPuerto.pack()

    selPuertoList = ttk.Combobox(puertoSelFrame ,width = 40, state = "readonly")
    selPuertoList.pack()
    selPuertoList.bind("<<ComboboxSelected>>", seleccionPuerto)
    btnActualizar = tk.Button(puertoSelFrame, text = "Actualizar lista", command = listaPuertos)
    btnActualizar.pack(fill = "both")

    voltajesFrame = tk.Frame(window)
    voltajesFrame.place(x = 570, y = 250)

    # btnConnect = tk.Button(voltajesFrame, text = "Conectar")
    # btnConnect.grid(column = 0, row = 0)

    btnTestV = tk.Button(window, text = "Prueba voltajes", width = 20, command = lambda : pruebaVoltajes(), state = "disabled")
    btnTestV.place(x = 570, y = 220)
    vcLabel = tk.Label(voltajesFrame, text = "VCAP: ")
    vcLabel.grid(column = 0, row = 1)
    vcValue = tk.Text(voltajesFrame, height = 1, width = 8, state = "disabled")
    vcValue.grid(column = 1, row = 1)
    vcStatus = tk.Text(voltajesFrame, height = 1, width = 1, state = "disabled")
    vcStatus.grid(column = 2, row = 1)
    _3v3Label = tk.Label(voltajesFrame, text = "+3.3V: ")
    _3v3Label.grid(column = 0, row = 2)
    _3v3Value = tk.Text(voltajesFrame, height = 1, width = 8, state = "disabled")
    _3v3Value.grid(column = 1, row = 2)
    _3v3Status = tk.Text(voltajesFrame, height = 1, width = 1, state = "disabled")
    _3v3Status.grid(column = 2, row = 2)
    _3v3ALabel = tk.Label(voltajesFrame, text = "+3.3VA: ")
    _3v3ALabel.grid(column = 0, row = 3)
    _3v3AValue = tk.Text(voltajesFrame, height = 1, width = 8, state = "disabled")
    _3v3AValue.grid(column = 1, row = 3)
    _3v3AStatus = tk.Text(voltajesFrame, height = 1, width = 1, state = "disabled")
    _3v3AStatus.grid(column = 2, row = 3)
    XCVRLabel = tk.Label(voltajesFrame, text = "+3.3V_XCVR: ")
    XCVRLabel.grid(column = 0, row = 4)
    XCVRValue = tk.Text(voltajesFrame, height = 1, width = 8, state = "disabled")
    XCVRValue.grid(column = 1, row = 4)
    XCVRStatus = tk.Text(voltajesFrame, height = 1, width = 1, state = "disabled")
    XCVRStatus.grid(column = 2, row = 4)
    _1v5Label = tk.Label(voltajesFrame, text = "+1.5V: ")
    _1v5Label.grid(column = 0, row = 5)
    _1v5Value = tk.Text(voltajesFrame, height = 1, width = 8, state = "disabled")
    _1v5Value.grid(column = 1, row = 5)
    _1v5Status = tk.Text(voltajesFrame, height = 1, width = 1, state = "disabled")
    _1v5Status.grid(column = 2, row = 5)
    _5v0Label = tk.Label(voltajesFrame, text = "+5.0V: ")
    _5v0Label.grid(column = 0, row = 6)
    _5v0Value = tk.Text(voltajesFrame, height = 1, width = 8, state = "disabled")
    _5v0Value.grid(column = 1, row = 6)
    _5v0Status = tk.Text(voltajesFrame, height = 1, width = 1, state = "disabled")
    _5v0Status.grid(column = 2, row = 6)
    _N5v0Label = tk.Label(voltajesFrame, text = "-5.0V: ")
    _N5v0Label.grid(column = 0, row = 7)
    _N5v0Value = tk.Text(voltajesFrame, height = 1, width = 8, state = "disabled")
    _N5v0Value.grid(column = 1, row = 7)
    _N5v0Status = tk.Text(voltajesFrame, height = 1, width = 1, state = "disabled")
    _N5v0Status.grid(column = 2, row = 7)
    
    


    desactivarBotones()
    
def resetVoltageInput():
    for i in voltajesFrame.winfo_children():
        try:
            i.config(state = "normal")
            i.delete('1.0', 'end')
            i.config(bg ="white")
            i.config(state = "disabled")
        except Exception as e:
            print(e)
            
def pruebaVoltajes():

    try: 

        campoRespuesta.delete('1.0', 'end')
        campoEstatus.delete('1.0', 'end')
        campoEstatus.insert(tk.INSERT, "Leyendo voltajes...")
        window.update()
        resetVoltageInput()
        serialPort.timeout = 2
        serialPort.flushInput()


        serialPort.write("voltajes".encode())
        respuesta = serialPort.readline()
        print(respuesta)
        respuestaArray = respuesta.decode().split("/")

        
        valorFloat = 0.0047 * int(respuestaArray[0])
        valorStr = str(valorFloat)[:6]
        if valorFloat < 4.2:
            voltajesFrame.winfo_children()[2].config(bg = "red")
        else:
            voltajesFrame.winfo_children()[2].config(bg = "green")

        vcValue.config(state = "normal")
        vcValue.insert(tk.INSERT, valorStr)
        vcValue.config(state = "disabled")
        

        
        valorFloat = (0.0047 * int(respuestaArray[1])) - 0.08
        valorStr = str(valorFloat)[:6]
        if valorFloat < 3.2:
            voltajesFrame.winfo_children()[5].config(bg = "red")
        else:
            voltajesFrame.winfo_children()[5].config(bg = "green")
        _3v3Value.config(state = "normal")
        _3v3Value.insert(tk.INSERT, valorStr)
        _3v3Value.config(state = "disabled")
        

        
        valorFloat = (0.0047 * int(respuestaArray[2])) - 0.08
        valorStr = str(valorFloat)[:6]
        if valorFloat < 3.2:
            voltajesFrame.winfo_children()[8].config(bg = "red")
        else:
            voltajesFrame.winfo_children()[8].config(bg = "green")
        _3v3AValue.config(state = "normal")
        _3v3AValue.insert(tk.INSERT, valorStr)
        _3v3AValue.config(state = "disabled")
        

        
        valorFloat = (0.0047 * int(respuestaArray[3])) - 0.08
        valorStr = str(valorFloat)[:6]
        if valorFloat < 3.2:
            voltajesFrame.winfo_children()[11].config(bg = "red")
        else:
            voltajesFrame.winfo_children()[11].config(bg = "green")
        XCVRValue.config(state = "normal")
        XCVRValue.insert(tk.INSERT, valorStr)
        XCVRValue.config(state = "disabled")
        

        
        valorFloat = 0.0047 * int(respuestaArray[4]) - 0.03
        valorStr = str(valorFloat)[:6]
        if valorFloat < 1.2:
            voltajesFrame.winfo_children()[14].config(bg = "red")
        else:
            voltajesFrame.winfo_children()[14].config(bg = "green")
        _1v5Value.config(state = "normal")
        _1v5Value.insert(tk.INSERT, valorStr)
        _1v5Value.config(state = "disabled")
        

        
        valorFloat = 0.0047 * int(respuestaArray[5])
        valorStr = str(valorFloat)[:6]
        if valorFloat < 4.2:
            voltajesFrame.winfo_children()[17].config(bg = "red")
        else:
            voltajesFrame.winfo_children()[17].config(bg = "green")
        _5v0Value.config(state = "normal")
        _5v0Value.insert(tk.INSERT, valorStr)
        _5v0Value.config(state = "disabled")
        


        
        valorFloat = ((0.0047 * int(respuestaArray[6])) * 2) - 4.899
        valorStr = str(valorFloat)[:6]
        if valorFloat > -4.2:
            voltajesFrame.winfo_children()[20].config(bg = "red")
        else:
            voltajesFrame.winfo_children()[20].config(bg = "green")
        _N5v0Value.config(state = "normal")
        _N5v0Value.insert(tk.INSERT, valorStr)
        _N5v0Value.config(state = "disabled")
        
        campoRespuesta.delete('1.0', 'end')
        campoEstatus.delete('1.0', 'end')
    except:
        messagebox.showinfo(title="ERROR", message= "Ocurrió un error al tratar de leer los voltajes")
        campoRespuesta.delete('1.0', 'end')
        campoEstatus.delete('1.0', 'end')
        resetVoltageInput()

def specialTest(comando, pruebanum):
    global HALL_LPF, IMEAS, ESFX, VCAP, CapCharge, TP

    serialPort.timeout = 8

    campoRespuesta.delete('1.0', 'end')
    campoEstatus.delete('1.0', 'end')
    campoEstatus.insert(tk.INSERT, "Espere...")
    window.update()

    campoRespuesta.configure(state = "disabled")
    campoEstatus.configure(state = "disabled")

    if AP == "False":
        commandAP()

    campoRespuesta.configure(state = "normal")
    campoEstatus.configure(state = "normal")

    comando += "\n"
    

    # for i in range(len(comando)):
    #     time.sleep(tiempoEnvio)
    #     serialPort.write(comando[i].encode())

    # time.sleep(tiempoEnvio)
    serialPort.write(comando.encode())

    respuestaBytes = serialPort.read_until(expected="mvm>".encode())
    print(respuestaBytes)
    valorRespuesta = respuestaBytes.decode("unicode_escape").split("\r\n")[1]
    
    campoRespuesta.delete('1.0', 'end')
    campoEstatus.delete('1.0', 'end')
    valorNum = valorRespuesta.split("=")[1]
    if pruebanum == 1:
        HALL_LPF = valorNum
        if int(valorNum) < 2000 or int(valorNum) > 2100:
            campoEstatus.insert(tk.INSERT, "(FAIL) El valor está fuera del rango establecido ")
        else:  
            campoEstatus.insert(tk.INSERT, "(PASS) Valor dentro del rango aceptable")

    if pruebanum == 2:
        IMEAS = valorNum
        if int(valorNum) < 2000 or int(valorNum) > 2100:
            campoEstatus.insert(tk.INSERT, "(FAIL) El valor está fuera del rango establecido ")
        else:  
            campoEstatus.insert(tk.INSERT, "(PASS) Valor dentro del rango aceptable")
    if pruebanum == 3:
        ESFX = valorNum
        if int(valorNum) < 2000 or int(valorNum) > 2500:
            campoEstatus.insert(tk.INSERT, "(FAIL) El valor está fuera del rango establecido (2000< x < 2500)")
        else:  
            campoEstatus.insert(tk.INSERT, "(PASS) Valor dentro del rango aceptable")

    if pruebanum == 4:
        voltround = str((int(valorNum)*2)/1000)[0:3] + " V"
        voltaje = str((int(valorNum)*2)/1000) + " Volts\n"
        VCAP = valorNum + " / " + voltround
        
        campoRespuesta.insert(tk.INSERT, voltaje )
    if pruebanum == 5:
        CapCharge = valorNum
    
    if pruebanum == 6:
        temperatura = str(((int(valorNum)-372) - 424) / 6.25)
        if (((int(valorNum)-372) - 424) / 6.25) > 35 or (((int(valorNum)-372) - 424) / 6.25) < 10:
            campoEstatus.insert(tk.INSERT, "(FAIL) El valor está fuera del rango establecido")
        else:  
            campoEstatus.insert(tk.INSERT, "(PASS) Valor dentro del rango aceptable")

        TP = valorNum + " / " + temperatura[0:2] +"°C"
        campoRespuesta.insert(tk.INSERT,"Temperatura: " + temperatura + "°C\n" )



    campoRespuesta.insert(tk.INSERT, valorRespuesta)
    
    asignarValores()
   
def hallTest(opcion):
    global HALL1, HALL2
    serialPort.flushInput()
    serialPort.timeout = 10
    campoRespuesta.delete('1.0', 'end')
    campoEstatus.delete('1.0', 'end')
    campoEstatus.insert(tk.INSERT, "Espere...")
    window.update()
    
    campoRespuesta.configure(state = "disabled")
    campoEstatus.configure(state = "disabled")
    if AP == "False":
        commandAP()
    if HALL_SEL == "False" and opcion == 2:
        cambiarEstadoNodo("P2.2 1", 1, "HALL_SEL")
    if HALL_SEL == "True" and opcion == 1:
        cambiarEstadoNodo("P2.2 0", 1, "HALL_SEL")

    campoRespuesta.configure(state = "normal")
    campoEstatus.configure(state = "normal")


    # for i in range(len("ihall")):
    #     time.sleep(tiempoEnvio)
    #     serialPort.write("ihall"[i].encode())

    #time.sleep(tiempoEnvio)
    serialPort.write("ihall\n".encode())

    respuestaBytes = serialPort.read_until(expected="mvm>".encode())
    print(respuestaBytes)
    valorRespuesta = respuestaBytes.decode('unicode_escape').split("\r\n")[1]
    valorNum = valorRespuesta.split("=")[1]
    campoRespuesta.delete('1.0', 'end')
    campoEstatus.delete('1.0', 'end')
    if int(valorNum) < 2000 or int(valorNum) > 2200:
        campoEstatus.insert(tk.INSERT, "(FAIL) Parece haber un problema con los valores")
    else:
        campoEstatus.insert(tk.INSERT, "(PASS) Valor dentro del rango aceptable")

    campoRespuesta.insert(tk.INSERT, valorRespuesta)

    if opcion == 1:
        HALL1 = valorNum
    if opcion == 2:
        HALL2 = valorNum
    asignarValores()

def commandAP():
    global AP

    campoRespuesta.delete('1.0', 'end')
    campoEstatus.delete('1.0', 'end')
    campoEstatus.insert(tk.INSERT, "Espere...")
    window.update()
    serialPort.flushInput()
    # comando = "AP"

    # for i in range(len(comando)):
    #     time.sleep(tiempoEnvio)
    #     serialPort.write(comando[i].encode())
    # #serialPort.write("AP".encode())
    # time.sleep(tiempoEnvio)
    # serialPort.write("\n".encode())
    serialPort.write("AP\n".encode())

    respuestaBytes = serialPort.read_until(expected="mvm>".encode())
    print(respuestaBytes)
    valorRespuesta = respuestaBytes.decode('unicode_escape').split("\r\n")[1]

    campoRespuesta.delete('1.0', 'end')
    campoEstatus.delete('1.0', 'end')
    campoRespuesta.insert(tk.INSERT, valorRespuesta)
    AP = valorRespuesta.split("=")[1].strip().lower().capitalize()
    asignarValores()
    
    time.sleep(2)

def cambiarEstadoNodo(comando, nodo, nombre, needAP = 0):
    global RATIO_SEL , HALL_SEL , LOWER_BURDEN , LO_ZIN_SKY , LO_ZIN_EARTH , EFS_G4 , EFS_G1_2

    serialPort.timeout = 7
    serialPort.flushInput()
    campoRespuesta.delete('1.0', 'end')
    campoEstatus.delete('1.0', 'end')
    campoEstatus.insert(tk.INSERT, "Espere...")
    window.update()

    setV = "S "
    readV = "R "
    comandoSet = setV + comando + "\n"
    comandoRead = readV + comando + "\n"

    # for i in range(len(comandoSet)):
    #     time.sleep(tiempoEnvio)
    #     serialPort.write(comandoSet[i].encode())

    # time.sleep(tiempoEnvio)
    # serialPort.write("\n".encode())
    serialPort.write(comandoSet.encode())

    primerRespuesta = serialPort.read_until(expected="mvm>".encode())
 
    if re.search("mvm>", str(primerRespuesta)):
        # for i in range(len(comandoRead)):
        #     time.sleep(tiempoEnvio)
        #     serialPort.write(comandoRead[i].encode())

        # time.sleep(tiempoEnvio)
        # serialPort.write("\n".encode())
        serialPort.write(comandoRead.encode())
        respuestaBytes = serialPort.read_until(expected="mvm>".encode())
        valorRespuesta = respuestaBytes.decode('unicode_escape').split("\r\n")[1]
        print(valorRespuesta)
        boolean = int(valorRespuesta.split(":")[1].strip())
        
        if boolean == 1:
            if nodo == 0:
                RATIO_SEL = "True"
            if nodo == 1:
                HALL_SEL = "True"
            if nodo == 2:
                LOWER_BURDEN = "True"
            if nodo == 3:
                LO_ZIN_SKY = "True"
            if nodo == 4:
                LO_ZIN_EARTH = "True"
            if nodo == 5:
                EFS_G1_2 = "True"
            if nodo == 6:
                EFS_G4 = "True"
        else:
            if nodo == 0:
                RATIO_SEL = "False"
            if nodo == 1:
                HALL_SEL = "False"
            if nodo == 2:
                LOWER_BURDEN = "False"
            if nodo == 3:
                LO_ZIN_SKY = "False"
            if nodo == 4:
                LO_ZIN_EARTH = "False"
            if nodo == 5:
                EFS_G1_2 = "False"
            if nodo == 6:
                EFS_G4 = "False"
        
        campoRespuesta.delete('1.0', 'end')
        campoEstatus.delete('1.0', 'end')
        if AP == "False" and needAP == 1:
            campoRespuesta.insert(tk.INSERT, nombre + " " + valorRespuesta + "\nPara cambiar estos puertos necesita habilitar los voltajes usando el botón AP")
        else:
            campoRespuesta.insert(tk.INSERT, nombre + " " + valorRespuesta)
    asignarValores()

    

    #respuesta = respuestaStringArray[respuestaPos]
    
def reiniciarFPGA():
    serialPort.timeout = 3

    campoRespuesta.delete('1.0', 'end')
    campoEstatus.delete('1.0', 'end')
    campoEstatus.insert(tk.INSERT, "Reiniciando FPGA, espere...")
    window.update()

    rstL = "S P2.3 0\n"
    rstH = "S P2.3 1\n"
    frznH = "S P2.0 1\n"

    # for i in range(len(rstL)):
    #     time.sleep(tiempoEnvio)
    #     serialPort.write(rstL[i].encode())

    # time.sleep(tiempoEnvio)
    # serialPort.write("\n".encode())
    serialPort.write(rstL.encode())

    respuesta = serialPort.read_until(expected="mvm>".encode())

    if re.search("mvm>", str(respuesta)):
        time.sleep(2)
        # for i in range(len(rstH)):
        #     time.sleep(tiempoEnvio)
        #     serialPort.write(rstH[i].encode())

        # time.sleep(tiempoEnvio)
        # serialPort.write("\n".encode())
        serialPort.write(rstH.encode())

        serialPort.read_until(expected="mvm>".encode())

        # for i in range(len(frznH)):
        #     time.sleep(tiempoEnvio)
        #     serialPort.write(frznH[i].encode())

        # time.sleep(tiempoEnvio)
        # serialPort.write("\n".encode())
        serialPort.write(frznH.encode())

        respuesta2 = serialPort.read_until(expected="mvm>".encode())
        print(respuesta2)
        if re.search("mvm>", str(respuesta2)):
            campoRespuesta.delete('1.0', 'end')
            campoEstatus.delete('1.0', 'end')
            campoEstatus.insert(tk.INSERT, "FPGA reiniciado con éxito.")
            window.update()
        else: 
            campoRespuesta.delete('1.0', 'end')
            campoEstatus.delete('1.0', 'end')
            campoEstatus.insert(tk.INSERT, "Ocurrió un error al intentar reiniciar el FPGA. Reiniciando unidad...")

            window.update()
            time.sleep(1)
            reiniciar()
    else:
        campoRespuesta.delete('1.0', 'end')
        campoEstatus.delete('1.0', 'end')
        campoEstatus.insert(tk.INSERT, "Ocurrió un error al intentar reiniciar el FPGA. Reiniciando unidad...")
        window.update()
        time.sleep(1)
        reiniciar()
    # respuestaStringArray = respuestaBytes.decode()

    #  = respuestaStringArray[respuestaPos]
    

    # if re.search("MV Monitor", respuesta):
    #     campoRespuesta.insert(tk.INSERT, ">La unidad se reinició al tratar de hacer la prueba. Inténtalo de nuevo\n")
    # else:
    #     campoRespuesta.insert(tk.INSERT, ">" + respuesta + "\n")

    # campoEstatus.delete('1.0', 'end')

    # serialPort.flushInput()
    # print(respuestaStringArray)
    #print(respuesta)

def enviarComandoSimple(comando, tiempoEspera = 2, respuestaPos = 2, reset = 0):
    global AP, RATIO_SEL, HALL_SEL, LOWER_BURDEN, LO_ZIN_SKY, LO_ZIN_EARTH, EFS_G4, EFS_G1_2, RAM, FLASH
    serialPort.timeout = tiempoEspera
    serialPort.flushInput()
    campoRespuesta.delete('1.0', 'end')
    campoEstatus.delete('1.0', 'end')
    campoEstatus.insert(tk.INSERT, "Espere...")
    window.update()

    # for i in range(len(comando)):
    #     time.sleep(tiempoEnvio)
    #     serialPort.write(comando[i].encode())

    # time.sleep(tiempoEnvio)
    # serialPort.write("\n".encode())
    comando += "\n"
    serialPort.write(comando.encode())
    respuestaBytes = serialPort.read_until(expected="mvm>".encode())
 
    respuestaStringArray = respuestaBytes.decode('unicode_escape').split("\r\n")

    respuesta = respuestaStringArray[respuestaPos]
    campoEstatus.delete('1.0', 'end')

    if re.search("MV Monitor", respuesta):
        campoRespuesta.insert(tk.INSERT, ">La unidad se reinició al tratar de hacer la prueba. Inténtalo de nuevo\n")
        AP = "False"
        RATIO_SEL = "False"
        HALL_SEL = "True"
        LOWER_BURDEN = "False"
        LO_ZIN_SKY = "False"
        LO_ZIN_EARTH = "False"
        EFS_G4 = "False"
        EFS_G1_2 = "False"
        asignarValores()
        serialPort.flushInput()
        return

    else:
        campoRespuesta.insert(tk.INSERT, ">" + respuesta + "\n")

    


    serialPort.flushInput()
    # print(respuestaStringArray)
    # print(respuesta)
    
    if comando == "MT RAM\n":
        RAM = respuesta.split("=")[1]
        print(RAM)
    if comando == "MT FLASH\n":
        FLASH = respuesta.split("=")[1]
    asignarValores()

def radioIniciar():
    serialPort.timeout = 10
    campoRespuesta.delete('1.0', 'end')
    campoEstatus.delete('1.0', 'end')
    campoEstatus.insert(tk.INSERT, "Conectando, espere...")
    window.update()

    


   
    comandosRadio = ["s f.54 1\n", "s f.54 0\n", "link radio 115200\n"]
    for i in range(3):

        # for j in range(len(comandosRadio[i])):
        #     time.sleep(tiempoEnvio)
        #     serialPort.write(comandosRadio[i][j].encode())
        # time.sleep(tiempoEnvio)
        serialPort.write(comandosRadio[i].encode())
        time.sleep(0.200) 
        if i < 2:
            serialPort.read_until(expected="mvm>".encode())

    respuestaBytes = serialPort.read_until("link...\r\n".encode())
    respuesta = respuestaBytes.decode('unicode_escape')
    print(respuesta)
    campoEstatus.delete('1.0', 'end')

    if re.search("link...\r\n", respuesta):
        campoEstatus.insert(tk.INSERT, "Conectado")
        desactivarBotones()
        activarBotonesRadio()
        time.sleep(4)
    else:
        campoEstatus.insert(tk.INSERT, "No se pudo conectar. Abortando...")
        window.update()
        
        time.sleep(2)
        salirRadio(1)
        return

    

    

    # respuestaBytes = serialPort.read_until(expected="mvm>".encode())
 
    # respuestaStringArray = respuestaBytes.decode().split("\r\n")

    # respuesta = respuestaStringArray[respuestaPos]

def radioComandos(comando, opcion):
    global IMEI , SIM , CSQ
    serialPort.timeout = 5
    serialPort.flushInput()
    campoRespuesta.delete('1.0', 'end')
    campoEstatus.delete('1.0', 'end')
    campoEstatus.insert(tk.INSERT, "Espere...")
    window.update()

    # for i in range(len(comando)):
    #     time.sleep(tiempoEnvio)
    #     serialPort.write(comando[i].encode())

    # time.sleep(tiempoEnvio)
    # serialPort.write("\r".encode())
    comando += "\r"
    serialPort.write(comando.encode())

    respuestaBytes = serialPort.read_until(expected="OK".encode())
 
    respuesta = respuestaBytes.decode('unicode_escape')

    campoEstatus.delete('1.0', 'end')
    # print(respuesta)
    # print(respuestaBytes)
    if respuesta.strip() == "" or re.search(b'\x00\x00', respuestaBytes):
        campoEstatus.insert(tk.INSERT, "Ocurrió un error. Saliendo de modo radio...")
        window.update()
        salirRadio(1)
        return
    else:
        campoRespuesta.insert(tk.INSERT, ">" + respuesta + "\n")
        if opcion == 1:
            IMEI = respuesta.split("\n")[1]
        if opcion == 2:
            SIM = respuesta.split("\n")[1]
        if opcion == 3:
            CSQ = respuesta.split("\n")[1]
        asignarValores()

    serialPort.flushInput()
    
def salirRadio(porError = 0):

    if porError == 0:
        campoEstatus.delete('1.0', 'end')
        campoEstatus.insert(tk.INSERT, "Saliendo de modo radio...")
        window.update()
        time.sleep(1)

    serialPort.write("\030".encode())


    serialPort.read_until()

    campoEstatus.delete('1.0', 'end')
    campoRespuesta.delete('1.0', 'end')
    activarBotones()
    desactivarBotonesRadio()

    serialPort.flushInput()
    
def reiniciar():
    global AP , RATIO_SEL , HALL_SEL , LOWER_BURDEN , LO_ZIN_SKY , LO_ZIN_EARTH , EFS_G4 , EFS_G1_2 , IMEI , SIM , CSQ 
    global RAM, FLASH, HALL1, HALL2, HALL_LPF, IMEAS, ESFX, VCAP, CapCharge
    serialPort.timeout = 5
    serialPort.flushInput()
    serialPort.flushOutput()
    campoRespuesta.delete('1.0', 'end')
    campoEstatus.delete('1.0', 'end')
    campoEstatus.insert(tk.INSERT, "Reiniciando...")
    window.update()
    
    serialPort.write("\n".encode())
    serialPort.read_until(expected="mvm>".encode())
    # for i in range(4):
    #     time.sleep(tiempoEnvio)
    #     serialPort.write("boot"[i].encode())
    serialPort.write("boot\n".encode())

    # time.sleep(tiempoEnvio)
    # serialPort.write("\n".encode())

    serialPort.read_until(expected="(y/n)>".encode())

    time.sleep(tiempoEnvio)
    serialPort.write("y\n".encode())
    # time.sleep(tiempoEnvio)
    # serialPort.write("\n".encode())

    respuestaReinicio = serialPort.read_until(expected="mvm>".encode())
    texto = respuestaReinicio.decode("unicode_escape").replace("ÿ", "").replace("mvm>", "").replace("\x00", "")
    
    if re.search("MV Monitor", texto ):
        campoEstatus.delete('1.0', 'end')
        campoEstatus.insert(tk.INSERT, "Se reinició con éxito")
        print(respuestaReinicio)
        print(texto)
        campoRespuesta.insert(tk.INSERT, texto )
        
        AP = "False"
        RATIO_SEL = "False"
        HALL_SEL = "True"
        LOWER_BURDEN = "False"
        LO_ZIN_SKY = "False"
        LO_ZIN_EARTH = "False"
        EFS_G4 = "False"
        EFS_G1_2 = "False"
        IMEI = "?"
        SIM = "?"
        CSQ = "?" 
        RAM = FLASH = HALL1 = HALL2 = HALL_LPF = IMEAS = ESFX = VCAP = CapCharge = "?"
        asignarValores()
        activarBotones()
        resetVoltageInput()
    else:
        campoEstatus.delete('1.0', 'end')
        campoEstatus.insert(tk.INSERT, "Error")
        campoRespuesta.insert(tk.INSERT, "Parece que hubo un problema. Inténtalo de nuevo.")
    print(texto)

def activarBotones():
    try: 
        for i in comandosSimplesFrame.winfo_children():
            i["state"] = "normal"

        for j in pruebasFrame.winfo_children():
            j["state"] = "normal"

        for k in pinesFrame.winfo_children():
            for l in k.winfo_children():
                for m in l.winfo_children():
                    m["state"] = "normal"
        btnRadio["state"] = "normal"
        

    except Exception as e:
        print(e)

def desactivarBotones():
    try: 
        for i in comandosSimplesFrame.winfo_children():
            i["state"] = "disabled"

        for j in pruebasFrame.winfo_children():
            j["state"] = "disabled"

        for k in pinesFrame.winfo_children():
            for l in k.winfo_children():
                for m in l.winfo_children():
                    m["state"] = "disabled"
        btnRadio["state"] = "disabled"

        
    except Exception as e:
        print(e)

def activarBotonesRadio():
    for i in comandosRadioFrame.winfo_children():
        try: 
            i["state"] = "normal"
        except: 
            pass
    btnRadioSalir["state"] = "normal"
    
def desactivarBotonesRadio():
    for i in comandosRadioFrame.winfo_children():
        try: 
            i["state"] = "disabled"
        except: 
            pass
    btnRadioSalir["state"] = "disabled"

def resetBG():
    pass

def asignarValores():
    campoValores.delete('1.0', 'end')
    campoValores2.delete('1.0', 'end')
    campoValores.insert(tk.INSERT,  "Puerto = " + puerto + "\n"
                                    "----------------------------------------\n"
                                    "AP = " + AP + " \n\n"
                                    "RATIO_SEL = " + RATIO_SEL  + "\n\n"
                                    "HALL_SEL = " + HALL_SEL + "   \n\n"
                                    "LOWER_BURDEN = " + LOWER_BURDEN + " \n\n"
                                    "LO_ZIN_SKY = " + LO_ZIN_SKY + " \n\n"
                                    "LO_ZIN_EARTH = " + LO_ZIN_EARTH + "\n\n"
                                    "EFS_G4 = " + EFS_G4 + "       \n\n"
                                    "EFS_G1/2 = " + EFS_G1_2  + "  \n\n"
                                     )

    campoValores2.insert(tk.INSERT,  "RAM = " + RAM + "\n\n"
                                    "FLASH = " + FLASH + " \n\n"
                                    "Hall1 = " + HALL1  + "\n\n"
                                    "Hall2 = " + HALL2 + "   \n\n"
                                    "Hall1 LPF = " + HALL_LPF + " \n\n"
                                    "IMEAS = " + IMEAS + "\n\n"
                                    "ESFX = " + ESFX + " \n\n"
                                    "VCAP = " + VCAP + "       \n\n"
                                    "CapCharge = " + CapCharge  + "  \n\n"
                                    "TP = " + TP + " \n\n"
                                    "IMEI = " + IMEI + "           \n\n"
                                    "SIM = " + SIM + "             \n\n"
                                    "Señal = " + CSQ
                                   )
    window.update()
    
def listaPuertos():

    try: 
        lista = ["--SELECCIONE UN PUERTO--"]
        #print(selPuertoList.get())
        ports = serial.tools.list_ports.comports()
    
        for port, desc, hwid in sorted(ports):
            lista.append("{}: {}".format(port, desc))
            
        
        selPuertoList.configure(values = lista)
        selPuertoList.current(0)
    except:
        print("Hubo un problema al buscar los puertos")

def seleccionPuerto(event):
    global serialPort, puerto
    puerto = ""
    window.focus()
    if selPuertoList.get() == "--SELECCIONE UN PUERTO--":
        return
    else:
        try: 
            try: 
                serialPort.close()
            except:
                pass
            campoRespuesta.delete('1.0', 'end')
            campoEstatus.delete('1.0', 'end')
            #campoEstatus.insert(tk.INSERT, "Esperando respuesta de Arduino...")
            window.update()
            #time.sleep(3)
            btnReboot.configure(state = "normal")
            btnTestV.configure(state = "normal")
            
            puerto = selPuertoList.get().split(":")[0]
            serialPort = serial.Serial(port = puerto, baudrate=9600, timeout = 5)#, stopbits =  serial.STOPBITS_ONE, bytesize = serial.EIGHTBITS)
            serialPort.close()
            serialPort.open()
            serialPort.flushInput()

            asignarValores()
            campoEstatus.delete('1.0', 'end')

        except: 
            mensajeError()

def mensajeError():
    
    messagebox.showinfo(title =  "Error", message = "El puerto está siendo usado por otro programa. Ciérrelo e intente de nuevo")

iniciar()
asignarValores()
listaPuertos()
buscarActualizacion()

window.iconbitmap(resource_path("agmicon.ico"))

window.mainloop()