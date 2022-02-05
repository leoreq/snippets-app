import logging, argparse, psycopg2

#Set the log output file, and the log level

logging.basicConfig(filename="snippets.log",level=logging.DEBUG)

logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets2")
logging.debug("Database Conection Established")

def put(name,snippet):
    """
    Store a snippet with an associated name.

    Returns the name and the snippet
    """
    logging.info("Storing snippet {!r},{!r}".format(name,snippet))
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

   

    return name,snippet

def get(name):
    """Retrieve the snippet with the given name.

    If there is no such snippet, return '404: Snippet not found'.

    Returns the snippet.
    """
    logging.info("Retrieving snippet {!r}".format(name))
    cursor=connection.cursor()
    command="select message from snippets where keyword =%s"
    cursor.execute(command,(name,))
    
    row=cursor.fetchone()
    connection.commit()

    
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
    cursor=connection.cursor()

    command="select keyword from snippets where keyword =%s"
    cursor.execute(command,(name,))
    row=cursor.fetchone()
    connection.commit()
    if not row:
        #No snippet was foud  with the name
        logging.debug("No record was found in database with {!r} name".format(name))
        message="404: Snippet not found"
        return message

    command="delete from snippets where keyword =%s"
    cursor.execute(command,(name,))
    logging.debug("Snippet with name = {!r} was found and deleted".format(name))
    message="Snippet with name = {!r} was found and deleted".format(name)
    connection.commit()

    logging.debug("Passing arguments to main function")
    return message

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

    #Subparser for the get command
    logging.debug("Constructing get subparser")
    put_parser=subparsers.add_parser("get",help="Retrieve a snippet")
    put_parser.add_argument("name",help="Name of the snippet that will be retrieved")

    #Subparser for the delete command
    logging.debug("Constructing delete subparser")
    delete_parser=subparsers.add_parser("delete",help="Delete a snippet")
    delete_parser.add_argument("name",help="Name of the snippet that will be deleted")

    arguments=parser.parse_args()
    #Convert parsed arguments from Namespace to Dictionary
    arguments=vars(arguments)
    command=arguments.pop("command")

    if command=="put":
        name,snippet=put(**arguments)
        print("Stored {!r} as {!r}".format(snippet,name))
    elif command=="get":
        snippet=get(**arguments)
        print("Retrieved snippet:{!r}".format(snippet))
    elif command=="delete":
        message2=delete(**arguments)
        print("{!r}".format(message2))

if __name__=="__main__":
    main()
