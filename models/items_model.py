import bd

class ItemModel:

    def __init__(self, description, quantite):
        self.description = description
        self.quantite = quantite

    def valider(self):
        messages = []
        if not self.description:
            messages.append("La description ne doit pas être vide")
            return messages
        try:
            float(self.quantite)
        except ValueError:
            messages.append("La quantite doit être un nombre")
            return messages
        return messages

    # def get_nbItems():
    #     try:
    #         nbItems = 0
    #         connexion = bd.obtenir_connexion()
    #         curseur = connexion.cursor()
    #         curseur.execute('SELECT * FROM produits')
    #         items = curseur.fetchall()

    #         if len(items) > 0:
    #             nbItems = len(items)
    #         else:
    #             nbItems = 0
    #         return nbItems
    #     except Exception as e:
    #         logging.error('Erreure! - ' + str(e))
    #     finally:
    #         connexion.close()
