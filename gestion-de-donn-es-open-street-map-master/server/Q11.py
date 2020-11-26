import database as db
from sys import argv


def search(keywords):
    """
        Serch for a given keyword in a node list
    """
    raw_query =\
        "SELECT tags->'name', ST_X(geom), ST_Y(geom), ST_Z(geom) " +\
        "FROM Nodes " + \
        "WHERE tags->'name' LIKE %s "

    # Pour chaque keyword passé en paramètre, on rajoute un "OR" à la recherche
    complete_query = raw_query + \
        ''.join(list(map(lambda _: " OR tags->'name' LIKE %s ", keywords[1:])))

    # Exec
    cursor = db.execute_query(
        complete_query,
        *keywords
    )

    # Affichage
    print("Searched name \tX_coord\tY_coord\tZ_coord\t".expandtabs(30))
    for row in cursor:
        print('\t'.join([str(el) for el in row]).expandtabs(30))

    cursor.close()
    db.close_connection()


def main():
    if len(argv) < 2:
        print("Pas assez d'arguments")
    search(argv[1:])


main()
