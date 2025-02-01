##############################################
# Author: Thomas Halsema
# Description:
#    This program stores information about Oracle Wallets in a centralized repository database. Users can create, update, delete, and view the information stored.
#    This program also allows users to generate Oracle Wallets based on the information stored. It pulls usernames/passwords from 1password.com and loads them into the Wallets as defined in the repository.
#    The program also allows users to deploy generated Wallets to remote servers/directories to be used by Oracle clients.
#

# Imports
from colorama import Fore
from datetime import datetime
from pathlib import Path
import configparser
import json
import oracledb
import paramiko
import secrets
import shutil
import subprocess
import time

# Global Variables and values from walman.conf
config = configparser.ConfigParser()
config.read('walman.conf')
local_wallets_directory = config['DEFAULTS']['local_wallets_directory']
walman_vault = config['DEFAULTS']['walman_vault']
walman_tns_name = config['DEFAULTS']['walman_tns_name']
search_string = ""

def confirm_yes_no(prompt_in: str) -> bool:

    # Prompt for, validate, and act on user input (Yes or No)
    reply_valid = False
    while reply_valid == False:
        reply = input(f"{prompt_in} [y/n]: ")
        reply = reply.lower().strip()
        reply_valid = True

        if reply == "y":
            return True
        elif reply == "n":
            return False
        else:           # Invalid response
            reply_valid = False
            print(f"{Fore.RED}ERROR:{Fore.RESET} Invalid Response: {reply}\n")

def cred_create(cred_name: str, cred_db_host_name: str, cred_db_port: int,  cred_db_service: str, cred_passmgr_entry: str) -> bool:

    # Attempt to insert the provided data into the database. If it fails, print the error code/message and return the user to the calling menu.
    try:
        cursor = walmandb_conn.cursor()
        cursor.execute("""INSERT INTO walman.credentials (cred_name, cred_db_host_name, cred_db_port, cred_db_service, cred_passmgr_entry)
                                            VALUES  (:cred_name, :cred_db_host_name, :cred_db_port, :cred_db_service, :cred_passmgr_entry)""",
                                                                [cred_name, cred_db_host_name, cred_db_port, cred_db_service, cred_passmgr_entry])
        cursor.close()
    except oracledb.Error as e:
        error_obj, = e.args
        print(f"{Fore.RED}ERROR:{Fore.RESET}{error_obj.message}")
        return False

    print(f"{Fore.GREEN}SUCCESS:{Fore.RESET} Created Credential {Fore.YELLOW}[{cred_name}]{Fore.RESET}")
    return True

def cred_modify(cred_id: int, cred_name: str, cred_db_host_name: str, cred_db_port: int,  cred_db_service: str, cred_passmgr_entry: str) -> bool:

    # Attempt to update a record in the database. If it fails, print the error code/message and return the user to the calling menu.
    try:
        cursor = walmandb_conn.cursor()
        cursor.execute("""UPDATE walman.credentials
                                        SET     cred_name = :cred_name,
                                                     cred_db_host_name = :cred_db_host_name,
                                                     cred_db_port = :cred_db_port,
                                                     cred_db_service = :cred_db_service,
                                                     cred_passmgr_entry = :cred_passmgr_entry
                                        WHERE   cred_id = :cred_id""", [cred_name, cred_db_host_name, cred_db_port, cred_db_service, cred_passmgr_entry, cred_id])
        walmandb_conn.commit()
        cursor.close()
    except oracledb.Error as e:
        error_obj, = e.args
        print(f"{Fore.RED}ERROR:{Fore.RESET}{error_obj.message}")
        return False

    print(f"{Fore.GREEN}SUCCESS:{Fore.RESET} Modified Credential {Fore.YELLOW}[{cred_name}]{Fore.RESET}")
    return True

def cred_delete(cred_id: int, cred_name: str):

    # Attempt to delete a record in the database. If it fails, print the error code/message and return the user to the calling menu.
    try:
        cursor = walmandb_conn.cursor()
        cursor.execute("DELETE FROM walman.credentials WHERE cred_id = :cred_id", [cred_id])
        cursor.close()
    except oracledb.Error as e:
        error_obj, = e.args
        print(f"{Fore.RED}ERROR:{Fore.RESET}{error_obj.message}")
    else:
        print(f"{Fore.GREEN}SUCCESS:{Fore.RESET} Deleted Credential {Fore.YELLOW}[{cred_name}]{Fore.RESET}")

def column_lengths(table_in: list[tuple]) -> list:
    # Take in a list of tuples (i.e. a table) and return a list of the lengths of each column, where the column length is equal to the length of the longest value in that column.

    return_list = [0] * (len(table_in[0]) + 1)

    for row in table_in:
        for index, val in enumerate(row):
            return_list[index] = max(return_list[index], len(val))

    return return_list

def disp_menu_main():

    # Display menu header and options
    print("")
    print("#########################################################################################")
    print("##############" + "WALMAN - MAIN MENU".center(61) + "##############")
    print("#########################################################################################")
    print("")
    print("1) Wallets - Create Wallet")
    print("2) Wallets - View/Manage Existing Wallet")
    print("3) Credentials - Manage Credentials")
    print("q) Quit")

    # Prompt for, validate, and act on user input
    reply_valid = False
    while reply_valid == False:
        reply = input("Select Option: ")
        reply = reply.lower().strip()
        reply_valid = True

        if reply == "1":                # 1) Wallet - Create Wallet
            disp_menu_wallet_create()
        elif reply == "2":              # 2) Wallet - Modify Existing Wallet
            disp_menu_wallet_manage_modwallet_select()
        elif reply == "3":              # 3) Credentials - Manage Credentials
            disp_menu_cred_manage()
        elif reply == "q":              # q) Quit
            program_exit()
        else:                               # Invalid response
            reply_valid = False
            print(f"{Fore.RED}ERROR:{Fore.RESET} Invalid Response: {reply}\n")

def disp_menu_cred_delete(**kwargs):

    # Populate variables from arguments set by user
    cred_id = kwargs.get("cred_id")
    cred_name = kwargs.get("cred_name")
    cred_db_host_name = kwargs.get("cred_db_host_name")
    cred_db_port = kwargs.get("cred_db_port")
    cred_db_service = kwargs.get("cred_db_service")
    cred_passmgr_entry = kwargs.get("cred_passmgr_entry")

    # Display menu header
    print("")
    print("#########################################################################################")
    print("##############" + "WALMAN - DELETE CREDENTIAL".center(61) + "##############")
    print("#########################################################################################")
    print("")

    # Display read-only info about Credential to be deleted
    print(f"{Fore.BLUE}Details for the Credential to be deleted:{Fore.RESET}")
    print(f"Credential Name: {Fore.YELLOW}[{cred_name}]{Fore.RESET}")
    print(f"DB Host Name: {Fore.YELLOW}[{cred_db_host_name}]{Fore.RESET}")
    print(f"DB Port: {Fore.YELLOW}[{cred_db_port}]{Fore.RESET}")
    print(f"DB Service: {Fore.YELLOW}[{cred_db_service}]{Fore.RESET}")
    print(f"Passmgr Entry: {Fore.YELLOW}[{cred_passmgr_entry}]{Fore.RESET}")
    print("")

     # Query the WALMANDB for Wallets from which the deleted Credential would be removed
    cursor = walmandb_conn.cursor()
    cursor.execute("""SELECT    w.wallet_passmgr_entry,
                                                         NVL(w.wallet_description, 'None'),
                                                         NVL(w.wallet_local_directory, 'None')
                                    FROM    walman.wallets w,
                                                    walman.wallet_credentials wc
                                    WHERE    w.wallet_id = wc.wallet_id
                                    AND           wc.cred_id = :cred_id
                                    ORDER BY 1""", [cred_id])
    query_results = cursor.fetchall()
    cursor.close()

    # Display Wallets which contain this Credential
    print(f"\n{Fore.BLUE}This Credential would be removed from these Wallets:{Fore.RESET}\n")
    headers = ("Wallet Name", "Wallet Description", "Wallet Local Directory")
    print_table(query_results, headers)
    print("")

    # Prompt the user to verify if the Credential should be deleted
    if confirm_yes_no("Are you sure you want to delete the above Credential and remove it from all Wallets?"):     # Yes
        delete_res = cred_delete(cred_id, cred_name)
    else:                                                                                                                                                                                       # No
        print(f"{Fore.BLUE}INFO:{Fore.RESET} User selected to not delete the Credential. \n")
    disp_menu_cred_manage()

def disp_menu_cred_manage():
    print("")
    print("#########################################################################################")
    print("##############" + "WALMAN - MANAGE CREDENTIALS".center(61) + "##############")
    print("#########################################################################################")
    print("")
    print("1) Create Credential")
    print("2) Modify Credential")
    print("3) Delete Credential")
    print("m) Return to the Main Menu")
    print("q) Quit")

    # Prompt for, validate, and act on user input
    reply_valid = False
    while reply_valid == False:
        reply = input("Select Option: ")
        reply = reply.lower().strip()
        reply_valid = True

        if reply == "1":                # 1) Create Credential
            disp_menu_cred_modify(new = True)
        elif reply == "2":             # 2) Modify Credential
            disp_menu_cred_modify_modcred_select(delete = False)
        elif reply == "3":             # 3) Delete Credential
            disp_menu_cred_modify_modcred_select(delete = True)
        elif reply == "m":            # m) Return to the Main Menu
            disp_menu_main()
        elif reply == "q":             # q) Quit
            program_exit()
        else:                               # Invalid response
            reply_valid = False
            print(f"{Fore.RED}ERROR:{Fore.RESET} Invalid Response: {reply}\n")

