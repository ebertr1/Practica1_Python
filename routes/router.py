from flask import Flask, json, flash, Blueprint, url_for, jsonify, make_response, request, render_template, redirect, abort
import requests
import registrar_historial
import datetime

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
