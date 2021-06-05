import bd

class UtilisateurModel:

    def __init__(self, identifiant, mot_de_passe, langue):
        self.identifiant = identifiant
        self.mot_de_passe = mot_de_passe
        self.langue = langue

    def valider_creation(self):
        try:
            messages = []
            if (not self.identifiant or not self.mot_de_passe):
                messages.append("L'identifiant et le mot de passe ne doivent pas être vides")
            if (self.langue is None):
                messages.append("Il doit avoir une langue de sélectionner")
            connexion = bd.obtenir_connexion()
            curseur = connexion.cursor()
            curseur.execute('SELECT * FROM utilisateurs WHERE identifiant = %s', (self.identifiant,))
            user = curseur.fetchone()
            if user is not None:
                messages.append("Un utilisateur existe déjà avec cet identifiant")

            if (not self.langue or self.langue == ""):
                self.langue = "fr_CA"
            
            return messages
        except Exception as e:
            logging.error('Messages : ' + str(e))
        finally:
            connexion.close()

    def valider_authentification(self):
        try:
            messages = []
            if (not self.identifiant or not self.mot_de_passe):
                messages.append("L'identifiant et le mot de passe ne doivent pas être vides")

            connexion = bd.obtenir_connexion()
            curseur = connexion.cursor()
            curseur.execute('SELECT * FROM utilisateurs WHERE identifiant = %s', (self.identifiant,))
            user = curseur.fetchone()
            if (user is None):
                messages.append("Combinaison identifiant/mot de passe invalide")
                return messages

            if (str(user[1]) != str(self.mot_de_passe) or str(user[0]) != str(self.identifiant)):
                messages.append("Combinaison identifiant/mot de passe invalide")
                return messages

            return messages
        except Exception as e:
            logging.error('Messages : ' + str(e))
        finally:
            connexion.close()

    def enregistrer(self):
        try:
            connexion = bd.obtenir_connexion()
            curseur = connexion.cursor()
            curseur.execute('INSERT INTO utilisateurs VALUEs (%s, %s, 0, %s)', (self.identifiant, self.mot_de_passe, self.langue))
            connexion.commit()
        except Exception as e:
            logging.error('Messages : ' + str(e))
        finally:
            connexion.close()

    def get_langue(self):
        try:
            connexion = bd.obtenir_connexion()
            curseur = connexion.cursor()
            curseur.execute('SELECT * FROM utilisateurs WHERE identifiant = %s', (self.identifiant,))
            user = curseur.fetchone()
            if (user is None):
                return "Aucune"
            return user[3]
        except Exception as e:
            logging.error('Messages : ' + str(e))
        finally:
            connexion.close()