def disp_menu_cred_modify(new: bool, **kwargs):

    # Populate variables from arguments set by user or assign default values
    cred_id = kwargs.get("cred_id", "")
    cred_name = kwargs.get("cred_name", "")
    cred_db_host_name = kwargs.get("cred_db_host_name", "")
    cred_db_port = kwargs.get("cred_db_port", 1521)
    cred_db_service = kwargs.get("cred_db_service", "")
    cred_passmgr_entry = kwargs.get("cred_passmgr_entry", "")

    if new == True:
        mod_word = "CREATE"
    else:
        mod_word = "MODIFY"

    # Display menu header and options
    print("")
    print("#########################################################################################")
    print("##############" + f"WALMAN -  {mod_word} CREDENTIAL".center(61) + "##############")
    print("#########################################################################################")
    print("")
    print(f"1) Set Credential Name {Fore.YELLOW}[{cred_name}]{Fore.RESET}")
    print(f"2) Set Credential DB Host Name {Fore.YELLOW}[{cred_db_host_name}]{Fore.RESET}")
    print(f"3) Set Credential DB Port {Fore.YELLOW}[{cred_db_port}]{Fore.RESET}")
    print(f"4) Set Credential DB Service Name {Fore.YELLOW}[{cred_db_service}]{Fore.RESET}")
    print(f"5) Select Credential Passmgr Entry {Fore.YELLOW}[{cred_passmgr_entry}]{Fore.RESET}")
    print(f"c) {Fore.BLUE}Confirm Choices{Fore.RESET} - {mod_word.capitalize()} Credential")
    print("p) Return to the Previous Menu")
    print("m) Return to the Main Menu")
    print("q) Quit")

    # Prompt for, validate, and act on user input
    reply_valid = False
    while reply_valid == False:
        reply = input("Select parameter to set or action to perform: ")
        reply = reply.lower().strip()
        reply_valid = True

        if reply == "1":                  # 1) Set Credential Name
            cred_name = input("Enter the Name for the Credential: ").upper().strip()
        elif reply == "2":               # 2) Set Credential DB Host Name
            cred_db_host_name = input("Enter the DB Host Name for the Credential: ").strip()
        elif reply == "3":               # 3) Set Credential DB Port
                db_port_response = input("Enter the DB Port for the Credential: ").strip()
                if db_port_response.isdecimal():
                    cred_db_port = int(db_port_response)
                else:
                    print(f"{Fore.RED}ERROR:{Fore.RESET} Invalid Response (must be integer): {db_port_response}\n")
        elif reply == "4":               # 4) Set Credential DB Service Name
            cred_db_service = input("Enter the DB Service for the Credential: ").strip()
        elif reply == "5":               # 5) Select Credential Passmgr Entry
            cred_passmgr_entry = disp_menu_cred_passmgr_select(f"{mod_word} CREDENTIAL")
        elif reply == "c":               # c) Confirm Choices
            if confirm_yes_no("Are the values entered above correct?"):         # Yes
                if new == True:
                    reply_valid = cred_create(cred_name = cred_name,
                                                                  cred_db_host_name = cred_db_host_name,
                                                                  cred_db_port = cred_db_port,
                                                                  cred_db_service = cred_db_service,
                                                                  cred_passmgr_entry = cred_passmgr_entry)
                else:
                    reply_valid =  cred_modify(cred_id = cred_id,
                                                                    cred_name = cred_name,
                                                                    cred_db_host_name = cred_db_host_name,
                                                                    cred_db_port = cred_db_port,
                                                                    cred_db_service = cred_db_service,
                                                                    cred_passmgr_entry = cred_passmgr_entry)
            else:                                                                                                        # No
                print(f"{Fore.BLUE}INFO:{Fore.RESET} User selected to not {mod_word.lower()} the Credential. \n")
                reply_valid = False
        elif reply == "p":               # p) Return to the Previous Menu
            disp_menu_cred_manage()
        elif reply == "m":              # m) Return to the Main Menu
            disp_menu_main()
        elif reply == "q":               # q) Quit
            program_exit()
        else:                                # Invalid response
            reply_valid = False
            print(f"{Fore.RED}ERROR:{Fore.RESET} Invalid Response: {reply}\n")

        if (reply.isdecimal() and int(reply) >= 1 and int(reply) <=5) or reply == "c":
            if reply == "c":
                new = False
            disp_menu_cred_modify(new = new,
                                                         cred_id = cred_id,
                                                         cred_name = cred_name,
                                                         cred_db_host_name = cred_db_host_name,
                                                         cred_db_port = cred_db_port,
                                                         cred_db_service = cred_db_service,
                                                         cred_passmgr_entry = cred_passmgr_entry)
    disp_menu_cred_manage()

def disp_menu_cred_modify_modcred_select(delete: bool):

    if delete == True:
        mod_word = "DELETE"
    else:
        mod_word = "MODIFY"

    # Display menu header
    print("")
    print("#########################################################################################")
    print("##############" + f"WALMAN - {mod_word} CREDENTIAL - SELECT CREDENTIAL".center(61) + "##############")
    print("#########################################################################################")
    print("")

    reply_valid = False
    while reply_valid == False:
        # Prompt the user for a SEARCH_STRING to use to narrow the search for entries in the CREDENTIALS table:
        print("")
        search_string = ""
        search_string = input("Enter the Search String to be used to find the Credential: ")

        # Query the WALMANDB for Credentials with a name containing the search_string
        cursor = walmandb_conn.cursor()
        cursor.execute("""SELECT    c.cred_id,
                                                            c.cred_name,
                                                            c.cred_db_host_name,
                                                            c.cred_db_port,
                                                            c.cred_db_service,
                                                            c.cred_passmgr_entry
                                        FROM    walman.credentials c
                                        WHERE   TRIM(LOWER(c.cred_name)) LIKE TRIM(LOWER('%' || :search_string || '%'))
                                        ORDER BY 2""", [search_string])
        query_results = cursor.fetchall()
        cursor.close()

        if len(query_results) == 0:
            print(f"{Fore.RED}ERROR:{Fore.RESET} No Credentials found for the current Search String. To see all Credentials, respond with blank when prompted for Search String.")
        else:
            reply_valid = True

    # Display query results as dynamic menu options
    for i in range(len(query_results)):
        print(str(i+1) + ") " + str(query_results[i][1]))
    # Display static menu options
    print(f"s) {Fore.BLUE}Change Credential Search String: {Fore.YELLOW}[{search_string}]{Fore.RESET}")
    print("p) Return to the Previous Menu")
    print("m) Return to the Main Menu")
    print("q) Quit")

    # Prompt for, validate, and act on user input
    reply_valid = False
    while reply_valid == False:
        reply = input("Select Credential or navigation option: ")
        reply = reply.lower().strip()
        reply_valid = True

        if reply.isdecimal() and int(reply) > 0 and int(reply) <= len(query_results):           # Valid dynamic menu option
            if delete == True:
                disp_menu_cred_delete(cred_id = query_results[int(reply)-1][0],
                                                            cred_name = query_results[int(reply)-1][1],
                                                            cred_db_host_name = query_results[int(reply)-1][2],
                                                            cred_db_port = query_results[int(reply)-1][3],
                                                            cred_db_service = query_results[int(reply)-1][4],
                                                            cred_passmgr_entry = query_results[int(reply)-1][5])
            else:
                disp_menu_cred_modify(new = False,
                                                             cred_id = query_results[int(reply)-1][0],
                                                             cred_name = query_results[int(reply)-1][1],
                                                             cred_db_host_name = query_results[int(reply)-1][2],
                                                             cred_db_port = query_results[int(reply)-1][3],
                                                             cred_db_service = query_results[int(reply)-1][4],
                                                             cred_passmgr_entry = query_results[int(reply)-1][5])
        elif reply == "s":                       # s) Change Credential Search String
            disp_menu_cred_modify_modcred_select(delete = delete)
        elif reply == "p":                       # p) Return to Previous Menu
            disp_menu_cred_manage()
        elif reply == "m":                      # m) Return to the Main Menu
            disp_menu_main()
        elif reply == "q":                       # q) Quit
            program_exit()
        else:                                          # Invalid Response
            reply_valid = False
            print(f"{Fore.RED}ERROR:{Fore.RESET} Invalid Reponse: {reply}\n")

