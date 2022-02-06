import logging, argparse, psycopg2

#Set the log output file, and the log level

logging.basicConfig(filename="snippets.log",level=logging.DEBUG)

logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets2")
logging.debug("Database Conection Established")

def put(name,snippet,hidden_status):
    """
    Store a snippet with an associated name.

    Returns the name and the snippet
    """
    logging.info("Storing snippet {!r},{!r},{!r}".format(name,snippet,hidden_status))
    with connection,connection.cursor() as cursor:
        try:
            cursor.execute("insert into snippets values (%s,%s,%s)",(name,snippet,hidden_status))
            logging.debug("Snippet stored succesfully")
        except psycopg2.IntegrityError as e:
            connection.rollback()
            cursor.execute("update snippets set message =%s , hidden_status = %s where keyword=%s",(snippet,hidden_status,name))
            logging.debug("Snippet updated succesfully")

    """
    cursor=connection.cursor()
    try:
        command="insert into snippets values (%s,%s)"
        cursor.execute(command,(name,snippet))
        logging.debug("Snippet stored succesfully")
    except psycopg2.IntegrityError as e:
        connection.rollback()
        command="update snippets set message =%s where keyword=%s"
        cursor.execute(command,(snippet,name))
        logging.debug("Snippet updated succesfully")
    connection.commit()
    """

   

    return name,snippet,hidden_status

def get(name):
    """Retrieve the snippet with the given name.

    If there is no such snippet, return '404: Snippet not found'.

    Returns the snippet.
    """
    logging.info("Retrieving snippet {!r}".format(name))
    with connection,connection.cursor() as cursor:
        cursor.execute("select message from snippets where keyword =%s",(name,))
        row=cursor.fetchone()


    
    if not row:
        #No snippet was foud  with the name
        logging.debug("No snippet was found in database with {!r} name".format(name))
        return "404: Snippet not found"

    logging.debug("Snippet {!r}  retrieved succesfully".format(row[0]))
    return row[0]

def delete(name):
    """
    Delete the snippet with a given name.

    If there is no such snippet, reutrn '404: Snippet not found'.

    Return 'Snippet Deleted Succesfuly'
    """
    logging.info("Deleting snippet {!r}".format(name))
    with connection, connection.cursor() as cursor:
        cursor.execute("select keyword from snippets where keyword =%s",(name,))
        row=cursor.fetchone()

        if not row:
            #No snippet was foud  with the name
            logging.debug("No record was found in database with {!r} name".format(name))
            message="404: Snippet not found"
            return message
        
        cursor.execute("delete from snippets where keyword =%s",(name,))
        logging.debug("Snippet with name = {!r} was found and deleted".format(name))
        message="Snippet with name = {!r} was found and deleted".format(name)
        logging.debug("Passing arguments to main function")
    return message

def catalog(catalog_type):
    """
    This function will retrieve all items from the catalog and display them 
    """
    logging.info("Retrieving catalog of all names")
    with connection, connection.cursor() as cursor:
        if catalog_type == 'nombres':
            cursor.execute("select keyword from snippets order by keyword",())
            rows=cursor.fetchall()
            return rows,catalog_type
        elif catalog_type == 'completo':
            cursor.execute("select * from snippets order by keyword",())
            rows=cursor.fetchall()
    return rows,catalog_type

def search(name_string):
    """
    This function will retrieve all items from the catalog that match the name_string name
    """
    logging.info("Retrieving catalog of all names that match search function")
    name_string="%"+name_string+"%"
    with connection, connection.cursor() as cursor:
        #print("select keyword from snippets where keyword like {!r} order by keyword".format(name_string))
        cursor.execute("select keyword from snippets where keyword like %s order by keyword",(name_string,))
        rows=cursor.fetchall()
    return rows

def update(name,snippet):
    """
    Update a snippet with an associated name.

    If there is no such a snippet, then reutrn '404: Snippet not found'.

    Returns the name and the snippet
    """
    logging.error("FIXME: unimplemented - update({!r},{!r})".format(name,snippet))

    return name,snippet

def main():
    """Main Function"""
    logging.info("Constructing Parser")
    parser =argparse.ArgumentParser(description="Store and retrieve snipets of text")

    subparsers=parser.add_subparsers(dest="command",help="Available Commands")

    #Subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser=subparsers.add_parser("put",help="Store a snippet")
    put_parser.add_argument("name",help="Name of the snippet")
    put_parser.add_argument("snippet",help="snippet text")
    put_parser.add_argument("-i","--hidden_status", action="store_true",help="will make sure the string is hidden")

    #Subparser for the get command
    logging.debug("Constructing get subparser")
    get_parser=subparsers.add_parser("get",help="Retrieve a snippet")
    get_parser.add_argument("name",help="Name of the snippet that will be retrieved")


    #Subparser for the delete command
    logging.debug("Constructing delete subparser")
    delete_parser=subparsers.add_parser("delete",help="Delete a snippet")
    delete_parser.add_argument("name",help="Name of the snippet that will be deleted")

    #Subparser for the catalog command
    logging.debug("Constructing catalog subparser")
    catalog_parser=subparsers.add_parser("catalog",help="Display a catalog of snippets names")
    catalog_parser.add_argument('-t','--catalog_type', action='store', choices=['nombres', 'completo'],help="Elige la forma de mostrar el catalogo")

    #Subparser for the search command
    logging.debug("Constructing search subparser")
    search_parser=subparsers.add_parser("search",help="Display a list of snippet names that match the search name_string")
    search_parser.add_argument("name_string",help="Search term that will be retrieved")
    

    arguments=parser.parse_args()
    #Convert parsed arguments from Namespace to Dictionary
    arguments=vars(arguments)
    command=arguments.pop("command")
    
    if command=="put":
        name,snippet,hidden_status=put(**arguments)
        print("Stored {!r} as {!r} with status as {!r}".format(snippet,name,hidden_status))
    elif command=="get":
        snippet=get(**arguments)
        print("Retrieved snippet:{!r}".format(snippet))
    elif command=="delete":
        message2=delete(**arguments)
        print("{!r}".format(message2))
    elif command=="catalog":
        rows2,catalog_type=catalog(**arguments)
        list_items=[]
        if catalog_type=='nombres':
            for item in rows2:
                list_items.append(item[0])
        else:
            for item in rows2:
                list_items.append(item)
        print("\n")
        print("The following is the catalog of items: \n")
        print(" =========================================\n")
        for i in list_items:
            print("{!r}".format(i))
        print("\n")
        print(" =========================================\n")
        print("Use the get() function to retrieve the list ... \n")
        
    elif command=="search":
        rows2=search(**arguments)
        list_items=[]
        for item in rows2:
            list_items.append(item[0])
        print(" =========================================\n")
        print("The following is the list of items that match the search term: \n")
        print("{!r} \n ".format(list_items))
        print("Use the get() function to retrieve the snippet for each name \n")
        print(" =========================================")

if __name__=="__main__":
    main()
