import psycopg2
from postgis.psycopg import register
from psycopg2 import pool
import config

connections = None


def set_connection(fn):
    def wrapped(*args, **kwargs):
        global connections
        if not connections:
            init_connections()
        connection = connections.getconn()
        return fn(connection, *args, **kwargs)
    return wrapped


OOM_HINT = """
Vérifiez que vous n'avez pas oublié une condition dans une jointure.
Si le problème persite, essayez de relancer l'exécuteur de requêtes.
"""

#########################################################
# Cette fonction exécute sur la base
# la requête passée en paramètre
#########################################################
@set_connection
def execute_query(*args, **kwargs):
    try:
        # On récupère un objet curseur qui permet de parcourir
        # l'ensemble résultat à la manière d'un itérateur.
        connection, query, parameters = args[0], args[1], args[2:]
        cursor = connection.cursor()
        print(connection, query)

        # On exécute la requête ici.
        cursor.execute(query, parameters)

        # Après exécution de la requête, on récupère la réponse du SGBD
        # et on renvoie le tout.
        return (cursor, connection)

    except MemoryError:
        print("""
Pas assez de mémoire pour exécuter la requête SQL.
{}""".format(OOM_HINT))
        raise
    except psycopg2.Error as e:
        if len(e.args) > 0:
            msg = e.args[0]
        else:
            msg = ("""
Erreur pendant l'exécution de la requête.
Cette erreur peut se produire s'il n'y a pas assez de mémoire.
""".format(OOM_HINT))
        print(msg)
        raise


#########################################################
# Cette fonction exécute sur la base
# la requête de mise-à-jour passée en paramètre
#########################################################
@set_connection
def execute_update(connection, query):
    try:
        # On récupère un objet curseur qui permet de parcourir
        # l'ensemble résultat à la manière d'un itérateur.
        cursor = connection.cursor()

        # On exécute la requête ici.
        cursor.execute(query)

    except psycopg2.Error as e:
        print("Erreur d'exécution de la requête - %s:" % e.args[0])


def commit(connection):
    try:
        connection.commit()

    except psycopg2.Error as e:
        print("Erreur d'exécution de la requête - %s:" % e.args[0])


#########################################################
# Cette fonction initialise la connexion à la base
#########################################################
def init_connections():
    global connections

    try:
        connections = pool.ThreadedConnectionPool(
            config.MIN_THREADS,
            config.MAX_THREADS,
            dbname=config.DATABASE,
            user=config.USER,
            password=config.PASSWORD,
            host=config.HOSTNAME
        )
        #register(connection)
    except psycopg2.Error as e:
        print("Database connexion error - %s:" % e.args[0])
        close_connections()


#########################################################
# Cette fonction ferme la connexion à la base
#########################################################
def close_connection(connection):
    global connections
    print(connection)
    if connection:
        connections.putconn(connection)
        
#########################################################
# Cette fonction ferme toutes les connexions à la base
#########################################################
def close_connections():
    global connections

    if connections:
        connections.closeall()
        connections = None