def disp_menu_cred_passmgr_select(heading: str) -> str:

    # Display menu header
    print("")
    print("#########################################################################################")
    print("##############" + f"WALMAN - {heading} - SELECT PASSMGR ENTRY".center(61) + "##############")
    print("#########################################################################################")
    print("")

    # Query the Passmgr for Oracle DB usernames
    search_results = passmgr_search("oracle", True, "")

    # Display query results as dynamic menu options
    for i, result in enumerate(search_results):
        print(str(i+1) + ") " + result["title"])
    # Display static menu options
    print(f"s) {Fore.BLUE}Change Passmgr Entry Search String: {Fore.YELLOW}[{search_string}]{Fore.RESET}")
    print("p) Return to the Previous Menu")
    print("m) Return to the Main Menu")
    print("q) Quit")

    # Prompt for, validate, and act on user input
    reply_valid = False
    while reply_valid == False:
        reply = input("Select Passmgr Entry or navigation option: ")
        reply = reply.lower().strip()
        reply_valid = True

        if reply.isdecimal() and int(reply) > 0 and int(reply) <= len(search_results):           # Valid dynamic menu option
            return search_results[int(reply)-1]["title"]
        elif reply == "s":                       # s) Change Passmgr Search String
            disp_menu_cred_passmgr_select(heading)
        elif reply == "p":                       # p) Go back to function that called this function
            return ""
        elif reply == "m":                      # m) Return to the Main Menu
            disp_menu_main()
        elif reply == "q":                       # q) Quit
            program_exit()
        else:                                        # Invalid Response
            reply_valid = False
            print(f"{Fore.RED}ERROR:{Fore.RESET} Invalid Reponse: {reply}\n")

    return ""

def disp_menu_wallet_create():

    # Display menu header
    print("")
    print("#########################################################################################")
    print("##############" + f"WALMAN - CREATE WALLET".center(61) + "##############")
    print("#########################################################################################")
    print("")

    # Prompt for wallet name and description
    wallet_name = input("Enter a name for the Wallet: WALLET - ")
    wallet_name = "WALLET - " + wallet_name.strip()
    wallet_description =  input("Enter a description for the Wallet: ")
    wallet_description = wallet_description.strip()

    # Show entered information for confirmation
    print("")
    print(f"{Fore.BLUE}INFO:{Fore.RESET} The Wallet will be created in Walman and the Passmgr with the following information:")
    print(f"Wallet Name / Passmgr Entry: {Fore.YELLOW}[{wallet_name}]{Fore.RESET}")
    print(f"Wallet Description: {Fore.YELLOW}[{wallet_description}]{Fore.RESET}")
    print("")

    # Prompt the user to verify if the Wallet should be created
    if confirm_yes_no("Would you like to proceed with Wallet creation?"):     # Yes
        wallet_create(wallet_name, wallet_description)
    else:                                                                     # No
        print(f"{Fore.BLUE}INFO:{Fore.RESET} User selected to not create the Wallet. \n")

    disp_menu_main()

def disp_menu_wallet_delete(modwallet_id: int, modwallet_name: str):

    # Display menu header
    print("")
    print("#########################################################################################")
    print("##############" + "WALMAN - DELETE WALLET".center(61) + "##############")
    print("#########################################################################################")
    print("")

    print(f"{Fore.BLUE}INFO:{Fore.RESET} The following are the full details of the Wallet to be deleted.")
    wallet_view(modwallet_id, modwallet_name)

    print("")
    print(f"{Fore.YELLOW}WARNING:{Fore.RESET} This delete operation only removes the Wallet from the Walman database.")
    print("         It does not delete any actual Oracle wallets which have been deployed to remote Sites. Take note of those Sites before proceeding.")
    print(f"{Fore.YELLOW}WARNING:{Fore.RESET} This delete operation does NOT remove any entries from the Passmgr.")
    print("")

    # Prompt the user to verify if the Wallet should be deleted
    if confirm_yes_no(f"Are you certain that you want to {Fore.YELLOW}permanently delete{Fore.RESET} the selected Wallet?"):     # Yes
        wallet_delete(modwallet_id, modwallet_name)
    else:                                                                                                                        # No                                                                                                       # No
        print(f"{Fore.BLUE}INFO:{Fore.RESET} User selected to not delete the Credential. \n")
    disp_menu_main()

def disp_menu_wallet_deploy(modwallet_id: int, modwallet_name: str):

    # Display menu header
    print("")
    print("#########################################################################################")
    print("##############" + "WALMAN - GENERATE / DEPLOY WALLET".center(61) + "##############")
    print("#########################################################################################")
    print(f"{Fore.BLUE}Currently selected Wallet: {Fore.YELLOW}[{modwallet_name}]{Fore.RESET}")
    print("")
    print("1) Generate Wallet locally")
    print("2) Test remote connectivity/permissions (optional)")
    print("3) Deploy Wallet remotely")
    print("p) Return to the Previous Menu")
    print("m) Return to the Main Menu")
    print("q) Quit")

    # Prompt for, validate, and act on user input
    reply_valid = False
    while reply_valid == False:
        reply = input("Select Option: ")
        reply = reply.lower().strip()
        reply_valid = True

        if reply == "1":                  # 1) Generate Wallet locally
            wallet_generate_locally(modwallet_id, modwallet_name, confirm_yes_no("Would you like to run a test of the local Wallet after it is created?"))
            disp_menu_wallet_deploy(modwallet_id, modwallet_name)
        elif reply == "2":               # 2) Test remote connectivity/permissions (optional)
            wallet_deploy_test(modwallet_id)
            disp_menu_wallet_deploy(modwallet_id, modwallet_name)
        elif reply == "3":               # 3) Deploy Wallet remotely
            wallet_deploy(modwallet_id)
            disp_menu_wallet_deploy(modwallet_id, modwallet_name)
        elif reply == "p":               # p) Return to the Previous Menu
            disp_menu_wallet_manage(modwallet_id, modwallet_name)
        elif reply == "m":              # m) Return to the Main Menu
            disp_menu_main()
        elif reply == "q":               # q) Quit
            program_exit()
        else:                                # Invalid response
            reply_valid = False
            print(f"{Fore.RED}ERROR:{Fore.RESET} Invalid Response: {reply}\n")

def disp_menu_wallet_manage(modwallet_id: int, modwallet_name: str):

    # Display menu header and options
    print("")
    print("#########################################################################################")
    print("##############" + "WALMAN - MANAGE WALLET".center(61) + "##############")
    print("#########################################################################################")
    print(f"{Fore.BLUE}Currently selected Wallet: {Fore.YELLOW}[{modwallet_name}]{Fore.RESET}")
    print("")
    print("1) View Wallet Details")
    print("2) Generate/Deploy Wallet")
    print("3) Credentials - Add to Wallet")
    print("4) Credentials - Remove from Wallet")
    print("5) Sites - Assign to Wallet")
    print("6) Sites - Unassign from Wallet")
    print("7) Delete Wallet")
    print(f"s) Change Selected Wallet to Modify {Fore.YELLOW}[{modwallet_name}]{Fore.RESET}")
    print("m) Return to the Main Menu")
    print("q) Quit")

    # Prompt for, validate, and act on user input
    reply_valid = False
    while reply_valid == False:
        reply = input("Select Option: ")
        reply = reply.lower().strip()
        reply_valid = True

        if reply == "1":                  # 1) View Wallet Details
            wallet_view(modwallet_id, modwallet_name)
            disp_menu_wallet_manage(modwallet_id, modwallet_name)
        elif reply == "2":               # 2) Generate/Deploy Wallet
            disp_menu_wallet_deploy(modwallet_id, modwallet_name)
        elif reply == "3":               # 3) Credentials - Add to Wallet
            disp_menu_wallet_modify_creds(True, modwallet_id, modwallet_name)
        elif reply == "4":               # 4) Credentials - Remove from Wallet
            disp_menu_wallet_modify_creds(False, modwallet_id, modwallet_name)
        elif reply == "5":               # 5) Sites - Assign to Wallet
            disp_menu_wallet_modify_sites_assign(modwallet_id, modwallet_name)
        elif reply == "6":               # 6) Sites - Unassign from Wallet
            disp_menu_wallet_modify_sites_unassign(modwallet_id, modwallet_name)
        elif reply == "7":               # 7) Delete Wallet
            disp_menu_wallet_delete(modwallet_id, modwallet_name)
        elif reply == "s":               # s) Change Selected Wallet to Modify
            disp_menu_wallet_manage_modwallet_select()
        elif reply == "m":              # m) Return to the Main Menu
            disp_menu_main()
        elif reply == "q":               # q) Quit
            program_exit()
        else:                                # Invalid response
            reply_valid = False
            print(f"{Fore.RED}ERROR:{Fore.RESET} Invalid Response: {reply}\n")

