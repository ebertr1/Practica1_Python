from flask import Flask, json, flash, Blueprint, url_for, jsonify, make_response, request, render_template, redirect, abort
import requests
import registrar_historial
import datetime
from urllib.parse import quote

router = Blueprint('router', __name__)

def registrar_historial(operacion, tipo, mensaje):
    # Leer el historial existente
    try:
        with open("historial.json", "r") as archivo:
            historial = json.load(archivo)
    except FileNotFoundError:
        historial = []

    # Crear una nueva entrada de historial
    nueva_entrada = {
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "operacion": operacion,
        "tipo": tipo,
        "mensaje": mensaje
    }
    historial.append(nueva_entrada)

    # Guardar el historial actualizado
    with open("historial.json", "w") as archivo:
        json.dump(historial, archivo, indent=4)

@router.route('/admin')
def admin():
    return render_template('fragmento/inversionista/lista.html')

@router.route('/admin/inversionista/list')
def list_inversionista():
    r = requests.get("http://localhost:8075/api/inversionista/list")
    data = r.json()
    return render_template('fragmento/inversionista/lista.html', list=data["data"])

@router.route('/admin/proyecto/list')
def list_proyecto():
    r = requests.get("http://localhost:8075/api/proyecto/list")
    data = r.json()
    return render_template('fragmento/proyecto/lista.html', list=data["data"])

@router.route('/admin/inversionista/edit/<int:id>')
def view_edit_inversionista(id):
    r = requests.get("http://localhost:8075/api/inversionista/list")
    data = r.json()
    r1 = requests.get(f"http://localhost:8075/api/inversionista/get/{id}")
    
    if r1.status_code == 200:
        data1 = r1.json()
        return render_template('fragmento/inversionista/editar.html', list=data["data"], inversionista=data1["data"])
    else:
        flash("Inversionista no encontrado", category='error')
        return redirect("/admin/inversionista/list")

@router.route('/admin/proyecto/edit/<int:id>')
def view_edit_proyecto(id):
    r = requests.get("http://localhost:8075/api/proyecto/list")
    data = r.json()
    r1 = requests.get(f"http://localhost:8075/api/proyecto/get/{id}")
    data1 = r1.json()
    
    if r1.status_code == 200:
        return render_template('fragmento/proyecto/editar.html', list=data["data"], proyecto=data1["data"])
    else:
        flash("Proyecto no encontrado", category='error')
        return redirect("/admin/proyecto/list")

@router.route('/admin/inversionista/register')
def view_register_inversionista():
    r = requests.get("http://localhost:8075/api/inversionista/list")
    data = r.json()
    return render_template('fragmento/inversionista/registro.html', list=data["data"])

@router.route('/admin/proyecto/register')
def view_register_proyecto():
    r = requests.get("http://localhost:8075/api/proyecto/list")
    data = r.json()
    return render_template('fragmento/proyecto/registro.html', list=data["data"])

@router.route('/admin/proyecto/save', methods=["POST"])
def save_proyecto():
    headers = {'Content-type': 'application/json'}
    form = request.form
    dataF = {
        "nombre": form["nombre"],
        "inversion": float(form["inversion"]),
        "inversionistas": form["inversionistas"],
        "duracion": int(form["duracion"]),
        "fechaInicio": form["fechaInicio"],
        "fechaFin": form["fechaFin"],
        "generacionDiaria": float(form["generacionDiaria"]),
        "costoOperativo": float(form["costoOperativo"]),
        "tipoEnergia": form["tipoEnergia"],
        "ubicacion": form["ubicacion"],
    }

    r = requests.post("http://localhost:8075/api/proyecto/save", data=json.dumps(dataF), headers=headers)
    dat = r.json()
    
    if r.status_code == 200:
        flash("Proyecto guardado correctamente", category='info')
        registrar_historial("crear", "proyecto", f"Proyecto {form['nombre']} creado")
    else:
        flash(str(dat["data"]), category='error')
    return redirect("/admin/proyecto/list")

