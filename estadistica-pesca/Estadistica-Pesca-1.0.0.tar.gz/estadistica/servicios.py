# coding=utf-8
import importlib
import StringIO
import datetime
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from settings import *
from datetime import timedelta, datetime
from django.http import HttpResponse
from xlsxwriter.workbook import Workbook
mod = importlib.import_module(MODELO)

def EstadisticaDeCaptura(campania_pk, especie_pk, juveniles):
    campania = mod.Campania.objects.get(pk=campania_pk)
    if mod.Lance_Pesca.objects.filter(actividad__estacion_general__etapa__campania=campania).exists():
        lances = mod.Lance_Pesca.objects.filter(actividad__estacion_general__etapa__campania=campania)
        output = StringIO.StringIO()
        filename = campania.codigo + ' - Listado Estadistica de una Captura.xlsx'
        workbook = Workbook(output, {'remove_timezone': True})
        bold_centrado = workbook.add_format({'bold': True, 'align': 'center'})
        centrado = workbook.add_format({'align': 'center'})
        worksheet_eg = workbook.add_worksheet('Estadistica de una captura')
        format5 = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm', 'align': 'center'})

        # TITULOS
        worksheet_eg.write(0, 0, 'Lance', bold_centrado)
        worksheet_eg.write(0, 1, 'Fecha', bold_centrado)
        worksheet_eg.write(0, 2, 'Latitud', bold_centrado)
        worksheet_eg.write(0, 3, 'Longitud', bold_centrado)
        worksheet_eg.write(0, 4, 'Profundidad', bold_centrado)
        worksheet_eg.write(0, 5, 'Captura Total', bold_centrado)
        worksheet_eg.write(0, 6, 'Captura Especie', bold_centrado)
        worksheet_eg.write(0, 7, 'Peso Muestra', bold_centrado)
        worksheet_eg.write(0, 8, 'Kg/h Especie', bold_centrado)
        worksheet_eg.write(0, 9, '% Juveniles < '+str(juveniles), bold_centrado)
        worksheet_eg.write(0, 10, 'Talla Media', bold_centrado)
        worksheet_eg.write(0, 11, 'Toneladas mn2', bold_centrado)
        worksheet_eg.write(0, 12, 'Miles de Individuos mn2', bold_centrado)

        row = 1
        for lance in lances:
            if mod.Especie.objects.filter(pk=especie_pk).exists():
                especie = mod.Especie.objects.get(pk=especie_pk)
                if mod.Captura.objects.filter(lance=lance, especie=especie).exists():
                    captura = mod.Captura.objects.get(lance=lance, especie=especie)
                    if mod.Muestra.objects.filter(captura=captura).exists():
                        muestra = mod.Muestra.objects.get(captura=captura)
                        if mod.DetalleMuestra.objects.filter(muestra=muestra).exists():
                            detalleMuestras = mod.DetalleMuestra.objects.filter(muestra=muestra)

                            cantPorTalla = 0
                            total = 0
                            cantidad = 0

                            #para calcular la talla media
                            for detalle in detalleMuestras:
                                cantPorTalla = cantPorTalla + (detalle.talla * detalle.total)
                                total = total + detalle.total
                            tallaMedia = float(cantPorTalla) / float(total)

                            milesIndividuosMn2 = ((float(captura.kg) * float(total)) / float(muestra.peso_mues)) / float(lance.area_barr)
                            toneladasMn2 = (float(captura.kg)/1000) / float(lance.area_barr)

                            #para calcular el % de juveniles segun lo que viene por parametro
                            total = 0
                            for detalle in detalleMuestras:
                                if detalle.talla < juveniles:
                                    cantidad = cantidad + detalle.total
                                total = total + detalle.total
                            porcJuveniles = (float(cantidad) * 100)/float(total)

                            final = timedelta(hours=lance.hora_final.hour, minutes=lance.hora_final.minute,
                                                seconds=lance.hora_final.second)
                            inicial = timedelta(hours=lance.hora_ini.hour, minutes=lance.hora_ini.minute, seconds=lance.hora_ini.second)

                            tiempoArrastre = final - inicial
                            kgPorHora=0
                            if devolverHoras(tiempoArrastre) < 1:
                                tiempoArrastreDecimal = devolverMinutosEnDecimal(tiempoArrastre)
                                kgPorHora = float(captura.kg) / tiempoArrastreDecimal

                            worksheet_eg.write(row, 0, lance.lance, centrado)
                            worksheet_eg.write_datetime(row, 1, lance.fecha_hora, format5)
                            worksheet_eg.write(row, 2, lance.lat_ini, centrado)
                            worksheet_eg.write(row, 3, lance.long_ini, centrado)
                            worksheet_eg.write(row, 4, lance.prof_inic, centrado)
                            worksheet_eg.write(row, 5, lance.capt_total, centrado)
                            worksheet_eg.write(row, 6, captura.kg, centrado)
                            worksheet_eg.write(row, 7, muestra.peso_mues, centrado)
                            worksheet_eg.write(row, 8, kgPorHora, centrado)
                            worksheet_eg.write(row, 9, porcJuveniles, centrado)
                            worksheet_eg.write(row, 10, tallaMedia, centrado)
                            worksheet_eg.write(row, 11, toneladasMn2, centrado)
                            worksheet_eg.write(row, 12, milesIndividuosMn2, centrado)
                            row = row + 1

        workbook.close()
        output.seek(0)
        response = HttpResponse(output.read(), content_type="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename='+filename
        return response

def devolverHoras(td):
    return int(td.days)

def devolverMinutosEnDecimal(td):
    decimal = float(td.seconds) / float(3600)
    return decimal

def devolverMinutos(td):
    return '0'+ str(td.seconds)

def ResumenPuenteCaptura(campania_pk):
    campania = mod.Campania.objects.get(pk=campania_pk)
    filename = campania.codigo + ' - Resumen de Puente y Captura.pdf'
    output = StringIO.StringIO()
    pdf = canvas.Canvas(output, pagesize=A4)
    if mod.Lance_Pesca.objects.filter(actividad__estacion_general__etapa__campania=campania).exists():
        lances = mod.Lance_Pesca.objects.filter(actividad__estacion_general__etapa__campania=campania)
        for lance in lances:
            final = timedelta(hours=lance.hora_final.hour, minutes=lance.hora_final.minute,seconds=lance.hora_final.second)
            inicial = timedelta(hours=lance.hora_ini.hour, minutes=lance.hora_ini.minute, seconds=lance.hora_ini.second)
            tiempoArrastre = final - inicial
            if devolverHoras(tiempoArrastre) < 1:
                tiempoArrastre = '0'+str(tiempoArrastre)
            path = 'site_media/images/logo.jpg'
            image = Image.open(path)
            pdf.setFont("Helvetica", 10)
            fechaActual = datetime.now().date()
            pdf.drawString(480, 800, str(fechaActual))
            pdf.drawImage(path, 20, 730, width=100, height=100,preserveAspectRatio=True)
            pdf.drawString(120, 770, "INSTITUTO NACIONAL DE INVESTIGACION Y DESARROLLO PESQUERO")
            pdf.rect(30, 720, 535, 20, stroke=1, fill=0)
            pdf.drawString(35, 727, "CAMPA\xd1A "+campania.codigo)
            pdf.drawString(300, 727, "LANCE "+ str(lance.lance))
            pdf.drawString(450, 727, "FECHA "+ str(lance.fecha_hora.date()))
            if mod.EstacionGeneral.objects.filter(pk=lance.actividad.estacion_general.pk).exists():
                estacion = mod.EstacionGeneral.objects.get(pk=lance.actividad.estacion_general.pk)
                datoAmbiental = mod.DatoAmbiental.objects.get(estacion_general=estacion)
                if lance.lat_ini > 0:
                    latitud_ini = (lance.lat_ini * -1)
                else:
                    latitud_ini = lance.lat_ini
                if lance.long_ini > 0:
                    longitud_ini = (lance.long_ini * -1)
                else:
                    longitud_ini = lance.long_ini

                if lance.lat_final > 0:
                    latitud_final = (lance.lat_final * -1)
                else:
                    latitud_final = lance.lat_final
                if lance.long_final > 0:
                    longitud_final = (lance.long_final * -1)
                else:
                    longitud_final = lance.long_final

                pdf.drawString(38, 700, "Estacion General:")
                pdf.drawString(200, 700, str(estacion.nro_estacion_barco))
                pdf.drawString(38, 685, "Hora Inicial:")
                pdf.drawString(200, 685, str(lance.hora_ini))
                pdf.drawString(38, 670, "Hora Final:")
                pdf.drawString(200, 670, str(lance.hora_final))
                pdf.drawString(38, 655, "Tiempo de Arrastre:")
                pdf.drawString(200, 655, str(tiempoArrastre))
                pdf.drawString(38, 640, "Latitud Inicial:")
                pdf.drawString(200, 640, str(latitud_ini))
                pdf.drawString(38, 625, "Longitud Inicial:")
                pdf.drawString(200, 625, str(longitud_ini))
                pdf.drawString(38, 610, "Latitud Final:")
                pdf.drawString(200, 610, str(latitud_final))
                pdf.drawString(38, 595, "Longitud Final:")
                pdf.drawString(200, 595, str(longitud_final))
                pdf.drawString(38, 580, "Estado del Tiempo:")
                pdf.drawString(200, 580, str(datoAmbiental.estado_tiempo))
                pdf.drawString(38, 565, "Direccion del Viento:")
                pdf.drawString(200, 565, str(datoAmbiental.viento_dir))
                pdf.drawString(38, 550, "Velocidad del Viento:")
                pdf.drawString(200, 550, str(datoAmbiental.viento_vel))
                pdf.drawString(38, 535, "Estado del Mar:")
                pdf.drawString(200, 535, str(datoAmbiental.mar_estado))

                pdf.drawString(320, 700, "Profundidad Inicial:")
                pdf.drawString(482, 700, str(lance.prof_inic))
                pdf.drawString(320, 685, "Profundidad Final:")
                pdf.drawString(482, 685, str(lance.prof_final))
                pdf.drawString(320, 670, "Presion Barometrica:")
                pdf.drawString(482, 670, str(datoAmbiental.presion))
                pdf.drawString(320, 655, "Velocidad de Arrastre:")
                pdf.drawString(482, 655, str(lance.vel_arras))
                pdf.drawString(320, 640, "Area Barrida:")
                pdf.drawString(482, 640, str(lance.area_barr))
                pdf.drawString(320, 625, "Cable Filado:")
                pdf.drawString(482, 625, str(lance.cab_filad))
                pdf.drawString(320, 610, "Distancia de Arrastre:")
                pdf.drawString(482, 610, str(lance.dist_arras))
                pdf.drawString(320, 595, "Rumbo de Arrastre:")
                pdf.drawString(482, 595, str(lance.rumbo))
                pdf.drawString(320, 580, "Distancia entre Alas:")
                pdf.drawString(482, 580, str(lance.dist_alas))
                pdf.drawString(320, 565, "Abertura Vertical:")
                pdf.drawString(482, 565, str(lance.aber_vert))
                pdf.drawString(320, 550, "Relinga Superior:")
                pdf.drawString(482, 550, "")
                pdf.drawString(320, 535, "Relinga Inferior:")
                pdf.drawString(482, 535, "")

            pdf.rect(30, 500, 535, 20, stroke=1, fill=0)
            pdf.drawString(35, 507, "ESPECIE")
            pdf.drawString(250, 507, "Nro EJEMP.")
            pdf.drawString(340, 507, "KILOS")
            pdf.drawString(400, 507, "TON.mn2")
            pdf.drawString(470, 507, "MILES IND.mn2")
            capturas = mod.Captura.objects.filter(lance=lance)
            posicion = 480
            for captura in capturas:
                nroEjemplares = 0
                milesIndividuosMn2 = 0
                if mod.Muestra.objects.filter(captura=captura, captura__especie=captura.especie).exists():
                    muestra = mod.Muestra.objects.get(captura=captura, captura__especie=captura.especie)
                    nroEjemplares = captura.kg * muestra.ej_kgr
                    total=0
                    if mod.DetalleMuestra.objects.filter(muestra=muestra).exists():
                        detalleMuestras = mod.DetalleMuestra.objects.filter(muestra=muestra)
                        for detalle in detalleMuestras:
                            total = total + detalle.total
                    if total != 0:
                        milesIndividuosMn2 = '%.4f' % (((float(captura.kg) * float(total)) / float(muestra.peso_mues)) / float(lance.area_barr))
                    else:
                        milesIndividuosMn2 = '%.4f' % ((float(nroEjemplares) / 1000) / float(lance.area_barr))

                nroEjemplares= int(round(nroEjemplares))
                toneladasMn2 = '%.4f' % ((float(captura.kg)/1000) / float(lance.area_barr))

                pdf.drawString(38, posicion, captura.especie.nombre_cientifico)
                pdf.drawString(270, posicion, str(nroEjemplares))
                pdf.drawString(340, posicion, str(captura.kg))
                pdf.drawString(405, posicion, str(toneladasMn2))
                pdf.drawString(480, posicion, str(milesIndividuosMn2))
                posicion = posicion - 15
            pdf.showPage()
    pdf.save()
    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename='+filename
    return response

def ValidarResumenPuenteCapturaUnaEspecie(campania_pk, especie_pk):
    error_list = []
    campania = mod.Campania.objects.get(pk=campania_pk)
    especie = mod.Especie.objects.get(pk=especie_pk)
    if mod.Lance_Pesca.objects.filter(actividad__estacion_general__etapa__campania=campania).exists():
        lances = mod.Lance_Pesca.objects.filter(actividad__estacion_general__etapa__campania=campania)
        if not mod.Captura.objects.filter(especie=especie,lance__in=lances).exists():
            error_list.append("La especie seleccionada "+str(especie.nombre_cientifico)+" no fue capturada en ningun lance, el listado no se ha generado.")
    return error_list

def ResumenPuenteCapturaUnaEspecie(campania_pk,especie_pk):
    campania = mod.Campania.objects.get(pk=campania_pk)
    especie = mod.Especie.objects.get(pk=especie_pk)
    filename = campania.codigo + ' - Resumen de Puente y Captura '+str(especie.nombre_cientifico)+'.pdf'
    output = StringIO.StringIO()
    pdf = canvas.Canvas(output, pagesize=A4)
    contador = 0

    if mod.Lance_Pesca.objects.filter(actividad__estacion_general__etapa__campania=campania).exists():
        lances = mod.Lance_Pesca.objects.filter(actividad__estacion_general__etapa__campania=campania)
        if mod.Captura.objects.filter(especie=especie,lance__in=lances).exists():
            crearCabecera(pdf, campania, especie)
            posicion = 685
            posicionLinea = 680
            for lance in lances:
                capturas = mod.Captura.objects.filter(especie=especie, lance=lance)
                if contador > 30:
                    pdf.showPage()
                    crearCabecera(pdf, campania, especie)
                    contador = 0
                    posicion = 685
                    posicionLinea = 680
                final = timedelta(hours=lance.hora_final.hour, minutes=lance.hora_final.minute,seconds=lance.hora_final.second)
                inicial = timedelta(hours=lance.hora_ini.hour, minutes=lance.hora_ini.minute, seconds=lance.hora_ini.second)
                tiempoArrastre = final - inicial
                if devolverHoras(tiempoArrastre) < 1:
                    tiempoArrastre = '0'+str(tiempoArrastre)
                for captura in capturas:
                    nroEjemplares = 0
                    milesIndividuosMn2 = 0
                    if mod.Muestra.objects.filter(captura=captura, captura__especie=captura.especie).exists():
                        muestra = mod.Muestra.objects.get(captura=captura, captura__especie=captura.especie)
                        nroEjemplares = captura.kg * muestra.ej_kgr
                        total = 0
                        if mod.DetalleMuestra.objects.filter(muestra=muestra).exists():
                            detalleMuestras = mod.DetalleMuestra.objects.filter(muestra=muestra)
                            for detalle in detalleMuestras:
                                total = total + detalle.total
                        if total != 0:
                            milesIndividuosMn2 = '%.4f' % (((float(captura.kg) * float(total)) / float(muestra.peso_mues)) / float(lance.area_barr))
                        else:
                            milesIndividuosMn2 = '%.4f' % ((float(nroEjemplares) / 1000) / float(lance.area_barr))

                    nroEjemplares= int(round(nroEjemplares))
                    toneladasMn2 = '%.4f' % ((float(captura.kg)/1000) / float(lance.area_barr))
                    if lance.lat_ini > 0:
                        latitud = (lance.lat_ini * -1)
                    else:
                        latitud = lance.lat_ini
                    if lance.long_ini > 0:
                        longitud = (lance.long_ini * -1)
                    else:
                        longitud = lance.long_ini
                    pdf.drawString(35, posicion, str(lance.lance))
                    pdf.drawString(69, posicion, str(lance.fecha_hora.date()))
                    pdf.drawString(128, posicion, str(latitud))
                    pdf.drawString(178, posicion, str(longitud))
                    pdf.drawString(245, posicion, str(tiempoArrastre))
                    pdf.drawString(320, posicion, str(nroEjemplares))
                    pdf.drawString(380, posicion, str(captura.kg))
                    pdf.drawString(435, posicion, str(toneladasMn2))
                    pdf.drawString(495, posicion, str(milesIndividuosMn2))
                    pdf.line(25, posicionLinea, 570, posicionLinea)
                    posicion = posicion - 20
                    posicionLinea = posicionLinea - 20
                    contador = contador + 1
    pdf.save()
    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename='+filename
    return response

def crearCabecera(pdf, campania, especie):
    path = 'site_media/images/logo.jpg'
    image = Image.open(path)
    pdf.setFont("Helvetica", 10)
    fechaActual = datetime.now().date()
    pdf.drawString(480, 800, str(fechaActual))
    pdf.drawImage(path, 20, 730, width=100, height=100,preserveAspectRatio=True)
    pdf.drawString(120, 770, "INSTITUTO NACIONAL DE INVESTIGACION Y DESARROLLO PESQUERO")
    pdf.drawString(120, 750, 'CAMPA\xd1A '+campania.codigo)
    pdf.drawString(380, 750, "ESPECIE "+ str(especie.nombre_cientifico))
    pdf.rect(25, 700, 545, 30, stroke=1, fill=0)
    pdf.drawString(28, 716, "LANCE")
    pdf.drawString(75, 716, "FECHA")
    pdf.drawString(125, 716, "LATITUD")
    pdf.drawString(175, 716, "LONGITUD")
    pdf.drawString(250, 716, "TIEMPO")
    pdf.drawString(240, 706, "ARRASTRE")
    pdf.drawString(315, 716, "NUMERO")
    pdf.drawString(305, 706, "EJEMPLARES")
    pdf.drawString(380, 716, "KILOS")
    pdf.drawString(430, 716, "TON. mn2")
    pdf.drawString(490, 716, "MILES IND. mn2")