def disp_menu_wallet_modify_creds(add: bool, modwallet_id: int, modwallet_name: str):

    if add == True:
        mod_word = "ADD"
    else:
        mod_word = "REMOVE"

    # Display menu header and options
    print("")
    print("#########################################################################################")
    print("##############" + f"WALMAN - MANAGE WALLET - {mod_word} CREDENTIALS".center(61) + "##############")
    print("#########################################################################################")
    print(f"{Fore.BLUE}Currently selected Wallet: {Fore.YELLOW}[{modwallet_name}]{Fore.RESET}")
    print(f"{Fore.BLUE}INFO:{Fore.RESET} You can select more than one Credential to {mod_word.lower()} by writing them comma-separated. (e.g. 1,3,7)")
    print("")

    reply_valid = False
    while reply_valid == False:
        # Prompt the user for a SEARCH_STRING to use to narrow the search for entries in the CREDENTIALS table:
        print("")
        search_string = ""
        search_string = input("Enter the Search String to be used to find Credentials: ")
        print("")

        # Query the WALMANDB for Credentials with a name containing the search_string
        cursor = walmandb_conn.cursor()
        if add == True:
            query =  """SELECT TO_CHAR(ROW_NUMBER() OVER(ORDER BY c.cred_name))||')' AS row_seq,
                                                c.cred_name,
                                                TO_CHAR(c.cred_id),
                                                c.cred_db_host_name,
                                                TO_CHAR(c.cred_db_port),
                                                c.cred_db_service,
                                                c.cred_passmgr_entry
                            FROM    walman.credentials c
                            WHERE   TRIM(LOWER(c.cred_name)) LIKE TRIM(LOWER('%' || :search_string || '%'))
                            AND          c.cred_id NOT IN (SELECT   wc.cred_id
                                                                                FROM    walman.wallet_credentials wc
                                                                                WHERE   wc.wallet_id = :modwallet_id)"""
        else:
            query = """SELECT TO_CHAR(ROW_NUMBER() OVER(ORDER BY c.cred_name))||')' AS row_seq,
                                                c.cred_name,
                                                TO_CHAR(c.cred_id),
                                                c.cred_db_host_name,
                                                TO_CHAR(c.cred_db_port),
                                                c.cred_db_service,
                                                c.cred_passmgr_entry
                                FROM    walman.credentials c,
                                                walman.wallet_credentials wc
                                WHERE   TRIM(LOWER(c.cred_name)) LIKE TRIM(LOWER('%' || :search_string || '%'))
                                AND          wc.cred_id = c.cred_id
                                AND          wc.wallet_id = :modwallet_id"""
        cursor.execute(query, [search_string, modwallet_id])
        query_results = cursor.fetchall()
        cursor.close()

        if len(query_results) == 0:
            if len(search_string) > 0:
                print(f"{Fore.RED}ERROR:{Fore.RESET} No Credentials found for the current Search String. To see all Credentials, respond with blank when prompted for Search String.")
            else:
                if add == True:
                    print(f"{Fore.YELLOW}WARNING:{Fore.RESET} There are no more Credentials in Walman which can be added to this Wallet.")
                else:
                    print(f"{Fore.YELLOW}WARNING:{Fore.RESET} There are no more Credentials in Walman which can be removed from this Wallet.")
                disp_menu_wallet_manage(modwallet_id, modwallet_name)
        else:
            reply_valid = True

    # Display Credentials that can be added to or removed from the Wallet as dynamic menu options
    headers = ("#)", "Credential", "ID", "DB Host Name", "DB Port", "DB Service",  "Passmgr Entry")
    print_table(query_results, headers)

     # Display static menu options
    print(f"s) {Fore.BLUE}Change Credential Search String: {Fore.YELLOW}[{search_string}]{Fore.RESET}")
    print("p) Return to the Previous Menu")
    print("m) Return to the Main Menu")
    print("q) Quit")

    # Prompt for, validate, and act on user input
    reply_valid = False
    while reply_valid == False:
        replies = input("Select Credential(s) or navigation option: ")
        reply_valid = True

        # Change user input into a list
        replies = replies.split(',')

        # If no input, give an error.
        if len(replies) == 0:
            reply_valid = False
            print(f"{Fore.RED}ERROR:{Fore.RESET} Invalid Reponse: {reply}\n")
            continue

        mod_creds = []

        for reply in replies:
            reply = reply.lower().strip()
            if reply.isdecimal() and int(reply) > 0 and int(reply) <= len(query_results):           # Valid dynamic menu option
                mod_creds.append(int(query_results[int(reply)-1][2]))
            elif reply == "s" and len(replies) == 1:                       # s) Change Credential Search String
                disp_menu_wallet_modify_creds(True, modwallet_id, modwallet_name)
            elif reply == "p" and len(replies) == 1:                      # p) Return to the Previous Menu
                disp_menu_wallet_manage(modwallet_id, modwallet_name)
            elif reply == "m" and len(replies) == 1:                      # m) Return to the Main Menu
                disp_menu_main()
            elif reply == "q" and len(replies) == 1:                       # q) Quit
                program_exit()
            else:                                                                                # Invalid Response
                reply_valid = False
                print(f"{Fore.RED}ERROR:{Fore.RESET} Invalid Reponse: {','.join(replies)}\n")
                break

    if len(mod_creds) > 0:
        if add == True:
            wallet_modify_creds_add(modwallet_id, mod_creds)
        else:
            wallet_modify_creds_remove(modwallet_id, mod_creds)

    disp_menu_wallet_manage(modwallet_id, modwallet_name)

def disp_menu_wallet_manage_modwallet_select():

    # Display menu header
    print("")
    print("#########################################################################################")
    print("##############" + "WALMAN - MANAGE WALLET - SELECT WALLET".center(61) + "##############")
    print("#########################################################################################")
    print("")

    reply_valid = False
    while reply_valid == False:
        # Prompt the user for a SEARCH_STRING to use to narrow the search for entries in the WALLETS table:
        print("")
        search_string = ""
        search_string = input("Enter the Search String to be used to find the Wallet: ")

        # Query the WALMANDB for Wallets with a name containing the search_string
        cursor = walmandb_conn.cursor()
        cursor.execute("SELECT w.wallet_id, w.wallet_passmgr_entry FROM wallets w WHERE TRIM(LOWER(w.wallet_passmgr_entry)) LIKE TRIM(LOWER('%' || :search_string || '%')) ORDER BY 2", [search_string])
        query_results = cursor.fetchall()
        cursor.close()

        if len(query_results) == 0:
            print(f"{Fore.RED}ERROR:{Fore.RESET} No Wallets found for the current Search String. To see all Wallets, respond with blank when prompted for Search String.")
        else:
            reply_valid = True

    # Display query results as dynamic menu options
    for i in range(len(query_results)):
        print(str(i+1) + ") " + str(query_results[i][1]))
    # Display static menu options
    print(f"s) {Fore.BLUE}Change Wallet Search String: {Fore.YELLOW}[{search_string}]{Fore.RESET}")
    print("m) Return to the Main Menu")
    print("q) Quit")

    # Prompt for, validate, and act on user input
    reply_valid = False
    while reply_valid == False:
        reply = input("Select Wallet or navigation option: ")
        reply = reply.lower().strip()
        reply_valid = True

        if reply.isdecimal() and int(reply) > 0 and int(reply) <= len(query_results):           # Valid dynamic menu option
            disp_menu_wallet_manage(modwallet_id = query_results[int(reply)-1][0], modwallet_name = query_results[int(reply)-1][1])
        elif reply == "s":                       # s) Change Wallet Search String
            disp_menu_wallet_manage_modwallet_select()
        elif reply == "m":                      # m) Return to the Main Menu
            disp_menu_main()
        elif reply == "q":                       # q) Quit
            program_exit()
        else:                                        # Invalid Response
            reply_valid = False
            print(f"{Fore.RED}ERROR:{Fore.RESET} Invalid Reponse: {reply}\n")

def disp_menu_wallet_modify_sites_assign(modwallet_id: int, modwallet_name: str):

    # Display menu header
    print("")
    print("#########################################################################################")
    print("##############" + f"WALMAN - MODIFY WALLET - ASSIGN SITE".center(61) + "##############")
    print("#########################################################################################")
    print(f"{Fore.BLUE}Currently selected Wallet: {Fore.YELLOW}[{modwallet_name}]{Fore.RESET}")
    print("")

    # Prompt for Site details
    site_host_name = input("Enter the Site's Host Name: ")
    site_host_name = site_host_name.strip()
    site_directory =  input("Enter the Site's full directory path: ")
    site_directory = site_directory.strip()
    site_owner = input("Enter the Site's owner: ")
    site_owner = site_owner.strip()

    # Show entered information for confirmation
    print("")
    print(f"{Fore.BLUE}INFO:{Fore.RESET} The following Site will be assigned to the selected Wallet:")
    print(f"Site Host Name: {Fore.YELLOW}[{site_host_name}]{Fore.RESET}")
    print(f"Site Directory: {Fore.YELLOW}[{site_directory}]{Fore.RESET}")
    print(f"Site Owner: {Fore.YELLOW}[{site_owner}]{Fore.RESET}")
    print("")

    # Prompt the user to verify if the Site should be added to Wallet
    if confirm_yes_no("Would you like to proceed with assigning this Site to the Wallet?"):     # Yes
        wallet_modify_sites_assign(modwallet_id, site_host_name, site_directory, site_owner)
    else:                                                                                       # No
        print(f"{Fore.BLUE}INFO:{Fore.RESET} User selected to not assign the Site to the Wallet. \n")

    disp_menu_wallet_manage(modwallet_id, modwallet_name)