@router.route('/admin/inversionista/save', methods=["POST"])
def save_inversionista():
    headers = {'Content-type': 'application/json'}
    form = request.form
    dataF = {
        "apellido": form["ape"],
        "nombre": form["nom"],
        "dni": form["dni"],
    }
    
    r = requests.post("http://localhost:8075/api/inversionista/save", data=json.dumps(dataF), headers=headers)
    dat = r.json()
    
    if r.status_code == 200:
        flash("Inversionista guardado correctamente", category='info')
        registrar_historial("crear", "inversionista", f"Inversionista {form['nom']} {form['ape']} creado")
    else:
        flash(str(dat["data"]), category='error')

    return redirect("/admin/inversionista/list")

from flask import Flask, request, jsonify, flash, redirect, url_for

@router.route('/admin/proyecto/delete/<int:id>', methods=['DELETE'])
def delete_proyecto(id):
    try:
        response = requests.delete(f"http://localhost:8075/api/proyecto/delete/{id}")
        if response.status_code == 200:
            flash("Proyecto eliminado exitosamente", "info")
            registrar_historial("eliminar", "proyecto", f"Proyecto con ID {id} eliminado")
            return jsonify({"message": "Proyecto eliminado exitosamente."}), 200  # Responder con JSON
        else:
            flash("Error al eliminar el proyecto.", "danger")
            return jsonify({"error": "No se pudo eliminar el proyecto."}), response.status_code
    except Exception as e:
        flash(f"Hubo un error: {str(e)}", "danger")
        return jsonify({"error": str(e)}), 500  # Responder con JSON


@router.route('/admin/inversionista/delete/<int:id>', methods=["POST"])
def delete_inversionista(id):
    r = requests.delete(f"http://localhost:8075/api/inversionista/delete/{id}")
    
    if r.status_code == 200:
        flash("Inversionista eliminado exitosamente.", category='info')
        registrar_historial("eliminar", "inversionista", f"Inversionista con ID {id} eliminado")
    else:
        flash("No se pudo eliminar el inversionista.", category='error')
    
    return redirect(url_for('router.list_inversionista'))

@router.route('/admin/proyecto/update', methods=["POST"])
def update_proyecto():
    headers = {'Content-type': 'application/json'}
    form = request.form
    dataF = {
        "idProyecto": form["id"],
        "nombre": form["nombre"],
        "inversion": float(form["inversion"]),
        "inversionistas": form["inversionistas"],
        "duracion": int(form["duracion"]),
        "fechaInicio": form["fechaInicio"],
        "fechaFin": form["fechaFin"],
        "generacionDiaria": float(form["generacionDiaria"]),
        "costoOperativo": float(form["costoOperativo"]),
        "tipoEnergia": form["tipoEnergia"],
        "ubicacion": form["ubicacion"],
    }
    r = requests.post("http://localhost:8075/api/proyecto/update", data=json.dumps(dataF), headers=headers)
    dat = r.json()
    
    if r.status_code == 200:
        flash("Proyecto actualizado correctamente", category='info')
        registrar_historial("actualizar", "proyecto", f"Proyecto {form['nombre']} actualizado")
    else:
        flash(str(dat["data"]), category='error')

    return redirect("/admin/proyecto/list")

@router.route('/admin/inversionista/update', methods=["POST"])
def update_inversionista():
    headers = {'Content-type': 'application/json'}
    form = request.form
    dataF = {
        "idInversionista": form["id"],
        "apellido": form["ape"],
        "nombre": form["nom"],
        "dni": form["dni"],
    }
    
    r = requests.post("http://localhost:8075/api/inversionista/update", data=json.dumps(dataF), headers=headers)
    dat = r.json()
    
    if r.status_code == 200:
        flash("Inversionista actualizado correctamente", category='info')
        registrar_historial("actualizar", "inversionista", f"Inversionista {form['nom']} {form['ape']} actualizado")
    else:
        flash(str(dat["data"]), category='error')

    return redirect("/admin/inversionista/list")

@router.route("/admin/proyecto/historial")
def ver_historial():
    try:
        with open("historial.json", "r") as archivo:
            historial = json.load(archivo)
    except FileNotFoundError:
        historial = []
    
    return render_template("fragmento/proyecto/historial.html", historial=historial)


@router.route("/admin/inversionista/historial")
def ver_historssial():
    try:
        with open("historial.json", "r") as archivo:
            historial = json.load(archivo)
    except FileNotFoundError:
        historial = []
    
    return render_template("fragmento/inversionista/historial.html", historial=historial)

