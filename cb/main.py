'''
Main file that includes all functions in appropriate order
'''
from config import *
from time import sleep
import connection
import modellists
import run

if __name__ == '__main__':
    # Main section
    # Set logging
    Logging()
    # Create directories
    Remove_folder(Script_folder)
    Preconditions(Script_folder)
    Preconditions(Video_folder)
    Preconditions(Converted_folder)
    # Connecting to server
    client_factory = connection.ClientFactory()
    client = connection.Connection(client_factory)
    # Get the models list and create main list
    Models_list_store = modellists.Models_list(client)
    # Select models for recording according to wishlist
    Selected_models = modellists.Select_models(Models_list_store)
    # Parse page for each model and creatr links for rtmpdump
    modellists.Get_links(client, Selected_models)
    # Run scripts
    run.Run_scripts()
    # First delay before loop
    logging.info('Waiting for %d seconds' % Time_delay)
    sleep(Time_delay)


    while True:
        # Reassign updated main models list
        # Connecting to server
        try:
            client = connection.Connection(client_factory)
        except KeyError:
            # Sometimes missing CSRF token, which raises KeyError. Just go
            # again if this happens.
            continue

        #Models_list_store = Compare_lists(Models_list_store, Models_list(client))
        logging.info(str(len(Models_list_store)) +
                     ' Models in the list before checking: ' + str(Models_list_store))
        # Models_list_store_new is a list of new models
        Models_list_store = modellists.Compare_lists(
            modellists.Models_list(client), modellists.Rtmpdump_models())
        logging.info('[Loop]List of new models for adding: ' + str(Models_list_store))
        Selected_models = modellists.Select_models(Models_list_store)
        # Remove old and create new script folder if we have someone to add
        if len(Selected_models) != 0:
            Remove_folder(Script_folder)
            Preconditions(Script_folder)
            # Parse page for each model and creatr links for rtmpdump
            modellists.Get_links(client, Selected_models)
            # Run scripts
            run.Run_scripts()
        logging.info('[Loop]Model list after check looks like: %d models:\n %s \n and models currently being recorded are:\n %s' % (
            len(Models_list_store), str(Models_list_store), str(modellists.Rtmpdump_models())))
        logging.info('[Sleep] Waiting for next check (%d seconds)' % Time_delay)
        sleep(Time_delay)