def disp_menu_wallet_modify_sites_unassign(modwallet_id: int, modwallet_name: str):

    # Display menu header and options
    print("")
    print("#########################################################################################")
    print("##############" + f"WALMAN - MANAGE WALLET - UNASSIGN SITES".center(61) + "##############")
    print("#########################################################################################")
    print(f"{Fore.BLUE}Currently selected Wallet: {Fore.YELLOW}[{modwallet_name}]{Fore.RESET}")
    print(f"{Fore.BLUE}INFO:{Fore.RESET} You can select more than one Site to unassign by writing them comma-separated. (e.g. 1,3,7)")
    print("")

    reply_valid = False
    while reply_valid == False:
        # Query the WALMANDB for Sites assigned to the selected Wallet
        cursor = walmandb_conn.cursor()
        cursor.execute("""SELECT   TO_CHAR(ROW_NUMBER() OVER(ORDER BY ws.site_host_name, ws.site_directory))||')' AS row_seq,
                                                            ws.site_host_name,
                                                            ws.site_directory,
                                                            ws.site_owner,
                                                            TO_CHAR(ws.site_id)
                                    FROM    walman.wallet_sites ws
                                    WHERE   ws.wallet_id = :modwallet_id""", [modwallet_id])
        query_results = cursor.fetchall()
        cursor.close()

        if len(query_results) == 0:
            print(f"{Fore.YELLOW}WARNING:{Fore.RESET} There are no Sites assigned to this Wallet.")
            disp_menu_wallet_manage(modwallet_id, modwallet_name)
        else:
            reply_valid = True

    # Display Credentials that can be added to or removed from the Wallet as dynamic menu options
    headers = ("#)", "Site Host Name", "Site Directory", "Site Owner", "Site ID")
    print_table(query_results, headers)

     # Display static menu options
    print("p) Return to the Previous Menu")
    print("m) Return to the Main Menu")
    print("q) Quit")

    # Prompt for, validate, and act on user input
    reply_valid = False
    while reply_valid == False:
        replies = input("Select Site(s) or navigation option: ")
        reply_valid = True

        # Change user input into a list
        replies = replies.split(',')

        # If no input, give an error.
        if len(replies) == 0:
            reply_valid = False
            print(f"{Fore.RED}ERROR:{Fore.RESET} Invalid Reponse: {reply}\n")
            continue

        mod_sites = []

        for reply in replies:
            reply = reply.lower().strip()
            if reply.isdecimal() and int(reply) > 0 and int(reply) <= len(query_results):           # Valid dynamic menu option
                mod_sites.append(int(query_results[int(reply)-1][4]))
            elif reply == "p" and len(replies) == 1:                      # p) Return to the Previous Menu
                disp_menu_wallet_manage(modwallet_id, modwallet_name)
            elif reply == "m" and len(replies) == 1:                      # m) Return to the Main Menu
                disp_menu_main()
            elif reply == "q" and len(replies) == 1:                       # q) Quit
                program_exit()
            else:                                                                                # Invalid Response
                reply_valid = False
                print(f"{Fore.RED}ERROR:{Fore.RESET} Invalid Reponse: {','.join(replies)}\n")
                break

    if len(mod_sites) > 0:
        wallet_modify_sites_unassign(mod_sites)

    disp_menu_wallet_manage(modwallet_id, modwallet_name)

def disp_menu_walman_initialize():

    # Display menu header
    print("")
    print("#########################################################################################")
    print("##############" + f"WALMAN - INITIALIZE REPOSITORY".center(61) + "##############")
    print("#########################################################################################")
    print("")

    print(f"{Fore.BLUE} INFO:{Fore.RESET} Please enter the prompted information to generate a new Walman Repository wallet.")

    walman_repo_hostname = input("Enter the hostname for your Walman Repository database: ")
    walman_repo_hostname = walman_repo_hostname.strip()

    walman_repo_port = input("Enter the Port number for your Walman Repository database: ")
    walman_repo_port = walman_repo_port.strip()

    walman_repo_service_name = input("Enter the Service Name for your Walman Repository database: ")
    walman_repo_service_name = walman_repo_service_name.strip()

    walman_repo_password = input("Enter the password for the WALMAN account in your Walman Repository database: ")
    walman_repo_password = walman_repo_password.strip()

    # Show entered information for confirmation
    print("")
    print(f"{Fore.BLUE}INFO:{Fore.RESET} The Walman Repository wallet will be created with the following settings:")
    print(f"Walman Repo Hostname: {Fore.YELLOW}[{walman_repo_hostname}]{Fore.RESET}")
    print(f"Walman Repo Port: {Fore.YELLOW}[{walman_repo_port}]{Fore.RESET}")
    print(f"Walman Repo Service Name: {Fore.YELLOW}[{walman_repo_service_name}]{Fore.RESET}")
    print(f"Walman Repo TNS Alias: {Fore.YELLOW}[{walman_tns_name}]{Fore.RESET}")
    print(f"Walman Repo wallet location: {Fore.YELLOW}[{local_wallets_directory}/walman_wallet]{Fore.RESET}")
    print("")

    # Prompt the user to verify if the repo wallet should be created
    if confirm_yes_no("Would you like to proceed with Walman Repository wallet creation?"):     # Yes
        walman_initialize(walman_repo_hostname, walman_repo_port, walman_repo_service_name, walman_repo_password)
    else:                                                                     # No
        print(f"{Fore.BLUE}INFO:{Fore.RESET} User selected to not generate the Walman Repository wallet. \n")
        exit()

def passmgr_search(tag: str, search_prompt: bool, search_string_in: str) -> list:
    global search_string

    reply_valid = False
    while reply_valid == False:

        if search_prompt == True:
            # Prompt the user for a SEARCH_STRING to use to narrow the search for entries in the Passmgr:
            search_string = ""
            print("")
            search_string = input("Enter the Search String to be used to find entries in the Passmgr: ")
        else:
            search_string = search_string_in

        # Query the Passmgr to get a list of entries containing the Search String
        run_proc_results = subprocess.run(f"op item list --vault {walman_vault} --tags {tag} --format json", shell=True, check=True, capture_output=True, encoding='utf-8').stdout
        search_results_raw = json.loads(run_proc_results)
        search_results = [x for x in search_results_raw if search_string.lower() in x["title"].lower()]

        if len(search_results) == 0 and search_prompt == True:
            print(f"{Fore.RED}ERROR:{Fore.RESET} No Passmgr entries found for the current Search String. To see all Passmgr entries, respond with blank when prompted for Search String.")
        else:
            reply_valid = True

    return  search_results

def print_table(table_in: list[tuple], headers: tuple):
     # Print the contents of a table and its headers in a user-readable fashion

    col_lens = column_lengths(table_in + [headers])
    header_line = ""
    under_line=""

    # Print table headers with equal number of dashes beneath them
    for index, header in enumerate(headers):
        header_line = header_line + header.ljust(col_lens[index]+1)
        under_line = under_line + "-".ljust(col_lens[index],'-') + " "
    print(header_line)
    print(under_line)

    for row in table_in:
        row_line = ""
        for index, field in enumerate(row):
            row_line = row_line + field.ljust(col_lens[index]+1)
        print(row_line)

def program_exit():
    # Close connection to WALMANDB and close the program
    print("Quitting the program...")
    walmandb_conn.close()
    exit()

def wallet_create(wallet_name: str, wallet_description: str):

    # Check if the name already exists in the Passmgr and add it to the Passmgr if not
    wallet_name_exists = False
    while wallet_name_exists == False:
        search_results = passmgr_search("wallet", False, wallet_name)

        if len(search_results) == 0:
            # No entry in Passmgr for this wallet_name, so create it in Passmgr with random password
            try:
                results = subprocess.run(f"op item create --title=\"{wallet_name}\" --category=login --tags=wallet --vault={walman_vault} username=\"{wallet_name}\" --generate-password='letters,digits,symbols,16'", shell=True, check=True, capture_output=True, encoding='utf-8')
            except:
                print(f"{Fore.RED}ERROR:{Fore.RESET} Error encountered while creating record for {Fore.YELLOW}[{wallet_name}]{Fore.RESET} in the Passmgr. Cancelling Wallet creation.")
                return
            else:
                print(f"{Fore.BLUE}INFO:{Fore.RESET} Created record for {Fore.YELLOW}[{wallet_name}]{Fore.RESET} in the Passmgr.")
        else:
            print(f"{Fore.BLUE}INFO:{Fore.RESET} A record for {Fore.YELLOW}[{wallet_name}]{Fore.RESET} exists in the Passmgr.")
            wallet_name_exists = True

    # Attempt to insert the provided data into the database. If it fails, print the error code/message and return the user to the calling menu.
    try:
        cursor = walmandb_conn.cursor()
        cursor.execute("""INSERT INTO walman.wallets (wallet_passmgr_entry, wallet_description) VALUES (:wallet_passmgr_entry, :wallet_description)""", [wallet_name, wallet_description])
        cursor.close()
    except oracledb.Error as e:
        error_obj, = e.args
        print(f"{Fore.RED}ERROR:{Fore.RESET}{error_obj.message}")
    else:
        print(f"{Fore.GREEN}SUCCESS:{Fore.RESET} Created Wallet {Fore.YELLOW}[{wallet_name}]{Fore.RESET}")