@router.route('/admin/proyecto/search/<criterio>/<texto>')
def view_buscar_person(criterio, texto):
    url = "http://localhost:8075/api/proyecto/list/search/"
    
    # Codifica el texto para asegurar que los caracteres especiales y espacios no causen problemas
    texto_codificado = quote(texto)
    print(f"Texto recibido para búsqueda de {criterio}: {texto_codificado}")  # Agregar log para verificar el texto recibido
    
    r = None  # Inicializa la variable r para evitar errores en caso de que no se ejecute ningún bloque
    if criterio == "nombre":
        r = requests.get(url + "nombre/" + texto_codificado)
    elif criterio == "inversionistas":
        print(f"Buscando inversionista con el texto: {texto_codificado}")  # Agregar log para la búsqueda
        r = requests.get(url + "inversionistas/" + texto_codificado)
    elif criterio == "ubicacion":
        r = requests.get(url + "ubicacion/" + texto_codificado)

    # Verifica si la solicitud fue exitosa y si r no es None
    if r:
        if r.status_code == 200:
            try:
                data1 = r.json()  # Intenta convertir la respuesta a JSON
                print(f"Datos recibidos: {data1}")  # Agregar log para verificar los datos recibidos
                if type(data1["data"]) is dict:
                    # Si los datos son un diccionario, crea una lista con él
                    lista = [data1["data"]]
                    return render_template('fragmento/proyecto/lista.html', list=lista)
                else:
                    # Si los datos son una lista, solo pásalos
                    return render_template('fragmento/proyecto/lista.html', list=data1["data"])
            except requests.exceptions.JSONDecodeError:
                return render_template('fragmento/proyecto/lista.html', list=[], message="Error al procesar la respuesta JSON")
        else:
            # Si el código de estado no es 200, muestra un mensaje de error
            return render_template('fragmento/proyecto/lista.html', list=[], message="No existe el elemento")
    else:
        return render_template('fragmento/proyecto/lista.html', list=[], message="Criterio no válido o error en la solicitud")
    
@router.route('/admin/proyecto/list/<atributo>/<tipo>/<metodo>')
def view_order_person(atributo, tipo, metodo):
    try:
        print(f"Recibido: atributo={atributo}, tipo={tipo}, metodo={metodo}")

        if metodo == "order":
            url = f"http://localhost:8075/api/proyecto/list/order/{atributo}/{tipo}"
        elif metodo == "merge":
            url = f"http://localhost:8075/api/proyecto/list/merge/{atributo}/{tipo}"
        elif metodo == "shell":
            url = f"http://localhost:8075/api/proyecto/list/shell/{atributo}/{tipo}"
        else:
            flash("Método de ordenación no válido", category='error')
            return render_template('fragmento/proyecto/lista.html', list=[])

        r = requests.get(url)

        if r.status_code == 200:
            data = r.json()
            return render_template('fragmento/proyecto/lista.html', list=data["data"])
        else:
            flash("Error al ordenar los datos", category='error')
            return render_template('fragmento/proyecto/lista.html', list=[], message='Error al ordenar los datos')

    except requests.RequestException as e:
        flash(f"Error de conexión: {str(e)}", category='error')
        return redirect(url_for('router.list'))
    

@router.route('/admin/proyecto/list/search/<categoria>/<texto>')
def view_buscar_proyecto(categoria, texto):
    try:
        # Base URL de la API
        base_url = "http://localhost:8075/api/proyecto/list/search"

        # Validar la categoría
        if categoria not in ["nombre", "inversionistas", "ubicacion"]:
            flash("Categoría de búsqueda no válida", category='error')
            return redirect(url_for('router.list'))

        # Construir la URL con el criterio dinámico
        criterio = "binario" if len(texto) <= 10 else "lineal"
        api_url = f"{base_url}/{criterio}/{categoria}/{texto}"

        # Consumir la API
        r = requests.get(api_url)
        data = r.json()

        # Manejo de la respuesta
        if r.status_code == 200:
            proyectos = data.get("data", [])
            return render_template('fragmento/proyecto/lista.html', list=proyectos)
        else:
            flash("No se encontraron resultados", category='info')
            return render_template('fragmento/proyecto/lista.html', list=[])

    except requests.RequestException as e:
        flash(f"Error de conexión: {str(e)}", category='error')
        return redirect(url_for('router.list'))

