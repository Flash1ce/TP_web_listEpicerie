from models.utilisateur_model import UtilisateurModel
from models.items_model import ItemModel
from flask import (
    Flask,
    render_template,
    url_for,
    request,
    redirect,
    session,
    flash,
    make_response
)
from datetime import datetime
from bd import obtenir_connexion
import logging
import hashlib
from flask_babel import Babel
from babel import (
  numbers,
  dates
)

app = Flask(__name__)
app.secret_key = "grb[>Wsfe342Zy.pre9**IFg*F"
logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
app.config["BABEL_DEFAULT_LOCALE"] = "fr_CA" 

def get_locale():
    try:
        langue = session['langue']
    except KeyError:
        langue = None
    if langue is not None:
        return langue
    return request.accept_languages.best_match(['fr_CA', 'en_CA'])

def get_date():
    date = datetime.now()
    date = dates.format_date(date, locale=get_locale())
    return date

def hachage(value):
    empreinte = hashlib.sha256(value.encode()).hexdigest()
    return empreinte

def verifierSiListeExistante():
    if ("utilisateur" in session):
        nb = len(items)
        if nb < 1:
            nb = 0
    else:
        nb = 0
    
    return nb
    # return ItemModel.get_nbItems()

@app.route('/')
def accueil():
    try:
        nbItems = verifierSiListeExistante()

        if ("utilisateur" not in session):
            region = request.args.get("region")
            if (region):
                region = region.replace("-", "_")
                session["langue"] = region
            else:
                session["langue"] = get_locale()

        if not request.cookies.get('cookie'):
            cookie = "rebonjour"
            resp = make_response(render_template('accueil.html', date=get_date(), nbItems=nbItems))

            expire_date = datetime.now()
            
            expire_date = expire_date + datetime.timedelta(days=1)

            resp.set_cookie('cookie', cookie, expires=expire_date)
            return resp
        else:
            cookie = request.cookies.get('cookie')
            return render_template('accueil.html', date=get_date(), cookie=cookie, nbItems=nbItems)

    except Exception as e:
        logging.error('Messages : ' + str(e))
        return render_template("page500.html"), 500
        

@app.route('/utilisateurs/creer-compte')
def creation_compte():
    try:
        return render_template('/utilisateurs/creer.html', date=get_date())
    except Exception as e:
        logging.error('Messages : ' + str(e))
        return render_template("page500.html"), 500


@app.route('/utilisateurs/creer-compte', methods=['POST'])
def creation_compte_post():
    try:
        identifiant = request.form.get('id')
        mot_de_passe = request.form.get('mot-passe')
        langue = request.form.get('langue')

        model = UtilisateurModel(identifiant, mot_de_passe, langue)
        messages = model.valider_creation()
        if len(messages) > 0:
            return render_template('/utilisateurs/creer.html', messages=messages, date=get_date())
        
        model.mot_de_passe = hachage(mot_de_passe)

        model.enregistrer()
        session["utilisateur"] = model.identifiant
        session["langue"] = model.langue
        return redirect(url_for('accueil'))
    except Exception as e:
        logging.error('Messages : ' + str(e))
        return render_template("page500.html"), 500


@app.route("/authentification/connexion")
def authentification():
    try:
        return render_template("authentification/authentification.html", date=get_date())
    except Exception as e:
        logging.error('Messages : ' + str(e))
        return render_template("page500.html"), 500


@app.route("/authentification/connexion", methods=["POST"])
def authentification_post():
    try:
        identifiant = request.form.get('id')
        mot_de_passe = request.form.get('mot-passe')

        langue = get_locale()

        if (mot_de_passe != ""):
            mot_de_passe = hachage(mot_de_passe)

        model = UtilisateurModel(identifiant, mot_de_passe, langue)
        messages = model.valider_authentification()
        if (len(messages) > 0):
            for messages in messages:
                flash(messages)
            return redirect(url_for("authentification"))

        langue = model.get_langue()
        model.langue = langue
        session["langue"] = model.langue
        session["utilisateur"] = model.identifiant
        return redirect(url_for("liste"))
    except Exception as e:
        logging.error('Messages : ' + str(e))
        return render_template("page500.html"), 500


@app.route("/authentification/deconnexion")
def deconnexion():
    try:
        flash('Vous vous êtes déconecté')
        session.pop('utilisateur', None)
        session.pop('langue', None)
        return redirect(url_for("authentification"))
    except Exception as e:
        logging.error('Messages : ' + str(e))
        return render_template("page500.html"), 500

# données static, car faut pas de BD
itemsFixe = ['0','patate',3.0]
itemsFixe2 = ['1','pomme',2.0]
itemsFixe3 = ['2','steak',1200.0]
itemsFixe4 = ['3','orange',8.3]
itemsFixe5 = ['4','chips',5.0]
itemsFixe6 = ['5','poulet',7.0]
items = [itemsFixe, itemsFixe2, itemsFixe3, itemsFixe4, itemsFixe5, itemsFixe6]
itemsID = [5]

@app.route('/liste')
def liste():
    try:
        itemsTempo2 = []
        # Utilisation de list, car pas de bd
        i = 0
        while i < len(items):
            itemsTempo = []
            quantite = items[i][2]
            quantite = numbers.format_decimal(quantite, locale=session['langue'])
            itemsTempo.append(items[i][0])
            itemsTempo.append(items[i][1])
            itemsTempo.append(str(quantite))
            itemsTempo2.append(itemsTempo)
            i = i + 1

        return render_template("items/liste.html", date=get_date(), items=itemsTempo2)
    except Exception as e:
        logging.error('Messages : ' + str(e))
        return render_template("page500.html"), 500

@app.route('/items/ajouter')
def creer_item():
    try:
        return render_template("items/creer.html", date=get_date())
    except Exception as e:
        logging.error('Messages : ' + str(e))
        return render_template("page500.html"), 500

@app.route('/items/ajouter', methods=['POST'])
def creer_item_post():
    try:
        description = str(request.form.get('description'))
        quantite = request.form.get('quantite')
        if (not quantite):
            quantite = 0.0

        model = ItemModel(description, quantite)

        messages = model.valider()
        if (len(messages) > 0):
            return render_template("items/creer.html", date=get_date(), messages=messages)

        # enregistrement sans bd...
        iid = itemsID[0]
        iid = iid + 1
        itemsID[0] = iid

        itemsFixeTempo = []
        itemsFixeTempo.append(str(iid))
        itemsFixeTempo.append(model.description)
        itemsFixeTempo.append(model.quantite)
        items.append(itemsFixeTempo)
        
        return redirect(url_for("liste"))
    except Exception as e:
        logging.error('Messages : ' + str(e))
        return render_template("page500.html"), 500

@app.route('/items/effacer/<int:id>')
def effacer_item(id):
    try:
        trouver = False
        i = 0
        while trouver == False:
            value = items[i][0]
            if int(value) == int(id):
                trouver = True
            else:
                i = i + 1

        del items[i]
        
        return redirect(url_for("liste"))
    except Exception as e:
        logging.error('Messages : ' + str(e))
        return render_template("page500.html"), 500

@app.errorhandler(500)
def page500(error):
  return render_template("page500.html"), 500


if __name__ == '__main__':
    app.run(debug=True)