def wallet_delete(wallet_id: int, wallet_name: str):

    # Attempt to delete a record in the database. If it fails, print the error code/message and return the user to the calling menu.
    try:
        cursor = walmandb_conn.cursor()
        cursor.execute("DELETE FROM walman.wallets WHERE wallet_id = :wallet_id", [wallet_id])
        cursor.close()
    except oracledb.Error as e:
        error_obj, = e.args
        print(f"{Fore.RED}ERROR:{Fore.RESET}{error_obj.message}")
    else:
        print(f"{Fore.GREEN}SUCCESS:{Fore.RESET} Deleted Wallet {Fore.YELLOW}[{wallet_name}]{Fore.RESET}")

def wallet_deploy(wallet_id: int):

    # Make sure the Wallet can be deployed before attempting to do so.
    if wallet_deploy_test(wallet_id) == False:
        print(f"{Fore.RED}ERROR:{Fore.RESET} The Wallet cannot be deployed until the Deploy Test passes. Address the problems listed above before trying again.")
        return

     # Query the WALMANDB for the wallet_local_directory
    wallet_local_directory = ""
    cursor = walmandb_conn.cursor()
    cursor.execute("SELECT w.wallet_local_directory FROM wallets w WHERE w.wallet_id=:wallet_id", [wallet_id])
    query_results = cursor.fetchone()
    cursor.close()
    wallet_local_directory = query_results[0]

    if wallet_local_directory == None or Path(wallet_local_directory).is_dir() == False:
        print(f"{Fore.RED}ERROR:{Fore.RESET} The Wallet must be generated locally before it can be deployed.")
        return

    # Query the WALMANDB for Sites assigned to the Wallet
    cursor = walmandb_conn.cursor()
    cursor.execute("""SELECT    ws.site_host_name,
                                                ws.site_directory,
                                                ws.site_owner
                                FROM      walman.wallet_sites ws
                                WHERE   ws.wallet_id = :wallet_id
                                ORDER BY 1,2""", [wallet_id])
    query_results = cursor.fetchall()
    cursor.close()

    print("####################################################################")
    print(f"{Fore.BLUE}INFO:{Fore.RESET} Deploying the Wallet to all Sites assigned to the Wallet")

    for site in query_results:
        print("--------------------------------------------------------------------------------------------")
        print(f"{Fore.BLUE}Deploying to Site:{Fore.RESET} {site[2]}@{site[0]}:{site[1]}")

        # Back up any existing files at the Site and create the sqlnet.ora file at the Site
        print(f"{Fore.BLUE}    INFO:{Fore.RESET} Backing up existing tns_admin and generating sqlnet.ora")
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.load_system_host_keys()
            ssh_client.connect(hostname = site[0], port = 22, username = site[2])
            remote_command = f""" if [[ -d {site[1]}/tns_admin ]];
                                                    then mv {site[1]}/tns_admin {site[1]}/tns_admin_bkp_{str(datetime.now().strftime("%Y%m%d%H%M%S"))}
                                                fi
                                                if [[ -d {site[1]}/wallet ]];
                                                    then mv {site[1]}/wallet {site[1]}/wallet_bkp_{str(datetime.now().strftime("%Y%m%d%H%M%S"))}
                                                fi
                                                mkdir -p {site[1]}/tns_admin
                                                mkdir -p {site[1]}/wallet
                                                chmod 700 {site[1]}/wallet
                                                echo 'NAMES.DIRECTORY_PATH=(TNSNAMES,EZCONNECT)' > {site[1]}/tns_admin/sqlnet.ora
                                                echo 'SQLNET.WALLET_OVERRIDE = TRUE' >> {site[1]}/tns_admin/sqlnet.ora
                                                echo "WALLET_LOCATION=(SOURCE=(METHOD=FILE)(METHOD_DATA=(DIRECTORY={site[1]}/wallet)))" >> {site[1]}/tns_admin/sqlnet.ora"""
            ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(remote_command)

            result_err = ssh_stderr.read().decode('utf-8').strip()
        finally:
            ssh_client.close()

        # Copy the local tnsnames.ora to the Site
        print(f"{Fore.BLUE}    INFO:{Fore.RESET} Deploying tnsnames.ora, wallet files, and wallet_test.sh")
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.load_system_host_keys()
            ssh_client.connect(hostname = site[0], port = 22, username = site[2])
            sftp_client = ssh_client.open_sftp()
            sftp_client.put(f"{wallet_local_directory}/tns_admin/tnsnames.ora", f"{site[1]}/tns_admin/tnsnames.ora")
            sftp_client.put(f"{wallet_local_directory}/wallet/cwallet.sso", f"{site[1]}/wallet/cwallet.sso")
            sftp_client.put(f"{wallet_local_directory}/wallet/ewallet.p12", f"{site[1]}/wallet/ewallet.p12")
            sftp_client.put(f"{local_wallets_directory}/wallet_test.sh", f"{site[1]}/wallet_test.sh")
        finally:
            ssh_client.close()

        # Execute wallet_test.sh remotely
        print(f"{Fore.BLUE}    INFO:{Fore.RESET} Executing wallet_test.sh to test the Wallet at the Site")
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.load_system_host_keys()
            ssh_client.connect(hostname = site[0], port = 22, username = site[2])
            remote_command = f"bash -ic \"cd {site[1]}; . {site[1]}/wallet_test.sh\""
            ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(remote_command)
            time.sleep(5)

            result = ssh_stdout.read().decode('utf-8').strip()
            result_err = ssh_stderr.read().decode('utf-8').strip()

            print(result)
        finally:
            ssh_client.close()

def wallet_deploy_test(wallet_id: int) -> bool:

    # Query the WALMANDB for Sites assigned to the Wallet
    cursor = walmandb_conn.cursor()
    cursor.execute("""SELECT    ws.site_host_name,
                                                ws.site_directory,
                                                ws.site_owner
                                FROM      walman.wallet_sites ws
                                WHERE   ws.wallet_id = :wallet_id
                                ORDER BY 1,2""", [wallet_id])
    query_results = cursor.fetchall()
    cursor.close()

    print("####################################################################")
    print(f"{Fore.BLUE}INFO:{Fore.RESET} Testing connectivity/permissions for all Sites assigned to the Wallet")
    print("")

    ssh_errors = []
    for site in query_results:
        print(f"{Fore.BLUE}Testing Site:{Fore.RESET} {site[2]}@{site[0]}:{site[1]}")
        test_file = site[1] + "/wallet_deploy_test_" + str(datetime.now().strftime("%Y%m%d%H%M%S"))

        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.load_system_host_keys()
            ssh_client.connect(hostname = site[0], port = 22, username = site[2])
            remote_command = f"mkdir -p {site[1]}; touch {test_file}; chmod 600 {test_file}; ls {test_file}; rm {test_file};"
            ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(remote_command)

            result = ssh_stdout.read().decode('utf-8').strip()
            result_err = ssh_stderr.read().decode('utf-8').strip()

            if result == test_file:
                print(f"{Fore.GREEN}SUCCESS:{Fore.RESET} {site[2]}@{site[0]}:{site[1]}")
            else:
                print(f"{Fore.RED}ERROR:{Fore.RESET}\n{result_err}")
                ssh_errors.append(f"{site[2]}@{site[0]}:{site[1]}\n")
        finally:
            ssh_client.close()

    print("####################################################################")
    if len(ssh_errors) == 0:
        print(f"{Fore.GREEN}SUCCESS:{Fore.RESET} Test succeeded for all Sites")
        print("####################################################################")
        return True
    else:
        print(f"{Fore.RED}ERRORS:{Fore.RESET} The following Sites had errors:")
        print(''.join(ssh_errors))
    print("####################################################################")
    return False

