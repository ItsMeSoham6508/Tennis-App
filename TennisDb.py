# Importing connector
import mysql.connector
from tkinter import messagebox
from master_enums import Websites

class MasterDb:
    """Connector object for ``masterGui.py``"""
    
    # Connect method
    def connect(self) -> None:

        # Storing connection in mydb
        self.mydb = mysql.connector.connect(
            host="",
            user="",
            password="",
            database=""
        )

        # Create the cursor
        self.myCursor = self.mydb.cursor(buffered=True)
    
    # Disconnect from db
    def disconnect(self) -> None:
        self.mydb.close()

    # Load method to get all records from table (cRud)
    def getRecords(self) -> list:
        self.myCursor.execute("SELECT * FROM testBlob;")
        self.mydb.commit()
        return self.myCursor.fetchall()
    
    # (Crud) create a new record in db
    def insert(self, record: tuple) -> None:
        query = "INSERT INTO testBlob (Id, full_name, age, global_rank, achievements, wl_ratio, image_data) VALUES (Id, %s, %s, %s, %s, %s, %s);"
        self.myCursor.execute(query, record)
        self.mydb.commit()

    # Delete method on db, takes in parameters to check which record it is deleting
    def delete(self, identifier: int, name: str) -> bool:

        # Asking the user if they really wanna do it
        confirmation = messagebox.askyesno(title="Delete Confirmation", message=f"Are you sure you want to delete '{name.strip()}'?")
        
        # If so, go through with
        if (confirmation):
            query = "DELETE FROM testBlob WHERE Id = {};"
            self.myCursor.execute(query.format(identifier))
            self.mydb.commit()

        # Always return that boolean
        return confirmation
     
    # Create an update method, checks to see which record to change with id and the elements changed
    def update(self, identifier: int, changed_elements: tuple) -> None:
        query = "UPDATE testBlob SET full_name = '{}' WHERE Id = {};"
        query1 = "UPDATE testBlob SET age = {} WHERE Id = {};"
        query2 = "UPDATE testBlob SET global_rank = {} WHERE Id = {};"
        query3 = "UPDATE testBlob SET achievements = '{}' WHERE Id = {};"
        query4 = "UPDATE testBlob SET wl_ratio = {} WHERE Id = {};"
        query5 = "UPDATE testBlob SET image_data = %s WHERE Id = %s;"
        self.myCursor.execute(query.format(changed_elements[0], identifier))
        self.myCursor.execute(query1.format(changed_elements[1], identifier))
        self.myCursor.execute(query2.format(changed_elements[2], identifier))
        self.myCursor.execute(query3.format(changed_elements[3], identifier))
        self.myCursor.execute(query4.format(changed_elements[4], identifier))
        self.myCursor.execute(query5, (changed_elements[5], identifier))
        self.mydb.commit()
    
    # Method to create tables for match data
    def create_set_table(self, match_name, name, name2, date, record: list[list], identifier: str) -> None:

        name_str = str(name).replace(" ", "_") + "_" + str(identifier) + "_" + str(date).replace("-", "_")
        name_str2 = str(name2).replace(" ", "_") + "_" + str(identifier) + "_" + str(date).replace("-", "_")

        # Query strings
        query = f"INSERT INTO match_ids(match_name, player_one_table, player_two_table, player_one_name, player_two_name, date_of_play) VALUES ('{match_name}','{name_str}', '{name_str2}', '{name}', '{name2}', '{date}');"
        query1 = """CREATE TABLE {}(
            set_num int PRIMARY KEY AUTO_INCREMENT,
            games_won int,
            aces int,
            first_serve int,
            double_fault int,
            winner bool
        );"""

        # Execute
        self.myCursor.execute(query)
        self.myCursor.execute(query1.format(name_str))
        self.myCursor.execute(query1.format(name_str2))

        # Loop through and add the numerical data
        query2 = "INSERT INTO {} VALUES (set_num, {}, {}, {}, {}, {})"
        for x in range(7):
            self.myCursor.execute(query2.format(name_str, record[0][x], record[1][x], record[2][x], record[3][x], record[4][x]))
            self.myCursor.execute(query2.format(name_str2, record[5][x], record[6][x], record[7][x], record[8][x], record[9][x]))

        # Commit
        self.mydb.commit()

    # Get the records for match_ids
    def get_table_names(self) -> list:
        self.myCursor.execute("SELECT * FROM match_ids;")
        self.mydb.commit()
        return self.myCursor.fetchall()
    
    # Get data from one of the tables
    def get_match_stats(self, table: str) -> list:
        query = "SELECT * FROM {};"
        self.myCursor.execute(query.format(table))
        self.mydb.commit()
        return self.myCursor.fetchall()
    
    # Update the match data tables
    def update_match_stats(self, table1: str, table2: str, rec, names_list: list[str], identifier: int) -> None:

        # Ids of recs (only ever goes up to seven with these ones)
        ids = [1,2,3,4,5,6,7]

        # Query string
        query = "UPDATE {} SET games_won = {} WHERE set_num = {};"
        query1 = "UPDATE {} SET aces = {} WHERE set_num = {};"
        query2 = "UPDATE {} SET first_serve = {} WHERE set_num = {};"
        query3 = "UPDATE {} SET double_fault = {} WHERE set_num = {};"
        query4 = "UPDATE {} SET winner = {} WHERE set_num = {};"

        # Loop through and update
        for i, v in enumerate(ids):

            # For player one table
            self.myCursor.execute(query.format(table1, int(rec[0][i]), v))
            self.myCursor.execute(query1.format(table1, int(rec[1][i]), v))
            self.myCursor.execute(query2.format(table1, int(rec[2][i]), v))
            self.myCursor.execute(query3.format(table1, int(rec[3][i]), v))
            self.myCursor.execute(query4.format(table1, int(rec[4][i]), v))
            
            # For player two table
            self.myCursor.execute(query.format(table2, int(rec[5][i]), v))
            self.myCursor.execute(query1.format(table2, int(rec[6][i]), v))
            self.myCursor.execute(query2.format(table2, int(rec[7][i]), v))
            self.myCursor.execute(query3.format(table2, int(rec[8][i]), v))
            self.myCursor.execute(query4.format(table2, int(rec[9][i]), v))

        # Update in match_ids
        self.myCursor.execute("UPDATE match_ids SET match_name = '{}' WHERE Id = {}".format(names_list[0], identifier))
        self.myCursor.execute("UPDATE match_ids SET player_one_name = '{}' WHERE Id = {}".format(names_list[1], identifier))
        self.myCursor.execute("UPDATE match_ids SET player_two_name = '{}' WHERE Id = {}".format(names_list[2], identifier))
        self.myCursor.execute("UPDATE match_ids SET date_of_play = '{}' WHERE Id = {}".format(names_list[3], identifier))

        # Commit
        self.mydb.commit()

    # Delete match_stats
    def del_match_stats(self, table1: str, table2: str, identifier: int) -> None:

        # Delete tables, delete from match_ids
        self.myCursor.execute("DELETE FROM match_ids WHERE Id = {}".format(identifier))
        self.myCursor.execute("DROP TABLE {};".format(table1))
        self.myCursor.execute("DROP TABLE {};".format(table2))
        self.mydb.commit()

    # Insert an article into the table. Accepts website link from enum Websites
    def insert_article(self, host_site: Websites, article_link: str, article_content: str) -> None:
        query = "INSERT INTO news_articles VALUES (Id, %s, %s, %s);"
        self.myCursor.execute(query, (host_site.value, article_link, article_content,))
        self.mydb.commit()

    # Loading the articles from the table
    def load_saved_articles(self) -> list:
        query = "SELECT * FROM news_articles;"
        self.myCursor.execute(query)
        self.mydb.commit()
        return self.myCursor.fetchall()
    
    # Delete an article from the table
    def del_article(self, identifier: int) -> None:
        query = "DELETE FROM news_articles WHERE Id = {};"
        self.myCursor.execute(query.format(identifier))
        self.mydb.commit()

    # Update the article's contents, maybe the user translated it and wants to save
    def update_article(self, identifier: int, updated_contents: str):
        query = "UPDATE news_articles SET article_contents = %s WHERE Id = %s;"
        self.myCursor.execute(query, (updated_contents, identifier,))
        self.mydb.commit()