def wallet_generate_locally(wallet_id: int, wallet_name: str, wallet_test: bool):

    # Display the selected Wallet's name.
    print("")
    print(f"{Fore.BLUE}INFO:{Fore.RESET} Generating local files for Wallet: {Fore.YELLOW}[{wallet_name}]{Fore.RESET}")

    # Query the WALMANDB for the wallet_local_directory and wallet_passmgr_entry
    wallet_local_directory = ""
    cursor = walmandb_conn.cursor()
    cursor.execute("SELECT w.wallet_local_directory, w.wallet_passmgr_entry FROM wallets w WHERE w.wallet_id=:wallet_id", [wallet_id])
    query_results = cursor.fetchone()
    cursor.close()
    wallet_local_directory = query_results[0]
    wallet_passmgr_entry = query_results[1]

    # Create a new local directory (and its subdirectories) for the Wallet if none is stored in WALMANDB already.
    if wallet_local_directory == None:
        wallet_local_directory = local_wallets_directory + "/" + wallet_name.replace(" ","_")
        print(f"{Fore.BLUE}INFO:{Fore.RESET} No local directory is stored for the Wallet. Storing directory path: {Fore.YELLOW}[{wallet_local_directory}]{Fore.RESET}")

        # Add the wallet_local_directory value to the Wallet record in the WALMANDB
        try:
            cursor = walmandb_conn.cursor()
            cursor.execute("""UPDATE walman.wallets
                                            SET     wallet_local_directory = :wallet_local_directory
                                            WHERE   wallet_id = :wallet_id""", [wallet_local_directory, wallet_id])
            cursor.close()
        except oracledb.Error as e:
            error_obj, = e.args
            print(f"{Fore.RED}ERROR:{Fore.RESET}{error_obj.message}")
            return
        else:
            print(f"{Fore.BLUE}INFO:{Fore.RESET} Updated Wallet entry with new value for Local Directory")

    Path(wallet_local_directory).mkdir(parents = True, exist_ok = True)
    Path(wallet_local_directory + "/tns_admin").mkdir(parents = True, exist_ok = True)
    Path(wallet_local_directory + "/wallet").mkdir(parents = True, exist_ok = True)

    # Delete the Wallet's local files if they already exist
    Path(wallet_local_directory + "/tns_admin/sqlnet.ora").unlink(missing_ok = True)
    Path(wallet_local_directory + "/tns_admin/tnsnames.ora").unlink(missing_ok = True)
    Path(wallet_local_directory + "/wallet/cwallet.sso").unlink(missing_ok = True)
    Path(wallet_local_directory + "/wallet/cwallet.sso.lck").unlink(missing_ok = True)
    Path(wallet_local_directory + "/wallet/ewallet.p12").unlink(missing_ok = True)
    Path(wallet_local_directory + "/wallet/ewallet.p12.lck").unlink(missing_ok = True)

    # Create the Wallet's new sqlnet.ora file
    sqlnet_ora_file = open(wallet_local_directory + "/tns_admin/sqlnet.ora", "w")
    sqlnet_ora_file.write("SQLNET.WALLET_OVERRIDE = TRUE\n")
    sqlnet_ora_file.write("SSL_CLIENT_AUTHENTICATION = FALSE\n")
    sqlnet_ora_file.write("SSL_VERSION = 0\n")
    sqlnet_ora_file.write(f"WALLET_LOCATION=(SOURCE=(METHOD=FILE)(METHOD_DATA=(DIRECTORY={wallet_local_directory}/wallet)))\n")
    sqlnet_ora_file.close()
    print(f"{Fore.BLUE}INFO:{Fore.RESET} Generated the sqlnet.ora file for the local Wallet")

    # Query the WALMANDB for the Credentials to be added to the Wallet
    cursor = walmandb_conn.cursor()
    cursor.execute("""SELECT c.cred_name,
                                        c.cred_db_host_name,
                                        TO_CHAR(c.cred_db_port),
                                        c.cred_db_service,
                                        c.cred_passmgr_entry
                        FROM    walman.credentials c,
                                        walman.wallet_credentials wc
                        WHERE   wc.cred_id = c.cred_id
                        AND          wc.wallet_id = :wallet_id
                        ORDER BY 1""", [wallet_id])
    query_results = cursor.fetchall()
    cursor.close()

    # Retrieve the Credentials' usernames and passwords from the Passmgr.
    wallet_creds = []
    for query_cred in query_results:
        wallet_cred = { "cred_name": query_cred[0],
                                    "cred_db_host_name":  query_cred[1],
                                    "cred_db_port":  query_cred[2],
                                    "cred_db_service":  query_cred[3],
                                    "cred_username": subprocess.run(f"op item get \"{query_cred[4]}\" --vault={walman_vault} --fields username --reveal | head -1", shell=True, check=True, capture_output=True, encoding='utf-8').stdout.strip(),
                                    "cred_password": subprocess.run(f"op item get \"{query_cred[4]}\" --vault={walman_vault} --fields password --reveal | head -1", shell=True, check=True, capture_output=True, encoding='utf-8').stdout.strip(), }
        wallet_creds.append(wallet_cred)
    print(f"{Fore.BLUE}INFO:{Fore.RESET} Retrieved Credential data from WALMANDB and the Passmgr")

    # Retrieve the Wallet's password from the Passmgr
    wallet_password = subprocess.run(f"op item get \"{wallet_name}\" --vault={walman_vault} --fields password --reveal | head -1", shell=True, check=True, capture_output=True, encoding='utf-8').stdout.strip()
    print(f"{Fore.BLUE}INFO:{Fore.RESET} Retrieved Wallet password from the Passmgr")

    # Generate the local Wallet files
    try:
        subprocess.run(f"echo \"{wallet_password}\n{wallet_password}\" | mkstore -nologo -wrl {wallet_local_directory}/wallet -create", shell=True, check=True, capture_output=True, encoding='utf-8')
    except subprocess.CalledProcessError as e:
        print("Command failed with exit code:", e.returncode)
        print("Error output:", e.stdout + e.stderr)

    print(f"{Fore.BLUE}INFO:{Fore.RESET} Generated an empty local Wallet")

    # Populate the local Wallet
    for wal_cred in wallet_creds:
        try:
            subprocess.run(f"echo \"{wallet_password}\" | mkstore -nologo -wrl {wallet_local_directory}/wallet -createCredential {wal_cred['cred_name']} {wal_cred['cred_username']} {wal_cred['cred_password']}", shell=True, check=True, capture_output=True, encoding='utf-8')
        except subprocess.CalledProcessError as e:
            print("Command failed with exit code:", e.returncode)
            print("Error output:", e.stdout + e.stderr)

    print(f"{Fore.BLUE}INFO:{Fore.RESET} Populated the local Wallet")

    # Generate the tnsnames.ora file
    tnsnames_ora_file = open(wallet_local_directory + "/tns_admin/tnsnames.ora", "w")
    for wal_cred in wallet_creds:
        tnsnames_ora_file.write(f"{wal_cred['cred_name']} =\n")
        tnsnames_ora_file.write(f"    (DESCRIPTION = \n")
        tnsnames_ora_file.write(f"        (ADDRESS_LIST = \n")
        tnsnames_ora_file.write(f"            (ADDRESS = (PROTOCOL = TCP)(Host = {wal_cred['cred_db_host_name']})(Port = {wal_cred['cred_db_port']}))\n")
        tnsnames_ora_file.write(f"        )\n")
        tnsnames_ora_file.write(f"        (CONNECT_DATA = \n")
        tnsnames_ora_file.write(f"            (SERVICE_NAME = {wal_cred['cred_db_service']})\n")
        tnsnames_ora_file.write(f"        )\n")
        tnsnames_ora_file.write(f"    )\n\n")
    tnsnames_ora_file.close()
    print(f"{Fore.BLUE}INFO:{Fore.RESET} Generated the tnsnames.ora file for the local Wallet")

    # Run a test of the local Wallet if requested by user
    if wallet_test == True:
        wallet_test_creds(wallet_local_directory)

def wallet_modify_creds_add(wallet_id: int, mod_creds: list[int]):

    walmandb_conn.autocommit = False

    for cred_id in mod_creds:
        #Attempt to insert the provided data into the database. If it fails, print the error code/message and return the user to the calling menu.
        try:
            cursor = walmandb_conn.cursor()
            cursor.execute("""INSERT INTO walman.wallet_credentials (wallet_id, cred_id)
                                                VALUES  (:wallet_id, :cred_id)""", [wallet_id, cred_id])
            cursor.close()
        except oracledb.Error as e:
            error_obj, = e.args
            print(f"{Fore.RED}ERROR:{Fore.RESET}{error_obj.message}")
            walmandb_conn.rollback()
            walmandb_conn.autocommit = True
            return

    walmandb_conn.commit()
    walmandb_conn.autocommit = True
    print(f"{Fore.GREEN}SUCCESS:{Fore.RESET} Added Credentials to the Wallet")

def wallet_modify_creds_remove(wallet_id: int, mod_creds: list[int]):

    walmandb_conn.autocommit = False

    for cred_id in mod_creds:
        #Attempt to delete records from the database. If it fails, print the error code/message and return the user to the calling menu.
        try:
            cursor = walmandb_conn.cursor()
            cursor.execute("""DELETE FROM walman.wallet_credentials
                                            WHERE wallet_id = :wallet_id
                                            AND cred_id = :cred_id""", [wallet_id, cred_id])
            cursor.close()
        except oracledb.Error as e:
            error_obj, = e.args
            print(f"{Fore.RED}ERROR:{Fore.RESET}{error_obj.message}")
            walmandb_conn.rollback()
            walmandb_conn.autocommit = True
            return

    walmandb_conn.commit()
    walmandb_conn.autocommit = True
    print(f"{Fore.GREEN}SUCCESS:{Fore.RESET} Removed Credentials from the Wallet")

def wallet_modify_sites_assign(wallet_id: int, site_host_name: str, site_directory: str, site_owner: str):

 # Attempt to insert the provided data into the database. If it fails, print the error code/message and return the user to the calling menu.
    try:
        cursor = walmandb_conn.cursor()
        cursor.execute("""INSERT INTO walman.wallet_sites (wallet_id, site_host_name, site_directory, site_owner)
                                            VALUES  (:wallet_id, :site_host_name, :site_directory, :site_owner)""",
                                                                [wallet_id, site_host_name, site_directory, site_owner])
        cursor.close()
    except oracledb.Error as e:
        error_obj, = e.args
        print(f"{Fore.RED}ERROR:{Fore.RESET}{error_obj.message}")
        return False

    print(f"{Fore.GREEN}SUCCESS:{Fore.RESET} Assigned Site to Wallet")
    return True

def wallet_modify_sites_unassign(mod_sites):

    walmandb_conn.autocommit = False

    for site_id in mod_sites:
        #Attempt to delete records from the database. If it fails, print the error code/message and return the user to the calling menu.
        try:
            cursor = walmandb_conn.cursor()
            cursor.execute("""DELETE FROM walman.wallet_sites
                                            WHERE site_id = :site_id""", [site_id])
            cursor.close()
        except oracledb.Error as e:
            error_obj, = e.args
            print(f"{Fore.RED}ERROR:{Fore.RESET}{error_obj.message}")
            walmandb_conn.rollback()
            walmandb_conn.autocommit = True
            return

    walmandb_conn.commit()
    walmandb_conn.autocommit = True
    print(f"{Fore.GREEN}SUCCESS:{Fore.RESET} Unassigned Sites from the Wallet")

def wallet_test_creds(wallet_local_directory: str):

    # Copy the wallet_test.sh from the main local_wallets_directory to the Wallet's specific wallet_local_directory
    shutil.copy(local_wallets_directory + "/wallet_test.sh", wallet_local_directory + "/wallet_test.sh")

    # Execute the wallet_test.sh script
    script_output = subprocess.run(f"cd {wallet_local_directory}; ./wallet_test.sh", shell=True, check=True, capture_output=True, encoding='utf-8').stdout
    print(script_output)

def wallet_view(wallet_id: int, wallet_name: str):

    # Query the WALMANDB for Wallet single-field info
    cursor = walmandb_conn.cursor()
    cursor.execute("SELECT w.wallet_description, w.wallet_local_directory FROM wallets w WHERE w.wallet_id=:wallet_id", [wallet_id])
    query_results = cursor.fetchone()
    cursor.close()

    # Display Wallet single-field items
    print("#########################################################################################")
    print("")
    print(Fore.BLUE + "Wallet Name:".rjust(23) + f" {Fore.RESET}{wallet_name}")
    print(Fore.BLUE + "Wallet Description:".rjust(23) + f" {Fore.RESET}{query_results[0]}")
    print(f"{Fore.BLUE}Wallet Local Directory: {Fore.RESET}{query_results[1]}")

    # Query the WALMANDB for Credentials used by the Wallet
    cursor = walmandb_conn.cursor()
    cursor.execute("""SELECT c.cred_name,
                                        c.cred_db_host_name,
                                        TO_CHAR(c.cred_db_port),
                                        c.cred_db_service,
                                        c.cred_passmgr_entry
                        FROM    walman.credentials c,
                                        walman.wallet_credentials wc
                        WHERE   wc.cred_id = c.cred_id
                        AND          wc.wallet_id = :wallet_id
                        ORDER BY 1""", [wallet_id])
    query_results = cursor.fetchall()
    cursor.close()

    # Display Credentials used by the Wallet
    print(f"\n{Fore.BLUE}Wallet Credentials: {Fore.RESET}\n")
    headers = ("Credential", "DB Hostname", "DB Port", "DB Service",  "Passmgr Entry")
    print_table(query_results, headers)

    # Query the WALMANDB for Sites assigned to the Wallet
    cursor = walmandb_conn.cursor()
    cursor.execute("""SELECT  ws.site_host_name,
                                   ws.site_directory,
                                   ws.site_owner
                        FROM  walman.wallet_sites ws
                        WHERE   ws.wallet_id = :wallet_id
                        ORDER BY 1,2""", [wallet_id])
    query_results = cursor.fetchall()
    cursor.close()

    # Display Sites assigned to the Wallet
    print(f"\n{Fore.BLUE}Sites: {Fore.RESET}\n")
    headers = ("Site Host Name", "Site Directory", "Site Owner")
    print_table(query_results, headers)

def walman_initialize(walman_repo_hostname: str, walman_repo_port: int, walman_repo_service_name: str, walman_repo_password: str):
    print(f"{Fore.BLUE}INFO:{Fore.RESET} Initializing Walman...")
    Path(local_wallets_directory + "/walman_wallet").mkdir(parents = True, exist_ok = True)
    Path(local_wallets_directory + "/walman_wallet/tns_admin").mkdir(parents = True, exist_ok = True)
    Path(local_wallets_directory + "/walman_wallet/wallet").mkdir(parents = True, exist_ok = True)

    # Delete the wallet repo's local files if they already exist
    Path(local_wallets_directory + "/walman_wallet/tns_admin/sqlnet.ora").unlink(missing_ok = True)
    Path(local_wallets_directory + "/walman_wallet/tns_admin/tnsnames.ora").unlink(missing_ok = True)
    Path(local_wallets_directory + "/walman_wallet/wallet/cwallet.sso").unlink(missing_ok = True)
    Path(local_wallets_directory + "/walman_wallet/wallet/cwallet.sso.lck").unlink(missing_ok = True)
    Path(local_wallets_directory + "/walman_wallet/wallet/ewallet.p12").unlink(missing_ok = True)
    Path(local_wallets_directory + "/walman_wallet/wallet/ewallet.p12.lck").unlink(missing_ok = True)

    # Create the Wallet's new sqlnet.ora file
    sqlnet_ora_file = open(local_wallets_directory + "/walman_wallet/tns_admin/sqlnet.ora", "w")
    sqlnet_ora_file.write("SQLNET.WALLET_OVERRIDE = TRUE\n")
    sqlnet_ora_file.write("SSL_CLIENT_AUTHENTICATION = FALSE\n")
    sqlnet_ora_file.write("SSL_VERSION = 0\n")
    sqlnet_ora_file.write(f"WALLET_LOCATION=(SOURCE=(METHOD=FILE)(METHOD_DATA=(DIRECTORY={local_wallets_directory}/walman_wallet/wallet)))\n")
    sqlnet_ora_file.close()
    print(f"{Fore.BLUE}INFO:{Fore.RESET} Generated the sqlnet.ora file for the Walman Repository wallet.")

    # Generate the Walman Repository wallet files with random password
    try:
        walman_repo_wallet_password = secrets.token_urlsafe(16)
        subprocess.run(f"echo \"{walman_repo_wallet_password}\n{walman_repo_wallet_password}\" | mkstore -nologo -wrl {local_wallets_directory}/walman_wallet/wallet -create", shell=True, check=True, capture_output=True, encoding='utf-8')
    except subprocess.CalledProcessError as e:
        print("Command failed with exit code:", e.returncode)
        print("Error output:", e.stdout + e.stderr)

    print(f"{Fore.BLUE}INFO:{Fore.RESET} Generated an empty Walman Repository wallet.")

    # Populate the Walman Repository wallet with WALMAN usenrname/password
    try:
        subprocess.run(f"echo \"{walman_repo_wallet_password}\" | mkstore -nologo -wrl {local_wallets_directory}/walman_wallet/wallet -createCredential {walman_tns_name} WALMAN {walman_repo_password}", shell=True, check=True, capture_output=True, encoding='utf-8')
    except subprocess.CalledProcessError as e:
        print("Command failed with exit code:", e.returncode)
        print("Error output:", e.stdout + e.stderr)

    print(f"{Fore.BLUE}INFO:{Fore.RESET} Populated the Walman Respository wallet.")

    # Generate the tnsnames.ora file
    tnsnames_ora_file = open(local_wallets_directory + "/walman_wallet/tns_admin/tnsnames.ora", "w")
    tnsnames_ora_file.write(f"{walman_tns_name} = (DESCRIPTION = (ADDRESS_LIST = (ADDRESS = (PROTOCOL = TCP)(Host = {walman_repo_hostname})(Port = {walman_repo_port})))(CONNECT_DATA = (SERVICE_NAME = {walman_repo_service_name})))")
    tnsnames_ora_file.close()
    print(f"{Fore.BLUE}INFO:{Fore.RESET} Generated the tnsnames.ora file for the Walman Repository wallet.")
    print(f"{Fore.BLUE}INFO:{Fore.RESET} Walman Initialization complete. Please re-run walman.py. Exiting...")
    exit()


# Start of the program execution - Open connection to WALMANDB as WALMAN user, and display the main menu
oracledb.init_oracle_client()
try:
    conn_config_dir = "{local_wallets_directory}/walman_wallet"
    walmandb_conn = oracledb.connect(externalauth=True, dsn=walman_tns_name, config_dir=conn_config_dir)
    walmandb_conn.autocommit = True
except oracledb.Error as e:
    error_obj, = e.args
    print(f"{Fore.RED}ERROR:{Fore.RESET}{error_obj.message}")
    print(f"{Fore.RED}ERROR:{Fore.RESET} Walman is unable to connect to the Walman Repository database.")

    if confirm_yes_no("Would you like to run Walman Initialization to re-create the Walman Repository wallet?"):     # Yes
        disp_menu_walman_initialize()
    else:                                                                     # No
        print(f"{Fore.BLUE}INFO:{Fore.RESET} User selected to not run Walman Initialization. Exiting... \n")
        exit()

disp_menu_main()
program_exit()